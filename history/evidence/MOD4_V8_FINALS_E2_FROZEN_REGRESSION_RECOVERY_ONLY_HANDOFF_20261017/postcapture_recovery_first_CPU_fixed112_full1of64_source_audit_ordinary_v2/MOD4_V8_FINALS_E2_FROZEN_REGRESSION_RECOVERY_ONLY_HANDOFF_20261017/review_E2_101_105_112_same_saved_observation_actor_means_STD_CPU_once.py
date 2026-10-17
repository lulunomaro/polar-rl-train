"""Conditional network diagnostic on recorded112 observations; never a counterfactual rollout."""
from pathlib import Path
import os,time,json,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
import numpy as np
K=Path(__file__).resolve().parent;W=K.parent;R=K/'reports';J=W/'MOD4_V7_FINALS_AND_CLOSED101_FROZEN_RESIDUAL_20261017';I=W/'MOD4_TWO72_V6_FINALS_LATEST101_FROZEN_SAME_SCOPE_HANDOFF_20261017';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 c=json.loads((R/'E2_CLOSED112_FULL1500_V10_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());assert c['parent_child_launcher_actual_absent'] and c['shared_OS_lock_free'];row=next(r for r in c['files'] if r['relative'].endswith('/E2_CLOSED112_SINGLE_FULL_CONTROL_ACTUAL.npz'));p=Path(row['local_path']);assert row['twohost_complete_SHA'] and H(p)==row['SHA']
 with np.load(p,allow_pickle=False) as z:obs=z['shared_obs'].copy();actual=z['raw_action'].copy()
 assert obs.shape==(1500,88,35) and actual.shape==(1500,88,6) and np.isfinite(obs).all() and np.isfinite(actual).all();torch.set_num_threads(4);rng=torch.get_rng_state().clone();sources=[('101',I/'e2_closed101_frozen_prepared_v7/payload/source/E2_closed101.pt','61b9ee57c2f96c9a167fb61122a782ad2b17d28c6227dfa89f9de67ed5d3d84e'),('105',J/'e2_latest_closed105_frozen_source_CPU_v1/E2_actual_latest_closed105.pt','ef60ea74af483a281e7cbba436dbcd912b7568f86c4310865c1100e0e42b6b41'),('112',K/'e2_latest_closed112_frozen_source_CPU_v1/E2_actual_latest_closed112.pt','ca6fc2662d5bfe4d33ad63b370389504961a3c2500b4b476c1c527b17b12b2be')];means={};index=[]
 with torch.inference_mode():
  for name,path,sha in sources:
   assert H(path)==sha;sd=torch.load(path,map_location='cpu',weights_only=False)['actor_state_dict'];assert len(sd)==9 and all(torch.isfinite(v).all() for v in sd.values());flat=obs.reshape(-1,35);chunks=[]
   for start in range(0,len(flat),4096):
    y=torch.from_numpy(flat[start:start+4096].copy())
    for layer in (0,2,4,6):
     y=torch.nn.functional.linear(y,sd[f'mlp.{layer}.weight'],sd[f'mlp.{layer}.bias'])
     if layer!=6:y=torch.nn.functional.elu(y)
    chunks.append(y.numpy().copy())
   means[name]=np.concatenate(chunks).reshape(1500,88,6);assert np.isfinite(means[name]).all();index.append(dict(source_label=name,path=str(path),bytes=path.stat().st_size,SHA=sha,stored_distribution_std_param=sd['distribution.std_param'].tolist()))
 assert np.allclose(means['112'],actual,atol=1e-4,rtol=3e-5);masks={str(sign):obs[...,2]==sign*4. for sign in (1,-1)};stats={}
 for name,mean in means.items():
  groups={}
  for sign,mask in masks.items():
   values=mean[mask];delta=np.clip(values,-6,6)-np.clip(means['112'][mask],-6,6);groups[sign]=dict(recorded_input_rows=int(mask.sum()),conditional_raw_action_mean=values.mean(0).tolist(),conditional_abs_raw_action_mean=np.abs(values).mean(0).tolist(),conditional_clipped_delta_vs112_mean=delta.mean(0).tolist(),conditional_clipped_delta_vs112_RMS=np.sqrt(np.mean(delta**2,axis=0)).tolist(),raw_at_or_beyond6_fraction=(np.abs(values)>=6).mean(0).tolist())
  stats[name]=groups
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 report=dict(epoch=time.time(),passed_CPU_diagnostic_only=True,recorded112_input_file=row,sources=index,same_recorded_observation_conditional_network_statistics=stats,source112_reconstruction_max_abs_error=float(np.max(np.abs(means['112']-actual))),no_live_actor_sampling_RNG_optimizer_or_GPU_calls=True,no_model_or_STD_mutation=True,no_counterfactual_closed_loop_physics_or_qualification_claim=True,conditional_actions_do_not_identify_unique_regression_cause=True,original_frozen_source101_22_source105_0_source112_1_of64_preserved=True,E2_new_paid_learning_remains_held=True,next_requires_actual_source_command_reward_effective_config_and_control_frame_review_not_blind_PPO=True)
 with (R/'E2_SOURCE101105112_SAME_OBSERVATION_ACTOR_MEAN_STD_CPU_DIAGNOSTIC_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(CPU_diagnostic=True,all_same_recorded_observations=True,STD_parameters={r['source_label']:r['stored_distribution_std_param'] for r in index},112_reconstruction_max=report['source112_reconstruction_max_abs_error'],not_a_rollout_or_causal_proof=True)),flush=True)
if __name__=='__main__':main()
