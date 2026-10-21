"""Bounded read-only collection after this cohort's actual pre-GO owner error."""
from pathlib import Path
import ast,getpass,json,os,sys,time,traceback
import deploy_two50_reconciled_original_writer_once as d
import collect_current_two50_finals_original_cost_bounded_once as old
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
Q=v['q'];roots={k:Path(p) for k,p in v['roots'].items()};until=time.monotonic()+v['wait'];read=lambda p:json.loads(p.read_bytes()) if p.is_file() else None
def own():
 out=[]
 for p in psutil.process_iter(['pid','create_time','cmdline','exe']):
  try:
   if p.pid!=os.getpid() and any(any(x.startswith(str(root)+'/') for root in roots.values()) for x in p.info['cmdline'] or []):out.append(p.info)
  except psutil.Error:pass
 return out
while own() or any(not (root/('OWNER_EXIT_ACTUAL.json' if key=='owner' else 'NODE_EXIT_ACTUAL.json')).is_file() for key,root in roots.items()):
 assert time.monotonic()<until,'Actual pre-GO children have not exited; no guessed out'
 time.sleep(3)
texts=[];state={}
for key,root in roots.items():
 state[key]={n:read(root/n) for n in ('OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','OWNER_CURRENT.json','NODE_ORIGINAL_ERROR.json','NODE_EXIT_ACTUAL.json','NODE_TERMINAL_ACTUAL.json','NODE_CURRENT.json') if (root/n).is_file()}
 assert not (root/'job0/GO_PRODUCTION.json').exists() and not (root/'GO_PRODUCTION.json').exists()
 for p in root.rglob('*'):
  if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv'):
   raw=p.read_bytes();texts.append(dict(path=str(p),relative=key+'/'+p.relative_to(root).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
locks=[]
for path in v['locks']:
 with Path(path).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=path,actual_fcntl_free=True))
result=dict(epoch=time.time(),states=state,text_files=texts,all_own_actual_out=True,locks=locks,no_actual_GO_files=True,no_model_download_or_account_write=True)
if 'owner' in roots:
 c=read(Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json'));segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==Q['owner']['detached_pid'] and x['started_epoch']>=v['owner_creation']]
 assert c['active_segment'] is None and not segments and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7
 result['canonical_snapshot']=dict(active_segment=None,remaining=c['remaining_training_seconds'],charged=c['charged_training_seconds'],authorized=c['authorized_training_seconds'],extension_count=len(c['budget_extensions']),matching_completed_segments=segments)
print(json.dumps(result))
'''
def main():
 proof=json.loads((R/'TWO50_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_OR_PENDING_ACTUAL.json').read_bytes());assert not proof['passed'] and proof['source210']['errors'] and not proof['source210']['current']['go'];q=json.loads((R/'TWO50_ORIGINAL_ACCOUNT_COHORT_DETACHED_ACTUAL.json').read_bytes());put('V80_PREGO_FAILURE_COLLECTOR_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_owner=q['owner']));pw=getpass.getpass('72 pre-GO error and actual exits (hidden): ');c=None
 try:
  creation=proof['source210']['owner_identity']['creation'];common=dict(q=q,owner_creation=creation)
  c=d.t.connect();a=d.code(c,d.t.PY,READ,dict(common,roots=dict(owner=q['owner_root'],e2=q['roots']['e2']),wait=180,locks=['/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock','/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock',q['specs']['e2']['private_lock']]),timeout=210);put('V80_PREGO_SOURCE210_ACTUAL.json',a);t1,_=old.capture(c,a,[],'e2');c.close();c=None
  c=d.connect72(pw);pw=None;b=d.code(c,d.PY72,READ,dict(common,roots=dict(recovery=q['roots']['recovery']),wait=90,locks=[q['specs']['recovery']['private_lock'],'/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock']),timeout=120);put('V80_PREGO_TARGET72_ACTUAL.json',b);t2,_=old.capture(c,b,[],'recovery');put('V80_PREGO_OWNER_ERROR_ALL_OUT_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_transport_returned=True,source210=a,target72=b,all_texts=t1+t2,no_GO_or_PPO=True,no_current_canonical_segment_or_cost_interval=True,no_refund_or_budget_mutation=True));print(json.dumps(dict(actual_all_out=True,no_GO=True,no_new_cost_interval=True,remaining=a['canonical_snapshot']['remaining'])))
 finally:
  pw=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('V80_PREGO_COLLECTOR_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_once=True));raise
