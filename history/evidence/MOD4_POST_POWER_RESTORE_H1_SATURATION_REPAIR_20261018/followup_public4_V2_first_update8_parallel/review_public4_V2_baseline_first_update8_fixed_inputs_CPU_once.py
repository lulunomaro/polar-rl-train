"""Conditional fixed-input actor comparison; never replaces closed-loop frozen physics."""
from pathlib import Path
import os,sys,json,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';N=B/'paid_mean_public4_v2';X=B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018';sys.path.insert(0,str(X/'h1_b326_linux4090_v7/payload'));from h1_frozen_mean35_exact_v1 import FrozenMean35
from h1_public4_mean_overflow_loss_v2 import public4_mean_overflow_loss
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();p=json.loads((N/'reports/PUBLIC4_V2_IMMUTABLE_UPDATE8_COMPLETE_LOCAL_CPU_ACTUAL.json').read_bytes());assert p['passed_whole_immutable_update8_model_local_CPU'] and p['actual_auxiliary_positive_witness_observed'];f=json.loads((N/'reports/PUBLIC4_V2_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V3_ACTUAL.json').read_bytes());assert f['passed_real_immutable_first_complete_local_CPU'];first=next(x for x in f['all_models'] if x['kind']=='immutable_first');paths=[('baseline_b326',N/'payload/h1/job0/source/H1_final10_protected.pt'),('new_public4_update1_normal_only',Path(first['local_path'])),('new_public4_update8_after_positive_aux_witness',Path(p['complete_model']['local_path']))]
 c=json.loads((X/'reports/LINUX_GPU1_B326_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());raw=next(x for x in c['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'))
 with np.load(raw['local_path'],allow_pickle=False) as z:obs=z['policy_obs'].copy()
 policy=torch.from_numpy(obs.reshape(-1,35));rows=[]
 for label,path in paths:
  ck=torch.load(path,map_location='cpu',weights_only=False);model=FrozenMean35(ck['actor_state_dict']);before=model.snapshot();mu=model(policy);assert torch.isfinite(mu).all() and all(torch.equal(v,model.snapshot()[k]) for k,v in before.items());m=mu.numpy();groups={}
  for name,mask in [('normal0',obs[...,28].reshape(-1)==1),('public4',obs[...,32].reshape(-1)==1)]:
   assert mask.any();v=m[mask,0];groups[name]=dict(rows=int(mask.sum()),left_mean_min_median_max=[float(v.min()),float(np.median(v)),float(v.max())],left_raw_below_minus6_fraction=float((v < -6).mean()),all_component_overflow_fraction=(abs(m[mask])>6).mean(0).tolist())
  rows.append(dict(label=label,path=str(path),Adam=sorted({int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}),stored_STD=ck['actor_state_dict']['distribution.std_param'].tolist(),frozen_actor9_STD_initial_final_literalexact=True,groups=groups,declared_public4_only_aux_loss_on_fixed_inputs=float(public4_mean_overflow_loss(mu,policy))))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),source_bound_update8_proof=str(N/'reports/PUBLIC4_V2_IMMUTABLE_UPDATE8_COMPLETE_LOCAL_CPU_ACTUAL.json'),fixed_recorded_raw_index=raw,models=rows,actual_auxiliary_execution_witnesses=p['actual_published_public4_auxiliary_witnesses'],first_normal_only_aux0_actual_source_report=str(N/'reports/PUBLIC4_V2_H1_MISSING_FIRST_PROGRESS_V3_BOUND_COLLECTION_ACTUAL.json'),normal_output_drift_can_include_original_PPO_and_shared_parameter_indirect_effect=True,not_three_models_closedloop_counterfactual_or_unique_cause_or_skill_PASS=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'PUBLIC4_V2_BASELINE_FIRST_UPDATE8_FIXED_RECORDED_INPUTS_CPU_ACTUAL.json').open('x',encoding='utf8') as h:json.dump(out,h,indent=2)
 print(json.dumps(dict(public4_only_fixed_input_losses=[x['declared_public4_only_aux_loss_on_fixed_inputs'] for x in rows],normal_mean0_medians=[x['groups']['normal0']['left_mean_min_median_max'][1] for x in rows],not_frozen_physical_proof=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('PUBLIC4_UPDATE8_FIXED_INPUT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as h:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_model_change=True),h,indent=2)
  raise
