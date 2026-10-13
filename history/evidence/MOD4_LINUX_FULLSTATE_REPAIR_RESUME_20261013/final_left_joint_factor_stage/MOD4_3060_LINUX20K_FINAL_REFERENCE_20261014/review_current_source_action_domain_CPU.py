"""Current own final's observed raw and conditional training exploration diagnostic, no draws/GPU."""
from pathlib import Path
import json,time,hashlib,torch,numpy as np
D=Path(__file__).resolve().parent;R=D/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
review=json.loads((R/'LINUX20K_FINAL_FULL1500_COMPLETE_PAIRED91D_CPU_ACTUAL_REVIEW.json').read_bytes());row=review['raw_actual'];assert H(row['local_path'])==row['sha256']
source=D/'payload/source/model_32411_17b.pt';assert H(source)==review['source_Linux20k_final_SHA'];ck=torch.load(source,map_location='cpu',weights_only=False)
sigma=ck['actor_state_dict']['distribution.std_param'].double();assert sigma.shape==(6,) and torch.isfinite(sigma).all() and (sigma>0).all()
with np.load(row['local_path']) as z:
 action=z['action'].copy();target=z['guarded_leg_targets'].copy();reason=z['reasons'].copy();term=z['terminated'].copy();trunc=z['truncated'].copy()
assert action.shape==(1500,8,6) and target.shape==(1500,8,4)
# The native offset API was measured directly in both same-backend factor scopes.
# Verify zerooffset again against all current actualprocessedtargets; no API witness is invented.
offset=torch.zeros(4);a=torch.from_numpy(action);processed=a[:,:,:4].clip(-6,6)*.5
for c,h in ((0,1),(2,3)):
 processed[:,:,c]=torch.maximum(processed[:,:,c],processed[:,:,h]-1.0843)
 processed[:,:,c]=torch.minimum(processed[:,:,c],processed[:,:,h]+.85)
assert torch.equal(processed,torch.from_numpy(target))
left=a[:,:,0].double();hip=a[:,:,1].double().clip(-6,6);lo=(hip-1.0843/.5).clamp(min=-6);hi=(hip+.85/.5).clamp(max=6)
prob=torch.special.ndtr((hi-left)/sigma[0])-torch.special.ndtr((lo-left)/sigma[0]);assert (prob>=0).all() and (prob<=1).all()
rows=[]
for i in range(8):
 d=target[:,i,0]-target[:,i,1]
 rows.append(dict(env=i,standing=i==7,raw_left_mean_range=[float(left[:,i].min()),float(left[:,i].max())],raw_left_clip_lower_fraction=float((action[:,i,0]<=-6).mean()),actual_left_target_lower_guard_fraction=float((abs(d+1.0843)<=2e-6).mean()),conditional_probability_inside_left_raw_legal_interval_given_mean_hip_range=[float(prob[:,i].min()),float(prob[:,i].max())],conditional_probability_mean=float(prob[:,i].mean()),complete1N=bool(review['fullroute']['rows'][i]['complete_double1N_episodes'])))
p=R/'LINUX20K_FINAL_ACTION_DOMAIN_ACTUAL_DIAGNOSIS.json';assert not p.exists()
v=dict(epoch=time.time(),source_SHA=H(source),source_saved_envs=20000,source_finite107_checked_by_existing_CPU=True,complete_source_own_saved_updates=184,frozen_fixture_complete1N=review['fullroute']['complete_double1N_envs'],ordinary_events=review['ordinary_events'],actual_actor_nine_GPU_bytes_source_exact=True,actual_zero_offset_processor_reconstruction_byteexact=True,source_scalar_sigma_all_six=sigma.tolist(),perenv=rows,conditional_probability_is_not_full_joint_hip_crank_or_physical_transit_probability=True,sole_cause_of_nonpass_not_claimed=True,actual_left_deadzone_learning_flaw_evidence=True,existing_mean_only_factors_rejected_for_no_stable_passability=True,next_axis_requires_actual20k_whole_source_and_native_API_fullstate_admission_before_newPPO=True,no_RNG_draw_CUDA_budget_or_running_trainer_mutation=True,not_80env_50mm_qualification=True)
p.write_text(json.dumps(v,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(p),source_sigma0=float(sigma[0]),raw_left_lower_fraction=[r['raw_left_clip_lower_fraction'] for r in rows[:7]],probability_range=[min(r['conditional_probability_inside_left_raw_legal_interval_given_mean_hip_range'][0] for r in rows),max(r['conditional_probability_inside_left_raw_legal_interval_given_mean_hip_range'][1] for r in rows)],fullroute=review['fullroute']['complete_double1N_envs'],no_GPU=True)))
