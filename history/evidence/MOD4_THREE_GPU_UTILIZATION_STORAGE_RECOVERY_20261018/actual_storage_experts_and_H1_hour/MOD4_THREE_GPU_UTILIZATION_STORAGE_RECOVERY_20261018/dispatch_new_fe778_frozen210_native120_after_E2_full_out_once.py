"""Use reclaimed210 for the new complete H1 source; paid training continues independently on72."""
from inventory_current_owned210_storage_readonly_once import *
import deploy_two_idle_4090_linux_reward_frame_observations_once as base
import importlib.util,hashlib
Q=B/'H1_fe778_linux210_frozen_v1/payload';TARGET='/mnt/mod4_linux_durable_20261013/H1f7_1810ev1';GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
oldpath=W/'MOD4_POST_POWER_RESTORE_H1_SATURATION_REPAIR_20261018/resumed_ce3_original_fp32_v1/dispatch_8a7c_GPU1_own_native120_once.py';sp=importlib.util.spec_from_file_location('consumed_dispatch_pure_CPU_template_only',oldpath);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
CPU=old.CPU.replace('H1_CR3_FINAL_LINUX4090_MANIFEST_V1.json','H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json').replace('h1_cr3_finite_final_source_guard_v1','h1_hour1_finite_final_source_guard_v1').replace('linux72_GPU1_frozen_only','linux210_GPU0_frozen_only')
start=CPU.index("base=Path('/home/lc01/Zonglin Li/zonglin2');sdk=");end=CPU.index('bindings=sorted(',start)
CPU=CPU[:start]+"from importlib.machinery import PathFinder\npackage=PathFinder.find_spec('isaaclab');assert package and package.submodule_search_locations;sdk=Path(next(iter(package.submodule_search_locations)))/'utils/math.py';assert H(sdk)=='4ae6fe19d9b18c2747bf6546dc72f75cfe497ee2ba6046e95fabbeb33d958d33'\nsite=Path('/home/egde/anaconda3/envs/fangzhen-isaaclab/lib/python3.12/site-packages');"+CPU[end:]
INSTALL=r'''
from pathlib import Path
import json,sys,hashlib,zipfile
B=Path(sys.argv[1]);z=B/'payload.zip';assert hashlib.sha256(z.read_bytes()).hexdigest()==sys.argv[2]
with zipfile.ZipFile(z) as f:
 for name in f.namelist():assert not Path(name).is_absolute() and '..' not in Path(name).parts and (B/name).resolve().is_relative_to(B.resolve())
 f.extractall(B)
print(json.dumps(dict(actual_package_SHA_verified=True)))
'''
def main():
 prep=json.loads((R/'H1_FE778_LINUX210_FROZEN_COMPLETE_PACKAGE_CPU_PREPARED_ACTUAL.json').read_bytes());assert prep['passed_complete_source_CPU_and_AST'];e2=json.loads((R/'E2_LINUX_FULL1500_RECORDED_PHYSICS_REWARD_CPU_ACTUAL.json').read_bytes());assert e2['passed_recorded_full_data_source_physics_CPU'];save('H1_FE778_FROZEN210_NATIVE120_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transport=True))
 cfg=dict(base.S['E2'],root=TARGET);c=None
 try:
  c=a.t.connect();out=a.code(c,a.t.PY,r'''
from pathlib import Path
import json,psutil,time,os
B=Path('/mnt/mod4_linux_durable_20261013/E2rf_1810d4f');e=json.loads((B/'OBSERVATION_PARENT_EXIT_ACTUAL.json').read_bytes());assert e['actual_child_waited'] and e['returncode']==0 and not (B/'full1500_observation/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json').exists();own=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
assert not own;print(json.dumps(dict(epoch=time.time(),actual_E2_full_parent_children_out=True,old_data_retained=True)))
''',timeout=60);save('H1_FE778_FROZEN210_E2_FULL_ACTUAL_EXIT_HANDOFF.json',out)
  save('H1_FE778_FROZEN210_CURRENT_RESOURCE_REAL_FCNTL_ADMISSION.json',a.code(c,a.t.PY,base.codefmt(base.ADMIT,cfg),timeout=60));sf=c.open_sftp()
  try:sf.get_channel().settimeout(120);sf.put(prep['package']['path'],TARGET+'/payload.zip')
  finally:sf.close()
  a.code(c,a.t.PY,INSTALL,TARGET,prep['package']['SHA'],timeout=90);cpu=a.code(c,a.t.PY,CPU,TARGET,timeout=180);save('H1_FE778_FROZEN210_ACTUAL_TARGET_SOURCE_INSTALLED_RSL_SDK_CPU.json',cpu)
  m=json.loads((Q/'H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json').read_bytes());case=dict(router_mode='single_eval',kind='jump',steps=120,num_envs=80,seed=20260928,headless=True,device='cuda:0');lease=dict(target_host='10.24.4.210',execution_backend='linux210_GPU0_frozen_only',GPU_UUID=GPU,namespace='H1_HOUR1_FINAL_LINUX210_V1_20261018',GPU_lease_granted_by_root=True,actual_selected_GPU_idle_private_lock_free=True,human_authorized_4090_eval_parallel_training_not_interrupted=True,checkpoint_sha256=m['source']['SHA'],checkpoint_path=TARGET+'/'+m['source_relative'],worker_sha256=H(Q/'h1_linux4090_frozen_worker_v1.py'),source_manifest_sha256=H(Q/'H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json'),actual_Linux_backend_SHA=cpu['backend_file_SHA'],case_id='H1_FE778_LINUX210_NATIVE120_1810V1',case_parameters=case)
  parent=old.d.launch(a.code,c,a.t.PY,TARGET,'h1_linux4090_frozen_parent_v1.py',dict(role='frozen_eval_only',attempt=TARGET+'/native120',lease=lease));save('H1_FE778_FROZEN210_NATIVE120_DETACHED_ACTUAL.json',dict(epoch=time.time(),parent=parent,root=TARGET,lease=lease,actual_target_CPU_passed=True,no_PPO_or_canonical_charge=True,training_not_stopped_or_signalled=True,native_result_not_yet=True));print(json.dumps(dict(reclaimed210_new_H1_frozen_native_dispatched=True,parent=parent,H1_72_training_untouched=True)),flush=True)
 finally:
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('H1_FE778_FROZEN210_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_no_replay_or_live_patch=True));raise
