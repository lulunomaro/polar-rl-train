"""Actual early reset failure receipts only, not the gated normal FINAL collector.

No native model/first-Pi/raw/GPU read, no writer, no alteration of original900gate.
"""
from pathlib import Path
import json,sys,time,importlib.util,hashlib,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
REMOTE=r'''from pathlib import Path
import json,time,psutil,fcntl,hashlib
q=v['q'];backend=v['backend'];out=[]
for rec in v['known_own']:
 try:
  p=psutil.Process(rec['pid']);assert p.create_time()!=rec['creation'],'exact own process still alive'
  out.append(dict(pid=rec['pid'],creation=rec['creation'],actual_out=True,PID_recycled=True,no_foreign_exe_or_argv_query=True))
 except psutil.NoSuchProcess:out.append(dict(pid=rec['pid'],creation=rec['creation'],actual_out=True))
locks=[]
for p in map(Path,v['locks']):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 locks.append(dict(path=str(p),actual_fcntl_free=True))
texts={}
def capture(p):
 assert p.is_file() and not p.is_symlink() and p.stat().st_size<8000000
 raw=p.read_bytes();texts[str(p)]=dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),value=json.loads(raw))
keys=['h1'] if backend=='source210' else ['recovery']
for key in keys:
 B=Path(q['roots'][key]);identity=json.loads((B/'NODE_IDENTITY.json').read_bytes());assert identity['pid']==q['nodes'][key]['detached_pid']
 for rel in ['NODE_IDENTITY.json','NODE_EXIT_ACTUAL.json','NODE_TERMINAL_ACTUAL.json','NODE_ORIGINAL_ERROR.json','job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json']:capture(B/rel)
 e=texts[str(B/'NODE_EXIT_ACTUAL.json')]['value'];row=texts[str(B/'NODE_TERMINAL_ACTUAL.json')]['value']['row']
 assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and row['terminal_all_own_children_waited']
 assert row['original_error'] and row['final'] is None and row['errors'] and row['actual_exit']['actual_waited']
 error=texts[str(B/'job0/production/ORIGINAL_ERROR_BEFORE_APP_CLOSE.json')]['value']['error'];assert 'reset-bank contract hash mismatch' in error and 'vec_env = RslRlVecEnvWrapper' in error
 assert not (B/'job0/production/FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').exists()
 assert not (B/'job0/production/FINAL.json').exists()
account=None
if backend=='target72':
 B=Path(q['owner_root'])
 for rel in ['OWNER_IDENTITY.json','OWNER_EXIT_ACTUAL.json','COHORT_FINAL.json']:capture(B/rel)
 cohort=texts[str(B/'COHORT_FINAL.json')]['value'];assert cohort['go']==v['go'] and cohort['original_cost_settled']
 assert texts[str(B/'OWNER_EXIT_ACTUAL.json')]['value']['original_cost_settled']
 C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
 assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
 seg=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==q['owner_identity']['pid'] and x['started_epoch']>=q['owner_identity']['creation']];assert len(seg)==1
 account=dict(canonical_path=str(C),canonical_SHA=hashlib.sha256(raw).hexdigest(),canonical_None=True,original_segment=seg[0],actual_remaining=c['remaining_training_seconds'],no_account_write_or_copy=True)
print(json.dumps(dict(epoch=time.time(),backend=backend,actual_own_out=out,original_locks=locks,texts=texts,account=account,original_error_not_rc0_success=True,no_new_model_or_GPU_or_actor_or_physics_read=True,no_normal_FINAL_collector_or900gate_change=True)))'''
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 q=json.loads((R/'NATIVE88B_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes());g=json.loads((R/'NATIVE88B_ACTUAL_SIGNED_TWO_GO_METADATA_ACTUAL.json').read_bytes())['go'];obs=json.loads((R/'NATIVE88_FIRST_NEW_POLICY_FINITE_RETURNED_ACTUAL.json').read_bytes())
 assert not obs['passed'] and all(t.get('first_positive') is None for t in obs['targets'].values())
 put('NATIVE88B_FAILURE_RECEIPT_READER_CONSUMED_BEFORE_REMOTE_ACTUAL.json',dict(epoch=time.time(),run_id=q['run_id'],purpose='genuine already-terminal reset failure, independent of scheduled normal fullFINAL collector',no_model_or_GPU_or_retry=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native88B_failed_receipt_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None;results={}
 try:
  for key,backend in [('recovery','target72'),('h1','source210')]:
   owned=[obs['targets'][key]['node_identity']['recorded'],obs['targets'][key]['worker_identity']['recorded']]
   locks=[q['specs'][key]['private_lock']]
   if backend=='target72':
    owned.append(q['owner_identity']);base='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/';locks.extend([base+'native_floor_supervisor.lock',base+'autonomy_controller.lock','/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'])
   c=route.connect() if key=='h1' else d.connect72(secret);py=route.PY if key=='h1' else d.PY72
   value=d.code(c,py,REMOTE,dict(q=q,go=g,backend=backend,known_own=owned,locks=locks),timeout=60);put('NATIVE88B_'+key.upper()+'_ACTUAL_RESET_FAILURE_COST_ALLOUT_READONLY_RETURNED.json',value);results[key]=value;c.close();c=None
  account=results['recovery']['account'];segment=account['original_segment'];fees=segment['experts'];total=sum(x['charged_seconds'] for x in fees.values());assert set(fees)=={'h1','recovery'} and abs(total-segment['charged_expert_seconds'])<1e-5
  for k,r in fees.items():assert r['duration_bound_passed'] is True and r['started_epoch']==g[k]['learning_started_epoch'] and abs(r['charged_seconds']-(r['ended_epoch']-r['started_epoch']))<1e-5 and 0<r['charged_seconds']<=3900
  assert abs(569553.363275528-total-account['actual_remaining'])<1e-5
  put('NATIVE88B_ACTUAL_EARLY_RESET_FAILURE_ORIGINAL_COST_ALLOUT_QUALIFIED_FOR_NEXT_PREPARATION.json',dict(epoch=time.time(),passed_original_cost_allout_only=True,run_id=q['run_id'],original_owner=q['owner_identity'],both_failed_before_first_control_and_NEW_Pi=True,formal_FINALs=False,source_models_remain_qualified_R5=True,fee_sumonce=total,independent_original_fees=fees,closing_remaining=account['actual_remaining'],actual_nodes_owner_workers_out=True,canonical_None=True,original_locks_free=True,original_normal_duration_flags_unchanged=True,results=results,no_refund_or_rewrite_or_second_writer=True,not_new_native_source_or_skill=True))
  print(json.dumps(dict(actual_finite_returned=True,failed_before_first_control=True,allownout=True,original_fee_sumonce=total,actual_remaining=account['actual_remaining'],no_new_model_or_GPU_read=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE88B_FAILED_RECEIPT_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(original_error=traceback.format_exc(),no_retry=True));raise
