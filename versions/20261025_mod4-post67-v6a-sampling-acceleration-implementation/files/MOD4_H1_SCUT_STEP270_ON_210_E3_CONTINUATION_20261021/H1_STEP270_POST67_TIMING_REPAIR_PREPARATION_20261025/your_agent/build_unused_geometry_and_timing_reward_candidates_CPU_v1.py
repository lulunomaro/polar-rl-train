"""Write reviewable candidates in this preparation directory only.

V6A changes the length metric. V6B adds measured spatial launch timing.
Neither is selected, installed or authorized by running this builder.
"""
from pathlib import Path
import ast, hashlib, json, time, traceback

S=Path(__file__).resolve().parent; T=S.parent.parent; R=S/'reports'
P=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/repair_sources/h1_step270_path_reward_v1.py'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def functions(text):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}

try:
    before=P.read_text('utf8');assert sha(P)=='42909a5e40334e21a6bc7df83950756207f8366fce975662ab08ced1dea41193'
    helper='''def sagittal_leg_lengths(*, delta_world, root_quaternion_xyzw):
    """Actual chassis-frame XZ extension, excluding fixed mounting width.

    Quaternion is the existing measured root orientation. No guessed lateral
    offset, target pose, joint command or actor-visible signal is introduced.
    """
    q=root_quaternion_xyzw[:,None,:3]
    qw=root_quaternion_xyzw[:,None,3:4]
    # Inverse rotate measured vectors: q^-1 v q, for source unit xyzw q.
    t=2.*torch.cross(q.expand_as(delta_world),delta_world,dim=-1)
    local=delta_world-qw*t+torch.cross(q.expand_as(delta_world),t,dim=-1)
    return local[:,:,(0,2)].norm(dim=-1)


'''
    a=before.replace("version='step270_airborne_feasible_target_v5'","version='step270_sagittal_tuck_geometry_v6a_unused'")
    a=a.replace('def airborne_tuck_rate(env):',helper+'def airborne_tuck_rate(env):',1)
    old='''    # Same original SCUT/Fudan measured body-to-wheel length formula.
    # Request expiry must not end retraction shaping during measured flight.
    # Stop before landing extension once both wheels actually crossed.
    compact=torch.exp(-torch.sum(torch.abs(delta.norm(dim=-1)-.22),dim=1)*4.)'''
    new='''    # .22m is the measured sagittal extension target. MOD4's fixed
    # .2188m lateral wheel mounting distance is excluded from leg extension.
    # Existing phase mask, target scalar, gain and weight are retained.
    length=sagittal_leg_lengths(delta_world=delta,root_quaternion_xyzw=root[:,3:7])
    compact=torch.exp(-torch.sum(torch.abs(length-.22),dim=1)*4.)'''
    assert a.count(old)==1;a=a.replace(old,new)
    common=set(functions(before)) & set(functions(a))
    changes=[name for name in sorted(common) if functions(before)[name]!=functions(a)[name]]
    assert changes==['airborne_tuck_rate']
    d=S/'reward_candidate_V6A_GEOMETRY_UNUSED';d.mkdir()
    pa=d/'h1_step270_path_reward_v1.py'
    with pa.open('x',encoding='utf8') as f:f.write(a)

    # The full-strength point .15m is retained from the existing takeoff gate.
    # The .10m zero-strength point is the existing joint-clearance potential
    # start. This removes an early launch incentive rather than changing goal,
    # external command, physical loop, reset, observation, or phase witnesses.
    b=a.replace("version='step270_sagittal_tuck_geometry_v6a_unused'","version='step270_sagittal_tuck_spatial_release_v6b_unused'")
    b=b.replace("takeoff_gate_start_front_x_m=-.05", "takeoff_gate_start_front_x_m=.10",1)
    timing='''def spatial_release_shortfall(*, request, attempt, launched, wheel_front,
                               origin_x, vx, vz, target_body_peak):
    """Reward-only launch demand after measured approach, independent of age.

    This is a candidate shaping reference, never an expected physical result.
    Retains the original .31m ballistic release-height reference, 9.81m/s2,
    actual fresh-request target_body_peak, public request and attempt masks.
    """
    gate=forward_takeoff_factor(wheel_front=wheel_front,origin_x=origin_x,vx=vx)
    release_vz=(2.*9.81*(target_body_peak-.31).clamp_min(0.)).sqrt()
    active=request & attempt & ~launched
    return active.to(vz.dtype)*gate*(release_vz-vz).clamp_min(0.)


def measured_spatial_release_shortfall(env):
    from h1_takeoff_progress_environment_v2 import tensor
    p=env.h1_phase
    root=tensor(env.scene['robot'].data.root_state_w)
    return spatial_release_shortfall(request=p.request_for_action,attempt=p.attempt,
        launched=p.launched,wheel_front=p.previous_front,
        origin_x=env.scene.env_origins[:,0],vx=root[:,7],vz=root[:,9],
        target_body_peak=p.target_body_peak)


'''
    b=b.replace('def configure(cfg):',timing+'def configure(cfg):',1)
    old="    cfg._h1_step270_path_reward_recipe=dict(RECIPE)"
    new="""    # Only scalar learning reward binding changes. The old age-dependent
    # release_reference_vz remains intact in diagnostic/phase state.
    cfg.rewards.h1_step270_release_shortfall.func=measured_spatial_release_shortfall
    cfg.rewards.h1_step270_release_shortfall.params={}
    cfg._h1_step270_path_reward_recipe=dict(RECIPE)"""
    assert b.count(old)==1;b=b.replace(old,new)
    changes_b=[name for name in sorted(set(functions(a))&set(functions(b))) if functions(a)[name]!=functions(b)[name]]
    assert changes_b==['configure']
    d=S/'reward_candidate_V6B_GEOMETRY_SPATIAL_RELEASE_UNUSED';d.mkdir()
    pb=d/'h1_step270_path_reward_v1.py'
    with pb.open('x',encoding='utf8') as f:f.write(b)
    report=dict(epoch=time.time(),trial_id='H1_POST67_UNUSED_REWARD_SOURCE_BUILD_V1_20261025',
        status='unused_local_candidates_root_review_required_not_installed_not_Git_recorded',
        V5_source=dict(path=str(P),SHA=sha(P)),
        V6A=dict(path=str(pa),SHA=sha(pa),changed_existing_functions=changes,
                 new_functions=['sagittal_leg_lengths'],recipe_only_version_changed=True,
                 hypothesis='Correct unreachable .22 full3D norm to reachable .22 sagittal extension; no weight increase.'),
        V6B=dict(path=str(pb),SHA=sha(pb),additional_changed_functions=changes_b,
                 new_functions=['spatial_release_shortfall','measured_spatial_release_shortfall'],
                 takeoff_gate_start_front_x_m_before=-.05,takeoff_gate_start_front_x_m_candidate=.10,
                 takeoff_gate_full_front_x_m_unchanged=.15,
                 release_shortfall_weight_unchanged=-2.,
                 hypothesis='Permit measured ground approach before launch demand and retain launch demand after late approach; replace public-request-age ballistic timer only in scalar reward.'),
        runtime_SHA_unchanged='0ec7db1fc55ca0d552341e24237048a916d1cbb6b125905eb22b0001b60a8e34',
        all_V5_target_overdrive_formulas_weights_phase_masks_retained=True,
        no_phase_save_schema_action_actor_input_command_goal_mesh_physics_optimizer_budget_or_training_write=True,
        candidate_risk='Geometry or spatial timing repair alone cannot prove learning. Existing V5 policy may retain early launch; only a newly authorized bounded training prefix can show behavior.',
        not_a_deployment_selector_or_future68_replacement=True,archive_status='pending_root_unique_trial_archive')
    put('V6A_V6B_UNUSED_REWARD_CANDIDATE_SOURCE_AST_ACTUAL.json',report)
    print(json.dumps(report,ensure_ascii=False))
except BaseException:
    put('UNUSED_SOURCE_BUILD_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),same_once_not_retried=True))
    raise
