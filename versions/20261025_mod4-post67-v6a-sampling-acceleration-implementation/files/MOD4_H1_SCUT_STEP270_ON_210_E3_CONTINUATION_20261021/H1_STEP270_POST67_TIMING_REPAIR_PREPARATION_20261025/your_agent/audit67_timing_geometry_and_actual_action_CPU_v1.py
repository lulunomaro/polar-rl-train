"""New local-only post67 audit. Reads only saved text and small derived arrays.

No policy inference, physical integration, SSH, GPU initialization, trainer or Git.
Outputs are append-only and remain pending root's single archival operation.
"""
from pathlib import Path
import ast, hashlib, importlib.util, json, time, traceback, types
import numpy as np
import torch

S = Path(__file__).resolve().parent
T = S.parent.parent
U = T/'H1_STEP270_CLOSED67_SAVED_REPLAY_AFTER_V5_20261025'
P = T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025'
B = P/'current_pair_closed_text/h1/job0/runtime/isaac/mod4'
R = S/'reports'

def read(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n, v):
    with (R/n).open('x', encoding='utf8') as f:
        json.dump(v, f, ensure_ascii=False, indent=2, allow_nan=False)
def quant(x):
    return {str(q): np.quantile(x, q, axis=0).tolist() for q in (0, .1, .5, .9, 1)} if np.size(x) else None
def artifact(p): return dict(path=str(p), bytes=p.stat().st_size, SHA=sha(p))

