"""Replay existing actor observations and processor mathematics only; no GPU/physics/learning."""
from pathlib import Path
import json,hashlib,time,torch,numpy as np
from left_joint_domain_cpu_component import CPU_mean,guarded_targets,SOURCE_SHA
D=Path(__file__).resolve().parent;R=D/'reports'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=json.loads((R/'LEFT_JOINT_INTERIOR_COMPONENT_CPU_ACTUAL_REVIEW.json').read_bytes())
assert proof['CPU_math_passed'] and proof['no_production_adoption']
assert sha(proof['source']['path'])==SOURCE_SHA and sha(proof['candidate']['path'])==proof['candidate']['sha256']
baseline=json.loads((R/'REFERENCE17B_FULL1500_COMPLETE_PAIRED91D_CPU_ACTUAL_REVIEW.json').read_bytes())
rawrow=baseline['raw_actual'];assert sha(rawrow['local_path'])==rawrow['sha256']
with np.load(rawrow['local_path']) as z:
    obs=torch.from_numpy(z['policy_obs'].copy()).reshape(-1,35)
    action=torch.from_numpy(z['action'].copy()).reshape(-1,6)
    actual=torch.from_numpy(z['guarded_leg_targets'].copy()).reshape(-1,4)
assert obs.shape==(12000,35) and action.shape==(12000,6) and actual.shape==(12000,4)
assert torch.isfinite(obs).all() and torch.isfinite(action).all() and torch.isfinite(actual).all()
source=torch.load(proof['source']['path'],map_location='cpu',weights_only=False)
candidate=torch.load(proof['candidate']['path'],map_location='cpu',weights_only=False)
assert not torch.cuda.is_initialized()
offset=torch.tensor(source['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']['actual_GPU_API_offset_and_default_q_leg_order'],dtype=torch.float32)
lower=-1.0843;upper=.85;scale=.5
# Exact same processor order as frozen original mod4_task.py: clip, scale+offset,
# then max/min each crank relative to its own hip. TargetAPI has not been remeasured here.
requested=action[:,:4].clip(-6,6)*scale+offset
represented=requested.clone()
for c,h in ((0,1),(2,3)):
    represented[:,c]=torch.maximum(represented[:,c],represented[:,h]+lower)
    represented[:,c]=torch.minimum(represented[:,c],represented[:,h]+upper)
processor_error=float((represented-actual).abs().max())
assert processor_error<=2e-6,'Saved-target contract mismatch; do not deploy'
inverse=[]
for j in range(4):
    if j in (0,2):
        h=j+1;difference=actual[:,j]-actual[:,h];mask=(difference>lower+2e-6)&(difference<upper-2e-6)
    else:mask=torch.ones(len(actual),dtype=torch.bool)
    assert int(mask.sum())>100
    residual=actual[mask,j]-action[mask,j].clip(-6,6)*scale
    error=float((residual-offset[j]).abs().max());assert error<=2e-6
    inverse.append(dict(joint_index=j,unguarded_actual_samples=int(mask.sum()),saved_source_GPU_offset_witness=float(offset[j]),inverse_witness_max_error_rad=error,reference_API_direct_measurement_not_saved=True))
rng=torch.get_rng_state().clone();torch.set_num_threads(1)
with torch.inference_mode():
    old=CPU_mean(source['actor_state_dict'],obs)
    new=CPU_mean(candidate['actor_state_dict'],obs)
assert torch.equal(old[:,1:],new[:,1:]) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
error=(old-action).abs().max(0).values.tolist()
# CPU and GPU linear/ELU arithmetic need not be byteexact. Preserve actual
# discrepancies rather than claiming cross-device equivalence or changing tolerances.
old_guard=guarded_targets(old,offset);new_guard=guarded_targets(new,offset)
rows=[]
for i in range(8):
    a=action.reshape(1500,8,6)[:,i]
    oa=old.reshape(1500,8,6)[:,i];na=new.reshape(1500,8,6)[:,i]
    og=old_guard.reshape(1500,8,4)[:,i];ng=new_guard.reshape(1500,8,4)[:,i]
    def metrics(raw,target):
        clip=raw[:,:4].clip(-6,6)*scale+offset
        d=target[:,0]-target[:,1]
        return dict(actor_raw_clip6_fraction=(raw.abs()>=6).float().mean(0).tolist(),left_lower_guard_fraction=float(((d-lower).abs()<=2e-6).float().mean()),left_upper_guard_fraction=float(((d-upper).abs()<=2e-6).float().mean()),left_guard_changed_request_fraction=float(((target[:,0]-clip[:,0]).abs()>2e-6).float().mean()),left_mean_joint_difference_bounds_rad=[float(d.min()),float(d.max())])
    rows.append(dict(env=i,standing=i==7,actual_source_mean=a.mean(0).tolist(),old_CPU_mean=oa.mean(0).tolist(),candidate_CPU_mean=na.mean(0).tolist(),old_CPU_processor=metrics(oa,og),candidate_CPU_processor=metrics(na,ng),candidate_left_target_max_change_rad=float((ng[:,0]-og[:,0]).abs().max()),five_other_CPU_mean_outputs_byteexact=True,candidate_on_original_observations_only_not_its_own_physical_trajectory=True))
report=dict(epoch=time.time(),existing_raw_CPU_replay_complete=True,source=proof['source'],candidate=proof['candidate'],raw=rawrow,actual_observations=12000,represented_original_processor_vs_actual_guarded_targets_max_error_rad=processor_error,original_processor_tolerance_not_changed=True,inverse_saved_offset_witness=inverse,actual_source_GPU_action_vs_same_weight_CPU_action_max_errors=error,cross_device_actor_byteexact_not_claimed=True,five_other_CPU_mean_heads_same_obs_byteexact=True,no_RNG_draw_or_CUDA=True,per_env=rows,all_before_after_fields_CPU_mean_diagnostics_only=True,actual_candidate_physical_trajectory_unknown=True,new_GPU_fullstate_native_actualoffset_defaultq_and_behavior_still_required=True,source512_not_Linux20k_default=True,no_production_adoption=True,no_running_trainer_modified=True,qualified50=False)
p=R/'LEFT_JOINT_CANDIDATE_SAVED_ACTUAL_OBS_CPU_REPLAY.json';assert not p.exists();p.write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(p),processor_error=processor_error,old_CPU_vs_recorded_GPU_max_error=max(error),old_left_lower_fractions=[r['old_CPU_processor']['left_lower_guard_fraction'] for r in rows[:7]],candidate_left_lower_fractions=[r['candidate_CPU_processor']['left_lower_guard_fraction'] for r in rows[:7]],candidate_physical_pass_not_claimed=True)))
