"""One unused full case after this same source/backend native data CPU passed."""
import dispatch_new_fe778_frozen210_native120_after_E2_full_out_once as m
from inventory_current_owned210_storage_readonly_once import *
def main():
 n=R/'H1_FE778_LINUX210_120_ALL_PHYSICAL_PUBLIC04_SOURCE_FP64_REFERENCE_CPU_V3_ACTUAL.json';native=json.loads(n.read_bytes());assert native['passed_complete_data_and_source_CPU'] and native['source_SHA']=='fe7780a502743dc12c0826d82f4a5a5a5ee8917f095890c7bfb866c48b600309';T=m.TARGET+'f';save('FE778_FROZEN210_FULL1500_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transport=True));c=None
 try:
  c=a.t.connect();cfg=dict(m.base.S['E2'],root=T);save('FE778_FROZEN210_FULL1500_RESOURCE_REAL_PRIVATE_FCNTL_ADMISSION.json',a.code(c,a.t.PY,m.base.codefmt(m.base.ADMIT,cfg),timeout=60))
  copied=a.code(c,a.t.PY,r'''
from pathlib import Path
import sys,json,os,psutil,shutil,time
A=Path(sys.argv[1]);B=Path(sys.argv[2]);e=json.loads((A/'native120/PARENT_EXIT_RECEIPT.json').read_bytes());assert e['actual_child_returncode']==0 and e['all_actual_own_children_waited'] and e['complete'] and not e['original_errors'];alive=[]
for p in psutil.process_iter(['pid','cmdline']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(A)+'/') for x in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive;m=json.loads((A/'H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json').read_bytes());names=[r['relative'] for r in m['files']]+['H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json']
for name in names:(B/name).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(A/name,B/name)
print(json.dumps(dict(epoch=time.time(),native_parent_children_out_EXIT0=True,only_static_manifest_files_copied_no_native_data_or_Task_replay=True,files=len(names))))
''',m.TARGET,T,timeout=120);save('FE778_FROZEN210_FULL1500_NATIVE_EXIT_STATIC_SOURCE_HANDOFF.json',copied)
  code=m.CPU.replace('from importlib.machinery import PathFinder','from importlib.util import find_spec').replace("PathFinder.find_spec('isaaclab')","find_spec('isaaclab')");cpu=a.code(c,a.t.PY,code,T,timeout=180);save('FE778_FROZEN210_FULL1500_TARGET_SOURCE_ACTUAL_BACKEND_CPU.json',cpu)
  manifest=json.loads((m.Q/'H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json').read_bytes());case=dict(router_mode='single_eval',kind='jump',steps=1500,num_envs=80,seed=20260928,headless=True,device='cuda:0');lease=dict(target_host='10.24.4.210',execution_backend='linux210_GPU0_frozen_only',GPU_UUID=m.GPU,namespace='H1_HOUR1_FINAL_LINUX210_V1_20261018',GPU_lease_granted_by_root=True,actual_selected_GPU_idle_private_lock_free=True,human_authorized_4090_eval_parallel_training_not_interrupted=True,checkpoint_sha256=manifest['source']['SHA'],checkpoint_path=T+'/'+manifest['source_relative'],worker_sha256=m.H(m.Q/'h1_linux4090_frozen_worker_v1.py'),source_manifest_sha256=m.H(m.Q/'H1_HOUR1_FINAL_LINUX210_MANIFEST_V1.json'),actual_Linux_backend_SHA=cpu['backend_file_SHA'],case_id='H1_FE778_LINUX210_FULL1500_1810V1',case_parameters=case,actual_same_backend_source_native120_allrow_CPU_passed=True,native120_actual_exit_childrenout_lockfree=True,native_CPU_report_SHA=m.H(n))
  parent=m.old.d.launch(a.code,c,a.t.PY,T,'h1_linux4090_frozen_parent_v1.py',dict(role='frozen_eval_only',attempt=T+'/full1500',lease=lease));save('H1_FE778_FROZEN210_FULL1500_DETACHED_ACTUAL.json',dict(epoch=time.time(),parent=parent,root=T,lease=lease,no_PPO_or_budget_charge=True,H1_training_not_interrupted=True,not_full_result_yet=True));print(json.dumps(dict(new_full1500_dispatched=True,parent=parent,training_untouched=True)),flush=True)
 finally:
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('FE778_FROZEN210_FULL1500_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_no_replay=True));raise
