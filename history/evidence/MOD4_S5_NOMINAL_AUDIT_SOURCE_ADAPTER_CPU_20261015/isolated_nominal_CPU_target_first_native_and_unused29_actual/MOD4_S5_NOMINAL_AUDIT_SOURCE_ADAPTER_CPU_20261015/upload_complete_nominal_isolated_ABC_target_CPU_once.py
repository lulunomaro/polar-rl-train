"""One unused-namespace upload and actual target CPU source/model verification.

No AppLauncher, GPU task, lease or learning. Unknown mutation outcome is not retried.
"""
from pathlib import Path
import hashlib
import json
import time
import traceback
import transport_nominal_isolated_ABC_actual as t

D=Path(__file__).resolve().parent
R=D/'reports'
ROOT=t.ROOT
SHARED='D:/MOD4_async_eval/MOD4_3060_LEFT_REPAIR_FULL80_20261014/payload'


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()


def save(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)


def main():
    proof=json.loads((R/'NOMINAL_COMPLETE_ISOLATED_ABC_CPU_PREPARED_ACTUAL.json').read_bytes())
    assert proof['CPU_prepared_no_remote_or_GPU'] and proof['actual_target_CPU_import_GPU_native_readback_not_yet_passed']
    assert not (R/'NOMINAL_COMPLETE_ABC_UPLOAD_INTENT_ACTUAL.json').exists()
    z=Path(proof['package']['path']);assert sha(z)==proof['package']['sha256']
    c=sf=None
    try:
        c=t.connect();guard=t.py(c,t.guard_code())
        assert guard['new_root_unused'] and guard['shared_OS_lock_free']
        save('NOMINAL_COMPLETE_ABC_UPLOAD_INTENT_ACTUAL.json',dict(epoch=time.time(),root=ROOT,package=proof['package'],guard=guard,
            unknown_mutation_outcome_requires_readonly_recovery_no_retry=True,no_GPU_lease_Task_or_budget=True))
        sf=c.open_sftp();sf.get_channel().settimeout(60);sf.mkdir(ROOT)
        with sf.open(ROOT+'/'+z.name,'wx') as f:
            with z.open('rb') as src:
                for b in iter(lambda:src.read(1024*1024),b''):f.write(b)
            f.flush()
        code=r'''
from pathlib import Path
import ast,hashlib,importlib.machinery,importlib.metadata as metadata,json,os,sys,time,zipfile,torch
R=Path(ROOT);Q=R/'payload';S=Path(SHARED);I=Q/'frozen_shared';z=R/ZIP
def H(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
assert H(z)==ZIP_SHA and not Q.exists()
Q.mkdir();(R/'attempts').mkdir();(R/'leases').mkdir()
with zipfile.ZipFile(z) as f:
 for name in f.namelist():
  p=Q/name;assert p.resolve().is_relative_to(Q.resolve()) and not p.exists()
  p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(f.read(name))
m=json.loads((Q/'RETENTION_CPU_MANIFEST_V8.json').read_bytes())
assert H(Q/'RETENTION_CPU_MANIFEST_V8.json')==MANIFEST_SHA
assert m['namespace']==Path(ROOT).name and m['DR_profile']=='nominal' and m['approved_GPU'] is False
assert m['declared_development_seeds']==[20261002,20261003] and len(m['source_overlay'])==8
for row in m['package_files_v8']:
 p=Q/row['relative'];assert p.stat().st_size==row['bytes'] and H(p)==row['sha256'],row['relative']
for row in m['shared_source_freeze']:assert H(S/row['relative'])==row['sha256'],row['relative']
for row in m['isolated_source_freeze']:assert H(Q/row['relative'])==row['sha256'],row['relative']
assert H(m['V7_actual_native_binding']['path'])==m['V7_actual_native_binding']['sha256']
assert H(m['v5_sdk_primary_stub']['actual_installed_stub_path'])==m['v5_sdk_primary_stub']['actual_sha256']
sdk=json.loads((S/'EXPECTED_INSTALLED_3060_BACKEND_V2.json').read_bytes())
for name,version in sdk['versions'].items():
 if version is not None:assert metadata.version(name)==version
for row in sdk['files']:assert H(row['path'])==row['sha256']
search=[str(I/'runtime/isaac/mod4'),str(I/'runtime'),str(Q),str(I),str(S)]
origins={}
for name in ('nominal_d0_source_audit_v1','spring_pressure_audit_runtime','gas_damping_sdk_adapter','chassis_com_pose_roundtrip_sdk_adapter',
 'explicit_pd_sdk_adapter','chassis_pd_training_env','nominal_parameter_audit','factor_runtime_3060_reference17b_v1','mod4_task',
 's5_ABC_evaluation_adapter_v1','retention_native_witness_v8'):
 spec=importlib.machinery.PathFinder.find_spec(name,search);assert spec and Path(spec.origin).resolve().is_relative_to(Q.resolve())
 origins[name]=dict(path=str(Path(spec.origin).resolve()),sha256=H(spec.origin),resolution_only_not_SDK_import=True)
for p in Q.rglob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
sys.path[:0]=search
import nominal_d0_source_audit_v1 as own
assert Path(own.__file__).resolve()==(I/'runtime/isaac/mod4/nominal_d0_source_audit_v1.py').resolve()
from types import SimpleNamespace
rng=torch.get_rng_state().clone()
os.environ['RM_MILD_DR_PROFILE']='nominal';os.environ['RM_DR_OFF']='1'
assert own.mild_dr_present_or_nominal(SimpleNamespace()) is False
os.environ['RM_MILD_DR_PROFILE']='white_v3'
try:own.mild_dr_present_or_nominal(SimpleNamespace())
except RuntimeError:pass
else:raise AssertionError('Missing MildDR was incorrectly allowed outside explicit nominal')
os.environ['RM_MILD_DR_PROFILE']='nominal'
from s4_shared_feedback_hardtop1_v1 import PairRouter
from s4_eval_trained_gate_source_v1 import load_trained_gate
from s5_single_frozen35_v1 import Single35
pair=json.loads((Q/'S4_PAIR_SOURCE_MANIFEST.json').read_bytes());gate=json.loads((Q/'S4_TRAINED_GATE_SOURCE_MANIFEST.json').read_bytes())
router=PairRouter(pair['sources'],88,'cpu');gateproof=load_trained_gate(router,gate)
single=Single35(pair['sources'][1]['local_path'],88,'cpu');assert single.exact()
whole=[]
for path,expected,tensors_expected in [(pair['sources'][0]['local_path'],94,None),(pair['sources'][1]['local_path'],102,None),(gate['local_path'],113,194)]:
 tensors=[]
 def walk(x):
  if torch.is_tensor(x):assert x.device.type=='cpu' and (not x.is_floating_point() or torch.isfinite(x).all());tensors.append(x)
  elif hasattr(x,'items'):
   for v in x.values():walk(v)
  elif isinstance(x,(tuple,list)):
   for v in x:walk(v)
 walk(torch.load(path,map_location='cpu',weights_only=False))
 assert sum(v.is_floating_point() for v in tensors)==expected
 if tensors_expected:assert len(tensors)==tensors_expected
 whole.append(dict(path=path,sha256=H(path),tensors=len(tensors),floating=expected))
assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),actual_targetCPU=True,package_SHA=H(z),manifest_SHA=H(Q/'RETENTION_CPU_MANIFEST_V8.json'),
 package_files=len(m['package_files_v8']),original_shared_files=len(m['shared_source_freeze']),isolated_source_files=len(m['isolated_source_freeze']),
 declared_overlay_files=len(m['source_overlay']),actual_isolated_helper_import_exact=True,source_module_origins=origins,
 SDK_stub_nativebinding_and_all_source_SHA_actual=True,whole_source_CPU=whole,gateproof=gateproof,
 no_CUDA_global_CPU_RNG_advance_optimizer_PPO_budget=True,
 no_full_SDK_constructor_GPUsetter_native_physical_or_training_restore_admission=True,new_root_native_leases_and_Tasks_unused=True)))
'''
        prefix='ROOT='+repr(ROOT)+'\nSHARED='+repr(SHARED)+'\nZIP='+repr(z.name)+'\nZIP_SHA='+repr(proof['package']['sha256'])+'\nMANIFEST_SHA='+repr(proof['manifest_SHA'])+'\n'
        actual=t.py(c,prefix+code,120)
        assert actual['actual_targetCPU'] and actual['package_SHA']==proof['package']['sha256']
        save('NOMINAL_COMPLETE_ABC_UPLOAD_TARGET_CPU_ACTUAL.json',actual)
        print(json.dumps(actual),flush=True)
    except BaseException:
        save('NOMINAL_COMPLETE_ABC_UPLOAD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),
             unknown_mutation_outcome_readonly_first_no_retry=True,no_GPU_lease_Task_PPO_budget=True))
        raise
    finally:
        if sf:sf.close()
        t.close(c)


if __name__=='__main__':main()
