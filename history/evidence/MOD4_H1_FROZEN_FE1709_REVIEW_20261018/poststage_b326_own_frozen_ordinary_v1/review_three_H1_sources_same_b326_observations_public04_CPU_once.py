"""Conditional actor-source comparison only; no closed-loop counterfactual or reward edit."""
from pathlib import Path
import os,sys,time,json,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'h1_b326_linux4090_v7/payload';sys.path.insert(0,str(Q));from h1_frozen_mean35_exact_v1 import FrozenMean35
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();j=json.loads((R/'LINUX_GPU1_B326_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());row=next(r for r in j['files'] if r['relative'].endswith('/retention_full_control_substep_actual.npz'));assert row['twohost_complete_SHA'];cpu=json.loads((R/'H1_B326_LINUX72_120_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_ACTUAL.json').read_bytes());assert cpu['passed_complete_data_and_source_CPU']
 with np.load(row['local_path'],allow_pickle=False) as z:obs=z['policy_obs'].copy();actual=z['raw_actor_action'].copy()
 assert obs.shape==(120,80,35);base=torch.from_numpy(obs.reshape(-1,35));normal=base.clone();normal[:,28:35]=0;normal[:,28]=1;jump=base.clone();jump[:,28:35]=0;jump[:,32]=1
 sources=[('FE1709','h1_fe1709_linux4090_v5/payload/source/H1_fe1709_closed24.pt','fe1709ec470aa4995e0b271947b65135d2e0bd43bec26b28316a451c5f1fa49e',644660),('D723','h1_d723_linux4090_v6/payload/source/H1_d723_closed24.pt','d7238b885879705fa8312758337bf0b6ca1d97c2f906df51b72c27b475e7786a',645140),('B326','h1_b326_linux4090_v7/payload/source/H1_b326_closed24.pt','b32656cf3bfec37cef4ccfcbe06b6ce421054194f8ad627425e367d67240ccce',645620)];rows=[];means={};request=obs[...,32].reshape(-1)>0
 for label,path,sha,step in sources:
  p=B/path;ck=torch.load(p,map_location='cpu',weights_only=False);assert ck['owned_H1_completed_updates']==24 and len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and {int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}=={step};model=FrozenMean35(ck['actor_state_dict']);before=model.snapshot();mu=model(base).numpy();zero=model(normal).numpy();four=model(jump).numpy();clipped=np.clip(mu,-6,6);dz=np.clip(four,-6,6)-np.clip(zero,-6,6);assert all(torch.equal(before[k],model.snapshot()[k]) for k in before);means[label]=mu
  reconstruction=None
  if label=='B326':reconstruction=float(abs(mu-actual.reshape(-1,6)).max());assert reconstruction<=1e-4
  rows.append(dict(source=label,path=str(p),source_SHA_from_prior_complete_model_CPU_and_immutable_manifest=sha,actual_Adam=step,source_closed24=True,stored_STD=ck['actor_state_dict']['distribution.std_param'].tolist(),raw_action_min=np.min(mu,axis=0).tolist(),raw_action_max=np.max(mu,axis=0).tolist(),actual_observation_raw_clip6_fraction=np.mean(abs(mu)>=6,axis=0).tolist(),actual_request_observation_raw_clip6_fraction=np.mean(abs(mu[request])>=6,axis=0).tolist(),conditional_public4_minus0_clipped_action_abs_median=np.median(abs(dz),axis=0).tolist(),conditional_public4_minus0_clipped_action_signed_mean=np.mean(dz,axis=0).tolist(),conditional_public4_minus0_clipped_action_nonzero_rows_per_component=(abs(dz)>1e-6).sum(0).tolist(),B326_saved_action_reconstruction_maxabs=reconstruction,all_actor9_STD_initial_final_literalexact=True))
 comparisons={a+'_vs_'+b:dict(raw_mean_abs_median=np.median(abs(means[a]-means[b]),axis=0).tolist(),clipped_abs_median=np.median(abs(np.clip(means[a],-6,6)-np.clip(means[b],-6,6)),axis=0).tolist()) for a,b in [('FE1709','D723'),('D723','B326')]}
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_conditional_actor_source_CPU=True,recorded_observations_source='B326 own Linux native120, actual120x80x35',raw_actual_path=row['path'],raw_SHA=row['SHA'],no_old_remote_PT_or_raw_download_or_rehash=True,observations_actual_public_mode4_rows=int(request.sum()),source_rows=rows,same_actual_observations_between_sources=comparisons,only_public_onehot0or4_changed_in_separate_CPU_input=True,other28_observation_components_literalexact=True,no_closed_loop_counterfactual_physics_or_skill_or_unique_cause_claim=True,no_reward_LR_STD_threshold_or_checkpoint_mutation=True,RNG_unchanged0CUDA0optimizer=True)
 with (R/'H1_FE1709_D723_B326_SAME_B326_OBSERVATIONS_PUBLIC04_CONDITIONAL_ACTOR_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(conditional_CPU=True,public_mode4_rows=int(request.sum()),B326_reconstruction=rows[-1]['B326_saved_action_reconstruction_maxabs'],all_three_sources_respond_to_public_mode=all(any(n>0 for n in r['conditional_public4_minus0_clipped_action_nonzero_rows_per_component']) for r in rows))),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('H1_PUBLIC04_CONDITIONAL_ACTOR_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_checkpoint_edit=True),f,indent=2)
  raise
