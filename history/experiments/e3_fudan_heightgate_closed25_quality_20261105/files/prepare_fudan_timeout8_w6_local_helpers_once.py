"""Create three unused W6 helpers, no SSH/model/SDK/fixtures/ledger activity."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent
pairs=[('prepare_stage_fudan_n20000_w5_admission2_once.py','prepare_stage_fudan_timeout8_w6_once.py'),('dispatch_fudan_n20000_w5_admission2_original_owner_once.py','dispatch_fudan_timeout8_w6_original_owner_once.py'),('collect_fudan_n20000_w5_admission2_window_once.py','collect_fudan_timeout8_w6_window_once.py')]
assert all(not(D/b).exists()for a,b in pairs)
def one(t,a,b):
    assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)
results=[]
for src,dst in pairs:
    t=(D/src).read_text(encoding='utf8')
    t=t.replace('FDN_N20000_W5_','FDN_N20000_W6_TIMEOUT8_')
    if src.startswith('prepare_stage'):
        t=one(t,"native_payload_v5_n20000_admission2","native_payload_v6_n20000_timeout8")
        t=one(t,"source_fudan_native_worker_v3_20k","source_fudan_native_worker_v4_20k_timeout8")
        start=t.index('W4_CLOSED=');end=t.index('assert N.is_dir()',start)
        block='''prior=json.loads((D/'reports/FDN_N20000_W5_20261104_205335/CLOSED_RESULT.json').read_bytes());assert prior['closed'] is True
m=prior['metadata'];x=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];f=m['FDN_FINAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json'];qualification=m['FDN_PARENT_WAIT_QUALIFICATION.json']
assert x['errors']==[] and all(x[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))
assert outer['actual_wait_returncode']==0 and outer['original_owner_reaped']is True and outer['original_owner_pid']==1616384 and outer['controller_pid']==1616377
assert qualification['qualified']is True and all(v is True for v in qualification['checks'].values())
assert latest==f['latest_complete_save'] and latest['sha256']=='8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78' and latest['bytes']==1204250903
assert f['counters']==dict(updates=133,policy_optimizer_steps=2660,encoder_optimizer_steps=2660,transitions_seen=78822912) and f['window_counters']['updates']==69 and f['native_counters']['actual_native_policy_steps']==3360
assessment=json.loads((D/'FDN_N20000_CLOSED69_QUALITY_DECISION_V1.json').read_bytes());assert assessment['decision']=='KEEP_REGISTRY_V12_E3_1CD_NO_8AF4_PROMOTION' and assessment['original_N80']['execution_qualified']is True
source=dict(path=latest['path'],sha256=latest['sha256'],bytes=latest['bytes'],run=f['run'],counters=f['counters'],source_envs=20000,actual_native_policy_steps=3360,unoptimized_pending_controls=48,source_training_execution_qualified=True)
overlay=D/'source_task_runtime_v2_lowtimeout8/e3_fudan_task_runtime_v1.py';overlay_raw=overlay.read_bytes();assert len(overlay_raw)==8571 and H(overlay_raw)=='386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2'
'''
        t=t[:start]+block+t[end:]
        assert t.count('source_original_owner_v3_20k')==2;t=t.replace('source_original_owner_v3_20k','source_original_owner_v4_20k_timeout8')
        assert t.count('stage_fudan_nonpt_v3_20k.py')==3;t=t.replace('stage_fudan_nonpt_v3_20k.py','stage_fudan_nonpt_v4_20k_timeout8.py')
        t=one(t,"source_task_runtime_v1/e3_fudan_task_runtime_v1.py","source_task_runtime_v2_lowtimeout8/e3_fudan_task_runtime_v1.py")
        t=one(t,'MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W5_ADMISSION2_','MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_CONTINUE133_W6_')
    compile(ast.parse(t),dst,'exec');(D/dst).write_text(t,encoding='utf8',newline='\n');results.append(dict(path=str(D/dst),bytes=len(t.encode()),sha256=hashlib.sha256(t.encode()).hexdigest()))
p=D/'source_original_owner_v4_20k_timeout8/fudan_worker_close_contract_v1.py';compile(ast.parse(p.read_text(encoding='utf8')),str(p),'exec')
print(json.dumps(dict(new_sources=results,close_contract_AST_compile_pass=True,stage_dispatch_training_or_models_executed=False),indent=2))
