from pathlib import Path
import sys,time,json,getpass,os,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from collect_first_two_native_and_E2_handoff_actual_readonly_once import READ,S,T,code,H,connect72,t,PY
E2S='/mnt/mod4_linux_durable_20261013/MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016/e2_from58_plus75_same4_continuation_v2';E2T='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_CURB140_E2_58_HEALTHY_CONTINUATION_ADMISSION_20261016/e2_from58_plus75_same4_continuation_v2'
def main():
 with (R/'CLOSURE_SOURCE_REUSE_COLLECTOR_STARTED_ACTUAL.json').open('x') as f:json.dump(dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_transport=True),f)
 pw=getpass.getpass('Host72 actual terminal sources read only (hidden): ');c=None;v={}
 try:
  c=t.connect();v['curb']=code(c,t.PY,READ,S,'curb');v['old_E2']=code(c,t.PY,READ,E2S,'e2');v['canonical']=code(c,t.PY,"from pathlib import Path;import json,time,fcntl;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());locks=[]\nfor p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):\n with p.open('rb+') as f:\n  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)\n  except BlockingIOError:held=True\n  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)\n  locks.append(dict(path=str(p),held=held))\nprint(json.dumps(dict(epoch=time.time(),active=v['active_segment'],remaining=v['remaining_training_seconds'],charged=v['charged_training_seconds'],last2_completed=v['completed_segments'][-2:],actual_locks=locks)))")
 finally:t.close(c);c=None
 try:
  c=connect72(pw);pw=None;v['recovery']=code(c,PY,READ,T,'recovery');v['E2_target']=code(c,PY,READ,E2T,'e2');model=code(c,PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);v=json.loads((B/'job0/production/FINAL.json').read_bytes());r=v['final'];p=Path(r['path']);assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA'];print(json.dumps(r))",E2T);folder=D/'actual_closed_E2_source';folder.mkdir();p=folder/'closed_E2_final.pt';tmp=p.with_suffix('.pt.partial');sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:sf.get(model['path'],str(tmp));assert tmp.stat().st_size==model['bytes'] and H(tmp)==model['SHA'];tmp.replace(p)
  finally:sf.close()
  v['E2_complete_model']=dict(**model,local_path=str(p),twohost_complete_SHA_exact=True)
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time()
 with (R/'CURB1_E3_FAILED_E2_FINAL_ACTUAL_HANDOFF_AND_COMPLETE_SOURCE.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 print(json.dumps(dict(epoch=v['epoch'],E2_model=v['E2_complete_model'],canonical=v['canonical'],curb_processes=v['curb']['actual_own_processes'],recovery_processes=v['recovery']['actual_own_processes'],E2_processes=v['E2_target']['actual_own_processes'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('CLOSURE_COLLECT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_old_replay=True),f,indent=2)
  raise
