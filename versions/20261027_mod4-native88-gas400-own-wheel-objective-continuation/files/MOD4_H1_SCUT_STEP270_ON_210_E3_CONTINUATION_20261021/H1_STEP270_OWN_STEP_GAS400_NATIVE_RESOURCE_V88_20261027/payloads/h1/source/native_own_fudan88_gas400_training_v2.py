"""New native SuperMimic MOD4-owned converted-jump training entry.

Requires one signed sole72 GO, qualified closedH1 policy-only bootstrap, fresh
actual4096 plant and full typed source/SDK admission. No legacy native restore.
"""
from pathlib import Path
import hashlib,json,shutil,time,sys
sys.path.insert(0,str(Path(__file__).resolve().parent/"sm_deps"))
import torch
from native88_gas400_migration_v1 import (assert_declared_admission,verify_loaded_frozen_RSL_fresh_plant,install_restored_window,observe_first_original_preload_write,RequireNewWindowFinal)
from gas400_sdk_admission_candidate_v1 import check_actual_new_gas
from actual_DR_memory_getter_v1 import tensor
from dataclasses import asdict
BOOTSTRAP_SHA="0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394"
BOOTSTRAP_ADAM=832460
from native_wheel_leg_bridge_v4 import NativeWheelLegBridge
from own_step_differentiable_objective_v2 import build_own_step_mdp,OwnStepDifferentiableMdpV2
from actual_DR_memory_getter_v1 import RuntimeOrderBinding,indices
from native_finalization_own88_gas400 import NativeCheckpointPublisher,run_native_lifecycle,source_sha,atomic_json
from supermimic_wheel_leg_v3.learner import SuperMimicConfig,SuperMimicLearner

class OwnCompleteSavedStop(Exception):pass

