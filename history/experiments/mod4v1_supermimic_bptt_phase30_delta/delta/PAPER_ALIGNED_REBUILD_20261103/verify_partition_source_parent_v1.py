"""Read-only parent verification of the frozen SOURCE partition (not native admission)."""
from pathlib import Path
import sys,hashlib,json,runpy,io,contextlib
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent.parent;D=R/'source_phase1_state_context_partition_v1';out=R/'reports/PHASE1_PARTITION_PARENT_SOURCE_VERIFY_V1.json';assert not out.exists();sealraw=(D/'SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(sealraw).hexdigest()=='e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630';seal=json.loads(sealraw);assert seal['content_root_sha256']=='0feb70e552a915ca698b87cdc7a4e3b22ee614e86ce55c2b9677a6f0e9c30bdf'and len(seal['files'])==9

def verify_seal():
 for name,meta in seal['files'].items():
  p=(D/name).resolve();assert p.is_relative_to(D)and p.suffix in{'.py','.json','.txt','.md'};raw=p.read_bytes();assert len(raw)==meta['bytes']and hashlib.sha256(raw).hexdigest()==meta['sha256']
 assert (D/'SOURCE_SEAL.json').read_bytes()==sealraw
verify_seal();manifest=json.loads((D/'source_manifest.json').read_bytes());count=0
for name,meta in manifest['sources'].items():
 p=(R/name).resolve();assert p.is_relative_to(R)and p.suffix in{'.py','.json'};raw=p.read_bytes();assert len(raw)==meta['bytes']and hashlib.sha256(raw).hexdigest()==meta['sha256'];count+=1
assert count==202
sys.path.insert(0,str(D));ns=runpy.run_path(str(D/'test_phase1_contract.py'),run_name='_parent_source_contract_tests');buf=io.StringIO()
with contextlib.redirect_stdout(buf):rc=ns['main']()
verify_seal();receipt=dict(kind='PARENT_PHASE1_PARTITION_SOURCE_VERIFY_V1',returncode=rc,sealed_members=9,upstream_source_metadata_identities=202,source_seal_SHA256=hashlib.sha256(sealraw).hexdigest(),content_root_SHA256=seal['content_root_sha256'],test_output=buf.getvalue(),sealed_artifacts_changed=False,SDK_GPU_model_raw_canonical_operations=0,actual_sdk_pass=False,exact=False,stage1_status='SOURCE_CONTRACT_FROZEN_GATE1_UNKNOWN')
with out.open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2)
print(json.dumps(dict(report=str(out),returncode=rc,sealed_members=9,source_ids=count,SDK_pass=False,gate='UNKNOWN'),indent=2));print(buf.getvalue());assert rc==0
