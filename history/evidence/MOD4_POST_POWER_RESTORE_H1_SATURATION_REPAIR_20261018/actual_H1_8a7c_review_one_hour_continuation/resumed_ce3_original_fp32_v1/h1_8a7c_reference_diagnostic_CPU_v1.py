"""All-row fixed references; diagnostics cannot select or grant a passing protocol."""
import torch,numpy as np
def forward(sd,x,dtype):
 y=torch.from_numpy(x).to(dtype=dtype)
 for i in (0,2,4,6):
  y=torch.nn.functional.linear(y,sd[f'mlp.{i}.weight'].to(dtype=dtype),sd[f'mlp.{i}.bias'].to(dtype=dtype))
  if i<6:y=torch.nn.functional.elu(y)
 return y.numpy()
def compare_references(sd,x,actual,original_max):
 n=len(x);assert x.shape==(n,35) and actual.shape==(n,6)
 td=forward(sd,x,torch.float64);nd=x.astype(np.float64)
 for i in (0,2,4,6):
  nd=nd@sd[f'mlp.{i}.weight'].double().numpy().T+sd[f'mlp.{i}.bias'].double().numpy()
  if i<6:
   neg=nd<0;nd[neg]=np.expm1(nd[neg])
 percontrol=np.concatenate([forward(sd,x[k:k+80],torch.float32) for k in range(0,n,80)])
 f32=forward(sd,x,torch.float32);e=np.abs(actual.astype(np.float64)-f32.astype(np.float64));t=np.abs(actual.astype(np.float64)-td);u=np.abs(actual.astype(np.float64)-nd)
 assert np.isfinite(td).all() and np.isfinite(nd).all() and abs(float(e.max())-original_max)<1e-12 and not torch.cuda.is_initialized()
 return dict(rows=n,original_fixed_FP32_allrows_max=float(e.max()),original_over_bound_rows=int((e>1e-4).any(1).sum()),original_per_axis_max=e.max(0).tolist(),original_over_bound_control_env_axis_indices=np.argwhere(e>1e-4).tolist(),actual_raw_absmax=float(np.abs(actual).max()),FP32_percontrol80_diagnostic_max=float(np.abs(actual-percontrol).max()),Torch64_diagnostic_allrows_max=float(t.max()),NumPy64_diagnostic_allrows_max=float(u.max()),dual64_cross_allrows_max=float(abs(td-nd).max()),all_reference_results_diagnostic_only_not_admission=True,no_rowwise_or_posthoc_reference_selection_for_pass=True,no_original_absolute_bound_change=True)
