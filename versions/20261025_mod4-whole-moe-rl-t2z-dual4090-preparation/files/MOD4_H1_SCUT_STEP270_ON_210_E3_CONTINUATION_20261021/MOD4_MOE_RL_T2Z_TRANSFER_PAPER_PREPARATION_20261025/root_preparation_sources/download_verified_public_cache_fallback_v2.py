#!/usr/bin/env python3
"""Pinned official-content hashes via public cache transport; finite anonymous resumable download."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.error
import urllib.request
import uuid

ROOT = Path('/home/lc01/Zonglin Li/zonglin2/research/T2Z_MOE_RL_TRANSFER_PREP_20261025')
GUARD = 25*1024**3


def digest(path, algorithm='sha256', git_blob=False):
    h = hashlib.new(algorithm)
    if git_blob:
        h.update(f'blob {path.stat().st_size}\0'.encode())
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024**2), b''):
            h.update(block)
    return h.hexdigest()


def verify(path, item):
    if path.stat().st_size != item['bytes']:
        raise RuntimeError('Existing file size mismatch; preserved without overwrite')
    expected = item.get('lfs_sha256')
    if expected:
        actual = digest(path)
    else:
        expected = item.get('git_blob_sha1')
        actual = digest(path, 'sha1', git_blob=True)
    if not expected or actual != expected:
        raise RuntimeError('File digest mismatch or missing expected digest; preserved')
    return dict(bytes=path.stat().st_size,
                sha256=actual if item.get('lfs_sha256') else digest(path), expected_verified=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--manifest', type=Path, required=True)
    p.add_argument('--max-seconds', type=int, default=180)
    p.add_argument('--max-files', type=int, default=1)
    p.add_argument('--max-new-bytes', type=int, default=2*1024**3)
    p.add_argument('--verify-only', action='store_true')
    args = p.parse_args()
    if str(args.root) != str(ROOT) or args.root.resolve() != ROOT:
        p.error('Only exact approved research root permitted')
    if not 1 <= args.max_files <= 13 or not 10 <= args.max_seconds <= 1800:
        p.error('Use finite max-files1..13 and max-seconds10..1800')
    if not 1 <= args.max_new_bytes <= 50*1024**3:
        p.error('Use finite max-new-bytes up to50GiB')
    args.root.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text(encoding='utf-8-sig'))
    revisions={'Wan-AI/Wan2.2-TI2V-5B':'921dbaf3f1674a56f47e83fb80a34bac8a8f203e',
               'BLM-Lab/Boundless-World-Model':'738a8d3c008e637b8b1b18d5e98a82f6de9c04aa'}
    if (manifest['weights_total_bytes'] != 44253006084 or len(manifest['files']) != 13
            or sum(item['bytes'] for item in manifest['files']) != manifest['weights_total_bytes']):
        p.error('Unexpected minimum manifest; no download')
    for item in manifest['files']:
        if (revisions.get(item['repo_id']) != item['revision'] or
                item['url'] != f"https://huggingface.co/{item['repo_id']}/resolve/{item['revision']}/{item['file']}"):
            p.error('Only pinned official manifest URLs permitted')
    receipt_dir = args.root/'receipts'
    receipt_dir.mkdir(exist_ok=True)
    record = dict(id='T2ZMOE_FINITE_OFFICIAL_WEIGHT_PREP', epoch=time.time(),
                  manifest_sha256=digest(args.manifest), results=[], GPU_used=False,
                  training_started=False, authenticated=False, archive_status='PENDING_ROOT_GIT', transport_origin='hf-mirror.com public cache, identical pinned repo/revision/file', official_manifest_and_expected_full_hashes_unchanged=True)
    started = time.monotonic()
    new_bytes = 0
    processed = 0
    code = 0
    try:
        # No Authorization header, no token lookup, no HF login, no cookie jar.
        # Public official files are accessible anonymously at pinned revisions.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for item in manifest['files']:
            if time.monotonic()-started >= args.max_seconds:
                record['bounded_stop'] = True
                break
            target = args.root/item['destination']
            if not target.resolve().is_relative_to(ROOT):
                raise RuntimeError('Destination escaped research root')
            if target.is_file():
                if args.verify_only:
                    result = verify(target, item)
                    record['results'].append(dict(destination=item['destination'], status='EXISTING_VERIFIED', **result))
                else:
                    # Avoid repeatedly hashing all previous10GB files on every
                    # short resumable transfer. Final verify-only is mandatory.
                    record['results'].append(dict(destination=item['destination'],status='EXISTING_PRESENT_REQUIRES_FINAL_VERIFY'))
                continue
            if args.verify_only:
                record['results'].append(dict(destination=item['destination'], status='NOT_DOWNLOADED'))
                continue
            if processed >= args.max_files or time.monotonic()-started >= args.max_seconds or new_bytes >= args.max_new_bytes:
                record['bounded_stop'] = True
                break
            target.parent.mkdir(parents=True, exist_ok=True)
            partial = target.with_name(target.name+'.part')
            if not partial.resolve().is_relative_to(ROOT):
                raise RuntimeError('Partial destination escaped research root')
            offset = partial.stat().st_size if partial.exists() else 0
            if offset > item['bytes']:
                raise RuntimeError('Oversized partial preserved; manual review required')
            remaining = item['bytes']-offset
            if shutil.disk_usage(args.root).free-min(remaining, args.max_new_bytes-new_bytes) < GUARD:
                raise RuntimeError('Existing25GiB guard: own download stopped')
            if remaining:
                headers = {'User-Agent':'Mozilla/5.0'}
                if offset:
                    headers['Range'] = f'bytes={offset}-'
                transport_url=item['url'].replace('https://huggingface.co/','https://hf-mirror.com/',1)+'?download=true'
                req = urllib.request.Request(transport_url, headers=headers)
                with opener.open(req, timeout=20) as response:
                    if offset and (response.status != 206 or not response.headers.get('Content-Range','').startswith(f'bytes {offset}-')):
                        raise RuntimeError('Server did not honor resume range; existing partial preserved')
                    with partial.open('ab' if partial.exists() else 'xb') as stream:
                        while offset < item['bytes']:
                            if time.monotonic()-started >= args.max_seconds or new_bytes >= args.max_new_bytes:
                                break
                            room = min(4*1024**2, item['bytes']-offset, args.max_new_bytes-new_bytes)
                            if shutil.disk_usage(args.root).free-room < GUARD:
                                raise RuntimeError('Existing25GiB guard during download; partial preserved')
                            block = response.read(room)
                            if not block:
                                break
                            stream.write(block)
                            offset += len(block)
                            new_bytes += len(block)
                        stream.flush()
                        os.fsync(stream.fileno())
            if offset == item['bytes']:
                result = verify(partial, item)
                # Never replace an independently created complete file.
                if target.exists():
                    raise RuntimeError('Destination appeared; partial preserved without overwrite')
                partial.rename(target)
                record['results'].append(dict(destination=item['destination'], status='DOWNLOADED_VERIFIED', **result))
            else:
                record['results'].append(dict(destination=item['destination'], status='PARTIAL_RETAINED', bytes=offset))
            processed += 1
    except urllib.error.HTTPError as exc:
        # Do not print signed CDN URLs, headers, response bodies, or credentials.
        record.update(status='HTTP_FAILURE_PRESERVED', http_status=exc.code)
        code = 1
    except Exception as exc:
        record.update(status='FAILURE_PRESERVED', error_type=type(exc).__name__)
        # Reason strings produced by this script are safe; arbitrary network
        # exception strings can contain signed URLs and are deliberately omitted.
        if isinstance(exc, RuntimeError):
            record['reason'] = str(exc)
        code = 1
    record.setdefault('status', 'FINITE_PREPARATION_RETURNED')
    record['all_required_verified_in_this_receipt']=(len(record['results'])==13 and
        all(x['status'] in ('DOWNLOADED_VERIFIED','EXISTING_VERIFIED') for x in record['results']))
    record.update(new_bytes=new_bytes, elapsed_seconds=time.monotonic()-started,
                  free_bytes=shutil.disk_usage(args.root).free)
    out = receipt_dir/f'{time.time_ns()}_download_{uuid.uuid4().hex[:8]}.json'
    with out.open('x') as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps(dict(receipt=str(out), status=record['status'], new_bytes=new_bytes)))
    return code


if __name__ == '__main__':
    sys.exit(main())
