from pathlib import Path
import hashlib,json,os,sys,time,traceback
import strict_original_Linux_transport_memory as t
B=Path(__file__).resolve().parent;R=B/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');D=Path('/mnt/mod4_linux_durable_20261013/LINUX_RETURN_RECONCILIATION_2010v32');q=v['payload'];assert not D.exists() and D.parent.is_mount();locks=[]
try:
 for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
  f=p.open('rb+');locks.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
 raw=C.read_bytes();assert hashlib.sha256(raw).hexdigest()==q['expected_original_canonical_SHA'];c=json.loads(raw);assert c['active_segment'] is None and c['remaining_training_seconds']==q['expected_original_remaining'];assert not any(p.pid!=os.getpid() and any(x.startswith('/mnt/mod4_linux_durable_20261013/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
 scope={};exec(compile(v['pure_source'],'<CPU-reviewed exact pending debit>','exec'),scope);new,added=scope['apply_closed'](c,q['pending'],q['transaction_id']);assert sum(x['charged_expert_seconds'] for x in added)==q['expected_total_seconds'];assert new['active_segment'] is None
 D.mkdir();fd=os.open(D/'TRANSACTION_O_EXCL_RESERVATION.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:json.dump(dict(epoch=time.time(),transaction_id=q['transaction_id'],run_ids=[p['run_id'] for p in q['pending']],canonical_before_SHA=hashlib.sha256(raw).hexdigest()),f);f.flush();os.fsync(f.fileno())
 data=json.dumps(new,indent=2).encode();tmp=C.with_name(C.name+'.E3_PENDING_V32.partial');fd=os.open(tmp,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
 os.replace(tmp,C);fd=os.open(C.parent,os.O_RDONLY);os.fsync(fd);os.close(fd);after=C.read_bytes();assert after==data;again=json.loads(after);assert again['active_segment'] is None and len(again['completed_segments'])==len(c['completed_segments'])+len(added)
 receipt=dict(epoch=time.time(),passed=True,transaction_id=q['transaction_id'],original_canonical_path=str(C),canonical_before_SHA=hashlib.sha256(raw).hexdigest(),canonical_after_SHA=hashlib.sha256(after).hexdigest(),original_authorized_seconds=again['authorized_training_seconds'],original_extension_count=len(again['budget_extensions']),original_canonical_active_None_after=True,original_two_fcntl_held_during_transaction=True,distinct_run_ids_charged_once=[x['run_id'] for x in added],actual_added_segments=added,exact_original_interval_sumonce=q['expected_total_seconds'],charged_before=c['charged_training_seconds'],charged_after=again['charged_training_seconds'],remaining_before=c['remaining_training_seconds'],remaining_after=again['remaining_training_seconds'],legacy_Windows9400_pending_and_unknown512_separate=True,no_ledger_copy_refund_rounding_extension_or_active_clear=True)
 f=(D/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').open('x');json.dump(receipt,f,indent=2);f.flush();os.fsync(f.fileno());f.close()
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
print(json.dumps(receipt))
'''
def main():
 q=json.loads((R/'EXACT_CLOSED_E3_PENDING_RECONCILIATION_PAYLOAD_CPU_ACTUAL.json').read_bytes());assert json.loads((R/'EXACT_PENDING_RECONCILIATION_PURE_CPU_BOUNDARIES_ACTUAL.json').read_bytes())['passed'];put('EXACT_E3_ORIGINAL_CANONICAL_RECONCILIATION_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,transaction_id=q['transaction_id']));c=t.connect()
 try:
  v=t.code(c,CODE,dict(payload=q,pure_source=(B/'reconcile_exact_closed_E3_pending_CPU.py').read_text('utf8')),timeout=90);put('ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json',v);put('EXACT_E3_ORIGINAL_CANONICAL_RECONCILIATION_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_transport_returned=True,actual=v));print(json.dumps(dict(passed=True,intervals=len(v['distinct_run_ids_charged_once']),actual_debit=v['exact_original_interval_sumonce'],remaining=v['remaining_after'],original_active_None=True)),flush=True)
 finally:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('ORIGINAL_RECONCILIATION_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_transaction_or_once=True));raise
