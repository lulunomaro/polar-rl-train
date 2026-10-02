"""Verify first; optionally create a NEW candidate tree. Never patch the live project.

Default invocation is read-only. --create explicitly requests a separate candidate.
No shell commands, training, pip installs, git changes or service control are performed.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, shutil

PACKAGE = pathlib.Path(__file__).resolve().parents[1]

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda: stream.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def verified(source, contract):
    errors = []
    for rel, expected in contract['source_files'].items():
        p = source / rel
        if not p.is_file() or sha(p) != expected:
            errors.append(rel)
    for abs_path, expected in contract['runtime_files'].items():
        p = pathlib.Path(abs_path)
        if not p.is_file() or sha(p) != expected:
            errors.append(abs_path)
    for rel, expected in contract['overlay_files'].items():
        p = PACKAGE / 'overlay' / rel
        if not p.is_file() or sha(p) != expected:
            errors.append('PACKAGE/overlay/' + rel)
    if errors:
        raise ValueError('source/runtime/package changed; STOP and rebase the review patch: ' + ', '.join(errors))


def stage(source, destination, contract):
    source, destination = source.resolve(), destination.resolve()
    if destination == source or source in destination.parents or destination in source.parents:
        raise ValueError('candidate must be outside the live source and not an ancestor')
    if destination.exists():
        raise FileExistsError('candidate destination already exists')
    verified(source, contract)
    # Code/config copies are independent; large delivered assets remain read-only references
    # through incoming. PYTHONDONTWRITEBYTECODE=1 is mandatory in launch wrappers.
    destination.mkdir(parents=True)
    for name in ('isaac',):
        shutil.copytree(source/name, destination/name,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.bak', '*.usd', '*.usda', '*.usdc', '*.pt'))
    deploy = destination/'train/deploy'
    deploy.mkdir(parents=True)
    shutil.copy2(source/'train/deploy/contract_rm2025_later.json', deploy)
    for name in ('incoming', 'cad'):
        if (source/name).is_dir():
            (destination/name).symlink_to(source/name, target_is_directory=True)
    for p in (PACKAGE/'overlay').rglob('*'):
        if p.is_file() and p.suffix == '.py':
            target = destination/p.relative_to(PACKAGE/'overlay')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
    (destination/'REPAIR_ORIGIN.json').write_text(json.dumps({
        'package':str(PACKAGE), 'source':str(source), 'contract':contract}, indent=2), encoding='utf8')
    # Recheck source after copy. Concurrent source edits invalidate the candidate, even if
    # a user intended them; do not guess a three-way merge and never delete their edits.
    verified(source, contract)
    print('CANDIDATE_CREATED_NOT_RUN=' + str(destination))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default='/home/egde/fangzhen_linux')
    ap.add_argument('--destination')
    ap.add_argument('--create', action='store_true')
    args = ap.parse_args()
    contract = json.loads((PACKAGE/'baseline_manifest.json').read_text(encoding='utf8'))
    source = pathlib.Path(args.source)
    try:
        verified(source, contract)
        print('PASS_SOURCE_AND_PACKAGE_HASHES')
        if args.create:
            if not args.destination:
                raise ValueError('--create requires --destination')
            stage(source, pathlib.Path(args.destination), contract)
        return 0
    except (OSError, ValueError) as exc:
        print('STOP: ' + str(exc))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
