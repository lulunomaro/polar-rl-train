#!/usr/bin/env python3
"""Offline source/manifest/verification helper QA. Does not run remote preparation."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

z=Path(__file__).resolve().parents[1]
records=[]
for file in sorted((z/'scripts').glob('*.py')):
    ast.parse(file.read_text(encoding='utf-8-sig'))
    records.append(dict(check='PYTHON_AST', file=str(file.relative_to(z)), result='PASS'))
manifest=json.loads((z/'WEIGHTS_MANIFEST.json').read_text(encoding='utf-8-sig'))
assert len(manifest['files'])==13
assert sum(x['bytes'] for x in manifest['files'])==44253006084
assert len({x['destination'] for x in manifest['files']})==13
assert all(x['lfs_sha256'] or x['git_blob_sha1'] for x in manifest['files'])
for repo in manifest['repository_metadata']:
    meta=json.loads((z/repo['metadata_snapshot']).read_text(encoding='utf-8-sig'))
    assert repo['revision']==meta['sha']
    for item in [x for x in manifest['files'] if x['repo_id']==repo['repo_id']]:
        official=next(x for x in meta['siblings'] if x['rfilename']==item['file'])
        assert item['bytes']==official['size']
        assert item['git_blob_sha1']==official['blobId']
        if official.get('lfs'):
            assert item['lfs_sha256']==official['lfs']['sha256']
records.append(dict(check='MANIFEST13_SIZE_REVISION_DIGEST_METADATA_MATCH',result='PASS'))
spec=importlib.util.spec_from_file_location('t2z_download_qa',z/'scripts/download_required.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
# Use a small retained binary with no model/data content.
test=z/'reports/SYNTHETIC_HASH_FIXTURE.txt'
if not test.exists():
    test.write_bytes(b'T2ZH1 synthetic digest fixture, no training data\n')
b=test.read_bytes()
sha=hashlib.sha256(b).hexdigest()
blob=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
assert mod.verify(test,dict(bytes=len(b),lfs_sha256=sha))['expected_verified']
assert mod.verify(test,dict(bytes=len(b),lfs_sha256=None,git_blob_sha1=blob))['expected_verified']
for bad in (dict(bytes=len(b)+1,lfs_sha256=sha),dict(bytes=len(b),lfs_sha256='0'*64)):
    try:
        mod.verify(test,bad)
    except RuntimeError:
        pass
    else:
        raise AssertionError('Corrupt file must fail')
records.append(dict(check='SMALL_SYNTHETIC_SHA256_GITBLOB_POSITIVE_AND_CORRUPTION_NEGATIVE',result='PASS'))
for name in ('prepare_isolated.py','download_required.py','cpu_import_interface_check.py'):
    proc=subprocess.run([sys.executable,'-B',str(z/'scripts'/name),'--help'],capture_output=True,timeout=10)
    assert proc.returncode==0
    records.append(dict(check='CLI_HELP_ONLY',file=name,result='PASS'))
out=z/'reports'/f'LOCAL_VALIDATION_{time.time_ns()}_ACTUAL.json'
with out.open('x') as stream:
    json.dump(dict(id='T2ZH1_ENG_LOCAL_OFFLINE_QA',epoch=time.time(),python=sys.version,
                   records=records,remote_stage_executed=False,environment_installed=False,
                   official_CPU_import_executed=False,weights_downloaded=False,GPU_used=False,
                   H1_adapter_tested=False,archive_status='PENDING_ROOT_GIT'),stream,indent=2)
print(json.dumps(dict(receipt=str(out),checks=len(records),status='PASS_OFFLINE_BUNDLE_ONLY')))
