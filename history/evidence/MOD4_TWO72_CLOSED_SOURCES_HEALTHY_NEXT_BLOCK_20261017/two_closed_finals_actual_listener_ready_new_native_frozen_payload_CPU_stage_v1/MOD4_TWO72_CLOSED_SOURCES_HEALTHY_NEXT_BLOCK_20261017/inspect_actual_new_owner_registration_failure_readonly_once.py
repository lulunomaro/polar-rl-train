from pathlib import Path
import os,sys,time,json,traceback
G=Path(__file__).resolve().parent;R=G/'reports';F=G.parent/'MOD4_THREE_EXPERTS_HEALTHY_FOLLOWUP_V3_20261017';sys.path.insert(0,str(F))
from deploy_two72_followup_storage_rejected_H1_original_writer_once import a
CODE=r'''
from pathlib import Path
import os,json,time,psutil,fcntl
B=Path('/mnt/mod4_linux_durable_20261013/T3_1710v4r72/owner');files={}
for name in ('OWNER_IDENTITY.json','OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json','COHORT_FINAL.json','owner_CONSOLE.log'):
 p=B/name
 if p.is_file():files[name]=p.read_text('utf8') if p.suffix=='.log' else json.loads(p.read_bytes())
procs=[]
for p in psutil.process_iter(['pid','cmdline','create_time','cwd']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);free=True
  except BlockingIOError:free=False
 locks.append(dict(path=str(p),actual_free=free))
print(json.dumps(dict(epoch=time.time(),files=files,actual_own_processes=procs,active=v['active_segment'],locks=locks,old_owner_completed_segments=[x for x in v['completed_segments'] if x.get('owner_parent_pid')==int(sys.argv[1])] if False else [],readonly_no_runtime_or_GPU_or_budget_mutation=True)))
'''
def main():
 c=None
 try:c=a.t.connect();v=a.code(c,a.t.PY,CODE)
 finally:a.t.close(c)
 with (R/'NEW_OWNER_REGISTRATION_CONNECTION_REFUSED_ACTUAL_READONLY_INSPECTION.json').open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 print(json.dumps(v),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('OWNER_REGISTRATION_READONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),readonly=True),f,indent=2)
  raise
