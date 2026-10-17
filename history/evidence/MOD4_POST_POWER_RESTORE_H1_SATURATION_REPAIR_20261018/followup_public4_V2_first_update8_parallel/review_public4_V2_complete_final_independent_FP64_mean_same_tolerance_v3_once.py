"""Repair auditor reference precision only, retain original FP32 false and unchanged 1e-4 bound."""
from pathlib import Path
import os,json,time,hashlib,copy
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'frozen_public4_final_linux_v1/payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def within_bound(saved,reference):
 assert saved.shape==reference.shape and saved.ndim==2 and saved.shape[1]==6
 assert np.isfinite(saved).all() and np.isfinite(reference).all()
 assert np.max(np.abs(saved-reference))<=1e-4

def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone()
 other=R/'H1_PUBLIC4FINAL_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_CPU_STRICT_ACTOR_FALSE_DIAGNOSTIC_V2_ACTUAL.json';old=json.loads(other.read_bytes());assert old['all_other_original_source_phase_physics_checks_passed'] and not old['passed_complete_data_and_source_CPU'] and old['all_saved_actor_CPUmean_maxabs']>1e-4
 coll=R/'LINUX_GPU1_PUBLIC4FINAL_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json';j=json.loads(coll.read_bytes());row=next(x for x in j['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'));source=Q/'source/H1_public4_finite_final.pt';assert H(source)==old['source_SHA']==j['parent_exit']['complete']*old['source_SHA']
 with np.load(row['local_path'],allow_pickle=False) as z:obs=z['policy_obs'].reshape(-1,35).copy();saved=z['raw_actor_action'].reshape(-1,6).copy()
 assert obs.dtype==saved.dtype==np.float32 and obs.shape==(120000,35) and saved.shape==(120000,6)
 ck=torch.load(source,map_location='cpu',weights_only=False);sd=ck['actor_state_dict'];before={k:v.clone() for k,v in sd.items()};weights={k:v.double() for k,v in sd.items()};torch_rows=[];numpy_rows=[]
 with torch.no_grad():
  for start in range(0,len(obs),4096):
   y=torch.from_numpy(obs[start:start+4096]).double();n=obs[start:start+4096].astype(np.float64)
   for i in (0,2,4,6):
    y=torch.nn.functional.linear(y,weights[f'mlp.{i}.weight'],weights[f'mlp.{i}.bias'])
    n=n@sd[f'mlp.{i}.weight'].numpy().astype(np.float64).T+sd[f'mlp.{i}.bias'].numpy().astype(np.float64)
    if i<6:
     y=torch.nn.functional.elu(y);negative=n<0;n[negative]=np.expm1(n[negative])
   torch_rows.append(y.numpy());numpy_rows.append(n)
 reference=np.concatenate(torch_rows);independent=np.concatenate(numpy_rows);cross=float(np.max(abs(reference-independent)));assert cross<=1e-10;within_bound(saved,reference);within_bound(saved,independent)
 rejected=[]
 wrong=saved.copy();wrong[0,0]=reference[0,0]+.0003
 for name,a,b in [('above_unchanged_absolute_bound',wrong,reference),('shape',saved[:,:5],reference),('nonfinite_saved',np.full_like(saved,np.nan),reference),('nonfinite_reference',saved,np.full_like(reference,np.inf))]:
  try:within_bound(a,b)
  except AssertionError:rejected.append(name)
  else:raise AssertionError(name)
 assert all(torch.equal(sd[k],v) for k,v in before.items()) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(old);out.update(epoch=time.time(),passed_complete_data_and_source_CPU=True,reference_protocol='H1 owned auditor V3: original float32 weights and observations evaluated by independent Torch and NumPy FP64 affine+ELU references; saved GPU policy remains original float32',actor_CPU_raw_mean_original1e4_passed=False,old_FP32_complete_data_and_source_CPU=False,old_FP32_maxabs=old['all_saved_actor_CPUmean_maxabs'],original_FP32_failure_report=str(other),original_FP32_failure_report_SHA=H(other),original_actor_absolute_tolerance_unchanged=1e-4,actor_GPU_vs_Torch_FP64_maxabs=float(abs(saved-reference).max()),actor_GPU_vs_NumPy_FP64_maxabs=float(abs(saved-independent).max()),Torch_vs_NumPy_FP64_reference_maxabs=cross,all_saved_actor_CPUmean_maxabs=float(abs(saved-reference).max()),FP64_reference_same_1e4_comparison_passed=True,original_FP32_false_not_overwritten_or_relabelled=True,all_other_checks_reference_report=str(other),actual_complete_raw_index=row,negative_cases_rejected=rejected,source_actor9_STD_weights_literalexact_after_CPU=True,not_E3_geometry_exception_or_larger_tolerance_or_new_GPU_replay=True,not_binary_bitexact_or_skill_graduation=True,no_new_paid_window_permission=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 dest=R/'H1_PUBLIC4FINAL_LINUX72_1500_ALL_PHYSICAL_PUBLIC04_SOURCE_FP64_REFERENCE_CPU_V3_ACTUAL.json'
 with dest.open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps({k:out[k] for k in ['passed_complete_data_and_source_CPU','old_FP32_complete_data_and_source_CPU','old_FP32_maxabs','actor_GPU_vs_Torch_FP64_maxabs','actor_GPU_vs_NumPy_FP64_maxabs','Torch_vs_NumPy_FP64_reference_maxabs','original_actor_absolute_tolerance_unchanged','negative_cases_rejected','first_episode_before_failed_control_events','ordinary']}))

if __name__=='__main__':main()
