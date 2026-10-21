from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';R.mkdir(exist_ok=True)
W=B.parent
s=importlib.util.spec_from_file_location('strict210',W/'MOD4_TWO_LINUX_POLICY50_COHORT_49_20261021/strict_original_Linux_transport_memory.py');t=importlib.util.module_from_spec(s);s.loader.exec_module(t)
READ=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports');c=json.loads(C.read_bytes());H=lambda b:hashlib.sha256(b).hexdigest();locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(str(p));fcntl.flock(f,fcntl.LOCK_UN)
root=Path('/mnt/mod4_linux_durable_20261013/T2policy50_2010v48');ex=json.loads((root/'owner/OWNER_EXIT_ACTUAL.json').read_bytes());live=[dict(pid=p.pid,argv=p.info['cmdline'],creation=p.create_time()) for p in psutil.process_iter(['pid','cmdline']) if p.pid!=os.getpid() and any(x.startswith(str(root)+'/') for x in p.info['cmdline'] or [])];assert not live and c['active_segment'] is None and ex['original_cost_settled']
metadata={}
for name in ('PLAN_APPROVAL.json','MOD4_MOE_EXECUTION_CONTRACT.json','MOE_PLAN_EXECUTION_CURRENT.json'):
 raw=(E/name).read_bytes();j=json.loads(raw);metadata[name]=dict(SHA=H(raw),keys=list(j),budget=j.get('budget'),authorized_budget_ceiling_seconds=j.get('authorized_budget_ceiling_seconds'),approved=j.get('approved'),S8_authorized=j.get('S8_authorized'),approved_plan_sha256=j.get('approved_plan_sha256'))
print(json.dumps(dict(epoch=time.time(),canonical=str(C),canonical_SHA=H(C.read_bytes()),keys=list(c),authorized=c['authorized_training_seconds'],charged=c['charged_training_seconds'],remaining=c['remaining_training_seconds'],active_segment=c['active_segment'],extension_records=c['budget_extensions'],completed_count=len(c['completed_segments']),completed_digest=H(json.dumps(c['completed_segments'],sort_keys=True).encode()),original_locks_free=locks,cohort48_original_cost_settled=True,cohort48_all210out=True,metadata=metadata,no_canonical_copy=True)))
'''
try:
 with (R/'PROBE_STARTED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time()),f)
 c=t.connect()
 try:v=t.code(c,READ,timeout=90)
 finally:c.close()
 with (R/'ORIGINAL_BUDGET_EIGHTH_BEFORE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(v,ensure_ascii=False))
except BaseException:
 with (R/'PROBE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc()),f)
 raise
