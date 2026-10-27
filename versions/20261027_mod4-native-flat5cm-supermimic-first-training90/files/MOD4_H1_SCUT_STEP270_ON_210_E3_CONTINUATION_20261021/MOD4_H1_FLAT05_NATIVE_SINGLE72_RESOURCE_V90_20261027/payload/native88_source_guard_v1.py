"""Native88 exact source admission; import has no I/O or model access.

The input is an own formal R5 native checkpoint. A separate normal86 checkpoint
is only a frozen RSL witness. Neither old plant state is restored by this API.
"""
from pathlib import Path, PurePosixPath
import ast, hashlib, json, math
from native88_protocol_v1 import (KIND, METHOD, SOURCES, BOOTSTRAP_SHA,
    REFERENCE_SHA, PIN_FIELDS, validate_task_go as protocol_task_go)

SCHEMA='mod4.native88.changed_plant_objective.native_fullsource.v1'
CONTRACT='NATIVE88_SOURCE_CONTRACT_ACTUAL.json'
MANIFEST='THREE_SLOT_COMPLETE_MANIFEST_V1.json'
OBJECTIVE_QUALIFICATION_SHA='dc5a6f147309310acdb812848f509b03c41b0c44781c9c9281585cbf4edb5c89'
METADATA_HELPER='same_optimized_source_contract_metadata_candidate_v1.py'
METADATA_SHA='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
R5_NATIVE_CONTRACT=dict(state_joints=30,actions=6,obs_dim=86,goal_dim=146,
    packed_state_dim=127,dynamic_aux_dim=54,static_context_dim=31,
    fresh4096_policy_only_bootstrap=True,original_physics_and_success_unchanged=True,
    original_RSL_core_frozen_bootstrap_only=True,not_production_expert_source=True,
    replay_not_saved_matching_upstream_resume_not_exact_PhysX_replay=True)

def require(value,message):
    if not value:raise ValueError(message)
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def contained(B,relative):
    B=Path(B).resolve();require(isinstance(relative,str) and relative,'relative path required')
    p=PurePosixPath(relative);require(not p.is_absolute() and '..' not in p.parts and '\\' not in relative and ':' not in relative,'unsafe relative path '+relative)
    target=B/relative;require(target.resolve().is_relative_to(B),'path escaped payload '+relative)
    cursor=target
    while cursor!=B:
        require(not cursor.is_symlink(),'symlink in payload path '+relative);cursor=cursor.parent
    return target
def exact_plain(a,b):
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact_plain(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a) is type(b) and len(a)==len(b) and all(exact_plain(x,y) for x,y in zip(a,b))
    return type(a) is type(b) and a==b

def validate_task_source(task):
    key=task.get('key');require(key in SOURCES,'only available own native source slots')
    source=SOURCES[key]
    require(task['source_SHA']==source['SHA'] and task['source_progress']=={k:source[k] for k in ('updates','world_updates','policy_updates')},'own R5 source/counters')
    require(task['native_seed']==source['seed'] and task['GPU_UUID']==source['GPU_UUID'] and task['execution_backend']==source['execution_backend'],'role seed/backend/UUID')
    require(task['bootstrap_source_SHA']==BOOTSTRAP_SHA and task['source_Adamstep']==832460,'separate normal86 witness')
    require(exact_plain(task['source_native_contract'],R5_NATIVE_CONTRACT),'input contract must be old R5, never new88 output')
    require(task['method_config']==METHOD and task['fresh_environment_resume_scope']=='native_models_only_fresh400N_environment_no_old_DR','fresh changed plant scope')
    require(task['changed_plant700_to_nominal400'] is True and task['independent_own_step_objective_admission_passed'] is True,'plant and objective migration declared')
    require(task['reference_artifact_SHA']==REFERENCE_SHA and task['own_step_objective_qualification_SHA']==OBJECTIVE_QUALIFICATION_SHA,'original reference / selected objective qualification')
    native=task['source_filename'];normal=task['bootstrap_source_filename']
    for name in (native,normal):require(isinstance(name,str) and PurePosixPath(name).name==name and '\\' not in name and ':' not in name and name not in ('.','..'),'simple source filename required')
    require(native!=normal,'native and normal witness must be separate files')
    return source

