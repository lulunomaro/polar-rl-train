from pathlib import Path
import hashlib,importlib.util,json,os,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
read=lambda p:json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
SOURCE=r'''
from pathlib import Path
import fcntl,json,os,psutil,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());q=v['q'];B=Path(q['owner_root']);assert c['active_segment'] is None and c['remaining_training_seconds']==v['remaining'] and json.loads((B/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
for root in (B,Path(q['roots']['h1'])):assert not any(p.pid!=os.getpid() and any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(q['specs']['h1']['private_lock'])):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(epoch=time.time(),canonicalNone=True,remaining_snapshot=c['remaining_training_seconds'],original_owner_H1_out_locksfree=True,no_budget_write=True)))
'''
TARGET=r'''
from pathlib import Path
import fcntl,json,os,psutil,time
B=Path(v['root']);row=json.loads((B/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];e=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());assert row['original_error'] and not (row.get('final') or {}).get('passed') and row['terminal_all_own_children_waited'] and e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired']
assert not any(p.pid!=os.getpid() and any(a.startswith(str(B)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for p in (Path(v['private_lock']),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
last=row['latest_save'];assert last==v['last'] and last['policy_updates']>0 and last['world_updates']>0 and last['not_PPO_or_production_source'];p=Path(last['path']);assert p.resolve().is_relative_to((B/'job0/production/control_prefix_raw').resolve()) and not p.is_symlink() and p.name.startswith('preupdate_fullsource_') and p.suffix=='.pt';s=p.stat();assert s.st_size==last['bytes'] and s.st_nlink==1
idx=json.loads((B/'job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes());assert any(x['path']==str(p) and x['SHA']==last['SHA'] and x['bytes']==last['bytes'] for x in idx['preupdate_full_sources'])
states=[]
for name in ('native_supermimic_H1_final.pt','native_supermimic_H1_final.pt.partial','FAILED_PARTIAL_NATIVE_FULLSTATE.pt','FINAL.json','NATIVE_FULLSAVE_ORIGINAL_ERROR.json','NATIVE_SUPERMIMIC_LEARN_ORIGINAL_ERROR.json','APP_CLOSING.json','STOP_AFTER_SAVE.json'):
 x=B/'job0/production'/name;states.append(dict(path=str(x),present=x.exists(),bytes=x.stat().st_size if x.is_file() else None,no_content_read=True))
print(json.dumps(dict(epoch=time.time(),last=last,stat=dict(inode=s.st_ino,device=s.st_dev,mtime_ns=s.st_mtime_ns,bytes=s.st_size,nlink=s.st_nlink),original_index_complete_controls=idx['controls'],last_native_snapshot_not_FINAL_or_production_source=True,own_method_out_private_shared_free=True,finalization_path_stat_only=states,no_SHA_rehash_on_host=True)))
'''
try:
 q=read(R/'THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');co=read(R/'THREE_EXPERT_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert co['actual_finite_transport_returned'] and co['original_canonical_cost_settled'];last=co['source210']['cohort']['rows']['e2']['latest_save']
 put('LAST_NATIVE_EXECUTION_EVIDENCE_MISSING_ONLY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,one_exact_complete_preupdate_not_FINAL=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route;c=route.connect()
 try:a=d.code(c,route.PY,SOURCE,dict(q=q,remaining=co['source210']['original_canonical_remaining']),timeout=45)
 finally:c.close()
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);c=d.connect72(m.recover())
 try:
  b=d.code(c,d.PY72,TARGET,dict(root=q['roots']['e2'],private_lock=q['specs']['e2']['private_lock'],last=last),timeout=60);sf=c.open_sftp();sf.get_channel().settimeout(120);p=N/'last_complete_native_execution_evidence'/Path(last['path']).name;p.parent.mkdir();part=p.with_suffix('.pt.partial')
  try:
   sf.get(last['path'],str(part));s=sf.stat(last['path']);assert (s.st_size,int(s.st_mtime))==(last['bytes'],b['stat']['mtime_ns']//10**9)
  finally:sf.close()
  digest=hashlib.sha256()
  with part.open('rb') as f:
   for data in iter(lambda:f.read(8*1024**2),b''):digest.update(data)
  assert part.stat().st_size==last['bytes'] and digest.hexdigest()==last['SHA'];part.replace(p)
 finally:c.close()
 result=dict(epoch=time.time(),actual_finite_returned=True,source210=a,target72=b,checkpoint=dict(last,local_path=str(p),twohost_complete_SHA=True,not_FINAL_not_production_source=True),missing_FINAL_original_node_error_preserved=True,no_original_cost_or_model_qualification_rewritten=True)
 put('LAST_NATIVE_COMPLETE_PREUPDATE_EXECUTION_EVIDENCE_RETURNED_ACTUAL.json',result);print(json.dumps(dict(returned=True,policy_updates=last['policy_updates'],world_updates=last['world_updates'],not_FINAL=True)))
except BaseException:
 put('LAST_NATIVE_EXECUTION_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_replay=True));raise
