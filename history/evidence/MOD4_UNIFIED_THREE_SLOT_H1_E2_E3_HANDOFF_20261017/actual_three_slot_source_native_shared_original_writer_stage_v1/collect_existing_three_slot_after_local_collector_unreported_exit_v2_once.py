"""New read-only continuation after prior local process is actually absent."""
from pathlib import Path
import sys,os,time,json,getpass,traceback,subprocess
U=Path(__file__).resolve().parent;R=U/'reports'
import collect_new_three_slot_actual_native_and_first_models_finite_once as c
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
ACCOUNT=r'''
from pathlib import Path
import json,time,fcntl
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());locks=[]
for path in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with path.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);free=True
  except BlockingIOError:free=False
 locks.append(dict(path=str(path),actual_fcntl_free=free))
print(json.dumps(dict(epoch=time.time(),original_canonical=v,actual_locks=locks,readonly_no_canonical_write=True)))
'''
def get_models(conn,row,key):
 folder=U/'actual_three_slot_first_models'/key
 if row['models']:folder.mkdir(parents=True,exist_ok=True)
 sf=conn.open_sftp();sf.get_channel().settimeout(120);out=[]
 try:
  for item in row['models']:
   p=folder/Path(item['path']).name;tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf.get(item['path'],str(tmp));assert tmp.stat().st_size==item['bytes'] and c.a.H(tmp)==item['SHA'];tmp.replace(p);out.append(dict(item,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return out
def main():
 assert not (R/'THREE_SLOT_ACTUAL_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION.json').exists();q=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object {$_.Name -like 'python*' -and $_.CommandLine -like '*collect_new_three_slot_actual_native_and_first_models_finite_once.py*'} | Select-Object ProcessId,CreationDate | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True);assert not q.stdout.strip()
 put('PRIOR_FIRST_COLLECTOR_CIM_ABSENT_NO_FINAL_UNKNOWN_EXIT_PRESERVED_V2_ACTUAL.json',dict(epoch=time.time(),original_PID61720_actual_CIM_absent=True,old_exec_session92052_tool_Unknown_process_id=True,original_COMPLETE_and_ORIGINAL_ERROR_files_absent=True,last_local_CURRENT_epoch=json.loads((R/'THREE_SLOT_SOURCE_FIRST_FINITE_CURRENT.json').read_bytes())['epoch'],actual_process_exit_reason_and_remote_training_status_not_inferred=True,not_relaunching_old_collector_or_GPU_or_once=True))
 put('THREE_SLOT_EXISTING_ONLY_LOCAL_HANDOFF_RECOVERY_COLLECTOR_STARTED_V2_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True,new_bounded_sequential_existing_roots_read_only=True))
 pw=getpass.getpass('Host72 existing three-slot saved models only (hidden): ');conn=None;out={};models={}
 try:
  conn=c.a.t.connect();out['owner']=c.a.code(conn,c.a.t.PY,c.READ,c.SOURCE,'owner');out['h1']=c.a.code(conn,c.a.t.PY,c.READ,c.ROOTS['h1'],'h1');models['h1']=get_models(conn,out['h1'],'h1');out['actual_original_account_and_twofcntl_snapshot']=c.a.code(conn,c.a.t.PY,ACCOUNT)
  final=next((r['value'] for r in out['h1']['files'] if r['path'].endswith('/job0/production/FINAL.json')),None)
  if final and final.get('passed'):
   row=dict(final['final'],kind='actual_H1_complete_final');out['downloaded_H1_final']=get_models(conn,dict(models=[row]),'h1')
 finally:
  c.a.t.close(conn);conn=None
 try:
  conn=c.a.connect72(pw);pw=None
  for key in ('e2','recovery'):out[key]=c.a.code(conn,c.a.PY,c.READ,c.ROOTS[key],key);models[key]=get_models(conn,out[key],key)
 finally:
  pw=None
  if conn:conn.close()
 out.update(epoch=time.time(),downloaded_models=models,previous_local_collector_absent_reason_unknown_preserved=True,no_GPU_native_or_Task_replay=True);put('THREE_SLOT_ACTUAL_NATIVE_FIRST_IMMUTABLE_MODELS_COMPLETE_BOUND_COLLECTION.json',out);print(json.dumps(dict(epoch=out['epoch'],model_files={k:[dict(kind=r['kind'],SHA=r['SHA'],bytes=r['bytes']) for r in v] for k,v in models.items()},H1_final=out.get('downloaded_H1_final'),original_locks=out['actual_original_account_and_twofcntl_snapshot']['actual_locks'],new_errors={k:[r['path'] for r in out[k]['files'] if 'ORIGINAL_ERROR' in r['path']] for k in ('owner','h1','e2','recovery')})),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  put('THREE_SLOT_HANDOFF_RECOVERY_COLLECTION_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_native_or_once_replay=True));raise
