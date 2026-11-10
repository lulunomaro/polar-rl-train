"""Remove only byte-verified historical copies; keep their Git recovery mapping.

This dated maintenance operation does not launch experiments or follow junctions.
The input is the pre-cleanup inventory, not a recursive deletion expression.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import shutil
import stat
import subprocess
import time


ROOT = Path('C:/Users/lulu/Desktop/claude/mjcf')
REPO = ROOT / 'polar-rl-train'
PROTECTED_PREFIXES = ('MOD4_LOCAL_', 'MOD4_LATEST_HYBRID_', 'MOD4_MATLAB_',
                      'MOD4_H1_MATLAB_')


def git(*args, input=None):
    return subprocess.run(['git', '-C', str(REPO), *args], input=input,
                          capture_output=True, check=True).stdout


def safe_file(relative):
    parts = PureWindowsPath(relative).parts
    if not parts or any(p in ('.', '..') for p in parts):
        raise ValueError('Invalid relative path')
    if not parts[0].startswith(('MOD4_', 'RM2026_')):
        raise ValueError('Outside historical scope')
    path = ROOT.joinpath(*parts)
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Resolved path outside workspace')
    current = ROOT
    for part in parts:
        current = current / part
        info = current.lstat()
        if info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('Reparse point')
    if not path.is_file():
        raise ValueError('Not a regular file')
    return path


def fingerprint(path):
    info = path.stat()
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


def hashes(path):
    before = fingerprint(path)
    blob = hashlib.sha1(b'blob ' + str(before[2]).encode() + b'\0')
    sha = hashlib.sha256()
    with path.open('rb') as source:
        while raw := source.read(1024 * 1024):
            blob.update(raw)
            sha.update(raw)
    if fingerprint(path) != before:
        raise ValueError('File changed during hashing')
    return before, blob.hexdigest(), sha.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inventory', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.inventory.read_text(encoding='utf-8'))
    head = git('rev-parse', 'HEAD').decode().strip()
    if head != data['head']:
        raise ValueError('Repository moved since inventory')
    if git('status', '--porcelain=v1', '--untracked-files=no'):
        raise ValueError('Tracked worktree is not clean')
    args.archive.mkdir(parents=True, exist_ok=False)
    summary = dict(root=str(ROOT), repository=str(REPO), recovery_commit=head,
                   started_at=time.time(), free_before=shutil.disk_usage(ROOT).free,
                   checked=0, matched=0, matched_bytes=0, protected=0,
                   unmatched=0, changed=0, deleted=0, deleted_bytes=0,
                   last_link_bytes=0, errors=[])
    sizes = {row['bytes'] for row in data['git_files'].values()}
    matches = []
    plan = args.archive / 'git_verified_duplicates.jsonl.gz'
    with gzip.open(plan, 'xt', encoding='utf-8', newline='\n') as output:
        for row in data['candidates']:
            parts = PureWindowsPath(row['path']).parts
            name = parts[-1].upper()
            if (parts[0].startswith(PROTECTED_PREFIXES) or
                    any(token in name for token in ('CANONICAL', 'LEDGER', 'BUDGET')) or
                    any(p.lower() in ('.git', '.venv', 'venv', 'node_modules') for p in parts) or
                    Path(name).suffix.lower() in ('.lock', '.key', '.pem')):
                summary['protected'] += 1
                continue
            if row['bytes'] not in sizes:
                continue
            try:
                path = safe_file(row['path'])
                identity, oid, sha = hashes(path)
                summary['checked'] += 1
                git_path = data['git_oid_path'].get(oid)
                if not git_path:
                    summary['unmatched'] += 1
                    continue
                item = dict(path=row['path'], bytes=identity[2], sha256=sha,
                            git_blob=oid, git_path=git_path, identity=identity)
                output.write(json.dumps(item, ensure_ascii=False) + '\n')
                matches.append(item)
                summary['matched'] += 1
                summary['matched_bytes'] += identity[2]
            except (OSError, ValueError) as exc:
                summary['errors'].append(dict(path=row['path'], error=str(exc)))
            if summary['checked'] and summary['checked'] % 20000 == 0:
                print(json.dumps({'hash_progress': summary['checked'],
                                  'matched': summary['matched']}), flush=True)
    # Check all recovery objects before deleting any working copy.
    objects = sorted({row['git_blob'] for row in matches})
    checked = git('cat-file', '--batch-check',
                  input=('\n'.join(objects) + '\n').encode()).decode().splitlines()
    if len(checked) != len(objects) or any(' missing' in row or ' blob ' not in row for row in checked):
        raise ValueError('Missing recovery blob; no deletion performed')
    with gzip.open(args.archive / 'deletions.jsonl.gz', 'xt',
                   encoding='utf-8', newline='\n') as journal:
        for row in matches:
            try:
                path = safe_file(row['path'])
                if fingerprint(path) != tuple(row['identity']):
                    summary['changed'] += 1
                    continue
                info = path.stat()
                # Windows read-only flags are not permission grants; skip them.
                if info.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY:
                    summary['changed'] += 1
                    continue
                path.unlink()
                journal.write(json.dumps(row, ensure_ascii=False) + '\n')
                summary['deleted'] += 1
                summary['deleted_bytes'] += row['bytes']
                if info.st_nlink == 1:
                    summary['last_link_bytes'] += row['bytes']
            except (OSError, ValueError) as exc:
                summary['errors'].append(dict(path=row['path'], error=str(exc)))
            if summary['deleted'] and summary['deleted'] % 20000 == 0:
                journal.flush()
                print(json.dumps({'delete_progress': summary['deleted']}), flush=True)
    # Remove only empty directories under the historical parents just processed.
    parents = {ROOT.joinpath(*PureWindowsPath(row['path']).parts).parent for row in matches}
    while parents:
        next_parents = set()
        for parent in sorted(parents, key=lambda p: len(p.parts), reverse=True):
            if parent == ROOT or not parent.is_relative_to(ROOT):
                continue
            try:
                if parent.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
                    continue
                parent.rmdir()
                next_parents.add(parent.parent)
            except OSError:
                pass
        parents = next_parents
    summary.update(finished_at=time.time(), free_after=shutil.disk_usage(ROOT).free)
    summary['measured_free_delta'] = summary['free_after'] - summary['free_before']
    (args.archive / 'duplicates_summary.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
