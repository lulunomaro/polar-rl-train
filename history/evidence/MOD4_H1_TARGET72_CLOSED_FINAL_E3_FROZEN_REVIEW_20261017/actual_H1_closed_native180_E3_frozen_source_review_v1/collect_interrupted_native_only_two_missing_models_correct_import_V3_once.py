"""After actual local CIM handback, read existing native terminal and only two missing full PTs."""
from pathlib import Path
import sys,os,time,json,getpass,hashlib,traceback,subprocess,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';sys.path.insert(0,str(B));import deploy_latest_H1_native_only_after_actual_final_handoff_once as d
a=d.a
CODE=r'''
import sys,json,time,psutil,os,hashlib,fcntl,shutil,subprocess
from pathlib import Path
B=Path(sys.argv[1]);read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
rows={str(p.relative_to(B)):read(p) for p in sorted(B.rglob('*.json')) if ('job0/native' in str(p) or p.parent==B or p.name.endswith('WAITED_EXIT_ACTUAL.json')) and p.stat().st_size<20000000 and not p.name.startswith('THREE_SLOT_COMPLETE_MANIFEST')}
alive=[]
for proc in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  v=proc.info
  if proc.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in (v['cmdline'] or [])):alive.append(v)
 except psutil.Error:pass
models=[]
for name in ('own_source_full20k_startup0.pt','own_H1_ground_prelaunch_v2_native180.pt'):
 p=B/'job0/native'/name
 if p.is_file():models.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
locks=[];base=Path('/home/lc01/Zonglin Li/zonglin2')
for p in (base/'state/three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock',base/'state/finite_environment_validation.lock'):
 free=False
 with p.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);free=True;fcntl.flock(f,fcntl.LOCK_UN)
  except BlockingIOError:pass
 st=p.stat();locks.append(dict(path=str(p),actual_fcntl_free=free,inode=st.st_ino,device=st.st_dev))
print(json.dumps(dict(epoch=time.time(),root=str(B),rows=rows,actual_own_processes=alive,models=models,actual_target_locks=locks,compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode(),durable_free=shutil.disk_usage(base).free,parent_terminal_observed=bool(read(B/'NATIVE_ONLY_PARENT_EXIT_ACTUAL.json')),zero_PPO_zero_charge=True,old_native_Task_not_replayed=True)))
'''
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 cmd="Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -match 'collect_latest_H1_native_only_existing_parent_bounded_once|deploy_latest_H1_native_only_after_actual_final_handoff_once' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"
 raw=subprocess.check_output(['powershell','-NoProfile','-Command',cmd]).decode('utf8').strip();assert not raw,raw
 save('INTERRUPTED_NATIVE_COLLECTOR_V3_LOCAL_CIM_ACTUAL_OUT_NO_FORMAL_RETURN_REPORT.json',dict(epoch=time.time(),actual_old_finite_collectors_alive=[],old_started_but_completion_report_absent=True,old_exit_reason_or_natural_return_unknown=True,old_scope_GPU_not_replayed=True,new_bounded_missing_only_reader_pid=os.getpid(),actual_creation_argv_alive_only_exclusive_all_transport=True))
 pw=getpass.getpass('Host72 existing native terminal and two missing models (hidden): ');c=None
 try:
  # Original canonical is read once first, then the already launched target scope.
  import collect_existing_target72_H1_complete_final_original_cost_exit_once as closing;f=closing.f
  c=a.t.connect();account=a.code(c,a.t.PY,f.ACCOUNT,timeout=90);a.t.close(c);c=None
  c=a.connect72(pw);pw=None;v=a.code(c,a.PY,CODE,d.TARGET,timeout=150);v['original_account_actual']=account;out=B/'actual_latest_H1_native_models_V2';out.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in v['models']:
    p=out/Path(row['path']).name;assert not p.exists();q=p.with_suffix('.pt.partial');sf.get(row['path'],str(q));assert q.stat().st_size==row['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==row['SHA'];q.rename(p);row.update(local_path=str(p),twohost_complete_SHA=True)
  finally:sf.close()
  save('LATEST_H1_NATIVE_ONLY_EXISTING_TERMINAL_TWO_MISSING_FULL_MODELS_V3_COLLECTION_ACTUAL.json',v);print(json.dumps(dict(actual_parent_terminal=v['parent_terminal_observed'],models=len(v['models']),own_processes=len(v['actual_own_processes']),locks=v['actual_target_locks'],canonical_active=account['original_canonical']['active_segment'],compute=v['compute'])),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:save('LATEST_H1_NATIVE_ONLY_V3_MISSING_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_replay_or_automatic_retry=True));raise
