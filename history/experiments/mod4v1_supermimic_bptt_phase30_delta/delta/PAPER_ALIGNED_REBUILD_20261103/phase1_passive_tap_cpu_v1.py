"""Actual original Torch CPU classes plus frozen tap; fake env, NOT native preflight."""
from pathlib import Path
import sys,os,json,hashlib,random,importlib.util,argparse
os.environ['CUDA_VISIBLE_DEVICES']='';sys.dont_write_bytecode=True
ORIGINAL={'sensor_mild_math.py':'aa853a74a2c2d8840d003caab13a853bade0d761cf7966e4d13c200b929817b8','feedback_delay_mild.py':'90b339a6d3690294798befefb33e7f27cb7c3bfa0d8e38c98312e207685b5665'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();D=a.source_dir.resolve();sealraw=(D/'SOURCE_SEAL.json').read_bytes();assert hashlib.sha256(sealraw).hexdigest()=='3d5fd4febf9232a8113b4d93dbf8d3d6a19658690e973d6485c1aedc39e18881';seal=json.loads(sealraw);assert len(seal['files'])==13
 def verify():
  assert (D/'SOURCE_SEAL.json').read_bytes()==sealraw
  for meta in seal['files']:
   path=(D/meta['relative']).resolve();assert path.is_relative_to(D);blob=path.read_bytes();assert len(blob)==meta['bytes']and hashlib.sha256(blob).hexdigest()==meta['sha256']
 verify();mods={}
 for name,sha in ORIGINAL.items():
  path=D/name;raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;sp=importlib.util.spec_from_file_location('_original_'+path.stem,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);mods[name]=m
 sys.path.insert(0,str(D));import torch
 torch.set_num_threads(1);assert not torch.cuda.is_initialized();from cpu_reference_tap_fixture import run_cpu_reference_tap_fixture
 before_python=random.getstate();before_torch=torch.get_rng_state().clone();r=run_cpu_reference_tap_fixture(torch,mods['sensor_mild_math.py'].SensorCorruption,mods['feedback_delay_mild.py'].FeedbackDelay)
 assert r['bitwise_class_output_comparisons']==25 and r['return_identity_checks']==50 and r['source_rng_and_queue_state_equal']and r['capture_errors']==0
 assert random.getstate()==before_python and torch.equal(before_torch,torch.get_rng_state())and not torch.cuda.is_initialized();verify()
 receipt=dict(kind='ACTUAL_PHASE1_REAL_TORCH_CLASS_PLUS_PASSIVE_TAP_CPU_V1',status='PASS',frozen_source_seal_SHA256=hashlib.sha256(sealraw).hexdigest(),frozen_members_verified=13,original_source_pins=ORIGINAL,fixture=r,global_Python_and_Torch_RNG_unchanged=True,source_artifacts_changed=False,SDK_executed=False,native_binding_preflight_executed=False,actor35_native_equality_tested=False,selected_PT_raw_GPU_canonical_operations=0,native_BPTT_updates=0,stage1_status='REAL_CPU_CLASS_TAP_PASS_GATE1_ACTUAL_NATIVE_UNKNOWN')
 with a.output.open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2)
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
