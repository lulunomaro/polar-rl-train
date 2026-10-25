"""Local all20k float32 candidate verification and append-only handoff.

No current source replacement. SDK local fixture is identified separately
from a future root-run installed SDK compute test; no substitute pass claim.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,math,sys,time,traceback,types
import numpy as np
import torch
S=Path(__file__).resolve().parent;T=S.parent.parent;W=T.parent;R=S/'reports'
P=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025'
U=T/'H1_STEP270_CLOSED67_SAVED_REPLAY_AFTER_V5_20261025'
B=P/'current_pair_closed_text/h1/job0/runtime/isaac/mod4'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def file(p):return dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p))
def top_functions(text):return {n.name:ast.dump(n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}

def main():
    torch.set_num_threads(2);rng=torch.get_rng_state().clone()
    va=S/'reward_candidate_V6A_GEOMETRY_UNUSED';vb=S/'reward_candidate_V6B_GEOMETRY_SPATIAL_RELEASE_UNUSED'
    old=P/'repair_sources/h1_step270_path_reward_v1.py'
    checker=load(va/'step270_reward_installed_CPU_v1.py','v6a_installed_checker')
    fixture=W/'MOD4_4090_WINDOWS_REPAIR_20261013/repair_payload/CPU_SOURCE_ASSEMBLY_FIXTURE_V5_FINAL_BOUND_SOURCE/sdk_exact/source/isaaclab/isaaclab/managers/reward_manager.py'
    v6a=checker.check(va,fixture,allow_local_fixture=True,reference_path=old)
    # Independently retain the V5 new-target-cost fixtures, phase masks, fixed
    # weight, 20k float32 cost and no-mutation/RNG test on this same candidate.
    oldcheck=load(P/'repair_sources/step270_reward_installed_CPU_v1.py','old_v5_checker_reuse')
    old_result=oldcheck.check(va)
    a=load(va/'h1_step270_path_reward_v1.py','v6a_metrics')
    b=load(vb/'h1_step270_path_reward_v1.py','v6b_metrics')
    # V6B is intentionally not selected. Its no-action-write scalar function
    # is checked only so the future hypothesis is concrete and reviewable.
    n=20000;front=torch.linspace(-.10,.35,n);vx=torch.linspace(-.8,.8,n)
    request=torch.ones(n,dtype=torch.bool);attempt=request.clone();launched=torch.zeros(n,dtype=torch.bool)
    peak=torch.full((n,),.6);vz=torch.zeros(n);before=[v.clone() for v in (front,vx,request,attempt,launched,peak,vz)]
    values=b.spatial_release_shortfall(request=request,attempt=attempt,launched=launched,wheel_front=front[:,None].repeat(1,2),origin_x=torch.zeros(n),vx=vx,vz=vz,target_body_peak=peak)
    assert values.shape==(n,) and values.dtype==torch.float32 and torch.isfinite(values).all()
    assert not values[(front<=.1)|(vx<=0)].any()
    assert (values[(front>.15)&(vx>.1)]>0).all()
    assert all(torch.equal(x,y) for x,y in zip((front,vx,request,attempt,launched,peak,vz),before))
    aa=top_functions((va/'h1_step270_path_reward_v1.py').read_text('utf8'));bb=top_functions((vb/'h1_step270_path_reward_v1.py').read_text('utf8'))
    assert [name for name in aa if aa[name]!=bb[name]]==['configure']
    assert set(bb)-set(aa)=={'spatial_release_shortfall','measured_spatial_release_shortfall'}
    v6b=dict(passed_local_pure_CPU=True,selected_for_next_window=False,vectorized_float32_environments=n,
        far_or_nonforward_release_demand_zero=True,near_forward_release_demand_positive=True,
        no_input_mutation=True,new_scalar_gate_only_not_actor_observation=True,
        actual_installed_SDK_configure_compute_pending=True)

    z=np.load(U/'SELECTED_RECORDED_MOTION.npz',allow_pickle=False);k=np.load(U/'RECORDED_KINEMATIC_RECONSTRUCTION.npz',allow_pickle=False)
    geo=read(U/'reports/RECORDED_USD_KINEMATICS_CPU_ACTUAL.json');source=read(U/'reports/LATEST67_RECORDED_MOTION_SOURCE_CPU_ACTUAL.json')
    names=geo['body_names'];ids=[names.index(n) for n in ('left_wheel','right_wheel')];pos=k['body_pose'][...,:3,3]
    delta=pos[:,:,ids]-pos[:,:,[0]];delta_body=np.einsum('feji,fewj->fewi',k['body_pose'][:,:,0,:3,:3],delta)
    known=np.linalg.norm(delta_body[...,[0,2]],axis=-1)
    actual=a.sagittal_leg_lengths(delta_world=torch.tensor(delta.reshape(-1,2,3),dtype=torch.float32),root_quaternion_xyzw=torch.tensor(z['root13'][...,3:7].reshape(-1,4),dtype=torch.float32)).numpy().reshape(known.shape)
    err=float(np.max(np.abs(actual-known)));assert err<2e-6
    oldreward=.017*np.exp(-4*np.abs(np.linalg.norm(delta,axis=-1)-.22).sum(-1))
    hypothetical=.017*np.exp(-4*np.abs(known-.22).sum(-1))
    terms=source['reward_terms'];paid=z['reward_term_contribution'][...,terms.index('h1_scut_fudan_leg_tuck')]>0
    nearest=np.unravel_index(np.argmin(np.abs(known-.22)),known.shape)
    order=geo['joint_order_derived_from_actual_31link_order_each_one_DOF_incoming_joint']
    norm_check=float(np.max(np.abs(oldreward[paid]-z['reward_term_contribution'][...,terms.index('h1_scut_fudan_leg_tuck')][paid])))
    recorded=dict(saved91_environment_selected_48control_rows=True,
        source_scope=source['scope'],sagittal_function_vs_saved_reconstructed_body_pose_max_abs_error_m=err,
        old_actual_V5_tuck_formula_max_abs_error=norm_check,
        closest_recorded_sagittal_target_example=dict(control_row=int(nearest[0]),env_id=int(z['env_ids'][nearest[1]]),side=['left','right'][nearest[2]],sagittal_m=float(known[nearest]),error_from_target_m=float(abs(known[nearest]-.22)),recorded_no_fresh_rollout=True),
        selected_paid_hypothetical_V6A_reward_median=float(np.median(hypothetical[paid])),
        selected_paid_actual_V5_tuck_reward_median=float(np.median(oldreward[paid])),
        hypothetical_recomputed_scalar_not_new_received_reward_or_policy_gain=True)

    # Analytic endpoint proof supplements V1's 20k float32 scan. With fixed
    # thigh/wheel vectors, dL²/dq=2*(-A sin(q)+B cos(q)). Its stationary roots
    # are enumerated rather than treating a dense grid as a universal proof.
    contract=read(B/'import_contract.json');analytic=[]
    for side in ('left','right'):
        j=contract['joints'];v1=np.asarray(j[side+'_knee']['local_pos0'])[[0,2]];v2=np.asarray(j[side+'_wheel_spin']['local_pos0'])[[0,2]]
        lo,hi=j[side+'_knee']['limits_si'];A=float(np.dot(v1,v2));D=float(v1[0]*v2[1]-v1[1]*v2[0]);lateral=sum(j[n]['local_pos0'][1] for n in (side+'_hip',side+'_knee',side+'_wheel_spin'))
        first=math.atan2(D,A);critical=[first+i*math.pi for i in range(-3,4) if lo<=first+i*math.pi<=hi]
        def length(q):return math.sqrt(float(v1@v1+v2@v2+2*(A*math.cos(q)+D*math.sin(q))+lateral*lateral))
        candidates=[lo,hi]+critical;minimum=min(length(q) for q in candidates)
        assert not critical and minimum>.22
        analytic.append(dict(side=side,stationary_knee_angles_inside_authored_interval=critical,
            exact_chain_min_over_authored_knee_interval_m=minimum,
            original_full3D_target_m=.22,original_target_infeasible_within_this_relaxed_chain=True,
            analytical_chain_check_not_new_dynamics_or_health_gate=True))

    runtime=P/'repair_sources/h1_step270_sdk_runtime_candidate.py';runtime_text=runtime.read_text('utf8')
    task=(B/'mod4_task.py').read_text('utf8');train=(B/'train_H1_ground_prelaunch_fullstate_v2.py').read_text('utf8');reset=(B/'scut_flat_rescue.py').read_text('utf8')
    assert sha(runtime)=='0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34'
    assert 'return (self.age_control>=100)&(self.age_control<180)' in runtime_text
    assert 'self.h1_phase.public_request().float()*.8' in runtime_text
    assert 'v[:, 6] = 0.0' in task and 'actor_hidden_dims=RM_HIDDEN_DIMS' in train
    assert 'root[:,2]=' in reset and 'root[:,7:]=0.0' in reset
    obs=dict(policy35_slots=[
        dict(slots='0..2',name='body twist command'),dict(slots='3',name='height command'),
        dict(slots='4..6',name='delayed body angular velocity'),dict(slots='7..9',name='delayed projected gravity'),
        dict(slots='10..13',name='delayed leg joint position'),dict(slots='14..15',name='zero wheel position placeholders'),
        dict(slots='16..19',name='delayed leg joint velocity'),dict(slots='20..21',name='delayed wheel velocity'),
        dict(slots='22..27',name='previous requested action'),dict(slots='28..34',name='mode onehot; final state_time slot always0')],
        actor_is_feedforward_MLP=True,no_edge_gap_root_x_vision_terrain_or_episode_clock_input=True,
        critic38_has_extra_linear_velocity_not_edge_gap=True,
        public_command_is_existing_vx_point8_during_age100_through179=True,
        original_reset_base_xy_range_m=[-.1,.1],original_reset_base_yaw_range_rad=[-.3,.3],
        consistent_closed_pose_reset_retains_random_xy_yaw_and_only_sets_z_q_and_zero_velocity=True,
        translation_aliasing='On the same flat ground before edge contact, translating root x changes true edge gap but leaves actor cmd/proprio/lastaction/mode unchanged; an instantaneous memoryless actor cannot condition on that hidden gap.',
        V6B_observability_limit='A spatial scalar reward may bias the learned approach/jump sequence under the fixed task reset distribution. It does not make true distance observable or prove robust gap-dependent launch/generalization.',
        V6A_observability='Corrected sagittal extension is related to existing measured joint/orientation proprioception; it adds no actor input or terrain cue.',
        stage_reporting_limit='Any new-window result is reported under the actual initial-state distribution, with launch timing strata, never as generic edge-aware policy proof.',
        proposed_new_actor_inputs_or_reset_changes=False)
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    result=dict(epoch=time.time(),trial_id='H1_POST67_V6A_V6B_LOCAL_CPU_VERIFY_V1_20261025',
        status='local_CPU_passed_actual_installed_SDK_compute_pending_root_review',
        V6A=v6a,retained_V5_target_overdrive_fixture=old_result,V6B=v6b,
        recorded_metric_crosscheck=recorded,analytic_target_feasibility=analytic,
        actor_observability=obs,candidate_files=[file(va/'h1_step270_path_reward_v1.py'),file(va/'step270_reward_installed_CPU_v1.py'),file(vb/'h1_step270_path_reward_v1.py')],
        unchanged_runtime=file(runtime),local_SDK_fixture=file(fixture),
        local_fixture_SHA_differs_from_actual_installed_SDK=True,
        actual_installed_SDK_future_check='Call check(B, actual_sdk/managers/reward_manager.py) without allow_local_fixture. Expected installed SHA6be44...; only source-extracted compute runs on CPU stand-ins.',
        no_live_source_replacement_GO_training_native_query_PhysX_policy_GPU_budget_or_Git=True,
        archive_status='pending_root_unique_trial_archive')
    put('V6A_V6B_FLOAT32_CPU_ALLOWLIST_OBSERVABILITY_ACTUAL.json',result)
    plan='''# Post67 H1 reward geometry preparation — root review handoff

The next-window recommendation is V6A only. It changes the SCUT .22m extension metric from the full three-dimensional chassis-to-wheel norm to the measured chassis-frame sagittal XZ norm. The original 1.7 weight, exponential gain4, airborne/current-clearance/attempt/crossing masks, V5 target-overdrive term, release timing, requested-forward shaping and all remaining reward functions/configuration are AST-exact. Runtime SHA0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34 remains byte-exact. Both .22m definitions and every older failed/raw classification remain in their original files.

The geometry evidence is a contract-chain bound and saved67 kinematics. The fixed lateral wheel mounting offset is218.800mm. The original full3D .22m target lies below even the relaxed knee-chain lower bound247.361mm. The corrected sagittal .22m target lies in the authored range and near actual recorded poses. This identifies a target-definition error. It does not establish that the old reward was zero, that this was the sole learning bottleneck, or that V6A trains the skill successfully.

V6B is a separate unused hypothesis. It changes reward-only release demand to depend on measured approach and narrows the existing push gate to start at front.10m and reach full strength at.15m. It retains the external command and physical observers. It is not selected for68: changing timing and geometry together would obscure attribution. Actor35 has no edge gap, root x, terrain vision, episode age or phase clock. It is feedforward; wheel-position slots and final state_time slot are0. Original reset randomizes x/y±.1m and yaw±.3rad, and the later consistent reset retains those coordinates. V6B can only bias behavior under this fixed reset distribution; it cannot grant unobserved gap information or prove distance-adaptive generalization.

## Root's minimal new-window procedure

1. Close and settle both actual M4 owners/cost records using returned process receipts. Keep their benchmark sources separate. Re-read the ordinary fresh ownership/resource/storage/source guards. The only qualified H1 predecessor is closed67 complete118, Adam790000, SHAd1dd187177a1878f007b05da26e39c5ee101e937d2d86f0948dde1ffd37f062e. No old experiment, once helper or native/query test is replayed.
2. In root's new reviewed payload, replace only h1_step270_path_reward_v1.py with the V6A candidate and its reward CPU checker. Keep original runtime/commands.8/public100..179, actor35/critic38, PPO/std/17Adam restore and hardware/physics/save/account contracts. Do not use V6B. Do not promote these local files merely because CPU checks passed.
3. Run the corresponding pure CPU checker against the actual installed SDK reward_manager.py. The local saved fixture SHA2ff82... differs from installed SDK SHA6be44... and was explicitly labelled local fixture. The supplied checker requires the installed SHA when called without allow_local_fixture. Root should retain actual source/hash/compute receipt. This is the remaining integration check; it is not a new physical graduation gate.
4. Use only a fresh ordinary authorized bounded training window68. Preserve the existing save deadline/update/storage contract; do not alter budget or stop live work for this audit. Keep the same normal source/RNG/DR/optimizer restoration and real action path. Preserve all new failures and actual valid saves.
5. Save passive diagnostics together with the next ordinary prefix, if root's reviewed trace hook can add them without affecting action/reward/RNG/physical state: term.raw_actions; term.processed_actions; live term._offset/_scale; D4 queue applied/pending target and issue/apply tick; actual articulation joint_pos_target; root local x; already measured wheel min/max and reward masks. These distinguish current issued action, processed target, queued/applied target and achieved joint q. The67 selected arrays cannot reconstruct all those distinctions. This tracing is a separate diagnostic-only change requiring its own allowlist; the candidate does not install it.
6. For first and final ordinary saved prefixes, report all20k counts and distributions from newly saved data: genuine takeoff/edge/landing/recovery increments; sagittal/full3D lengths during true measured flight; actual new tuck term payments; issued-raw saturation; processed/applied target residuals if captured; takeoff wheel-leading gap and vx; clearance>=270mm intervals and actual crossing alignment; reset/failure causes and save completeness. Stratify by launch/root-x/gap cohorts. Selected extreme-case pictures remain illustrations.
7. Compare68 to the saved67 evidence descriptively under their stated sampling scopes. A sequential67→68 continuation does not identify a controlled causal gain. Do not branch/replay67 for a counterfactual or claim matched A/B. If future authorization explicitly calls for an A/B study, specify equal fresh budgets/seeds/source states as a separate new trial. Do not create that authorization here.
8. Retain the exact skill contract: both real wheel bottoms cross the270mm edge, real top contact footprint, and200 physical callbacks=.5s stable recovery. No height-only, hypothetical metric, CPU result, selected trace, or PPO-complete save counts as graduation. Existing native3/query9 evidence is reused; no FP64/1um/bit-identity/extra physical gate is added.

All preparation files/reports in this directory are local and pending root's unique Git trial archive. No training host connection, model/PT read, policy inference, rollout, GPU, GUI, cleanup, live source mutation or Git command was performed by this agent.
'''
    with (R/'V6A_NEXT_WINDOW_ROOT_REVIEW_AND_MINIMAL_COMPARISON_PLAN.md').open('x',encoding='utf8') as f:f.write(plan)
    put('SUPPLEMENTAL_READER_ERROR_AND_SCOPE_ACTUAL.json',dict(epoch=time.time(),action='read guessed reports/ACTUAL_RUNTIME_CALLBACK_AND_SDK_REWARD_COMPUTE_CPU_V3_ACTUAL.json',result='path not found',resolved='existing REPLAY_V2_REWARD_RUNTIME_AND_ACTUAL_SDK_COMPUTE_CPU_V3_ACTUAL.json and LOCAL_FIXTURE_AND_ACTUAL_INSTALLED_SDK_COMPUTE_SCOPE_ACTUAL.json read',local_only_not_training_failure=True,archive_status='pending_root_unique_trial_archive'))
    print(json.dumps(dict(report=str(R/'V6A_V6B_FLOAT32_CPU_ALLOWLIST_OBSERVABILITY_ACTUAL.json'),V6A=v6a,V6B=v6b,recorded=recorded,analytic=analytic,files=result['candidate_files']),ensure_ascii=False))

if __name__=='__main__':
    try:main()
    except BaseException:
        put('V6_CPU_VERIFICATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),same_once_not_retried=True));raise