def validate_task_go(task,go,manifest_SHA):
    validate_task_source(task);protocol_task_go(task,go,manifest_SHA)
    require(go.get('num_envs')==4096,'actual grant4096')
    require(go.get('fresh_environment_resume_scope',task['fresh_environment_resume_scope'])==task['fresh_environment_resume_scope'],'no old DR grant')
    return True

def validate_output_native_contract(value):
    require(value.get('original_physics_and_success_unchanged') is False and value.get('changed_plant700_to_nominal400') is True,'output is changed plant, never unchanged700N')
    require(value.get('native_objective_changed') is True,'native objective repair explicit in output')
    require(value.get('original_clock_solver_geometry_reward_command_success_unchanged') is not True,'ambiguous unchanged native reward declaration forbidden')
    require(value.get('original_clock_solver_geometry_physical_V8_reward_command_success_unchanged') is True,'physical V8/clock/control/success scope explicit')
    require(value.get('native_all_models_norms_threeopts_global_counters_restored') is True and value.get('fresh_physics_replay_history') is True,'models preserved, environment/replay/history fresh')
    require(value.get('fresh_control_warmup')==64 and value.get('new_window_world_only_iterations')==64 and value.get('minimum_new_WM_steps_before_first_newPi')==640,'new-window physical/WM adaptation, not old positive counters')
    return True

def validate_saved_source_evidence(c,task,docs):
    pair=docs['qualified_R5_pair_report'];require(pair['passed'] is True and pair['original_fees']['passed'] is True and pair['original_canonical_cost_settled'] is True,'R5 formal pair and original fees qualified')
    require(set(pair['models'])==set(SOURCES),'both own R5 sources preserved')
    for key,source in SOURCES.items():
        row=pair['models'][key];f=row['final']
        require(row['passed'] is True and f['SHA']==source['SHA'] and f['bytes']==256224393,'formal own R5 model proof')
        require(f['formal_manifest_passed'] is True and f['twohost_complete_SHA'] is True and f['original_full_save_chain_returned'] is True,'formal save/twohost proof')
        require(all(f[k]==source[k] for k in ('updates','world_updates','policy_updates')),'qualified source progress')
        require(row['native_fullstate_finite'] is True and row['native_modules']['passed'] is True and row['frozen_bootstrap']['actor9_critic8_STD6_17Adam_all_state_literal_exact'] is True,'whole native + frozen witness qualified')
    # The raw original close is immutable evidence. Its exact SHA, not a new
    # fabricated healthy-three summary, is bound here and in Task/spec/GO.
    require(c['previous_R5_closure_SHA']==task['previous_R5_closure_SHA'],'original closing receipt bound')
    closing=docs['previous_R5_closure'];authority=closing['authority72']
    require(closing['actual_finite_transport_returned'] is True and closing['all_active_node_collection_passed'] is True and closing['original_canonical_cost_settled'] is True,'actual original R5 collection and fees')
    require(authority['canonical_active_segment'] is None and authority['all_authority72_owner_children_actual_out'] is True and all(r['actual_fcntl_free'] is True for r in authority['original_locks']),'original sole72 CNone/allout/locks')
    require(authority['original_fees_CPU_metadata']==pair['original_fees'],'same independently charged original sumonce')
    require(set(closing['nodes'])==set(SOURCES) and all(n['all_selected_target_processes_actual_out'] is True and all(lock['actual_fcntl_free'] is True for lock in n['locks']) for n in closing['nodes'].values()),'two original node children out/private/shared locks')
    asset=docs['actual_asset_report']
    require(asset['actual_private_USD_CPU_composition_passed'] is True and asset['all_prim_types_paths_and_other_attribute_values_appliedschemas_same'] is True,'actual four-attribute asset proof')
    changes=asset['only_four_authored_attribute_changes']
    wanted={(f'/Robot/joints/{name}',attr) for name in ('left_gas_slide','right_gas_slide') for attr in ('drive:linear:physics:stiffness','physics:upperLimit')}
    require(len(changes)==4 and {(x['path'],x['attribute']) for x in changes}==wanted,'only four gas opinions')
    require(asset['parameter_source_contract_SHA']==c['gas400_parameter_contract_SHA'] and asset['actual_PhysX_runtime_parameter_admission'] is False,'gas source contract / actual PhysX still pending')
    q=docs['own_step_objective_qualification']
    require(q['passed'] is True and q['selected_class']=='OwnStepDifferentiableMdpV2' and q['qualification_scope']=='SOURCE_CPU_geometry_objective_gradient_only_NOT_runtime_or_training','selected positive objective source scope')
    require(q['source_CPU_checks']==45 and q['reference_SHA']==REFERENCE_SHA,'new objective math evidence')
    return True

