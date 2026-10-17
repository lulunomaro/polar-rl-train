"""Conditional final-model comparison on fixed recorded observations; no robot replay."""
from pathlib import Path
import os,json,time,traceback,sys
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
B=Path(__file__).resolve().parent;R=B/'reports';P=B/'paid_mean_v1';X=B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018';sys.path.insert(0,str(X/'h1_b326_linux4090_v7/payload'))
from h1_frozen_mean35_exact_v1 import FrozenMean35
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();cpu=json.loads((P/'reports/MEAN_REPAIR_P1_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());assert cpu['passed_whole_final_model_local_CPU']
 final=cpu['complete_final'];a=torch.load(P/'payload/h1/job0/source/H1_final10_protected.pt',map_location='cpu',weights_only=False);b=torch.load(final['local_path'],map_location='cpu',weights_only=False);assert b['owned_H1_learning_task']['optimization_candidate']['coefficient']==.001
 c=json.loads((X/'reports/LINUX_GPU1_B326_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());raw=next(x for x in c['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'))
 with np.load(raw['local_path'],allow_pickle=False) as z:obs=z['policy_obs'].copy()
 x=torch.from_numpy(obs.reshape(-1,35));request=obs[...,32].reshape(-1)>0;rows=[];values={}
 for label,ck in [('source_b326',a),('new_complete_final',b)]:
  model=FrozenMean35(ck['actor_state_dict']);before=model.snapshot();mu=model(x).numpy();assert np.isfinite(mu).all() and all(torch.equal(v,model.snapshot()[k]) for k,v in before.items());excess=np.maximum(abs(mu)-6,0);values[label]=mu
  rows.append(dict(label=label,Adam_steps=sorted({int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}),raw_mean0_actual_public4_min_median_max=[float(mu[request,0].min()),float(np.median(mu[request,0])),float(mu[request,0].max())],auxiliary_mean_overflow_loss_on_fixed_recorded_inputs=float(.001*np.mean(excess.astype(np.float64)**2)),per_component_overflow_fraction=(abs(mu)>6).mean(0).tolist(),stored_STD=ck['actor_state_dict']['distribution.std_param'].tolist(),actor9_STD_initial_final_literalexact=True))
 collection=json.loads((P/'reports/MEAN_REPAIR_P1_H1_FINAL_ORIGINAL_COST_EXIT_BOUND_COLLECTION_ACTUAL.json').read_bytes());runtime=next((x['value'] for x in collection['h1']['files'] if x['path'].endswith('/OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json')),None) # Original finite SNAP does not include this diagnostic file; do not invent or fetch it merely for CPU comparison.
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),passed_real_final_model_conditional_source_CPU=True,final_complete_model=final,source_and_final=rows,fixed_input_left_mean_signed_change_min_median_max=[float((values['new_complete_final']-values['source_b326'])[:,0].min()),float(np.median((values['new_complete_final']-values['source_b326'])[:,0])),float((values['new_complete_final']-values['source_b326'])[:,0].max())],overflow_loss_decreased_on_fixed_inputs=rows[1]['auxiliary_mean_overflow_loss_on_fixed_recorded_inputs']<rows[0]['auxiliary_mean_overflow_loss_on_fixed_recorded_inputs'],actual_runtime_auxiliary_loss_current=runtime,final_runtime_auxiliary_metadata_not_collected_by_original_SNAP=runtime is None,original_V1_StopIteration_retained=True,runtime_current_not_necessarily_same_minibatch_or_update_as_immutable_final=True,no_unique_cause_or_frozen_physical_jump_skill_claim=True,no_RNG_optimizer_GPU_or_checkpoint_mutation=True)
 with (R/'MEAN_REPAIR_FINAL_FIXED_RECORDED_OBSERVATIONS_MODEL_EFFECT_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(final_effect_CPU=True,overflow_loss_before_after=[r['auxiliary_mean_overflow_loss_on_fixed_recorded_inputs'] for r in rows],decreased=out['overflow_loss_decreased_on_fixed_inputs'])),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('FINAL_MODEL_EFFECT_CPU_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_actual_model_change=True),f,indent=2)
  raise
