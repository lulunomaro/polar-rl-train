"""Only current immutable finals and real accounting; never signal/restart."""
from pathlib import Path
import os,sys,json,time,getpass,traceback
D=Path(__file__).resolve().parent;R=D/'reports';sys.path.insert(0,str(D));from deploy_two_exact_source_continuation_native_cohort_once import code,H,connect72,t,S,T,PY
READ=r'''
from pathlib import Path
import sys,json,time,psutil,hashlib,fcntl
B=Path(sys.argv[1]);key=sys.argv[2];out=B/'job0'/('production_only' if key=='curb' else 'production');selected=[*B.glob('*.json'),*out.glob('*.json')];files=[]
for p in sorted(selected):
 raw=p.read_bytes();files.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw)))
final=json.loads((out/'FINAL.json').read_bytes()) if (out/'FINAL.json').exists() else None;model=None
if final and final['passed']:
 row=final['final'];p=Path(row['path']);assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];model=row
procs=[]
for p in psutil.process_iter(['pid','create_time','cmdline','cwd']):
 try:
  if any(str(B)+'/' in x for x in p.info['cmdline'] or []):procs.append(p.info)
 except psutil.Error:pass
v=dict(epoch=time.time(),files=files,actual_own_processes=procs,final=final,model=model,no_runtime_mutation=True)
if key=='curb':
 C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());v['canonical']={k:c[k] for k in ('active_segment','authorized_training_seconds','charged_training_seconds','remaining_training_seconds')};v['own_closed_segments']=[x for x in c['completed_segments'] if str(x.get('kind','')).startswith('Linux_TWO_DISTINCT_CURB35_E2_HEALTHY_CONTINUATIONS_')];paths=[C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
else:paths=[Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')]
locks=[]
for path in paths:
 with path.open('rb+') as f:
  try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:held=True
  else:held=False;fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(path),actual_held=held))
v['actual_locks']=locks;print(json.dumps(v))
'''
def get(c,v,key):
 if not v['model']:return
 row=v['model'];folder=D/'actual_two_continuation_final_models';folder.mkdir(exist_ok=True);p=folder/(key+'_final.pt');tmp=p.with_suffix('.pt.partial');assert not p.exists() and not tmp.exists();sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:sf.get(row['path'],str(tmp))
 finally:sf.close()
 assert tmp.stat().st_size==row['bytes'] and H(tmp)==row['SHA'];tmp.replace(p);v['local_model']=dict(path=str(p),remote=row['path'],bytes=row['bytes'],SHA=row['SHA'],twohost_complete_exact=True)
def main():
 p=R/'TWO_CONTINUATION_ACTUAL_FINAL_MODELS_COST_EXIT_READONLY_COLLECTION.json';assert not p.exists();pw=getpass.getpass('Host72 two continuation immutable FINAL collection password (hidden): ');c=None;v={}
 try:c=t.connect();v['curb']=code(c,t.PY,READ,S,'curb');get(c,v['curb'],'curb')
 finally:t.close(c);c=None
 try:c=connect72(pw);pw=None;v['e2']=code(c,PY,READ,T,'e2');get(c,v['e2'],'e2')
 finally:
  pw=None
  if c:c.close()
 v['epoch']=time.time();p.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(epoch=v['epoch'],curb=v['curb']['final'],e2=v['e2']['final'],curb_procs=v['curb']['actual_own_processes'],e2_procs=v['e2']['actual_own_processes'],segments=v['curb']['own_closed_segments'],locks=v['curb']['actual_locks']+v['e2']['actual_locks'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:(R/('TWO_FINAL_COLLECTION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),no_runtime_mutation_or_retry=True),indent=2),encoding='utf8');raise
