"""Execute the unchanged donor audit; redirect its sole output into this workspace."""
from nav_common import HERE, DONOR, put, sha256
import argparse
import runpy
import sys

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tag', default='before')
    p.add_argument('--official-only', action='store_true')
    args = p.parse_args()
    import fsm_io
    output = HERE / 'evidence' / f'PROTECTION_{args.tag.upper()}.json'
    def redirected(path, obj):
        if str(path).endswith('PROTECTION_VERIFICATION.json'):
            put(output, obj)
        else:
            raise RuntimeError(f'Unexpected donor audit write: {path}')
    fsm_io.put = redirected
    sys.argv = [str(DONOR / 'audit_assets.py'), '--verify']
    runpy.run_path(sys.argv[0], run_name='__main__')
    if args.official_only:return
    local = {str(path): sha256(path) for path in sorted(DONOR.rglob('*'))
             if path.is_file() and path.suffix in ('.py', '.pt', '.json', '.xml', '.bat')
             and '__pycache__' not in path.parts}
    if args.tag == 'before':
        put(HERE / 'evidence/DONOR_BASELINE.json', local)
    else:
        import json
        old = json.loads((HERE / 'evidence/DONOR_BASELINE.json').read_text(encoding='utf-8'))
        changed = [name for name, digest in old.items() if local.get(name) != digest]
        put(HERE / 'evidence/DONOR_FINAL.json', dict(files=len(old), changed=changed, passed=not changed))
        if changed:
            raise RuntimeError('Read-only manual donor changed')

if __name__ == '__main__':
    main()