def check_payload(B,*,verify_model_bytes=True):
    B=Path(B).resolve();manifest=read(B/MANIFEST);task=read(B/'job0/TASK.json')
    source=validate_task_source(task);cp=B/CONTRACT
    require(H(cp)==task['native88_contract_SHA'],'native88 contract SHA')
    c=read(cp);require(c['schema']==SCHEMA,'typed source contract schema')
    require(c['source_SHA']==manifest['source_SHA']==task['source_SHA'] and c['source_Adamstep']==832460,'native source binding')
    require(c['method_config']==METHOD and c['expected_runtime_joint_names'] and len(c['expected_runtime_joint_names'])==30 and len(set(c['expected_runtime_joint_names']))==30,'source config / named30')
    require(c['source_bytes']==256224393 and c['bootstrap_source_SHA']==BOOTSTRAP_SHA and c['bootstrap_source_bytes']==16868635,'native/witness producer sizes')
    approved=c['approved_python'];pins=c['candidate_pins'];require(approved and pins,'complete code inventories required')
    rows={};unverified=[]
    native_rel='job0/source/'+task['source_filename'];normal_rel='job0/source/'+task['bootstrap_source_filename']
    for row in manifest['files']:
        relative=row['relative'];path=contained(B,relative);require(relative not in rows,'duplicate manifest path')
        rows[relative]=row
        # Source-only local preparation does not touch any model bytes/stat.
        if not verify_model_bytes and path.suffix.lower() in ('.pt','.pth','.npz'):
            unverified.append(relative);continue
        require(path.is_file() and path.stat().st_size==row['bytes'],'file size/missing '+relative)
        require(H(path)==row['SHA'],'file SHA '+relative)
        if path.suffix=='.py':
            require(approved.get(relative)==row['SHA'],'unapproved Python '+relative);ast.parse(path.read_text('utf8'))
    for relative,SHA,bytes_ in ((native_rel,source['SHA'],256224393),(normal_rel,BOOTSTRAP_SHA,16868635)):
        require(relative in rows and rows[relative]['SHA']==SHA and rows[relative]['bytes']==bytes_,'separate exact model row '+relative)
    actual={p.relative_to(B).as_posix() for p in B.rglob('*.py')}
    require(actual==set(approved) and set(approved)<=set(rows),'exact Python inventory; no directory exception')
    for relative,SHA in pins.items():
        require(relative in rows and rows[relative]['SHA']==SHA and H(contained(B,relative))==SHA,'candidate pin '+relative)
    require(set(approved)<=set(pins),'every approved Python must be explicitly candidate pinned')
    helper=contained(B,METADATA_HELPER)
    require(helper.stat().st_size==2536 and H(helper)==METADATA_SHA,'original metadata helper byteexact CRLF')
    old_manifest=contained(B,c['source_R5_manifest_relative']);require(H(old_manifest)==c['source_R5_manifest_SHA'],'R5 lineage manifest pin')
    old_rows={r['relative']:r for r in read(old_manifest)['files']}
    protected=c['original_runtime_pins'];changed=c['explicit_changed_original_files'];require(protected,'original protected pins required')
    require(set(changed)<=set(protected),'changed file must have protected old source pin')
    for relative,oldSHA in protected.items():
        require(relative in old_rows and old_rows[relative]['SHA']==oldSHA,'protected oldSHA differs from actual R5 manifest '+relative)
        expected=oldSHA
        if relative in changed:
            change=changed[relative];require(change['old_SHA']==oldSHA and change['new_SHA']!=oldSHA and isinstance(change['reason'],str) and change['reason'].strip(),'exact reviewed old/new change '+relative)
            expected=change['new_SHA']
        require(relative in rows and rows[relative]['SHA']==expected and H(contained(B,relative))==expected,'protected runtime changed '+relative)
    from native87_role_metadata_closure_v1 import validate_role_metadata_closure
    role=validate_role_metadata_closure(B,task,c,manifest)
    docs={}
    for name in ('qualified_R5_pair_report','previous_R5_closure','native_sourceCPU_report','actual_asset_report','gas400_parameter_contract','own_step_objective_qualification','known_own_processes','previous_failed88B_cost_allout','reset_bank_source_qualification'):
        rel=c[name+'_relative'];SHA=c[name+'_SHA'];path=contained(B,rel)
        require(rel in rows and rows[rel]['SHA']==SHA and pins.get(rel)==SHA and H(path)==SHA,'pinned admission metadata '+name)
        docs[name]=read(path)
    require(c['qualified_R5_pair_report_relative']==c['native_sourceCPU_report_relative'] and c['qualified_R5_pair_report_SHA']==c['native_sourceCPU_report_SHA']==task['qualified_R5_pair_report_SHA'],'R5 proof alias exact')
    for ck,tk in (('actual_asset_report_SHA','actual_gas400_asset_composition_report_SHA'),('gas400_parameter_contract_SHA','gas400_parameter_source_contract_SHA'),('own_step_objective_qualification_SHA','own_step_objective_qualification_SHA')):require(c[ck]==task[tk],'Task metadata '+tk)
    validate_saved_source_evidence(c,task,docs)
    validate_failed_resource_and_reset_source(c,task,docs)
    for name,row in docs['own_step_objective_qualification']['runtime_modules'].items():
        relative='source/'+name
        require(relative in rows and rows[relative]['SHA']==row['SHA'] and rows[relative]['bytes']==row['bytes'] and pins.get(relative)==row['SHA'],'selected objective source bytes '+name)
    ref=contained(B,c['reference_relative']);require(H(ref)==REFERENCE_SHA and task['native_reference_SHA']==REFERENCE_SHA,'unchanged reference9223')
    return dict(manifest_SHA=H(B/MANIFEST),contract=c,task=task,documents=docs,role_metadata_closure=role,
        model_bytes_verified=verify_model_bytes,unverified_model_rows=unverified)

