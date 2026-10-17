"""Strict same-source/backend reuse; actual runtime checks surround this pure validator."""
from pathlib import Path
import json,hashlib,os,psutil,subprocess
def validate(spec,bind,oldm,newm,final,exitrow,cpuwait,gpuwait):
 assert spec['key']=='h1' and spec['execution_backend']=='target72' and spec['GPU_UUID']==bind['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 assert spec['source_SHA']==bind['source_SHA']==oldm['source_SHA']==newm['source_SHA'] and spec['source_Adamstep']==oldm['source_Adamstep']==newm['source_Adamstep']==645620
 assert oldm['key']==newm['key']=='h1' and spec['native_controls']==180
 assert final['passed_native_GPU_and_full_CPU'] and final['actual_GPU_worker_EXIT0'] and final['source_SHA']==spec['source_SHA'] and final['no_production_GO_or_PPO_or_canonical_charge']
 assert exitrow['all_actual_own_GPU_children_waited'] and exitrow['private_GPU_fcntl_released_if_acquired'] and exitrow['passed_native_CPU'] and not exitrow['original_error']
 assert cpuwait['returncode']==gpuwait['returncode']==0 and cpuwait['actual_waited'] and gpuwait['actual_waited']
 native=final['native_CPU'];v=native['value'];assert native['actual_CPU_waited_EXIT0'] and native['SHA']==bind['native_CPU_SHA']==hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest()
 assert v['passed'] and v['source_SHA']==spec['source_SHA'] and v['controls']==180 and v['callbacks']==720 and v['all_policy_rows']==3600000 and v['all_physical_rows']==14400000
 assert v['all17Adam_step645620'] and v['sourceactor9critic8STD17Adam_literal_exact'] and v['complete_original20k_typed_source_restore_actual']
 def fixed(m):return {r['relative']:r['SHA'] for r in m['files'] if r['relative'].startswith(('job0/runtime/','job0/assets/','lib/')) or r['relative']=='job0/original_run_manifest.json'}
 assert fixed(oldm)==fixed(newm) and fixed(oldm)
 return native
def reuse_H1_native(spec,b,B):
 m=b.read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');bind=m['H1_same_source_backend_native_reuse'];old=Path(bind['root']);owned=Path('/home/lc01/Zonglin Li/zonglin2')
 assert old.resolve().is_relative_to(owned.resolve()) and B.resolve().is_relative_to(owned.resolve()) and old!=B
 oldpath=old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';assert b.H(oldpath)==bind['manifest_SHA'];oldm=b.read(oldpath)
 final=b.read(old/'NATIVE_ONLY_FINAL_ACTUAL.json');native=validate(spec,bind,oldm,m,final,b.read(old/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json'),b.read(old/'job0/native_CPU_WAITED_EXIT_ACTUAL.json'),b.read(old/'job0/native_WAITED_EXIT_ACTUAL.json'))
 identity=b.read(old/'NATIVE_ONLY_PARENT_IDENTITY.json')
 if psutil.pid_exists(identity['pid']):
  p=psutil.Process(identity['pid']);assert abs(p.create_time()-identity['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
 alive=[]
 for p in psutil.process_iter(['pid','cmdline','create_time']):
  try:
   if p.pid!=os.getpid() and any(s.startswith(str(old)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
  except psutil.Error:pass
 assert not alive,alive
 for row in oldm['files']:
  if row['relative'].startswith(('job0/runtime/','job0/assets/','lib/')) or row['relative']=='job0/original_run_manifest.json':assert b.H(old/row['relative'])==b.H(B/row['relative'])==row['SHA']
 assert b.H(B/'job0/source/H1_final10_protected.pt')==b.H(old/'job0/source/H1_final10_protected.pt')==spec['source_SHA']
 assert b.H(native['path'])==native['SHA'];pt=Path(native['value']['native_checkpoint']['path']);assert pt.resolve().is_relative_to(old.resolve()) and pt.stat().st_size==native['value']['native_checkpoint']['bytes'] and b.H(pt)==native['value']['native_checkpoint']['SHA']
 compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(spec['GPU_UUID'] in s for s in compute.splitlines()),compute
 b.put(B/'STRICT_EXISTING_H1_NATIVE_REUSE_ACTUAL.json',dict(epoch=__import__('time').time(),source_SHA=spec['source_SHA'],source_Adam645620=True,exact_backend_GPU=spec['GPU_UUID'],native_CPU_SHA=native['SHA'],old_native_parent_children_actual_out=True,source_runtime_assets_and_installed_CPU_manifest_bound=True,no_GPU_native_replay_or_old_raw_download=True,not_jump_skill_qualification=True))
 return dict(native,strict_same_source_backend_reuse=True)
