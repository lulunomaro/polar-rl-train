"""Freeze existing LQR evidence without running controllers or changing sources.

Run from any directory with Python 3.11+. This program only reads the explicitly
named source directory. It writes a NEW version directory, retaining source text
bytes and indexing binary artifacts. It never stages, commits, tags, or pushes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile

sys.dont_write_bytecode = True
TEXT_SUFFIXES = {'.py', '.sh', '.md', '.json', '.jsonl', '.csv', '.xml', '.txt',
                 '.yaml', '.yml', '.toml', '.ini', '.cfg', '.tsv', '.sha256'}
SKIP_PARTS = {'__pycache__', '.git', '.venv', 'node_modules', '.ssh', '.aws', '.azure'}
ARCHIVE_NAME = 'MOD4_LQR_MPC_STEP270_20261101.tar.gz'
TAR_ROOT = 'MOD4_MUJOCO_LQR_MPC_STEP270_20261101'
VERSION_NAME = '20261101-lqr-mpc-step270'


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def stable_bytes(path: Path) -> bytes:
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError('Source changed during capture: ' + str(path))
    return raw


def safe_relative(value: str) -> str:
    item = PurePosixPath(value)
    if item.is_absolute() or '..' in item.parts or '\\' in value or not item.parts:
        raise ValueError('Unexpected archive member path')
    return item.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    repo = args.repo.resolve()
    dest = repo / 'versions' / VERSION_NAME
    meta = dest / '_archive'
    script = Path(__file__).resolve()
    existing = [p for p in dest.rglob('*') if p.is_file() and p.resolve() != script]
    if existing:
        raise FileExistsError('Archive already contains files; preserve the first capture')
    meta.mkdir(parents=True, exist_ok=True)
    scanner_spec = importlib.util.spec_from_file_location('mod4_existing_redactor', repo / 'archive_tools' / 'capture_history.py')
    scanner = importlib.util.module_from_spec(scanner_spec)
    scanner_spec.loader.exec_module(scanner)

    captured_at = datetime.now(timezone.utc).isoformat()
    manifest_raw = stable_bytes(source / 'TASK_ARCHIVE_MANIFEST.json')
    original_manifest = json.loads(manifest_raw)['files']
    original_receipt = json.loads(stable_bytes(source / 'ARCHIVE_RECEIPT.json'))
    tar_path = source / ARCHIVE_NAME
    tar_before = tar_path.stat()
    tar_bytes = stable_bytes(tar_path)
    tar_sha = digest(tar_bytes)
    if len(tar_bytes) != original_receipt['bytes'] or tar_sha != original_receipt['sha256']:
        raise RuntimeError('Original archive receipt does not match the source archive')
    del tar_bytes

    entries: dict[str, dict] = {}
    jsonl_rows: list[dict] = []
    individual_results: list[dict] = []
    summary_files: list[dict] = []
    tar_paths: set[str] = set()
    local_paths: set[str] = set()
    ignored_caches: list[str] = []
    scan_count = 0

    def consume(rel: str, raw: bytes, origin: dict) -> None:
        nonlocal scan_count
        rel = safe_relative(rel)
        sha = digest(raw)
        if rel in entries:
            previous = entries[rel]
            if previous['source_sha256'] != sha or previous['bytes'] != len(raw):
                raise RuntimeError('Local and tar evidence differ: ' + rel)
            previous['origins'].append(origin)
            return
        suffix = PurePosixPath(rel).suffix.lower()
        is_text = suffix in TEXT_SUFFIXES
        row = {'source_relative_path': rel, 'bytes': len(raw), 'source_sha256': sha,
               'origins': [origin], 'coverage': 'full_text' if is_text else 'artifact_index_only',
               'source_unchanged_during_read': True}
        if any(part.lower() in {'.ssh', '.aws', '.azure'} for part in PurePosixPath(rel).parts):
            raise ValueError('Credential directory unexpectedly present')
        if is_text:
            text = raw.decode('utf-8')
            cleaned, hit_count = scanner.redact(text)
            scan_count += 1
            if cleaned != text:
                raise ValueError('Credential scanner matched file; review before capture: ' + rel)
            if 'transcript' in PurePosixPath(rel).name.lower():
                raise ValueError('Transcript needs separate review: ' + rel)
            target = dest / rel
            if target.exists():
                raise FileExistsError('Preserve existing archive bytes: ' + str(target))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            row.update(repository_path=target.relative_to(repo).as_posix(),
                       archive_sha256=sha, redactions=0, archive_bytes=len(raw))
            if suffix == '.jsonl':
                count = 0
                for line_number, line in enumerate(text.splitlines(), 1):
                    if not line.strip():
                        continue
                    payload = json.loads(line)
                    count += 1
                    record = {'archive_attempt_id': rel + '#line-' + str(line_number),
                              'source_path': rel, 'source_line': line_number,
                              'line_sha256': digest(line.encode('utf-8')),
                              'state_authority': 'original record at source_path/source_line'}
                    if isinstance(payload, dict):
                        if 'id' in payload:
                            record['original_id'] = payload['id']
                        if 'score' in payload:
                            record['original_score'] = payload['score']
                        result = payload.get('result', payload)
                        if isinstance(result, dict):
                            for key in ('success', 'stop', 'stop_reason', 'seed', 'mpc', 'full_dr', 'dr'):
                                if key in result:
                                    record['original_' + key] = result[key]
                    jsonl_rows.append(record)
                row['jsonl_records'] = count
            elif suffix == '.json':
                payload = json.loads(text)
                if PurePosixPath(rel).name == 'result.json':
                    result_row = {'archive_attempt_id': rel, 'source_path': rel,
                                  'state_authority': 'original result; names are not success evidence'}
                    if isinstance(payload, dict):
                        for key in ('success', 'stop', 'stop_reason', 'seed', 'mpc', 'full_dr', 'dr'):
                            if key in payload:
                                result_row['original_' + key] = payload[key]
                    individual_results.append(result_row)
                if PurePosixPath(rel).name == 'summary.json':
                    summary_row = {'source_path': rel, 'bytes': len(raw), 'sha256': sha,
                                   'coverage': 'complete original report'}
                    if isinstance(payload, dict):
                        summary_row['list_lengths'] = {k: len(v) for k, v in payload.items() if isinstance(v, list)}
                    summary_files.append(summary_row)
            row['scanner_matches'] = 0
        else:
            row['retained_original'] = 'source archive member and/or unchanged local file; not committed'
        entries[rel] = row

    with tarfile.open(tar_path, 'r:gz') as tf:
        for member in tf:
            if not member.isfile():
                raise ValueError('Only regular files expected in source archive')
            path = PurePosixPath(member.name)
            if path.parts[0] != TAR_ROOT:
                raise ValueError('Unexpected archive root')
            rel = safe_relative('/'.join(path.parts[1:]))
            if rel in tar_paths:
                raise ValueError('Duplicate archive member: ' + rel)
            tar_paths.add(rel)
            raw = tf.extractfile(member).read()
            if len(raw) != member.size:
                raise ValueError('Incomplete archive read: ' + rel)
            if rel in original_manifest:
                expected = original_manifest[rel]
                if len(raw) != expected['bytes'] or digest(raw) != expected['sha256']:
                    raise ValueError('Original manifest mismatch: ' + rel)
            elif rel != 'TASK_ARCHIVE_MANIFEST.json':
                raise ValueError('Unexpected member missing from original manifest: ' + rel)
            consume(rel, raw, {'kind': 'tar_member', 'archive': str(tar_path),
                               'archive_sha256': tar_sha, 'member': member.name,
                               'member_mtime': member.mtime})
    if set(original_manifest) - tar_paths:
        raise ValueError('Source manifest has files absent from tar')
    if (tar_before.st_size, tar_before.st_mtime_ns) != (tar_path.stat().st_size, tar_path.stat().st_mtime_ns):
        raise RuntimeError('Archive changed during capture')

    for item in sorted(source.rglob('*')):
        if not item.is_file():
            continue
        rel = item.relative_to(source).as_posix()
        if any(part in SKIP_PARTS for part in item.relative_to(source).parts):
            ignored_caches.append(rel)
            continue
        if item.is_symlink():
            raise ValueError('Unexpected source symlink: ' + rel)
        local_paths.add(rel)
        raw = stable_bytes(item)
        consume(rel, raw, {'kind': 'local_file', 'path': str(item),
                           'mtime_ns': item.stat().st_mtime_ns})

    ordered = [entries[key] for key in sorted(entries)]
    full = [entry for entry in ordered if entry['coverage'] == 'full_text']
    indexed = [entry for entry in ordered if entry['coverage'] == 'artifact_index_only']
    required_root = [rel for rel in local_paths if '/' not in rel and PurePosixPath(rel).suffix.lower() in {'.py','.sh','.md','.json','.csv'}]
    if any(entries[rel]['coverage'] != 'full_text' for rel in required_root):
        raise RuntimeError('Required local root text was omitted')
    for entry in full:
        actual = (repo / entry['repository_path']).read_bytes()
        if len(actual) != entry['bytes'] or digest(actual) != entry['source_sha256']:
            raise RuntimeError('Captured bytes do not match source: ' + entry['source_relative_path'])
    totals = {'unique_source_files': len(ordered), 'tar_member_files': len(tar_paths),
              'original_manifest_files_verified': len(original_manifest),
              'local_source_files_excluding_caches': len(local_paths),
              'tar_only_files': len(tar_paths - local_paths),
              'local_only_files': len(local_paths - tar_paths),
              'shared_files_verified_equal': len(tar_paths & local_paths),
              'full_text_files': len(full), 'full_text_bytes': sum(x['bytes'] for x in full),
              'indexed_artifact_files': len(indexed), 'indexed_artifact_bytes': sum(x['bytes'] for x in indexed),
              'root_text_files_required_and_captured': len(required_root),
              'model_xml_files_captured': sum(x['source_relative_path'].startswith('model/') and x['source_relative_path'].endswith('.xml') for x in full),
              'summary_reports_captured': len(summary_files),
              'jsonl_files_captured': sum(x['source_relative_path'].endswith('.jsonl') for x in full),
              'jsonl_records_indexed': len(jsonl_rows),
              'individual_result_files_indexed': len(individual_results),
              'text_scanner_files_checked': scan_count, 'text_scanner_matches': 0,
              'local_tar_conflicts': 0, 'archive_manifest_mismatches': 0}
    inventory = {'schema': 'mod4.lqr.git_source_coverage.v1', 'captured_at_utc': captured_at,
                 'source_root': str(source), 'archive_path': str(tar_path),
                 'archive_bytes': tar_before.st_size, 'archive_sha256': tar_sha,
                 'source_tar_root': TAR_ROOT, 'version_root': dest.relative_to(repo).as_posix(),
                 'original_manifest_sha256': digest(manifest_raw), 'totals': totals,
                 'tar_only_paths': sorted(tar_paths-local_paths),
                 'local_only_paths': sorted(local_paths-tar_paths),
                 'ignored_cache_files': ignored_caches, 'files': ordered}
    save_json(meta / 'SOURCE_COVERAGE.json', inventory)
    save_json(meta / 'ARTIFACT_INDEX.json', {'schema':'mod4.lqr.binary_artifact_index.v1',
              'captured_at_utc':captured_at, 'index_only':True,
              'sha256_provenance':'computed from actual unchanged local bytes or the verified tar member',
              'files':indexed})
    with (meta / 'ATTEMPT_INDEX.jsonl').open('w', encoding='utf-8', newline='\n') as output:
        for item in jsonl_rows + individual_results:
            output.write(json.dumps(item, ensure_ascii=False, separators=(',',':')) + '\n')
    save_json(meta / 'REPORT_INDEX.json', {'schema':'mod4.lqr.report_index.v1',
              'summary_reports':summary_files, 'individual_results':individual_results,
              'jsonl_files':[{'source_path':x['source_relative_path'],'records':x['jsonl_records'],
                             'sha256':x['source_sha256']} for x in full if 'jsonl_records' in x],
              'all_text_files':[x['source_relative_path'] for x in full]})
    receipt = {'schema':'mod4.lqr.git_stage_receipt.v1', 'captured_at_utc':captured_at,
               'source_root':str(source), 'version_root':dest.relative_to(repo).as_posix(),
               'source_archive_verified_against_original_receipt':True,
               'all_original_manifest_files_verified':True, 'all_captured_text_byte_identical':True,
               'source_writes':False,'controllers_or_trials_rerun':False,
               'git_index_staged':False,'git_commit_created':False,'git_tag_created':False,
               'git_push_performed':False,'git_state':'pending parent confirmation and RL file completion',
               'totals':totals,
               'source_coverage_sha256':digest((meta/'SOURCE_COVERAGE.json').read_bytes()),
               'artifact_index_sha256':digest((meta/'ARTIFACT_INDEX.json').read_bytes()),
               'attempt_index_sha256':digest((meta/'ATTEMPT_INDEX.jsonl').read_bytes()),
               'report_index_sha256':digest((meta/'REPORT_INDEX.json').read_bytes()),
               'reader_attempts':[{'id':'capture-reader-01','status':'failed before writing',
                                  'issue':'Initial listing assumed tar prefix equals local source directory name; real tar root differs.',
                                  'resolution':'Read observed tar root and validate against MOD4_MUJOCO_LQR_MPC_STEP270_20261101; no evidence bytes changed.'}]}
    save_json(meta/'STAGE_RECEIPT.json', receipt)
    print(json.dumps({'stage':'prepared_without_commit','totals':totals,
                      'version_root':str(dest),'tar_only_files_sample':sorted(tar_paths-local_paths)[:5]},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
