"""Metadata/AST only; no owner/node, fee function, installer or model execution."""
from pathlib import Path
import json,copy,ast,hashlib,traceback,datetime
import native87_protocol_v1 as p
import native87_installer_plan_v1 as install
D=Path(__file__).resolve().parent;T=D.parent.parent
N=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026';OLD=N/'controllers_v2'
rows=[]
def case(name,fn):
    try:detail=fn();rows.append(dict(name=name,passed=True,detail=detail))
    except Exception:rows.append(dict(name=name,passed=False,error=traceback.format_exc()))
def yes(v):assert bool(v)
def reject(fn):
    try:fn()
    except (ValueError,KeyError):return True
    raise AssertionError('Expected rejection')
def spec(key):
    return dict(key=key,native87_policy_only=True,new_native_architecture_fresh=True,finite_method_test=True,
        closed_production_continuation=False,native_continuation=False,bootstrap_source_kind='closed_production_policy_only',
        source_SHA=p.SOURCE_SHA,bootstrap_source_SHA=p.SOURCE_SHA,source_Adamstep=832460,source_normal_PPO_update=138,
        seed=p.SEEDS[key],method_config=copy.deepcopy(p.METHOD),GPU_UUID=p.GPUS[key],execution_backend='source210' if key=='h1' else 'target72',
        policy_hz=100,max_parent_seconds=3900,exit_headroom_seconds=300,owner_authority_generation=p.AUTHORITY_GENERATION,
        fresh_environment_resume_scope='policy_only_no_source_environment_state',manifest_SHA='1'*64,native87_contract_SHA='2'*64,
        qualified_H1_report_SHA='3'*64,previous86_closure_SHA='4'*64,reference_artifact_SHA='5'*64,objective_contract_SHA='6'*64,
        candidate_pins={'fixture_source.py':'7'*64})
def ready(s):
    v=dict(passed=True,kind=p.KIND,source_SHA=p.SOURCE_SHA,bootstrap_SHA=p.SOURCE_SHA,bootstrap_Adam=832460,
        source_normal_PPO_update=138,native_continuation_restore_required=False,native_environment_state_from_source=False,
        source_environment_count=20000,actual_environment_count=4096,episode_timeout_s=5.,GPU_UUID=s['GPU_UUID'],
        execution_backend=s['execution_backend'],seed=s['seed'],method_config=copy.deepcopy(p.METHOD),candidate_pins=s['candidate_pins'],
        **{k:s[k] for k in ('native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA','reference_artifact_SHA','objective_contract_SHA')},
        **{k:True for k in p.READY_FLAGS})
    return dict(key=s['key'],phase='ready',manifest_SHA=s['manifest_SHA'],original_error=False,
        closed_source_CPU=dict(value=v,SHA=p.digest(v),actual_CPU_waited_EXIT0=True))
for key in p.SEEDS:case('typed_'+key+'_same_H1_source_distinct_seed',lambda key=key:yes(p.native87_valid_ready(ready(spec(key)),spec(key))))
cfg=dict(experts={k:spec(k) for k in p.SEEDS},deferred_experts=[],scheduling_authority='human_requested_available_experts',authority_generation=p.AUTHORITY_GENERATION)
case('three_H1_schedule',lambda:p.validate_schedule(cfg))
for field,value in [('source_SHA','7f8f270c84b7e3d9e7efd0b1bd29d10d430a51bb976e1689222859f24e714d59'),('native_continuation',True),('closed_production_continuation',True),('seed',99),('source_Adamstep',829700),('policy_hz',50)]:
    def bad(field=field,value=value):s=spec('recovery');s[field]=value;return reject(lambda:p.validate_spec(s))
    case('wrong_scope_'+field,bad)
for flag in p.READY_FLAGS:
    def badflag(flag=flag):
        s=spec('e2');r=ready(s);v=r['closed_source_CPU']['value'];v[flag]=False;r['closed_source_CPU']['SHA']=p.digest(v)
        yes(not p.native87_valid_ready(r,s))
    case('missing_actual_admission_'+flag,badflag)
case('savedqualified_reports_only_no_PT',lambda:p.validate_saved_source_and_closure(
    json.loads((N/'reports/THREE_GPU86B_HEALTHY_H1_CPU_INITIAL_LOAD_ACTUAL.json').read_bytes()),
    json.loads((N/'reports/THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes()),
    json.loads((N/'reports/THREE_GPU86B_CLOSED_AUTHORITY72_ORIGINAL_COST_ACTUAL.json').read_bytes())))
def ast_fn(path,name):return ast.dump(next(n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
case('original_charge_values_AST_exact_not_executed',lambda:yes(ast_fn(D/'controllers/three_slot_common_v1.py','charge_values')==ast_fn(OLD/'three_slot_common_v1.py','charge_values')))
case('original_owner_account_AST_exact_not_executed',lambda:yes(ast_fn(D/'controllers/three_slot_finite_owner_V86_authority72.py','account')==ast_fn(OLD/'three_slot_finite_owner_V86_authority72.py','account')))
for name in ['forwarded_original_owner_control_v1.py','single_writer72_authority_V85M_source.py']:
    case('byteexact_'+name,lambda name=name:yes((D/'controllers'/name).read_bytes()==(OLD/name).read_bytes()))
def inventory():
    rows=[dict(relative='fixture_source.py',bytes=1,SHA='7'*64)]
    return install.installer_plan(spec('h1'),rows,{'fixture_source.py':'7'*64},{k:'pending' for k in install.REQUIRED_FRESH_HOOKS})['actual_install_performed'] is False
case('installer_plan_all_pending_not_actual_install',lambda:yes(inventory()))
case('unapproved_Python_rejected',lambda:reject(lambda:install.validate_exact_inventory([dict(relative='evil.py',bytes=1,SHA='7'*64)],{})))
case('path_escape_rejected',lambda:reject(lambda:install.validate_exact_inventory([dict(relative='../escape.py',bytes=1,SHA='7'*64)],{})))
case('worker_replay_estimate',lambda:yes(p.worker_plan(spec('h1'))['replay_bytes']==4935680000))
report=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=all(x['passed'] for x in rows),
    passed_count=sum(x['passed'] for x in rows),total=len(rows),tests=rows,positive_ready_values_are_synthetic_fixtures_only=True,
    actual_installed_SDK_CPU_passed=False,no_actual_ready_Task_GO_install_fee_model_or_network=True)
with (D/'NATIVE87_TYPED_OWNER_WORKERPLAN_SOURCE_CPU_V1_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=report['passed'],passed_count=report['passed_count'],total=report['total'])))
if not report['passed']:raise SystemExit(1)