def finite_tree(value):
    import torch
    if torch.is_tensor(value):require(bool(torch.isfinite(value).all()),'nonfinite checkpoint tensor')
    elif isinstance(value,dict):
        for v in value.values():finite_tree(v)
    elif isinstance(value,(list,tuple)):
        for v in value:finite_tree(v)
    elif isinstance(value,float):require(math.isfinite(value),'nonfinite scalar')

def validate_whole_policy(source):
    finite_tree(source)
    require(len(source['actor_state_dict'])==9 and len(source['critic_state_dict'])==8,'whole actor9/critic8')
    require(tuple(source['actor_state_dict']['distribution.std_param'].shape)==(6,),'STD6')
    state=source['optimizer_state_dict']['state'];require(len(state)==17 and {int(v['step']) for v in state.values()}=={832460},'17Adam832460')
    require(source['H1_step270_task_state']['version']==270,'phase270')
    return True

def validate_precontrol_actual(runner,env,task,go,B):
    import torch
    from gas400_sdk_admission_candidate_v1 import check_actual_new_gas
    from actual_DR_memory_getter_v1 import tensor
    require(env.num_envs==4096 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4,'actual4096 original clock')
    require(float(env.cfg.episode_length_s)==5. and env.cfg.seed==task['native_seed'],'actual5s seed')
    require(env._sim_step_counter==0 and not bool(env.h1_phase.age_control.any()),'before first physical control')
    require(float(runner.env.clip_actions)==6.,'actual RSL clip6')
    props=env.cfg.scene.robot.spawn.articulation_props
    require(props.solver_position_iteration_count==32 and props.solver_velocity_iteration_count==4 and env.cfg.sim.physics.solver_type==1,'actual TGS32/4')
    c=read(Path(B)/CONTRACT)
    require(list(env.scene['robot'].joint_names)==c['expected_runtime_joint_names'] and len(env.scene['robot'].body_names)==31,'actual runtime30/31 order')
    from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
    bank=check_runtime_source(Path(B)/'job0/runtime/isaac/mod4')
    cache=getattr(env,'_rescue_reset_bank',None);resetq=getattr(env,'_rescue_reset_q',None)
    require(isinstance(cache,tuple) and len(cache)==2 and tuple(cache[0].shape)==(74,30) and tuple(cache[1].shape)==(74,) and resetq is not None and tuple(resetq.shape)==(4096,30),'actual first original reset cache and writes required')
    audit=env._mild_dr.audit();require(audit['actual_parameters_pass'] is True,'actual D0-D7 backend audit')
    states=[component.state_dict() for component in (env._sensor_mild,env._physics_action_delay,env._spring_pressure,env._gas_damping,env._chassis_com,env._explicit_pd)]
    require(all(s.get('n',s.get('num_envs'))==4096 for s in states),'fresh actual DR populations4096')
    require(env._physics_action_delay.queue.control_us==10000 and not torch.is_inference_mode_enabled(),'original delay / training mode')
    gas=check_actual_new_gas(env,expected_joint_names=c['expected_runtime_joint_names'],tensor=tensor,require_active_preload=False)
    require(gas['actual_new_gas_parameters_passed'] is True,'actual changed plant400N')
    return dict(passed=True,actual_environment_count=4096,original_first_reset_completed=True,reset_bank_exact_compatibility_source_CPU=bank,actual_runtime30joint_order_passed=True,
        actual_fresh_D0_D7_backend_readback_passed=True,actual_solver_original32_4_passed=True,before_first_control_and_Pi=True,
        source20k_environment_state_not_restored=True,native700N_environment_DR_not_restored=True,
        actual_DR_audit=audit,gas400=gas,changed_plant_not_exact_PhysX_resume=True)


