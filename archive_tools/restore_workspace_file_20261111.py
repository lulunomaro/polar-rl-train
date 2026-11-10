"""Recover a single path removed by the 2026-11-11 workspace cleanup.

Usage: python -B archive_tools/restore_workspace_file_20261111.py
       "MOD4_STAGE_202610xx/reports/file.json"
No existing file is overwritten. Git commit/blob and SHA256 are checked.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PureWindowsPath
import stat
import subprocess

ROOT = Path('C:/Users/lulu/Desktop/claude/mjcf')
REPO = ROOT / 'polar-rl-train'
ARCHIVE = Path('F:/RMPOLAR-RL/mjcf_workspace_cleanup_20261111')
COMMIT = '0876a1f8dd1698dc49b7e25b9b315a18055b2582'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('workspace_relative_path')
    args = parser.parse_args()
    relative = PureWindowsPath(args.workspace_relative_path)
    if relative.is_absolute() or any(part in ('.', '..') for part in relative.parts):
        raise ValueError('Expected a relative workspace path')
    path = ROOT.joinpath(*relative.parts)
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Path outside workspace')
    parent = ROOT
    for part in relative.parts[:-1]:
        parent = parent / part
        if parent.exists() and parent.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('Refusing to restore through a junction')
    if path.exists():
        raise FileExistsError(path)
    match = None
    raw = None
    compacted = json.loads((ARCHIVE / 'large_text_relocation.json').read_text(encoding='utf-8'))
    for item in compacted['files']:
        if PureWindowsPath(item['original_path']) == relative:
            match = item
            raw = gzip.decompress(Path(item['retained_path']).read_bytes())
            break
    if match is None:
        with gzip.open(ARCHIVE / 'deletions.jsonl.gz', 'rt', encoding='utf-8') as source:
            match = next((item for line in source
                          if PureWindowsPath((item := json.loads(line))['path']) == relative), None)
        if match is None:
            raise KeyError('No cleanup record for this path')
        raw = subprocess.check_output(['git', '-C', str(REPO), 'show',
                                       COMMIT + ':' + match['git_path']])
    if len(raw) != match['bytes'] or hashlib.sha256(raw).hexdigest() != match['sha256']:
        raise ValueError('Recovered content hash mismatch')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as output:
        output.write(raw)
    print(str(path))


if __name__ == '__main__':
    main()
