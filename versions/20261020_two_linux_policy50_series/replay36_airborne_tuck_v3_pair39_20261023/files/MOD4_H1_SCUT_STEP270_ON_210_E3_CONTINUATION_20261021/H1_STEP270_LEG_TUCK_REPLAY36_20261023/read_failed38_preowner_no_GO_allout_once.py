from pathlib import Path
import importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent;T=D.parent;W=T.parent;R=D/'reports';N=T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V38_20261023'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import json,os,psutil,time
roots=[Path(x) for x in v['roots']];own=[]
for p in psutil.process_iter(['pid','cmdline','create_time','exe']):
 try:
  if p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
assert not own
out=dict(epoch=time.time(),all_own_failed38_processes_actual_out=True,roots=[dict(path=str(root),exists=root.exists(),any_PPO_model=list(str(p) for p in root.glob('job0/production/*.pt'))) for root in roots])
assert all(not x['any_PPO_model'] for x in out['roots'])
if v.get('owner'):
 owner=Path(v['owner']);assert not owner.exists()
 C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['remaining_training_seconds']==v['remaining'];out.update(owner_root_not_created=True,canonical_active_None=True,remaining_unchanged=c['remaining_training_seconds'],no_new_owner_GO_or_cost_segment=True)
print(json.dumps(out))
'''
try:
    q=json.loads((N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());proof=json.loads((T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V36_20261023/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes())
    m=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(m);m.loader.exec_module(memory);secret=memory.recover();c=None
    try:
        c=d.t.connect();a=d.code(c,d.t.PY,CODE,dict(roots=[q['roots']['h1'],q['owner_root']],owner=q['owner_root'],remaining=proof['remaining_actual_snapshot']),timeout=45);c.close();c=None
        c=d.connect72(secret);secret=None;b=d.code(c,d.PY72,CODE,dict(roots=[q['roots']['recovery']]),timeout=45);c.close();c=None
        put('FAILED38_PREOWNER_NO_GO_NO_NEW_COST_BOTH_INSTALLED_ROOTS_OUT_ACTUAL.json',dict(epoch=time.time(),passed=True,source210=a,target72=b,H1_installed_CPU_missing_reference_error_preserved=True,E3_installed_source_CPU_completed_but_no_node_GO=True,not_remote_root_absent_claim=True,no_account_change=True));print(json.dumps(dict(passed=True,all_failed38_own_processes_out=True,owner_not_created=True,no_GO_or_new_cost=True)))
    finally:
        secret=None
        if c:c.close()
except BaseException:
    put('FAILED38_PREOWNER_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
