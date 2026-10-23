from pathlib import Path
import importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
READ=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,time
roots=[Path(x) for x in v['roots']];own=[]
for p in psutil.process_iter(['pid','cmdline']):
 if p.pid!=os.getpid() and any(any(a.startswith(str(r)+'/') for r in roots) for a in p.info['cmdline'] or []):own.append(p.pid)
assert not own
flags={str(r):dict(root_exists=r.exists(),GO=(r/'GO_PRODUCTION.json').exists() or (r/'job0/GO_PRODUCTION.json').exists(),node_identity=(r/'NODE_IDENTITY.json').exists(),owner_identity=(r/'OWNER_IDENTITY.json').exists()) for r in roots};assert not any(x['GO'] or x['node_identity'] or x['owner_identity'] for x in flags.values())
for name in v['locks']:
 with Path(name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
result=dict(epoch=time.time(),own_roots_processes_actual_out=True,roots=flags,original_locks_free=True,durable_free=shutil.disk_usage(v['disk']).free)
if v.get('canonical'):
 C=Path(v['canonical']);raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None and c['remaining_training_seconds']==v['remaining'] and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8;assert not roots[-1].exists();result.update(canonical_None=True,remaining_unchanged=c['remaining_training_seconds'],canonical_SHA=hashlib.sha256(raw).hexdigest(),owner_root_not_created=True,actual_disk25_component=result['durable_free']>25*1024**3)
print(json.dumps(result))
'''
try:
 q=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());proof=json.loads((T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V49_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());put('FAILED50_PREOWNER_READ_STARTED_ACTUAL.json',dict(epoch=time.time(),read_only=True))
 c=d.t.connect()
 try:a=d.code(c,d.t.PY,READ,dict(roots=[q['roots']['h1'],q['owner_root']],locks=['/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/native_floor_supervisor.lock','/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock',q['specs']['h1']['private_lock']],disk='/mnt/mod4_linux_durable_20261013',canonical='/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json',remaining=proof['remaining_actual_snapshot']),timeout=45)
 finally:c.close()
 sp=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=d.connect72(secret);secret=None
 try:b=d.code(c,d.PY72,READ,dict(roots=[q['roots']['recovery']],locks=[q['specs']['recovery']['private_lock'],'/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'],disk='/home/lc01/Zonglin Li/zonglin2'),timeout=45)
 finally:c.close()
 result=dict(epoch=time.time(),passed=True,source210=a,source72=b,no_GO_PPO_or_new_cost_segment=True,no_owner_root_created=True,installed_roots_and_original_error_preserved=True,no_budget_refund_or_second_writer=True,precise_owner_disk25_guard_failed_after_required_install_copy=not a['actual_disk25_component']);put('FAILED50_INSTALLED_SOURCE_CPU_THEN_PREOWNER_DISK25_NO_GO_ALLOUT_ACTUAL.json',result);print(json.dumps(result))
except BaseException:
 put('FAILED50_PREOWNER_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rerun_old_once=True));raise
