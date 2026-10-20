"""Run only near this actual cohort's save boundary; collect complete exits/costs once."""
from pathlib import Path,PurePosixPath
import getpass,hashlib,json,os,sys,time,traceback
import deploy_two50_reconciled_original_writer_once as d
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ210=r'''
from pathlib import Path
import fcntl,json,os,psutil,subprocess,time
Q=v['q'];owner=Path(Q['owner_root']);node=Path(Q['roots']['e2']);until=time.monotonic()+850;read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
def own():
 out=[]
 for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
  try:
   if p.pid!=os.getpid() and any(x.startswith((str(owner)+'/',str(node)+'/')) for x in p.info['cmdline'] or []):out.append(p.info)
  except psutil.Error:pass
 return out
while not (owner/'COHORT_FINAL.json').is_file() or not (owner/'OWNER_EXIT_ACTUAL.json').is_file() or not (node/'NODE_EXIT_ACTUAL.json').is_file() or own():
 assert time.monotonic()<until,'Current cohort has not actually closed; no schedule-based FINAL'
 time.sleep(3)
co=read(owner/'COHORT_FINAL.json');oe=read(owner/'OWNER_EXIT_ACTUAL.json');ne=read(node/'NODE_EXIT_ACTUAL.json');assert co['original_cost_settled'] and oe['original_cost_settled'] and oe['own_original_two_fcntl_released_if_held'] and ne['actual_all_own_children_waited'];C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=read(C);assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7;seg=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==Q['owner']['detached_pid'] and x['started_epoch']>=v['owner_creation']];assert len(seg)==1 and set(seg[0]['experts'])=={'e2','recovery'};locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(Q['specs']['e2']['private_lock'])):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_fcntl_free=True))
texts=[]
for root in (owner,node):
 for p in root.rglob('*'):
  if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):
   raw=p.read_bytes();texts.append(dict(path=str(p),relative=('owner/' if root==owner else 'e2/')+p.relative_to(root).as_posix(),bytes=len(raw),SHA=__import__('hashlib').sha256(raw).hexdigest()))
print(json.dumps(dict(epoch=time.time(),cohort=co,owner_exit=oe,e2_node_exit=ne,original_segment=seg[0],original_canonical_remaining=c['remaining_training_seconds'],original_canonical_charged=c['charged_training_seconds'],original_locks=locks,all_current_owner_and_E2_processes_actual_out=True,text_files=texts,compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True),no_account_write_or_model_hash=True)))
'''
READ72=r'''
from pathlib import Path
import fcntl,json,os,psutil,subprocess,time
Q=v['q'];node=Path(Q['roots']['recovery']);until=time.monotonic()+180;read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
def own():
 out=[]
 for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
  try:
   if p.pid!=os.getpid() and any(x.startswith(str(node)+'/') for x in p.info['cmdline'] or []):out.append(p.info)
  except psutil.Error:pass
 return out
while not (node/'NODE_EXIT_ACTUAL.json').is_file() or own():
 assert time.monotonic()<until,'E3 node still actually active'
 time.sleep(3)
exit=read(node/'NODE_EXIT_ACTUAL.json');terminal=read(node/'NODE_TERMINAL_ACTUAL.json');assert exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired'];locks=[]
for p in (Path(Q['specs']['recovery']['private_lock']),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(dict(path=str(p),actual_fcntl_free=True))
texts=[]
for p in node.rglob('*'):
 if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):
  raw=p.read_bytes();texts.append(dict(path=str(p),relative='recovery/'+p.relative_to(node).as_posix(),bytes=len(raw),SHA=__import__('hashlib').sha256(raw).hexdigest()))
print(json.dumps(dict(epoch=time.time(),node_exit=exit,node_terminal=terminal,locks=locks,all_E3_processes_actual_out=True,text_files=texts,compute_snapshot=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True),no_peer_identity_or_account_change=True)))
'''
def capture(c,actual,models,key):
 sf=c.open_sftp();sf.get_channel().settimeout(90);out=[];saved=[]
 try:
  for row in actual['text_files']:
   rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts;p=B/'current_two50_closed_text'/Path(*rel.parts);p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'];out.append(dict(row,local_path=str(p)))
  for m in models:
   p=B/'current_two50_closed_models'/key/PurePosixPath(m['path']).name;p.parent.mkdir(parents=True,exist_ok=True);assert not p.exists();partial=p.with_suffix(p.suffix+'.partial');sf.get(m['path'],str(partial));assert partial.stat().st_size==m['bytes'] and H(partial)==m['SHA'];partial.replace(p);saved.append(dict(m,local_path=str(p),twohost_complete_SHA=True))
 finally:sf.close()
 return out,saved
def main():
 proof=json.loads((R/'TWO50_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_OR_PENDING_ACTUAL.json').read_bytes());assert proof['passed'];q=json.loads((R/'TWO50_ORIGINAL_ACCOUNT_COHORT_DETACHED_ACTUAL.json').read_bytes());put('TWO50_CLOSING_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_owner=q['owner']));pw=getpass.getpass('72 actual two50 complete finals and original cost (hidden): ');c=None
 try:
  c=d.t.connect();a=d.code(c,d.t.PY,READ210,dict(q=q,owner_creation=proof['source210']['owner_identity']['creation']),timeout=900);put('TWO50_CLOSED_SOURCE210_CANONICAL_COST_ACTUAL.json',a);rows=a['cohort']['rows'];m=rows['e2'].get('final') or {};texts1,saved1=capture(c,a,[m['final']] if m.get('passed') else [],'e2');c.close();c=None
  c=d.connect72(pw);pw=None;b=d.code(c,d.PY72,READ72,dict(q=q),timeout=210);m=rows['recovery'].get('final') or {};texts2,saved2=capture(c,b,[m['final']] if m.get('passed') else [],'recovery');put('TWO50_CLOSED_TARGET72_ACTUAL.json',b);v=dict(epoch=time.time(),actual_finite_transport_returned=True,source210=a,target72=b,complete_models={'e2':saved1,'recovery':saved2},all_texts=texts1+texts2,original_canonical_cost_settled=True,not_skill_qualification=True);put('TWO50_CURRENT_COHORT_COMPLETE_FINALS_ORIGINAL_COST_RETURNED_ACTUAL.json',v);print(json.dumps(dict(closed=True,models={k:len(x) for k,x in v['complete_models'].items()},original_cost_settled=True)),flush=True)
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('TWO50_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_collector_or_GPU=True));raise
