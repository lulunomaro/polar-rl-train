"""Compress the fixed list of large, closed-stage logs before removing copies."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PureWindowsPath
import shutil
import stat
import time
from cleanup_local_workspace_20261111 import ROOT, safe_file, fingerprint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidates', required=True, type=Path)
    parser.add_argument('--archive', required=True, type=Path)
    args = parser.parse_args()
    candidates = json.loads(args.candidates.read_text(encoding='utf-8'))
    store = args.archive / 'closed_text'
    store.mkdir(exist_ok=False)
    report = dict(started_at=time.time(), free_before=shutil.disk_usage(ROOT).free,
                  files=[], errors=[], missing=0)
    manifest = args.archive / 'large_text_relocation.json'
    for row in candidates:
        if not ROOT.joinpath(*PureWindowsPath(row['path']).parts).exists():
            report['missing'] += 1
            continue
        try:
            source = safe_file(row['path'])
            identity = fingerprint(source)
            if source.suffix.lower() not in ('.json', '.jsonl', '.txt', '.log'):
                raise ValueError('Outside large-log scope')
            if source.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY:
                raise ValueError('Read-only source retained')
            temp = store / 'current.gz'
            if temp.exists():
                raise FileExistsError(temp)
            sha = hashlib.sha256()
            with source.open('rb') as inp, gzip.open(temp, 'xb', compresslevel=3) as out:
                while raw := inp.read(1024 * 1024):
                    sha.update(raw)
                    out.write(raw)
            digest = sha.hexdigest()
            verification = hashlib.sha256()
            restored_bytes = 0
            with gzip.open(temp, 'rb') as inp:
                while raw := inp.read(1024 * 1024):
                    restored_bytes += len(raw)
                    verification.update(raw)
            if (verification.hexdigest() != digest or restored_bytes != identity[2]
                    or fingerprint(source) != identity):
                raise ValueError('Compression or source identity mismatch')
            destination = store / (digest + '.gz')
            if destination.exists():
                if hashlib.sha256(gzip.decompress(destination.read_bytes())).hexdigest() != digest:
                    raise ValueError('Existing content-addressed file mismatch')
                temp.unlink()
            else:
                temp.rename(destination)
            item = dict(original_path=row['path'], retained_path=str(destination),
                        bytes=identity[2], sha256=digest,
                        compressed_bytes=destination.stat().st_size)
            report['files'].append(item)
            # Persist the recovery record before removing this source.
            manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n',
                                encoding='utf-8')
            if fingerprint(source) != identity:
                raise ValueError('Source changed before deletion')
            source.unlink()
            item['expanded_copy_removed'] = True
        except (OSError, ValueError) as exc:
            report['errors'].append(dict(path=row['path'], error=str(exc)))
        if len(report['files']) and len(report['files']) % 20 == 0:
            print(json.dumps({'compressed_logs': len(report['files'])}), flush=True)
    report.update(finished_at=time.time(), free_after=shutil.disk_usage(ROOT).free)
    report['removed_files'] = sum(item.get('expanded_copy_removed', False) for item in report['files'])
    report['removed_bytes'] = sum(item['bytes'] for item in report['files'] if item.get('expanded_copy_removed'))
    report['compressed_bytes'] = sum(p.stat().st_size for p in store.glob('*.gz'))
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
