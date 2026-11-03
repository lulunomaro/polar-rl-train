"""Real installed-file metadata imports only; no plan/admission/SDK/torch/PT/FD fake."""
from pathlib import Path
import sys,os,json,hashlib,importlib,argparse,time
sys.dont_write_bytecode=True;os.environ['CUDA_VISIBLE_DEVICES']=''
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=a.root.resolve();assert not a.output.exists();indexraw=(root/'CAPTURE_SOURCE_INDEX.json').read_bytes();assert hashlib.sha256(indexraw).hexdigest()=='234f8a3d0baf2a84338e9a0bf2170510f99d33c416654bf23b47bc3b5b5aa5ad';index=json.loads(indexraw);rows=index['original17']+index['new_sources']+index['dependency_sources'];assert len(rows)==27
 def verify():
  for r in rows:
   path=root/r['install_relative'];raw=path.read_bytes();assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA256']
 verify();forbid={'torch','isaaclab','isaacsim','omni','pxr','carb','warp','rsl_rl','tensordict'};events=[]
 def audit(event,args):
  if event=='import' and str(args[0]).split('.')[0]in forbid:raise AssertionError('Native/Torch import in metadata closure: '+str(args[0]))
  if event in('subprocess.Popen','os.system','socket.connect'):raise AssertionError('Process/network operation in metadata closure')
  if event=='open' and type(args[0])is str:
   path=args[0];low=path.lower()
   if low.endswith(('.pt','.pth','.ckpt','.jsonl','.csv'))or '/state/mod4_single_canonical_authority_'in low or low.endswith('.lock'):raise AssertionError('Forbidden model/raw/canonical/lock open')
   mode=args[1]
   if type(mode)is str and any(x in mode for x in('w','a','+','x'))and Path(path).resolve()!=a.output.resolve():raise AssertionError('Unrelated write in metadata closure')
 sys.addaudithook(audit);sys.path.insert(0,str(root))
 import phase1_capture_contract as contract
 import phase1_capture_runtime as runtime
 import phase1_capture_observer as observer
 import worker_passive_interface_v1 as worker
 import phase1_capture_parent_actual_wait_controller_v1 as controller
 runtime.validate_installed_root(root,runtime.HERE)
 for bad_group,bad_here in((root,root/'other'),(root.parent,root.parent),(Path('/tmp/not-the-task'),Path('/tmp/not-the-task'))):
  try:runtime.validate_installed_root(bad_group,bad_here)
  except ValueError:pass
  else:raise AssertionError('Foreign/misinstalled root accepted')
 core=runtime.core();assert Path(core.__file__).resolve()==root/'a1_frozen_eval_runtime_v2.py'
 app=runtime._pinned_module('app_close_semantics_v5',runtime.APP_PIN);base=app._base;bp=Path(base.__file__).resolve();assert bp==root/'resume_runtime_contracts_v3.py';match=next(r for r in rows if r['install_relative']==bp.name);b=bp.read_bytes();assert len(b)==match['bytes']and hashlib.sha256(b).hexdigest()==match['SHA256'];assert callable(base.close_original_resources)
 api=runtime.dependency('source_api','phase1_deps/sensor/source_api.py');sensor=runtime.dependency('passive_capture','phase1_deps/sensor/passive_capture.py');act=runtime.dependency('phase1_sealed_actuation_tap','phase1_deps/actuation/actuation_tap.py');assert callable(sensor.install_passive_capture)and callable(act.install_actuation_tap)and callable(worker.main)
 verify();loaded=sorted(x for x in sys.modules if x.split('.')[0]in forbid);assert not loaded
 receipt=dict(kind='ACTUAL_PHASE1_REAL_METADATA_IMPORT_ALIAS_CPU_V1',status='PASS',source_rows=27,original17=17,full_AppV6_and_Base_imported_not_stubbed=True,base_source=dict(path=str(bp),bytes=len(b),SHA256=hashlib.sha256(b).hexdigest()),correct_same_root_accepted=True,source_foreign_misinstalled_roots_rejected=True,new_worker_imported_but_main_not_called=True,sensor_actuation_metadata_APIs_imported=True,forbidden_modules_loaded=loaded,SDK_PT_GPU_canonical_lock_subprocess_operations=0,parent_controller_main_called=False,actual_resource_admission=False,actual_capture_interface_pass=False,gate1='UNKNOWN',stage2_GO=False)
 with a.output.open('x',encoding='utf-8')as f:json.dump(receipt,f,indent=2)
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
