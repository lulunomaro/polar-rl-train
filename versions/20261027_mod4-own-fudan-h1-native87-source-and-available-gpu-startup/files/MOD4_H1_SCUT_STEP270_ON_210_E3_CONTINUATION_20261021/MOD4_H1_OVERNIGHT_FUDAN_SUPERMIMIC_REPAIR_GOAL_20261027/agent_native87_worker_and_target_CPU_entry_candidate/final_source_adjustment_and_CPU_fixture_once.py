"""New tiny fixture and source/negative checks; never execute worker or target entry."""
from pathlib import Path
import sys,json,ast,hashlib,traceback,copy
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
for filename in ('h1_native_own87_worker_v1.py','build_native87_worker_source_once.py'):
    path=D/filename;value=path.read_text();value=value.replace("args.seed==task['seed']","args.seed==task['native_seed']")
    path.write_text(value,encoding='utf8')
path=D/'native87_protocol_v1.py';value=path.read_text()
value=value.replace("'new_native_architecture_initialized_fresh','new_native_optimizers_initialized_fresh'","'new_native_architecture_source_API_CPU_passed','new_native_optimizer_scope_source_CPU_passed'")
path.write_text(value,encoding='utf8')
rows=[]
def case(name,fn):
    try:rows.append(dict(name=name,passed=True,detail=fn()))
    except Exception:rows.append(dict(name=name,passed=False,error=traceback.format_exc()))
def yes(v):assert bool(v)
def reject(fn):
    try:fn()
    except (ValueError,KeyError):return True
    raise AssertionError('expected rejection')
import native87_protocol_v1 as p
from native87_source_guard_v1 import validate_task_go
task=dict(key='h1',native_seed=27,source_SHA=p.SOURCE_SHA,bootstrap_source_SHA=p.SOURCE_SHA,source_Adamstep=832460,
    source_normal_PPO_update=138,bootstrap_source_kind='closed_production_policy_only',fresh_environment_resume_scope='policy_only_no_source_environment_state',
    native87_contract_SHA='a'*64,method_config=p.METHOD)
go=dict(source_SHA=p.SOURCE_SHA,bootstrap_SHA=p.SOURCE_SHA,bootstrap_Adam=832460,bootstrap_source_kind='closed_production_policy_only',
    fresh_environment_resume_scope='policy_only_no_source_environment_state',native87_policy_only=True,new_native_architecture_fresh=True,
    native_continuation_restore_required=False,source_qualification_kind=p.KIND,manifest_SHA='b'*64,native87_contract_SHA='a'*64,
    seed=27,num_envs=4096,max_parent_seconds=3900,exit_headroom_seconds=300,nominal_end_epoch=4900,save_deadline=4600)
case('typed_Task_GO_metadata_positive_only',lambda:validate_task_go(task,go,'b'*64))
for field,val in [('native_continuation_restore_required',True),('num_envs',20000),('source_qualification_kind','UNISUPERMIMIC_FUDAN_NATIVE85_CONTINUATION_SOURCE_SDK_CPU_V86'),('bootstrap_Adam',829700)]:
    def wrong(field=field,val=val):g=dict(go);g[field]=val;return reject(lambda:validate_task_go(task,g,'b'*64))
    case('reject_'+field,wrong)
def source_AST():
    text=(D/'h1_native_own87_worker_v1.py').read_text();tree=ast.parse(text)
    assert "c.scene.num_envs=N;c.seed=args.seed;c.episode_length_s=5." in text
    assert "N=4096" in text and "checkpoint_API.resume_h1_new_episode=resume_policy_only_fresh4096" in text
    assert "checkpoint_API.install_h1_save_contract=install_step270_save_contract" in text
    assert "from native_own_fudan87_training import run" in text and "J/'GO_PRODUCTION.json'" in text
    assert 'resume_step270_new_episode' not in text and 'native_continuation_v1' not in text
    assert "'actual_fresh4096_environment_CPU_passed'" not in (D/'native87_protocol_v1.py').read_text()
    return dict(factory4096_timeout5=True,original_save_chain=True,actual_GPU_not_claimed_preGO=True)
case('worker_source_wiring_and_CPU_scope_AST',source_AST)
for file in D.glob('*.py'):case('parse_'+file.name,lambda file=file:ast.parse(file.read_text()) is not None)
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
sys.path[:0]=[str(L/'root_native_bridge_integration_candidate'),str(L/'root_compact_static_context_candidate'),
    str(L/'agent_actual_DR_memory_getter_candidate_v1'),str(L/'agent_static_dynamic_delay_contract_candidate'),
    str(L/'root_augmented_world_model_candidate/v5'),str(B/'source'),str(B/'source/sm_deps')]
reference=L/'root_native_bridge_integration_candidate/MOD4_OWN_CONVERTED_FUDAN_JUMP_REFERENCE_V1_NOT_ADMITTED.json'
document=json.loads(reference.read_bytes())
contract=dict(expected_runtime_joint_names=document['joint_names'],expected_leg_joint_names=document['metadata']['actuator_leg_joint_names'])
tiny_task=dict(native_reference_relative=str(reference),native_seed=27)
def actual_tiny_api():
    from native87_tiny_API_fixture_v1 import check
    return check(D,contract,tiny_task)
case('new_actual_v5_vendor_v4_MDP_tiny_API_CPU_fixture_only',actual_tiny_api)
report=dict(passed=all(r['passed'] for r in rows),passed_count=sum(r['passed'] for r in rows),total=len(rows),tests=rows,
    actual_worker_or_target_CPU_executed=False,no_model_read_hash_copy_or_GPU=True,synthetic_Task_GO_are_inmemory_only=True)
put('NATIVE87_WORKER_SOURCE_AND_NEW_TINY_API_CPU_V1_ACTUAL.json',report)
print(json.dumps(dict(passed=report['passed'],passed_count=report['passed_count'],total=report['total'])))
if not report['passed']:raise SystemExit(1)
