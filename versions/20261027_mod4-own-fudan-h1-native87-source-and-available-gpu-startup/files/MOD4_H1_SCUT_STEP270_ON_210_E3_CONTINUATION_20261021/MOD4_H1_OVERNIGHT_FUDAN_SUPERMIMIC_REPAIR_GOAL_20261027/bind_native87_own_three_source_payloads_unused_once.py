"""New local source binding only. No remote call, model load or training grant."""
from pathlib import Path
import ast, hashlib, importlib.util, json, shutil, sys, time, traceback

T=Path(__file__).resolve().parent.parent
L=Path(__file__).resolve().parent
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026'
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
BASE=OLD/'payloads/e2'
BR=L/'root_native_bridge_integration_candidate'
WORK=L/'agent_native87_worker_and_target_CPU_entry_candidate'
INSTALL=L/'agent_native87_actual_install_activate_sources_candidate'
CONTROL=L/'agent_three_H1_native87_sole72_protocol_candidate/controllers_v2'
SOURCE_SHA='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394'
SOURCE_FILE='H1_closed86_policy_only_update138.pt'
REFERENCE='MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json'

def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def copy(src,dst):
    dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copy2(src,dst)
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
    assert not N.exists(),'Never rebind an existing actual attempt namespace'
    (N/'reports').mkdir(parents=True)
    put(N/'reports/LOCAL_BIND_NATIVE87_STARTED_ACTUAL.json',dict(epoch=time.time(),source_only=True,no_model_load_or_remote=True))
    old_manifest=read(BASE/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    prior={r['relative']:r for r in old_manifest['files']}
    source=OLD/'current_baseline_closed_models/h1/model_update138.pt'
    typed_path=OLD/'reports/THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json'
    typed=read(typed_path);assert typed['passed'] and typed['original_canonical_cost_settled'] and not typed['errors']
    qualified=dict(passed=True,key='h1',value=typed['models']['h1'],original_report_path=str(typed_path),original_report_SHA=H(typed_path))
    assert qualified['value']['final']['SHA']==SOURCE_SHA and source.stat().st_size==16868635
    authority_path=OLD/'reports/THREE_GPU86B_CLOSED_AUTHORITY72_ORIGINAL_COST_ACTUAL.json';authority=read(authority_path)
    assert authority['canonical_active_segment'] is None and authority['original_canonical_remaining']==577055.9868602753
    order=read(OLD/'current_three_closed_text/e2/job0/production/NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json')['actual_robot_joint_names']
    assert len(order)==30 and len(set(order))==30
    # Exact original LEG_ORDER source literal; runtime verifies actual actuator order.
    tree=ast.parse((BASE/'job0/runtime/isaac/mod4/mod4_task.py').read_text('utf8'))
    legs=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LEG_ORDER' for t in n.targets))
    assert legs==['left_crank','left_hip','right_crank','right_hip']
    controllers=N/'controllers';controllers.mkdir()
    for p in CONTROL.glob('*.py'):copy(p,controllers/p.name)
    # Explicit two reviewed newer revisions, never mutate old frozen helpers.
    for name,src in [('native87_protocol_v1.py',WORK/'native87_protocol_v1.py'),('native87_closed_source_CPU_v1.py',L/'native87_dispatcher_v3/native87_closed_source_CPU_v1.py')]:
        assert src.is_file(),str(src)
        dst=controllers/name
        old=dst.read_bytes();copy(dst,N/'source_prebind_history'/(name+'.original_bytes.txt'));dst.write_bytes(src.read_bytes())
    sys.path.insert(0,str(controllers));protocol=module('native87_protocol_v1',controllers/'native87_protocol_v1.py')
    support=module('native87_install_activate_support_v1',INSTALL/'native87_install_activate_support_v1.py')
    assert set(p.name for p in controllers.glob('*.py'))==set(support.OWNER_FILES)
    for name in ('install_three_H1_native87_source_sdk_CPU_finite_unused_once.py','activate_three_H1_native87_sole72_after_actual_CPU_unused_once.py','native87_install_activate_support_v1.py'):
        copy(INSTALL/name,N/name)
    reference=BR/REFERENCE;assert H(reference)=='9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3'
    old_specs=read(OLD/'reports/THREE_GPU86B_SOURCE_ADMITTED_PREPARED_ACTUAL.json')['specs']
    common_source_files=[BR/x for x in ('native_own_fudan87_training.py','native_wheel_leg_bridge_v4.py','converted_MOD4_jump_mdp_v4.py','fresh_policy_only_bootstrap87_v1.py','native_finalization_own_v3.py')]
    common_source_files += [L/'root_compact_static_context_candidate/compact_episode_static31_v1.py',L/'agent_actual_DR_memory_getter_candidate_v1/actual_DR_memory_getter_v1.py',L/'agent_static_dynamic_delay_contract_candidate/static_dynamic_delay_contract_v1.py']
    vendor=L/'root_augmented_world_model_candidate/v5/supermimic_wheel_leg_v3'
    root_new=[WORK/x for x in ('h1_native_own87_worker_v1.py','target_native87_source_sdk_cpu_v1.py','native87_source_guard_v1.py','native87_tiny_API_fixture_v1.py')]
    objective=dict(schema='mod4.own_native87.reference_objective_source_contract.v1',source_reference_SHA=H(reference),
        source_reference_scope='Fudan measured standing jump retargeted to own closed-chain geometry and explicit step translation/contact recovery',
        dimensions=dict(physical_joints=30,packed_state=127,dynamic_aux=54,episode_static_xi=31,observation=86,goal_frame=146,future_frames=10),
        dynamic_aux_predicted=True,task_relative_step_coordinates_observed=True,encoder_bias_actual_name_binding=True,
        soft_survival_temperatures=dict(height=.02,tilt=.04),coordinate_tracking_norm='masked_squared_sum',
        fixed_original_physical_success='dual wheel270mm cross+top contact+200 physics callbacks stable recovery',
        actual_target_SDK_or_physics_passed=False,no_foreign_transition_as_own_WM_truth=True,not_successful_demonstration_of_MOD4=True)
    payloads={};specs={};sources={};summaries={}
    for key in support.KEYS:
        P=N/'payloads'/key;P.mkdir(parents=True)
        known={};changed={};original={}
        def newcopy(src,rel):
            dest=P/rel
            if dest.exists():
                copy(dest,P/'prebind87_exact_history'/(rel+'.original_bytes.txt'))
                dest.write_bytes(Path(src).read_bytes())
            else:copy(src,dest)
            changed[rel]=H(dest)
        for row in old_manifest['files']:
            rel=row['relative'];p=BASE/rel
            if p.suffix.lower() in ('.pt','.pth','.npz') or rel=='job0/TASK.json':continue
            assert p.is_file() and p.stat().st_size==row['bytes'],rel
            copy(p,P/rel);known[rel]=row
            original[rel]=row['SHA']
        for p in controllers.glob('*.py'):newcopy(p,p.name)
        for p in root_new:newcopy(p,p.name)
        for p in common_source_files:newcopy(p,'source/'+p.name)
        for p in vendor.rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:newcopy(p,'source/supermimic_wheel_leg_v3/'+p.relative_to(vendor).as_posix())
        newcopy(reference,'source/'+REFERENCE)
        copy(source,P/'job0/source'/SOURCE_FILE)
        modelrel='job0/source/'+SOURCE_FILE
        known[modelrel]=dict(relative=modelrel,bytes=source.stat().st_size,SHA=SOURCE_SHA)
        put(P/'native_source_metadata/QUALIFIED_CLOSED86_H1_POLICY_SOURCE_ACTUAL.json',qualified)
        copy(typed_path,P/'native_source_metadata/CLOSED86_TYPED_ALL3_CPU_ACTUAL.json')
        copy(authority_path,P/'native_source_metadata/CLOSED86_AUTHORITY72_COST_ALLOUT_ACTUAL.json')
        put(P/'NATIVE87_OWN_REFERENCE_OBJECTIVE_SOURCE_ACTUAL.json',objective)
        for rel in ('native_source_metadata/QUALIFIED_CLOSED86_H1_POLICY_SOURCE_ACTUAL.json','native_source_metadata/CLOSED86_TYPED_ALL3_CPU_ACTUAL.json','native_source_metadata/CLOSED86_AUTHORITY72_COST_ALLOUT_ACTUAL.json','NATIVE87_OWN_REFERENCE_OBJECTIVE_SOURCE_ACTUAL.json'):
            changed[rel]=H(P/rel)
        approved={p.relative_to(P).as_posix():H(p) for p in P.rglob('*.py')}
        contract=dict(schema='mod4.native87.policy_only_fresh4096.source_contract.v1',source_SHA=SOURCE_SHA,source_Adamstep=832460,
            method_config=protocol.METHOD,approved_python=approved,
            original_runtime_pins={k:v for k,v in original.items() if k not in changed},candidate_pins=changed,
            expected_runtime_joint_names=order,expected_leg_joint_names=legs,
            expected_installed_versions={'isaaclab':'6.1.14','rsl-rl-lib':'5.0.1','torch':'2.10.0+cu128'},
            qualified_H1_report_relative='native_source_metadata/QUALIFIED_CLOSED86_H1_POLICY_SOURCE_ACTUAL.json',
            previous86_typed_close_relative='native_source_metadata/CLOSED86_TYPED_ALL3_CPU_ACTUAL.json',
            previous86_authority_close_relative='native_source_metadata/CLOSED86_AUTHORITY72_COST_ALLOUT_ACTUAL.json',
            source_model_qualification_not_recomputed_locally=True,actual_target_CPU_or_GPU_readback=False)
        put(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json',contract)
        task=dict(id=N.name+'_'+key,key=key,kind='H1_STEP270_SCUT_100HZ',GPU_UUID=protocol.GPUS[key],execution_backend='source210' if key=='h1' else 'target72',
            num_envs=4096,seed=protocol.SEEDS[key],native_seed=protocol.SEEDS[key],physics_dt=.0025,decimation=4,policy_hz=100,
            source_SHA=SOURCE_SHA,bootstrap_source_SHA=SOURCE_SHA,source_Adamstep=832460,source_normal_PPO_update=138,bootstrap_Adam=832460,
            source_filename=SOURCE_FILE,bootstrap_source_kind='closed_production_policy_only',fresh_environment_resume_scope='policy_only_no_source_environment_state',
            method_config=protocol.METHOD,native87_contract_SHA=H(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json'),
            native_reference_relative='source/'+REFERENCE,native_reference_SHA=H(reference),reference_artifact_SHA=H(reference),
            qualified_H1_report_SHA=H(P/contract['qualified_H1_report_relative']),previous86_closure_SHA=H(typed_path),objective_contract_SHA=H(P/'NATIVE87_OWN_REFERENCE_OBJECTIVE_SOURCE_ACTUAL.json'),
            reward_recipe_version='step270_sampled_leg_excess_v8_reward_only',max_parent_seconds=3900,exit_headroom_seconds=300,
            fresh_environment_4096_timeout5s=True,native_physical_reward_original_retained=True,
            native_learning_objective_is_converted_reference=True,not_PPO_or_production_source=True,
            native_continuation=False,native_continuation_restore_required=False,new_native_architecture_fresh=True,
            original_success_270mm_and_200callbacks_unchanged=True,actual_target_CPU_or_GPU_readback=False,
            approved_future_prefix_retention_policy='future_first1_latest2_complete_pairs_plus_incomplete_and_current_failure_v1')
        put(P/'job0/TASK.json',task)
        rows=[]
        for p in sorted(P.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(P).as_posix()
            if rel in known and rel not in changed:
                row=known[rel];assert p.stat().st_size==row['bytes'];rows.append(row)
            else:rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=H(p)))
        manifest=dict(key=key,kind=protocol.KIND,source_SHA=SOURCE_SHA,source_filename=SOURCE_FILE,source_Adamstep=832460,
            execution_backend=task['execution_backend'],policy_hz=100,expected_actual_RSL_sources=old_manifest['expected_actual_RSL_sources'],
            expected_actual_SDK_math_SHA=old_manifest['expected_actual_SDK_math_SHA'],files=rows,
            actual_native3_and_query9_reuse_binding=old_manifest['actual_native3_and_query9_reuse_binding'],
            original_runtime_and_assets_exact=True,new_native_method_not_production_source=True)
        put(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',manifest)
        s=dict(key=key,GPU_UUID=protocol.GPUS[key],execution_backend=task['execution_backend'],python=old_specs[key]['python'],
            private_lock=old_specs[key]['private_lock'],previous_runtime_root=('/mnt/mod4_linux_durable_20261013/H1step270_three_gpu_native_cont_2610v86b/h1' if key=='h1' else '/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_gpu_native_cont_2610v86b/'+key),
            previous_exit_kind='node',max_parent_seconds=3900,exit_headroom_seconds=300,source_SHA=SOURCE_SHA,bootstrap_source_SHA=SOURCE_SHA,
            source_filename=SOURCE_FILE,source_Adamstep=832460,source_normal_PPO_update=138,policy_hz=100,source_policy_hz=100,
            native_controls=0,native_script='UNUSED_NO_NATIVE_REPLAY.py',native_CPU_script='UNUSED_NO_NATIVE_REPLAY_CPU.py',reuse_completed_native=False,
            production_script='h1_native_own87_worker_v1.py',closed_source_CPU_script='target_native87_source_sdk_cpu_v1.py',
            native87_policy_only=True,new_native_architecture_fresh=True,finite_method_test=True,closed_production_continuation=False,native_continuation=False,
            native_continuation_restore_required=False,bootstrap_source_kind='closed_production_policy_only',fresh_environment_resume_scope=task['fresh_environment_resume_scope'],
            seed=protocol.SEEDS[key],method_config=protocol.METHOD,owner_authority_generation=protocol.AUTHORITY_GENERATION,
            manifest_SHA=H(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),candidate_pins=changed,
            **{k:task[k] for k in ('native87_contract_SHA','qualified_H1_report_SHA','previous86_closure_SHA','reference_artifact_SHA','objective_contract_SHA')})
        if key=='h1':s['owner_control_dependency_binding_SHA']=old_specs['h1']['owner_control_dependency_binding_SHA']
        protocol.validate_spec(s)
        payloads[key]=str(P);specs[key]=s
        sources[key]=dict(path='/mnt/mod4_linux_durable_20261013/H1step270_three_gpu_native_cont_2610v86b/h1/job0/production/model_update138.pt',local_path=str(source),bytes=16868635,SHA=SOURCE_SHA)
        summaries[key]=dict(files=len(rows),Python=len(approved),source_model_local_hash_repeated=False,all_new_source_AST_parsed=True)
        for p in P.rglob('*.py'):ast.parse(p.read_text('utf8'))
    q=dict(passed=True,epoch=time.time(),preparation_scope='local_only_no_actual_target_SDK_or_GPU_or_GO',specs=specs,payloads=payloads,roots=support.ROOTS,
        owner_root=support.OWNER,owner_script='three_slot_finite_owner_V86_authority72.py',sources=sources,
        sole72_closed_balance_snapshot=577055.9868602753,summaries=summaries,old_production_and_native86_sources_preserved=True,
        all_three_slots_service_only_H1_step_repair=True,actual_install_or_GO=False)
    support.validate_prepared(q,protocol)
    put(N/'reports/THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json',q)
    print(json.dumps(dict(passed=True,source_only=True,summaries=summaries)))

if __name__=='__main__':
    try:main()
    except BaseException:
        d=N/'reports' if N.exists() else L/'reports'
        put(d/('LOCAL_NATIVE87_BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),source_only=True,no_remote_or_GO=True));raise
