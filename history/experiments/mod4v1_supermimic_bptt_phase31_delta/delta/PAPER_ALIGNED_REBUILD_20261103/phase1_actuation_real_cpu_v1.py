"""Real original PhysicsActionQueue + sealed observer CPU fixture; fake env only."""
from pathlib import Path
import os,sys,json,hashlib,importlib.util,argparse,random
os.environ['CUDA_VISIBLE_DEVICES']='';sys.dont_write_bytecode=True
FIXTURE_SEAL='14d7223d09842dddb8e90ab7ee236f3a87aff30e671fab6ef6fe36dad79a9a5a';TAP_SEAL='ed77f3a3b0ce7aea6f904a09be8d038097bfb00729d57bec94feae5ab67bd081';QUEUE='a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8'
def verify(directory,expected):
 raw=(directory/'SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==expected;s=json.loads(raw);assert len(s['files'])==8
 for name,meta in s['files'].items():
  path=(directory/name).resolve();assert path.is_relative_to(directory);b=path.read_bytes();assert len(b)==meta['bytes']and hashlib.sha256(b).hexdigest()==meta['sha256']
 return s

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();D=a.source_dir.resolve();assert not a.output.exists();verify(D/'fixture',FIXTURE_SEAL);verify(D/'tap',TAP_SEAL);qp=D/'original/action_delay_physics_queue.py';assert hashlib.sha256(qp.read_bytes()).hexdigest()==QUEUE
 import torch
 torch.set_num_threads(1);assert not torch.cuda.is_initialized();sp=importlib.util.spec_from_file_location('_original_pinned_physics_action_queue',qp);qmod=importlib.util.module_from_spec(sp);sys.modules[sp.name]=qmod;sp.loader.exec_module(qmod)
 sys.path[:0]=[str(D/'fixture'),str(D/'tap')];import real_cpu_fixture as fixture;import actuation_tap as tap
 assert hashlib.sha256(Path(fixture.__file__).read_bytes()).hexdigest()=='2805adf3530def6f1a0e73634a54fdc91ddb1e74e0c157023f008d5a3581277c'
 before_py=random.getstate();before_t=torch.get_rng_state().clone();cases=[]
 for n in (2,3):
  r=fixture.run_fixture(torch,qmod.PhysicsActionQueue,tap,n=n,seed=20261103);assert r['original_queue_private_rng_and_full_state_bitwise_equal']and r['global_torch_cpu_rng_unchanged']and r['captured_cpu_tensors_owned']and r['same_tick_and_original_exception_identity']and r['bounded_overflow_unknown'];assert r['totals']['normal_apply_ticks']==432 and r['totals']['partial_resets']==18 and len(r['cases'])==9 and not r['actual_sdk_pass']and not r['gate1_admitted'];cases.append(r)
 assert random.getstate()==before_py and torch.equal(before_t,torch.get_rng_state())and not torch.cuda.is_initialized();verify(D/'fixture',FIXTURE_SEAL);verify(D/'tap',TAP_SEAL)
 receipt=dict(kind='ACTUAL_PHASE1_ORIGINAL_ACTION_QUEUE_AND_PASSIVE_TAP_TORCH_CPU_V1',status='PASS',cases=cases,fixture_seal_SHA256=FIXTURE_SEAL,tap_seal_SHA256=TAP_SEAL,queue_source_SHA256=QUEUE,case_N=[2,3],lag_pairs_per_N=9,normal_apply_ticks_total=sum(x['totals']['normal_apply_ticks']for x in cases),global_Python_Torch_CPU_RNG_unchanged=True,frozen_source_artifacts_changed=False,SDK_or_selected_PT_raw_GPU_canonical_operations=0,native_BPTT_updates=0,actual_native_binding_pass=False,actor35_native_equality_test=False,physical_readback='UNKNOWN',stage1_status='REAL_ORIGINAL_QUEUE_COMPONENT_TAP_CPU_PASS_ACTUAL_SDK_GATE_UNKNOWN')
 with a.output.open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2)
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
