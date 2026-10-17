"""Diagnose saved full-row raw-mean failure; never substitutes a weaker H1 gate."""
from pathlib import Path
import os,json,time,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import numpy as np,torch
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'frozen_public4_final_linux_v1/payload'

def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();j=json.loads((R/'LINUX_GPU1_PUBLIC4FINAL_FULL1500_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());row=next(x for x in j['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'))
 with np.load(row['local_path'],allow_pickle=False) as z:obs=z['policy_obs'].copy();gpu=z['raw_actor_action'].copy();done=z['terminated']|z['truncated'];modes=z['H1_public_request'].copy()
 source=Q/'source/H1_public4_finite_final.pt';ck=torch.load(source,map_location='cpu',weights_only=False);sd=ck['actor_state_dict'];S,N,_=obs.shape;flat=obs.reshape(-1,35);actual=gpu.reshape(-1,6)
 def forward(batch,dtype):
  result=[]
  with torch.no_grad():
   for start in range(0,len(flat),batch):
    y=torch.from_numpy(flat[start:start+batch]).to(dtype)
    for i in (0,2,4,6):
     y=torch.nn.functional.linear(y,sd[f'mlp.{i}.weight'].to(dtype),sd[f'mlp.{i}.bias'].to(dtype))
     if i<6:y=torch.nn.functional.elu(y)
    result.append(y.numpy())
  return np.concatenate(result)
 fp32=forward(4096,torch.float32);small=forward(N,torch.float32);fp64=forward(4096,torch.float64);err=abs(fp32-actual).reshape(S,N,6);first=np.where(done.any(0),done.argmax(0),S);valid=np.arange(S)[:,None]<first[None,:]
 masks={'all_rows':np.ones((S,N),bool),'before_first_failure':valid,'first_failed_controls':np.arange(S)[:,None]==first[None,:],'after_first_failure':np.arange(S)[:,None]>first[None,:],'normal_before_first_failure':valid&~modes,'public4_before_first_failure':valid&modes}
 groups={k:dict(rows=int(v.sum()),raw_fp32_original4096_maxabs=float(err[v].max()) if v.any() else None,rows_exceed_original1e4=int((err[v].max(-1)>1e-4).sum()) if v.any() else 0) for k,v in masks.items()}
 t,e,a=np.unravel_index(err.argmax(),err.shape);i=t*N+e
 maxrow=dict(control=int(t),environment=int(e),action_component=int(a),is_first_valid_prefix=bool(valid[t,e]),is_failed_control=bool(done[t,e]),public4=bool(modes[t,e]),original_saved_GPU=float(actual[i,a]),original_FP32_CPU4096=float(fp32[i,a]),FP32_CPU_batch80=float(small[i,a]),FP64_CPU=float(fp64[i,a]),policy_obs=obs[t,e].tolist(),maxabs_policy_obs=float(abs(obs[t,e]).max()))
 metrics=dict(original_raw_FP32_CPU4096_vs_saved_GPU_maxabs=float(abs(fp32-actual).max()),FP32_CPU80_vs_saved_GPU_maxabs=float(abs(small-actual).max()),FP64_CPU_vs_saved_GPU_maxabs=float(abs(fp64-actual).max()),FP32_CPU4096_vs_FP64_maxabs=float(abs(fp32-fp64).max()),clipped_FP32_CPU4096_vs_saved_clipped_maxabs=float(abs(np.clip(fp32,-6,6)-np.clip(actual,-6,6)).max()),clipped_FP64_CPU_vs_saved_clipped_maxabs=float(abs(np.clip(fp64,-6,6)-np.clip(actual,-6,6)).max()))
 assert metrics['original_raw_FP32_CPU4096_vs_saved_GPU_maxabs']>1e-4 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),source_SHA=hashlib.sha256(source.read_bytes()).hexdigest(),actual_raw_index=row,original_H1_raw_actor1e4_gate_still_false=True,metrics=metrics,original_FP32_error_partition=groups,worst_original_row=maxrow,alternative_precision_batch_diagnostics_not_replacement_gate_or_qualification=True,no_E3_tolerance_exception_or_model_update_or_GPU_replay=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'PUBLIC4_V2_FINAL_FULL1500_RAW_MEAN_STRICT_FALSE_NUMERICAL_PARTITION_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(original_false_retained=True,metrics=metrics,groups=groups,worst_row={k:v for k,v in maxrow.items() if k!='policy_obs'})))

if __name__=='__main__':main()
