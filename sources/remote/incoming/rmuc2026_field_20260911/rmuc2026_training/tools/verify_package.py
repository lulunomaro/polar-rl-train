"""Verify the immutable delivery manifest before running tools that update reports."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'MANIFEST.sha256.json').read_text(encoding='utf8'))
    failures=[]
    for rel,expected in manifest['files'].items():
        path=(ROOT/rel).resolve()
        if not path.is_relative_to(ROOT.resolve()):raise ValueError(f'Unsafe manifest path: {rel}')
        actual=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        if actual!=expected:failures.append(rel)
    report=dict(status='PASS_PACKAGE_HASHES' if not failures else 'FAIL_PACKAGE_HASHES',
                checked_files=len(manifest['files']),failures=failures)
    print(json.dumps(report,indent=2))
    if failures:raise RuntimeError('Missing or modified delivery files. Re-extract or compare intended changes.')

if __name__=='__main__':main()
