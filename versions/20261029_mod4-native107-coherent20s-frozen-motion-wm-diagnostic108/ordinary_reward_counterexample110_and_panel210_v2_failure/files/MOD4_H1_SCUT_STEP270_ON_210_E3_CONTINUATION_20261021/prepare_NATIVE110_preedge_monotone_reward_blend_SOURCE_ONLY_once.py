"""SOURCE ONLY: remove explicit position-induced adverse mode baseline."""
from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
B=L/'native110_preedge_monotone_reward_blend_source_v1';assert not B.exists();B.mkdir();(B/'reports').mkdir()
src=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029/payloads_v2/seed27/source'
H=lambda raw:hashlib.sha256(raw).hexdigest()
rname='mod4_fudan_contact_phase_reward_candidate_v2.py';qname='OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json';aname='native_fudan_step_adapter_candidate_v2.py'
old=(src/rname).read_bytes()
near_old=b"    near=torch.sigmoid((.18-front_gap)/.03)*torch.sigmoid((front_gap+.10)/.03)"
near_new=b"""    # Before the leading wheel edge crosses, approach gating is monotone.
    # Preserve a continuous decay after the edge rather than fading beforehand.
    post_edge_decay=torch.where(front_gap>=0,torch.ones_like(front_gap),
        torch.sigmoid((front_gap+.10)/.03)/torch.sigmoid(front_gap.new_tensor(.10/.03)))
    near=torch.sigmoid((.18-front_gap)/.03)*post_edge_decay"""
assert old.count(near_old)==1
oldbody=old[old.index(b'def combined_reward'):]
newbody=b"""def combined_reward(m,p,modes):
    \"\"\"Native110 common baseline plus mode advantages; declared MOD4 adaptation.\"\"\"
    j,jparts=_weighted(instantaneous_jump_terms(m,p),JUMP_WEIGHTS,2.5,p.control_dt_s)
    r,rparts=_weighted(instantaneous_stair_recovery_terms(m,p),RECOVERY_WEIGHTS,1.,p.control_dt_s)
    quiet=torch.exp(-m['root_planar_velocity'].square().sum(-1)/.15**2-m['body_angular_velocity'].square().sum(-1)/.3**2)
    placement=modes['top_support']*quiet
    # All six bonuses are nonnegative. The recovery-specific residual is
    # nonpositive: base_height is capped at dt, other two terms are costs.
    jump_bonus=sum(jparts[k] for k in
        ('flight','encourage_jump_upward_only','base_height_flight','leg_tuck','takeoff_extend','line_z'))
    recovery_extra=rparts['base_height']+rparts['base_height_enhance']+rparts['lin_vel_z']-p.control_dt_s
    mode_advantage=jump_bonus-recovery_extra
    # Equivalent to common + jump*bonus + recovery*extra + dt.
    # At jump=0 this is exactly the original recovery reward (no new alive offset).
    total=r+modes['jump']*mode_advantage+p.control_dt_s*placement
    assert torch.isfinite(total).all()
    return dict(total=total,jump_reward=j,recovery_reward=r,jump_terms=jparts,recovery_terms=rparts,
                own_top_support_quiet_placement=placement,unsupported_original_terms=NATIVE_UNAVAILABLE_OR_STATEFUL_ORIGINAL_TERMS,
                actual_success_not_inferred=True,nonnegative_jump_bonus=jump_bonus,
                nonpositive_recovery_extra=recovery_extra,mode_advantage=mode_advantage)
"""
new=old.replace(near_old,near_new).replace(oldbody,newbody)
assert new.replace(newbody,oldbody).replace(near_new,near_old)==old
ast.parse(new)
for name,data in [(rname,new),(qname,(src/qname).read_bytes()),(aname,(src/aname).read_bytes())]:(B/name).write_bytes(data)
contract=dict(kind='SOURCE_ONLY_NATIVE107_TO110_PREEDGE_MODE_BLEND_REPAIR_V1',epoch=time.time(),
 parent_source_SHA=H(old),candidate_reward_SHA=H(new),reference_SHA=H((src/qname).read_bytes()),adapter_SHA=H((src/aname).read_bytes()),
 input_model_metadata_only=dict(SHA='36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef',bytes=256234249,global_iteration=17272,WM=172720,Pi=16632),
 changes=['Replace blending two different total-reward baselines by original recovery common baseline plus nonnegative jump mode advantage.',
 'Make near-edge gate monotone before the leading wheel reaches the edge; retain continuous decay after crossing and original top-support recovery.'],
 algebra=dict(J='sum of six nonnegative clipped jump bonuses',E='recovery base_height + base_height_enhance + lin_vel_z - dt, always <=0',R='original recovery reward',w='original request-masked jump mode after corrected preedge gate',new='R + w*(J-E) + dt*top_support*quiet',old='w*jump_total + (1-w)*recovery_total + dt*top_support*quiet',
 derivative_wrt_w='J-E >=0 for finite valid measurement domain',common_upper_bound=.02,jump_bonus_upper_bound=.0985,placement_upper_bound=.01,dt_restore=.01,total_upper_bound=.1385),
 exact_inverse_source_bytes=True,reference_and_adapter_bytes_unchanged=True,
 unrelated_109_geometry_and_velocity_gate_changes_NOT_selected=True,
 preserved=['all instantaneous Fudan-derived formulas, original weights/clips/dt','extension0.31/tuck0.16/positive-vz takeoffgate unchanged for this bounded blend repair',
 '20s/request200..1999/private4096/age_seconds/horizon32/goal10/focus sampler/architecture/learner/models/norms/threeopts',
 '400plant/native100Hz/2.5msTGS32/4/FP32/PD/clip6/delay/DR/reset',
 'actual270dualwheelcross/fullfootprint/topcontact12+stable200 and terminal goal'],
 validity=['Monotone positional claim is for an unchanged supported floor pose before leading-edge crossing, so top support is absent and command/support surface do not change.',
 'No monotonicity claim across actual landing, top-support activation, command changes, collisions, resets, arbitrary inconsistent scene states or postedge decay.',
 'Source algebra/CPU passing is not complete reward correctness, policy improvement, GPU admission or270mm success.',
 'Native109 source-only calibration retained NOT_SELECTED because its unchanged total blend must be checked against the same counterexample.',
 'No new force/action script/airborne reset/state/RNG/model read/raw decode/SDK/remote/GO/account operation.'],
 actual_sourceSDK_fullstate_payload_producer_Task_GO_resource_admission_pending=True,source_only=True)
(B/'SOURCE_DELTA_TYPED_CONTRACT_110_V1.json').write_text(json.dumps(contract,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(source_only=True,candidate_reward_SHA=H(new),path=str(B))))