def main():
    torch.set_num_threads(2)
    rng = torch.get_rng_state().clone()
    source = read(U/'reports/LATEST67_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json')
    geometry = read(U/'reports/RECORDED_USD_KINEMATICS_CPU_ACTUAL.json')
    contract = read(B/'import_contract.json')
    actions = read(T/'H1_STEP270_LATEST65_REPLAY_REPAIR_20261024/reports/ACTUAL_INSTALLED_JOINT_ACTION_AND_LIMIT_SDK_SOURCE_ACTUAL.json')
    reward_path = P/'repair_sources/h1_step270_path_reward_v1.py'
    assert sha(reward_path) == '42909a5e40334e21a6bc7df83950756207f8366fce975662ab08ced1dea41193'
    assert sha(P/'repair_sources/h1_step270_sdk_runtime_candidate.py') == '0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34'
    spec = importlib.util.spec_from_file_location('post67_v5_reward_reference', reward_path)
    reward = importlib.util.module_from_spec(spec); spec.loader.exec_module(reward)
    z = np.load(U/'SELECTED_RECORDED_MOTION.npz', allow_pickle=False)
    k = np.load(U/'RECORDED_KINEMATIC_RECONSTRUCTION.npz', allow_pickle=False)
    names = geometry['body_names']; order = geometry['joint_order_derived_from_actual_31link_order_each_one_DOF_incoming_joint']
    pos = k['body_pose'][..., :3, 3]
    wheels = [names.index(n) for n in ('left_wheel', 'right_wheel')]
    delta = pos[:, :, wheels] - pos[:, :, [0]]
    # Already reconstructed source poses supply the body orientation; transpose
    # rotates each measured world vector back into the actual chassis frame.
    body_delta = np.einsum('feji,fewj->fewi', k['body_pose'][:, :, 0, :3, :3], delta)
    lengths3 = np.linalg.norm(delta, axis=-1)
    planar = np.linalg.norm(body_delta[..., [0, 2]], axis=-1)
    terms = source['reward_terms']; con = z['reward_term_contribution']
    tuck = con[:, :, terms.index('h1_scut_fudan_leg_tuck')]; paid = tuck > 0
    bottom = k['wheel_min'][..., 2].min(-1); front = k['wheel_max'][..., 0].min(-1)
    gap = .35-front
    clean = z['continuous_no_reset'].astype(bool)
    cases = []
    for env in (11804, 1685, 6846, 6171):
        e = int(np.flatnonzero(z['env_ids'] == env)[0])
        clear = bottom[:, e] >= .270
        apex = int(np.argmax(bottom[:, e])); rows = np.flatnonzero(clear)
        take_rows = np.flatnonzero(np.r_[False, np.diff(z['takeoff_count'][:, e]) > 0])
        closest = int(np.argmin(gap[:, e]))
        reward_rows = {n: dict(sum=float(con[:, e, terms.index(n)].sum()),
                              apex=float(con[apex, e, terms.index(n)]))
                       for n in ('action_rate', 'action_acc', 'h1_scut_fudan_leg_tuck',
                                 'h1_step270_airborne_leg_target_overdrive',
                                 'h1_step270_path_progress', 'h1_step270_requested_forward',
                                 'h1_step270_release_shortfall')}
        cases.append(dict(env_id=env, continuous_no_reset=bool(clean[e]),
            observed_takeoff_increment_rows=take_rows.tolist(),
            front_at_observed_takeoff_m=front[take_rows, e].tolist(),
            root_vx_at_observed_takeoff_m_s=z['root13'][take_rows, e, 7].tolist(),
            apex_control_row=apex, apex_clearance_m=float(bottom[apex, e]),
            apex_front_gap_m=float(gap[apex, e]),
            apex_root_vx_m_s=float(z['root13'][apex, e, 7]),
            apex_instantaneous_gap_over_vx_s=float(gap[apex, e]/max(float(z['root13'][apex, e, 7]), 1e-6)),
            clearance_ge270_control_rows=rows.tolist(),
            observed_clearance_ge270_span_s=float((rows[-1]-rows[0])*.01) if len(rows) else 0.,
            observed_front_travel_while_ge270_m=float(front[rows[-1],e]-front[rows[0],e]) if len(rows) else 0.,
            min_front_gap_while_ge270_m=float(gap[rows,e].min()) if len(rows) else None,
            closest_front_row=closest, closest_front_gap_m=float(gap[closest,e]),
            clearance_at_closest_front_m=float(bottom[closest,e]),
            apex_body_relative_wheel_center_m=body_delta[apex,e].tolist(),
            apex_full3D_leg_lengths_m=lengths3[apex,e].tolist(),
            apex_sagittal_leg_lengths_m=planar[apex,e].tolist(),
            apex_measured_leg_joint_q={n:float(z['q30'][apex,e,order.index(n)]) for n in ('left_crank','left_hip','left_knee','right_crank','right_hip','right_knee')},
            actual_recorded_reward_contributions=reward_rows,
            gap_over_vx_is_descriptive_not_ballistic_or_counterfactual=True))

    # Exact geometric lower bound over the authored knee interval. Both sides
    # have a planar thigh->knee->wheel chain rotating about the chassis Y axis.
    # This deliberately does not solve or rerun dynamics/closed-chain branches.
    feasibility = []
    for side in ('left', 'right'):
        joints = contract['joints']; hip = joints[side+'_hip']; knee = joints[side+'_knee']; wheel = joints[side+'_wheel_spin']
        v1 = np.asarray(knee['local_pos0'])[[0,2]]
        v2 = np.asarray(wheel['local_pos0'])[[0,2]]
        lateral = float(hip['local_pos0'][1]+knee['local_pos0'][1]+wheel['local_pos0'][1])
        q = np.linspace(*knee['limits_si'], 20000, dtype=np.float32)
        c, sn = np.cos(q), np.sin(q)
        # Quaternion local_rot0/local_rot1 maps joint X to world/chassis Y.
        xv = v1[0]+c*v2[0]+sn*v2[1]
        zv = v1[1]-sn*v2[0]+c*v2[1]
        sagittal = np.sqrt(xv*xv+zv*zv)
        spatial = np.sqrt(sagittal*sagittal+lateral*lateral)
        real_q = z['q30'][:,:,order.index(side+'_knee')]
        c, sn = np.cos(real_q), np.sin(real_q)
        predicted = np.sqrt((v1[0]+c*v2[0]+sn*v2[1])**2+(v1[1]-sn*v2[0]+c*v2[1])**2+lateral*lateral)
        eidx=0 if side=='left' else 1
        loweridx=int(np.argmin(spatial)); nearidx=int(np.argmin(np.abs(sagittal-.22)))
        # The derivative of squared planar length has no interior zero on this
        # interval: its sign is checked densely; extrema therefore lie at ends.
        derivative = 2*xv*(-sn*v2[0]+c*v2[1])+2*zv*(-c*v2[0]-sn*v2[1]) if False else None
        feasibility.append(dict(side=side, fixed_lateral_mount_offset_m=lateral,
            authored_knee_limits_rad=knee['limits_si'],
            sampled_float32_configurations=20000,
            full3D_length_min_m=float(spatial.min()),full3D_length_max_m=float(spatial.max()),
            full3D_min_at_knee_rad=float(q[loweridx]),
            full3D_target_m=.22,full3D_target_below_authored_chain_min_by_m=float(spatial.min()-.22),
            sagittal_length_min_m=float(sagittal.min()),sagittal_length_max_m=float(sagittal.max()),
            sagittal_target_m=.22,sagittal_target_nearest_sample_m=float(sagittal[nearidx]),
            sagittal_target_nearest_knee_rad=float(q[nearidx]),
            recorded_full3D_norm_vs_contract_chain_max_abs_error_m=float(np.max(np.abs(predicted-lengths3[...,eidx]))),
            chain_bound_ignores_additional_closures_so_cannot_overstate_reachability=True,
            no_new_physical_health_tolerance_or_joint_target_write=True))

    # Execute the actual saved SDK method body with CPU stand-ins, then the
    # actual MOD4 CAD guard method. No Isaac or environment package imported.
    sdk = next(s for s in actions['sources'] if s['path'].endswith('/joint_actions.py'))
    assert hashlib.sha256(sdk['text'].encode()).hexdigest()==sdk['SHA']
    tree=ast.parse(sdk['text']); cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='JointAction')
    process=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='process_actions')
    process.name='sdk_process'
    ns={'torch':torch};exec(compile(ast.Module(body=[process],type_ignores=[]),sdk['path'],'exec'),ns)
    base=type('CPUSavedSDKBase',(),{'process_actions':ns['sdk_process'],
        'processed_actions':property(lambda self:self._processed_actions)})
    modtree=ast.parse((B/'mod4_task.py').read_text('utf8'))
    mixin=next(n for n in modtree.body if isinstance(n,ast.ClassDef) and n.name=='_DelayMixin')
    mixin.bases=[]
    delayed=next(n for n in modtree.body if isinstance(n,ast.ClassDef) and n.name=='DelayedJointPositionAction')
    delayed.bases=[ast.Name(id='_DelayMixin',ctx=ast.Load()),ast.Name(id='CPUSavedSDKBase',ctx=ast.Load())]
    delayed.body=[n for n in delayed.body if isinstance(n,ast.FunctionDef) and n.name=='process_actions']
    ns={'torch':torch,'CPUSavedSDKBase':base};exec(compile(ast.fix_missing_locations(ast.Module(body=[mixin,delayed],type_ignores=[])),str(B/'mod4_task.py'),'exec'),ns)
    obj=ns['DelayedJointPositionAction']();obj._max_lag=0;obj._scale=.5
    obj._offset=torch.zeros(20000,4);obj._raw_actions=torch.zeros_like(obj._offset);obj.cfg=types.SimpleNamespace(clip=None)
    obj.diff_min=-1.0843;obj.diff_max=.85
    raw=torch.linspace(-6,6,20000)[:,None].repeat(1,4)
    raw[:,1]=torch.linspace(-1,1,20000);raw[:,3]=torch.linspace(1,-1,20000)
    before=raw.clone();obj.process_actions(raw)
    expected=raw*.5
    expected[:,0]=torch.minimum(torch.maximum(expected[:,0],expected[:,1]+obj.diff_min),expected[:,1]+obj.diff_max)
    expected[:,2]=torch.minimum(torch.maximum(expected[:,2],expected[:,3]+obj.diff_min),expected[:,3]+obj.diff_max)
    assert torch.equal(obj.processed_actions,expected) and torch.equal(raw,before)
    lower=raw.new_tensor([-1.2,-.5,-1.2,-.5]);upper=raw.new_tensor([.9,.5,.9,.5])
    outside=(expected<lower)|(expected>upper)
    direct_target=raw*.5
    v5=reward.infeasible_leg_target_cost(raw_actions=raw,scale=.5,offset=obj._offset,lower=lower,upper=upper,diff_min=obj.diff_min,diff_max=obj.diff_max)
    sample=torch.tensor([[6.,.46465075,6.,.4310294]])
    ex=sample*.5
    ex[:,0]=ex[:,0].clamp(ex[:,1]+obj.diff_min,ex[:,1]+obj.diff_max)
    ex[:,2]=ex[:,2].clamp(ex[:,3]+obj.diff_min,ex[:,3]+obj.diff_max)
    action_report=dict(actual_saved_SDK_source_path=sdk['path'],actual_saved_SDK_SHA=sdk['SHA'],
        actual_saved_MOD4_source=artifact(B/'mod4_task.py'),
        saved_SDK_and_MOD4_method_bodies_executed_CPU=True,vectorized_float32_environments=20000,
        actual_processed_mapping_is_affine_then_optional_cfg_clip_then_CAD_difference_projection=True,
        original_ActionsCfg_leg_clip_is_None=True,
        actual_processed_mapping_max_abs_error=0.,
        synthetic_processed_outside_authored_joint_limits_envs=int(outside.any(-1).sum()),
        synthetic_V5_reference_cost_min_max=[float(v5.min()),float(v5.max())],
        V5_reference_cost_is_not_actual_processed_target_residual=True,
        zero_offset_example_not_live_saved_processed_telemetry=dict(raw_issued_action=sample.tolist(),affine_target=(sample*.5).tolist(),actual_SDK_guarded_target=ex.tolist()),
        real_default_offset_is_live_term_offset_never_assumed_for_production=True,
        inherited_D4_queue_actual_first_transition_delay_ms=[0,2.5,5],
        inherited_D4_queue_requires_original_term_max_lag_zero=True,
        reward_is_computed_after_four_physical_callbacks_and_all_current_targets_due_by_callback3=True,
        no_saved_delayed_raw_or_processed_or_articulation_target_in_selected_arrays=True,
        executed6_is_current_issued_action_manager_input_not_delayed_processed_target=True,
        delay_is_not_a_supported_explanation_for_200_to_500ms_travel_shortfall=True)
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    report=dict(epoch=time.time(),trial_id='H1_POST67_LOCAL_GEOMETRY_TIMING_CPU_V1_20261025',
        status='local_CPU_diagnostic_complete_not_deployed_not_Git_recorded',
        scope=source['scope'],checkpoint_SHA='d1dd187177a1878f007b05da26e39c5ee101e937d2d86f0948dde1ffd37f062e',
        physical_clock_ms=2.5,control_clock_ms=10.,unchanged_solver='TGS32/4',
        source_inputs=[artifact(p) for p in (reward_path,P/'repair_sources/h1_step270_sdk_runtime_candidate.py',B/'import_contract.json',U/'SELECTED_RECORDED_MOTION.npz',U/'RECORDED_KINEMATIC_RECONSTRUCTION.npz')],
        cases=cases,geometry_target_feasibility=feasibility,actual_action_path=action_report,
        selected_paid_tuck_full3D_length_quantiles_m=quant(lengths3[paid]),
        selected_paid_tuck_sagittal_length_quantiles_m=quant(planar[paid]),
        selected_paid_tuck_body_lateral_abs_quantiles_m=quant(np.abs(body_delta[...,1][paid])),
        recommendations=[
          'Correct the reward geometry definition before increasing its weight: .22m full3D chassis-to-wheel includes ~.219m mounting width and lies below the authored chain minimum.',
          'Treat sagittal .22m as a candidate metric, not a skill claim; verify against saved poses and all20k float32 fixtures.',
          'Decouple release-shortfall timing from request age: its existing ballistic profile demands release soon after vx request, while the wheels are still far from edge.',
          'Use actual measured front/gap and current forward speed only as reward timing inputs, retaining the exact external .8m/s public command and strict actual crossing/contact/recovery witnesses.',
          'Keep V5 target-cost semantics explicit; audit current issued raw, current processed target, queued/applied target and actual joint target separately on next authorized saved prefix.',
          'Do not infer a controlled learning gain from selected65/67 clips; no matched cohort or frozen FINAL evaluation occurred.'
        ],
        no_SSH_GPU_policy_PhysX_rollout_training_hotpatch_budget_cleanup_or_Git=True,
        archive_status='pending_root_unique_trial_archive')
    put('POST67_TIMING_GEOMETRY_ACTUAL_ACTION_CPU_V1_ACTUAL.json',report)
    put('LOCAL_READER_AND_INTERPRETER_ERRORS_ACTUAL.json',dict(epoch=time.time(),
        errors=[
          dict(action='Get-Content guessed repair_sources/scut_ballistic_reference_uninstalled.py',result='path not found',resolution='existing payloads/h1/scut_ballistic_reference_uninstalled.py read; no old file changed'),
          dict(action='python alias -c import numpy',result='WindowsApps python exit1 without stdout',resolution='explicit existing env_isaaclab/python.exe used'),
          dict(action='miniconda base python import torch',result="ModuleNotFoundError: No module named torch",resolution='explicit existing env_isaaclab/python.exe used; no packages installed'),
          dict(action='rg inventory workspace python/venv files',result='access denied on unrelated rmuc2026_work/unpack_verify_4zomhj13',resolution='no access attempted further; explicit existing interpreter discovered'),
          dict(action='rg guessed payload step270_training_entry_v1.py',result='file not found',resolution='no content inference from missing filename; real existing worker paths used'),
          dict(action='broad rg source search',result='output truncated due duplicate source snapshots',resolution='subsequent reads restricted to current67/h1 exact source and small reports')
        ],errors_are_local_readers_not_new_training_failures=True,
        original_tool_errors_preserved_in_chat=True,archive_status='pending_root_unique_trial_archive'))
    print(json.dumps(dict(report=str(R/'POST67_TIMING_GEOMETRY_ACTUAL_ACTION_CPU_V1_ACTUAL.json'),geometry=feasibility,cases=cases[:2],actual_action=action_report),ensure_ascii=False))

if __name__=='__main__':
    try: main()
    except BaseException:
        put('CPU_V1_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),not_retried_same_trial=True))
        raise