def H(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def put(path,value):
    path=Path(path);tmp=path.with_suffix(path.suffix+'.partial')
    tmp.write_text(json.dumps(value,indent=2,allow_nan=False),'utf8');tmp.replace(path)

def config_for(seed):
    if seed not in (27,28,29):raise ValueError('explicit three source-bound native seeds required')
    return SuperMimicConfig(iterations=1000000,buffer_steps=1000,utd=.4,horizon=32,
        goal_frames=10,hist=10,z_dim=32,wm_hidden=(2048,2048,2048),
        policy_hidden=(2048,1024,512,256),critic_hidden=(256,128),
        wm_window=8,wm_batches=10,wm_batch=1024,pi_batch=1024,
        warmup_steps=64,wm_only_iters=64,critic_epochs=5,critic_minibatches=4,
        ckpt_every=1000000,log_every=1,amp='none',compile=False,log_backend='none',seed=seed)

def actual_encoder_joint_names(env,names):
    from native87_encoder_actual_sdk_adapter_v1 import actual_encoder_joint_names as read_actual_encoder_order
    return read_actual_encoder_order(env,names)

def run(runner,n,log_dir,B,J,out,task,go,src,phase):
    B,J,out=Path(B),Path(J),Path(out)
    if phase!='production':raise ValueError('production changed-plant source scope required')
    native_source=assert_declared_admission(task['key'],task,go)
    if go['max_parent_seconds']!=3900 or go['exit_headroom_seconds']!=300:
        raise ValueError('original finite lifecycle required')
    if H(src)!=native_source['SHA']:raise ValueError('actual qualified R5 native source differs')
    runner.logger.writer=None
    env=runner.env.unwrapped
    source=torch.load(src,map_location='cpu',weights_only=False)
    bootstrap=verify_loaded_frozen_RSL_fresh_plant(runner,env,source)
    if task['source_Adamstep']!=BOOTSTRAP_ADAM:raise ValueError('source17Adam832460 required')
    props=env.cfg.scene.robot.spawn.articulation_props
    if props.solver_position_iteration_count!=32 or props.solver_velocity_iteration_count!=4 or env.cfg.sim.physics.solver_type!=1:
        raise ValueError('actual fresh4096 TGS32/4 readback failed')
    if float(env.cfg.terminations.closure.params['threshold'])!=.002:
        raise ValueError('original per-env2mm closure reset required')
    if env._physics_action_delay.queue.control_us!=10000:
        raise ValueError('original100Hz target queue period required')

    from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
    sdk_reward_probe=isolated_actual_SDK_dt_probe(env)

    # Read actual SDK names before first native control/Pi, never infer them from
    # a same-width PPO tensor or label a CPU fixture as actual GPU readback.
    robot=env.scene['robot'];names=tuple(robot.joint_names);body=tuple(robot.body_names)
    def group(key):return tuple(names[i] for i in indices(robot.actuators[key].joint_indices,30))
    binding=RuntimeOrderBinding(body,names,group('legs'),group('wheels'),group('gas_springs'),
        int(env._mild_dr.materials.shape[1]))
    reference_path=B/task['native_reference_relative']
    if H(reference_path)!=task['native_reference_SHA']:raise ValueError('converted own reference differs from source auth')
    document=json.loads(reference_path.read_bytes())
    encoder_names=actual_encoder_joint_names(env,names)
    geometry_path=B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'
    if H(geometry_path)!=task['own_step_geometry_SHA']:raise ValueError('own authored wheel geometry source pin differs')
    geometry=json.loads(geometry_path.read_bytes())
    if list(body)!=geometry['body_names']:raise ValueError('actual body-name mapping differs from own-wheel source geometry')
    capture=env._integrated_contact
    if list(capture.sensor.body_names)!=['left_wheel','right_wheel'] or tuple(capture.history.shape)!=(env.num_envs,3,2,3):
        raise ValueError('original contact18 named order/history layout differs')
    mdp=build_own_step_mdp(json.loads((J/'assets/import_contract.json').read_bytes()),geometry,document,names,encoder_names,device=env.device,order_scope='actual_SDK_readback')
    if type(mdp) is not OwnStepDifferentiableMdpV2:raise ValueError('selected bounded-positive own-wheel head V2 required')

    # Keep original full preupdate save/trace path. The frozen PPO is a complete
    # save/bootstrap witness, not a second policy driving the plant.
    runner.alg.act=lambda *args,**kwargs:None
    from h1_production_control_prefix_trace_v1 import H1ControlPrefixTrace
    trace=H1ControlPrefixTrace(runner,out/'control_prefix_raw');trace.install()
    holder={'bridge':None,'learner':None,'publisher':None,'curve_iteration':None,'window':None}

    def before_action():
        if time.time()>=go['save_deadline'] or (out/'STOP_AFTER_SAVE.json').exists() or shutil.disk_usage(out).free<8*1024**3:
            raise OwnCompleteSavedStop()
        runner.alg.act(runner.env.get_observations())
        bridge=holder['bridge'];learner=holder['learner'];publisher=holder['publisher']
        if holder['curve_iteration']!=learner.iteration:
            row=dict(epoch=time.time(),GO_elapsed_s=time.time()-go['learning_started_epoch'],
                native_iteration=learner.iteration,world_updates=bridge.wm_updates,
                policy_updates=bridge.pi_updates,environment_transitions=trace.total*env.num_envs,
                completed_control_rows=trace.total,events=trace.lifetime_goal_counter.snapshot(),
                wm_last=bridge.last_wm,policy_last=bridge.last_pi,
                native88_migration_window=holder['window'].snapshot(),
                not_frozen_evaluation_or_causal_PPO_comparison=True)
            with (out/'ACTUAL_H1_CONVERGENCE_CURVE.jsonl').open('a',encoding='utf8') as f:
                f.write(json.dumps(row,allow_nan=False)+'\n')
            holder['curve_iteration']=learner.iteration
        # A positive optimizer counter alone must not relabel an earlier zero-Pi
        # checkpoint. Require the actual fresh trace preupdate publication.
        publication=publisher.last_publication
        if publication is not None and trace.source_models and holder['window'].qualifies_preupdate(publication,trace.source_models[-1]):
            checkpoint=trace.source_models[-1]
            if checkpoint['before_control']==trace.total and checkpoint['SHA']==publication['SHA'] and checkpoint['bytes']==publication['bytes']:
                proof=dict(checkpoint,updates=publication['updates'],
                    world_updates=publication['world_updates'],policy_updates=publication['policy_updates'],
                    native88_migration_window=publication['native88_migration_window'],
                    producer=publication['producer'],run_token=publication['run_token'],save_token=publication['save_token'],
                    original_task_events=trace.lifetime_goal_counter.snapshot(),
                    native_actual_method='own_MOD4_native88_nominal400_changed_plant',
                    original_source_actor_frozen_not_PPO_learning=True,
                    not_PPO_or_production_source=True)
                put(out/'latest_complete.json',proof)
                if not (out/'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json').exists():
                    atomic_json(out/'FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json',proof)

    bridge=NativeWheelLegBridge(runner,trace,mdp,binding,before_action)
    holder['bridge']=bridge
    bridge.install_exact_pre_reset_aux_hook()
    bridge.wm_updates=0;bridge.pi_updates=0;bridge.last_wm=None;bridge.last_pi=None

    # Learner construction must not reset the original post-reset global streams.
    cpu_rng=torch.random.get_rng_state();cuda_rng=torch.cuda.get_rng_state_all()
    try:
        learner=SuperMimicLearner(bridge,config_for(int(task['native_seed'])),
            out/'native_supermimic',device=env.device,backend='original_Isaac_MOD4_H1_own_step_native_v3')
    finally:
        torch.random.set_rng_state(cpu_rng);torch.cuda.set_rng_state_all(cuda_rng)
    holder['learner']=learner;bridge.learner=learner
    gas400_admission=check_actual_new_gas(env,expected_joint_names=names,tensor=tensor)
    window,restore_proof=install_restored_window(learner,bridge,trace,source,key=task['key'],source_SHA=task['source_SHA'],
        expected_source_contract=task['source_native_contract'],expected_args=asdict(config_for(int(task['native_seed']))),
        parameter_contract_SHA=task['gas400_parameter_source_contract_SHA'],asset_report_SHA=task['actual_gas400_asset_composition_report_SHA'])
    holder['window']=window;del source
    atomic_json(out/'NATIVE88_RESTORED_SOURCE_AND_CHANGED_PLANT_WINDOW_START_ACTUAL.json',dict(restore=restore_proof,actual_new_gas_parameters=gas400_admission,window=window.snapshot()))
    observe_first_original_preload_write(env,window,expected_joint_names=names,
        emit=lambda value:atomic_json(out/'NATIVE88_FIRST_ORIGINAL_PRELOAD_PREWRITE_ACTUAL.json',value))
    objective=mdp.contract_manifest()
    atomic_json(out/'NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json',objective)
    atomic_json(out/'NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json',dict(
        epoch=time.time(),actual_environment_count=env.num_envs,
        actual_GPU_runtime_readback_passed=True,before_first_native_physical_control_and_Pi=True,
        actual_joint_names=list(names),actual_body_names=list(body),
        actual_leg_names=list(binding.leg_joint_names),actual_wheel_names=list(binding.wheel_joint_names),
        actual_leg_encoder_names=list(encoder_names),
        actual_material_shapes=binding.material_shape_count,
        actual_static_context_dim=bridge.static.xi().shape[-1],
        actual_dynamic_aux_dim=54,packed_state_dim=127,actor_obs_dim=86,goal_frame_dim=146,
        actual_source_frozen_RSL_witness=bootstrap,source_SHA=task['source_SHA'],frozen_RSL_bootstrap_SHA=BOOTSTRAP_SHA,
        actual_installed_original_RewardManager_dt_probe=sdk_reward_probe,
        actual_reference_SHA=task['native_reference_SHA'],
        actual_selected_own_step_objective_class=type(mdp).__name__,actual_own_geometry_SHA=task['own_step_geometry_SHA'],
        actual_contact_history_shape=list(capture.history.shape),actual_contact_wheel_order=list(capture.sensor.body_names),
        contact_force_used_as_soft_magnitude_not_platform_face_truth=True,
        actual_physics_dt=env.physics_dt,actual_control_dt=env.step_dt,
        actual_solver=[1,props.solver_position_iteration_count,props.solver_velocity_iteration_count],
        original_true_physical_success_unchanged=True,new_native_model_initialization=False,
        native88_changed_plant_source_restore=restore_proof,actual_new_gas_parameters=gas400_admission,
        legacy_native86_model_or_optimizer_loaded=False,not_own_skill_success=True))

    publisher=NativeCheckpointPublisher(runner.save,learner,bridge,out,producer=dict(
        bridge_source_SHA=H(Path(__file__)),finalization_source_SHA=source_sha(),
        bootstrap_task_source_SHA=BOOTSTRAP_SHA,bootstrap_Adam=BOOTSTRAP_ADAM,
        reference_artifact_SHA=task['native_reference_SHA'],method='MOD4_own_Fudan_native88_nominal400_changed_plant',
        initial_native_source=window.source,gas400_parameter_source_contract_SHA=window.parameter_contract_SHA,
        own_step_objective_qualification_SHA=task['own_step_objective_qualification_SHA'],
        own_step_geometry_SHA=task['own_step_geometry_SHA'],native_task_objective_changed_from_R5=True,
        actual_gas400_asset_composition_report_SHA=window.asset_report_SHA,
        native_architecture_fresh=False,original_source_cost_and_physical_save_chain_preserved=True,
        runtime_objective_contract_SHA=H(out/'NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json'),
        native_not_production_H1_or_E2_source=True))
    holder['publisher']=publisher
    runner.save=publisher
    original_wm=learner.wm_update;original_pi=learner.policy_update
    def wm_update():
        value=original_wm()
        if not all(torch.isfinite(x).all() for x in value) or not all(torch.isfinite(p).all() for p in learner.wm.parameters()):
            raise ValueError('native world model nonfinite')
        bridge.wm_updates+=1;window.completed_world_update();bridge.last_wm=[float(x) for x in value]
        return value
    def pi_update():
        window.before_policy_update()
        value=original_pi()
        if not all(torch.isfinite(x).all() for x in value) or not all(torch.isfinite(p).all() for p in learner.pi.parameters()):
            raise ValueError('native policy nonfinite')
        bridge.pi_updates+=1;window.completed_policy_update();bridge.last_pi=[float(x) for x in value]
        return value
    learner.wm_update=wm_update;learner.policy_update=pi_update
    from native_policy_phase_coverage_v1 import attach_optional_policy_phase_coverage
    bridge.phase_sampling_diagnostic=attach_optional_policy_phase_coverage(learner,out/'NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json')
    return run_native_lifecycle(train=learner.train,stop_types=(OwnCompleteSavedStop,),
        persist_trace=trace.persist,save=RequireNewWindowFinal(publisher),out=out,
        iteration=lambda:learner.iteration,world_updates=lambda:bridge.wm_updates,
        policy_updates=lambda:bridge.pi_updates,events=trace.lifetime_goal_counter.snapshot)

