"""Readonly derivative geometry of public4 auxiliary loss; no optimizer or model update."""
from pathlib import Path
import os,sys,json,time,hashlib,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
from h1_public4_mean_overflow_loss_v2 import public4_mean_overflow_loss
B=Path(__file__).resolve().parent;R=B/'reports';N=B/'paid_mean_public4_v2';X=B.parent/'MOD4_H1_FROZEN_FE1709_REVIEW_20261018';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();source=N/'payload/h1/job0/source/H1_final10_protected.pt';assert H(source)=='b32656cf3bfec37cef4ccfcbe06b6ce421054194f8ad627425e367d67240ccce';assert H(B/'h1_public4_mean_overflow_loss_v2.py')==H(N/'payload/h1/job0/runtime/isaac/mod4/h1_public4_mean_overflow_loss_v2.py');ck=torch.load(source,map_location='cpu',weights_only=False);sd=ck['actor_state_dict'];original={k:v.clone() for k,v in sd.items()};names=[f'mlp.{i}.{kind}' for i in (0,2,4,6) for kind in ('weight','bias')];w=[sd[k].clone().requires_grad_(True) for k in names]
 c=json.loads((X/'reports/LINUX_GPU1_B326_NATIVE120_COMPLETE_OR_PENDING_BOUND_COLLECTION_ACTUAL.json').read_bytes());row=next(x for x in c['files'] if x['relative'].endswith('/retention_full_control_substep_actual.npz'))
 with np.load(row['local_path'],allow_pickle=False) as z:normal=torch.from_numpy(z['policy_obs'][99,:8].copy());public=torch.from_numpy(z['policy_obs'][100,:8].copy())
 assert (normal[:,28]==1).all() and (public[:,32]==1).all()
 def forward(x):
  for i in range(4):
   x=torch.nn.functional.linear(x,w[2*i],w[2*i+1])
   if i<3:x=torch.nn.functional.elu(x)
  return x
 mu=forward(public);aux=public4_mean_overflow_loss(mu,public);ga=torch.autograd.grad(aux,w);gn=torch.autograd.grad(forward(normal)[:,0].mean(),w);dot=float(sum((a*b).double().sum() for a,b in zip(ga,gn)));col32_dot=float((ga[0][:,32]*gn[0][:,32]).double().sum());assert not gn[0][:,32].any() and not ga[0][:,28].any() and col32_dot==0
 assert all(torch.equal(v,original[k]) for k,v in sd.items()) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 out=dict(epoch=time.time(),source_SHA=H(source),actual_recorded_input_index=row,normal_control99_env0to7_and_public4_control100_env0to7=True,public4_aux_loss=float(aux.detach()),normal_mean0_derivative_dot_public4_auxiliary_gradient=dot,normal_mean_derivative_dot_only_firstlayer_public4_column_gradient=col32_dot,firstlayer_public4_column_has_zero_normal_output_derivative=True,public4_loss_has_zero_firstlayer_normal0_column_gradient=True,parameter_auxiliary_gradient_norms={k:float(g.norm()) for k,g in zip(names,ga)},shared_parameter_coupling_possible_despite_zero_direct_normal_row_auxiliary_gradient=True,not_actual_optimizer_direction_or_trajectory_or_unique_regression_cause_proof=True,restriction_to_public4_column_not_deployed_or_new_GO_permission=True,original_actor9_STD_literalexact_after_CPU=True,CPU_RNG_unchanged0CUDA0optimizer=True)
 with (R/'PUBLIC4_V2_SOURCE_REAL_NETWORK_AUXILIARY_NORMAL_SHARED_GRADIENT_COUPLING_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(actual_network_derivative_CPU=True,shared_direction_dot=dot,restricted_column_dot=col32_dot,no_checkpoint_or_optimizer_update=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('PUBLIC4_NORMAL_COUPLING_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_optimizer_or_model_mutation=True),f,indent=2)
  raise
