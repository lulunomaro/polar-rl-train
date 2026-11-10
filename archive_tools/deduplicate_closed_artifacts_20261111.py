"""Coalesce identical closed-stage model/trajectory files on one NTFS volume.

All original paths remain readable. Content is compared before every atomic
replacement. Only completed MOD4/RM2026 stages from October 2026 are eligible.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import stat
import time
from cleanup_local_workspace_20261111 import ROOT, PROTECTED_PREFIXES, safe_file, hashes, fingerprint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidates', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    args = parser.parse_args()
    groups = json.loads(args.candidates.read_text(encoding='utf-8'))
    result = dict(started_at=time.time(), free_before=shutil.disk_usage(ROOT).free,
                  considered=0, already_shared=0, linked=0, linked_bytes=0,
                  last_link_bytes=0, skipped=0, errors=[])
    allowed = {'.pt', '.pth', '.npz', '.npy', '.onnx'}
    log = args.archive / 'artifact_deduplication.jsonl.gz'
    with gzip.open(log, 'xt', encoding='utf-8', newline='\n') as output:
        for size, entries in sorted(groups.items(), key=lambda pair: int(pair[0]), reverse=True):
            by_digest = {}
            seen = {}
            for row in entries:
                parts = PureWindowsPath(row['path']).parts
                if (Path(parts[-1]).suffix.lower() not in allowed or
                        parts[0].startswith(PROTECTED_PREFIXES) or
                        not re.search(r'202610\d\d(?:$|_)', parts[0])):
                    result['skipped'] += 1
                    continue
                if not ROOT.joinpath(*parts).exists():
                    result['skipped'] += 1
                    continue
                try:
                    path = safe_file(row['path'])
                    info = path.stat()
                    identity = fingerprint(path)
                    if (info.st_size != int(size) or
                            info.st_file_attributes & stat.FILE_ATTRIBUTE_READONLY):
                        result['skipped'] += 1
                        continue
                    if identity[:2] in seen:
                        result['already_shared'] += 1
                        continue
                    before, _, sha = hashes(path)
                    result['considered'] += 1
                    donor_row = by_digest.get(sha)
                    if not donor_row:
                        by_digest[sha] = (row['path'], before)
                        seen[before[:2]] = row['path']
                        continue
                    donor = safe_file(donor_row[0])
                    if fingerprint(donor) != donor_row[1] or fingerprint(path) != before:
                        raise ValueError('Content changed before coalescing')
                    # Link first, then atomically replace the redundant file.
                    temp = path.with_name(path.name + '.cleanup20261111-link')
                    if temp.exists():
                        raise ValueError('Temporary link already exists')
                    os.link(donor, temp)
                    try:
                        if fingerprint(path) != before:
                            raise ValueError('Destination changed')
                        os.replace(temp, path)
                    finally:
                        if temp.exists():
                            temp.unlink()
                    if not os.path.samefile(path, donor):
                        raise ValueError('Hardlink replacement not observed')
                    output.write(json.dumps(dict(path=row['path'], retained_path=donor_row[0],
                                                 bytes=info.st_size, sha256=sha),
                                            ensure_ascii=False) + '\n')
                    result['linked'] += 1
                    result['linked_bytes'] += info.st_size
                    if info.st_nlink == 1:
                        result['last_link_bytes'] += info.st_size
                except (OSError, ValueError) as exc:
                    result['errors'].append(dict(path=row['path'], error=str(exc)))
            if result['linked'] and result['linked'] % 100 < 5:
                output.flush()
                print(json.dumps({k: result[k] for k in ('considered', 'linked', 'last_link_bytes')}), flush=True)
    result.update(finished_at=time.time(), free_after=shutil.disk_usage(ROOT).free)
    result['measured_free_delta'] = result['free_after'] - result['free_before']
    (args.archive / 'artifact_deduplication_summary.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
