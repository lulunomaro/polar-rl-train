from pathlib import Path
import importlib.util,json,sys,time
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def closed():return json.loads((T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V63_20261024/reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes())
def secret():
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.recover()
READ210=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports');raw=C.read_bytes();c=json.loads(raw);H=lambda b:hashlib.sha256(b).hexdigest()
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8
owner=Path(v['closed']['owner_root']);node=Path(v['closed']['roots']['h1']);assert json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'] and json.loads((owner/'COHORT_FINAL.json').read_bytes())['original_cost_settled'] and json.loads((node/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in (owner,node)) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
locks=[C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['closed']['specs']['h1']['private_lock'])]
for p in locks:
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
metadata={n:dict(SHA=H((E/n).read_bytes()),value=json.loads((E/n).read_bytes())) for n in ('PLAN_APPROVAL.json','MOD4_MOE_EXECUTION_CONTRACT.json','MOE_PLAN_EXECUTION_CURRENT.json')}
assert metadata['PLAN_APPROVAL.json']['value']['authorized_budget_ceiling_seconds']==1548000 and metadata['MOD4_MOE_EXECUTION_CONTRACT.json']['value']['budget']['authorized_seconds']==1548000
print(json.dumps(dict(epoch=time.time(),canonical_SHA=H(raw),authorized=c['authorized_training_seconds'],charged=c['charged_training_seconds'],remaining=c['remaining_training_seconds'],active_segment=c['active_segment'],extension_records=c['budget_extensions'],completed_count=len(c['completed_segments']),completed_digest=H(json.dumps(c['completed_segments'],sort_keys=True).encode()),original_locks_free=[str(p) for p in locks],closed63_all210out=True,metadata=metadata,historical_master_SHA=H((E/'MOD4_MOE_MASTER_PLAN.md').read_bytes()),no_canonical_copy_or_write=True)))
'''
READ72=r'''
from pathlib import Path
import fcntl,json,os,psutil,time
root=Path(v['closed']['roots']['recovery']);assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert not any(p.pid!=os.getpid() and any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for p in (Path(v['closed']['specs']['recovery']['private_lock']),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(epoch=time.time(),closed63_all72out=True,private_shared_locks_free=True,no_GPU_query_or_mutation=True)))
'''
