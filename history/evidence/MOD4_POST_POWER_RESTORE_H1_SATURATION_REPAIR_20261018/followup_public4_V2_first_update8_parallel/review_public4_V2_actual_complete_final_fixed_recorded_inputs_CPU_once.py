"""Conditional actor comparison on recorded observations, never closed-loop proof."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
B=Path(__file__).resolve().parent;R=B/'reports';N=B/'paid_mean_public4_v2';X=B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018'
sys.path[:0]=[str(X/'h1_b326_linux4090_v7/payload'),str(N/'payload/h1/job0/runtime/isaac/mod4')]
from h1_frozen_mean35_exact_v1 import FrozenMean35
from h1_public4_mean_overflow_loss_v2 import public4_mean_overflow_loss
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 p=json.loads((N/'reports/PUBLIC4_V2_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());assert p['passed_whole_final_model_local_CPU']
 firstproof=json.loads((N/'reports/PUBLIC4_V2_H1_IMMUTABLE_FIRST_COMPLETE_LOCAL_CPU_V3_ACTUAL.json').read_bytes());assert firstproof['passed_real_immutable_first_complete_local_CPU'];first=next(x for x in firstproof['all_models'] if x['kind']=='immutable_first')
 old=json.loads((B/'paid_mean_v1/reports/MEAN_REPAIR_P1_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json').read_bytes());assert old['passed_whole_final_model_local_CPU']
 paths=[('protected_b326',N/'payload/h1/job0/source/H1_final10_protected.pt','b32656cf3bfec37cef4ccfcbe06b6ce421054194f8ad627425e367d67240ccce'),('global_aux_failed_final',Path(old['complete_final']['local_path']),old['complete_final']['SHA']),('new_public4_normal_only_first',Path(first['local_path']),first['SHA']),('new_public4_complete_final',Path(p['complete_final']['local_path']),p['complete_final']['SHA'])]
 collection=json.loads((X/'reports/LINUX_GPU1_B326_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());raw=next(x for x in collection['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'))
 with np.load(raw['local_path'],allow_pickle=False) as z:obs=z['policy_obs'].copy()
 policy=torch.from_numpy(obs.reshape(-1,35));rows=[]
 for label,path,sha in paths:
  assert H(path)==sha
  ck=torch.load(path,map_location='cpu',weights_only=False);model=FrozenMean35(ck['actor_state_dict']);before=model.snapshot();mu=model(policy);assert torch.isfinite(mu).all() and all(torch.equal(v,model.snapshot()[k]) for k,v in before.items());m=mu.numpy();groups={}
  for name,mask in [('normal0',obs[...,28].reshape(-1)==1),('public4',obs[...,32].reshape(-1)==1)]:
   assert mask.any();v=m[mask,0];groups[name]=dict(rows=int(mask.sum()),left_mean_min_median_max=[float(v.min()),float(np.median(v)),float(v.max())],left_raw_below_minus6_fraction=float((v < -6).mean()),all_component_overflow_fraction=(abs(m[mask])>6).mean(0).tolist())
  rows.append(dict(label=label,path=str(path),bytes=path.stat().st_size,SHA=sha,Adam=sorted({int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}),stored_STD=ck['actor_state_dict']['distribution.std_param'].tolist(),frozen_actor9_STD_initial_final_literalexact=True,groups=groups,declared_public4_only_aux_loss_on_fixed_inputs=float(public4_mean_overflow_loss(mu,policy))))
 assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),actual_final_proof=str(N/'reports/PUBLIC4_V2_H1_COMPLETE_FINAL_FULL_CPU_COST_EXIT_ACTUAL.json'),fixed_recorded_raw_index=raw,models=rows,normal_first_24controls_aux0=True,not_four_models_closedloop_counterfactual_or_unique_cause_or_skill_PASS=True,normal_drift_can_include_PPO_and_shared_parameter_indirect_effect=True,no_model_update_RNG_CUDA_optimizer=True)
 with (R/'PUBLIC4_V2_ACTUAL_BASELINE_GLOBAL_FINAL_NORMAL_FIRST_PUBLIC4_FINAL_FIXED_INPUTS_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(public4_fixed_input_losses={r['label']:r['declared_public4_only_aux_loss_on_fixed_inputs'] for r in rows},normal_mean0_medians={r['label']:r['groups']['normal0']['left_mean_min_median_max'][1] for r in rows},not_physical_proof=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('PUBLIC4_FINAL_FIXED_INPUT_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_model_mutation=True),f,indent=2)
  raise