def validate_failed_resource_and_reset_source(c,task,docs):
    failed=docs['previous_failed88B_cost_allout'];q=docs['reset_bank_source_qualification']
    require(failed['passed_original_cost_allout_only'] is True and failed['both_failed_before_first_control_and_NEW_Pi'] is True and failed['formal_FINALs'] is False and failed['source_models_remain_qualified_R5'] is True,'failed88B is resource/cost only, never model source')
    require(failed['run_id']=='AVAILABLE_TWO_H1_GAS400_OWN_STEP_NATIVE88B_1793079421832793100' and failed['original_owner']['pid']==523069 and failed['original_owner']['creation']==1793079430.42,'exact latest original failed owner')
    require(failed['fee_sumonce']==161.60727643966675 and failed['closing_remaining']==569391.7559990883 and failed['actual_nodes_owner_workers_out'] and failed['canonical_None'] and failed['original_locks_free'] and failed['original_normal_duration_flags_unchanged'],'original failed fee/allout and latest balance')
    require(q['passed'] is True and q['count']==17 and q['no_model_PT_USD_raw_actor_or_physics_read_or_run'] is True,'exact17 source-only resetbank CPU proof')
    for name in ('previous_failed88B_cost_allout','reset_bank_source_qualification'):require(task[name+'_SHA']==c[name+'_SHA'],'Task new resource/reset pin '+name)
    return True
