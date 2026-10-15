"""One new namespace upload and actual target CPU; no GPU/lease/Task launch."""
from pathlib import Path
import hashlib,json,sys,time,traceback
D=Path(__file__).resolve().parent;Q=D/'payload';R=D/'reports'
import transport_whitev2_ABC_actual as t
ROOT=t.ROOT;SHARED='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(name,value):
    p=R/name;assert not p.exists();p.write_text(json.dumps(value,indent=2),encoding='utf8')

def main():
    proof=json.loads((R/'WHITEV2_ABC_CPU_PREPARED_ACTUAL.json').read_bytes());assert proof['CPU_prepared_no_remote_or_GPU']
    assert not (R/'WHITEV2_ABC_UPLOAD_INTENT.json').exists()
    z=Path(proof['package']['path']);assert H(z)==proof['package']['sha256']
    c=sf=None
    try:
        c=t.connect();guard=t.py(c,t.guard_code());assert guard['new_root_unused'] and guard['shared_OS_lock_free']
        save('WHITEV2_ABC_UPLOAD_INTENT.json',dict(epoch=time.time(),root=ROOT,package=proof['package'],guard=guard,unknown_outcome_readonly_recovery_not_retry=True))
        sf=c.open_sftp();sf.get_channel().settimeout(60);sf.mkdir(ROOT)
        with sf.open(ROOT+'/'+z.name,'wx') as f:f.write(z.read_bytes());f.flush()
        code=r'''
from pathlib import Path
import hashlib,json,zipfile,torch,sys,time,importlib.metadata as metadata
R=Path(ROOT);Q=R/'payload';S=Path(SHARED);z=R/ZIP;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert H(z)==ZIP_SHA and not Q.exists();Q.mkdir();(R/'attempts').mkdir();(R/'leases').mkdir()
with zipfile.ZipFile(z) as f:
 for name in f.namelist():
  p=Q/name;assert p.resolve().is_relative_to(Q.resolve()) and not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(f.read(name))
m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes());assert m['DR_profile']=='white_v2' and m['declared_development_seeds']==[20261002,20261003];assert H(Q/'RETENTION_CPU_MANIFEST_V8.json')==MANIFEST_SHA
for row in m['package_files_v8']:assert (Q/row['relative']).stat().st_size==row['bytes'] and H(Q/row['relative'])==row['sha256'],row['relative']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
assert H(m['V7_actual_native_binding']['path'])==m['V7_actual_native_binding']['sha256']
assert H(m['v5_sdk_primary_stub']['actual_installed_stub_path'])==m['v5_sdk_primary_stub']['actual_sha256']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for row in sdk['files']:assert H(row['path'])==row['sha256']
sys.path.insert(0,str(Q))
from s4_shared_feedback_hardtop1_v1 import PairRouter
from s4_eval_trained_gate_source_v1 import load_trained_gate
pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes());gate=json.loads((Q/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())
assert pair['allowed_modes']==['rule_eval','gate_eval'] and pair['no_gate_learning'] is True
router=PairRouter(pair['sources'],88,'cpu');proof=load_trained_gate(router,gate)
source=torch.load(gate['local_path'],map_location='cpu',weights_only=False);tensors=[]
def walk(x):
 if torch.is_tensor(x):assert x.device.type=='cpu' and (not x.is_floating_point() or torch.isfinite(x).all());tensors.append(x)
 elif hasattr(x,'items'):
  for v in x.values():walk(v)
 elif isinstance(x,(list,tuple)):
  for v in x:walk(v)
walk(source);assert len(tensors)==194 and sum(v.is_floating_point() for v in tensors)==113 and not torch.cuda.is_initialized()
for ref,expected in zip(pair['sources'],(94,102)):
 assert H(ref['local_path'])==ref['sha256'];tensors.clear();walk(torch.load(ref['local_path'],map_location='cpu',weights_only=False));assert sum(v.is_floating_point() for v in tensors)==expected
from s5_single_frozen35_v1 import Single35
rng=torch.get_rng_state().clone();single=Single35(pair['sources'][1]['local_path'],88,'cpu');assert single.exact() and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()

print(json.dumps(dict(epoch=time.time(),actual_targetCPU=True,source_gate_SHA=gate['sha256'],whole_tensors=194,floating=113,gate_proof=proof,
 package_SHA=H(z),manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),package_files=len(m['package_files_v8']),shared_files=len(m['shared_source_freeze']),
 SDK_stub_binding_and_all_source_SHA_actual=True,no_CUDA_PPO_or_budget_write=True)))
'''
        prefix='ROOT='+repr(ROOT)+'\nSHARED='+repr(SHARED)+'\nZIP='+repr(z.name)+'\nZIP_SHA='+repr(proof['package']['sha256'])+'\nMANIFEST_SHA='+repr(proof['manifest_SHA'])+'\n'
        actual=t.py(c,prefix+code,90);save('WHITEV2_ABC_UPLOAD_TARGET_CPU_ACTUAL.json',actual)
        print(json.dumps(actual),flush=True)
    except BaseException:
        save('WHITEV2_ABC_UPLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_unknown_mutation_actual_readonly_first=True));raise
    finally:
        if sf:sf.close()
        t.close(c)

if __name__=='__main__':main()
