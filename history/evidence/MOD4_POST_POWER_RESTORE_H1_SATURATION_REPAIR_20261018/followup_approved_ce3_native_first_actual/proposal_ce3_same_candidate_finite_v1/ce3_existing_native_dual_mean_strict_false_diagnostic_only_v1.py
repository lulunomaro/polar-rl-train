"""Readonly CPU actor reference. Original F32 GPU policy and absolute1e-4 bound are unchanged."""
import numpy as np
import torch
def audit_saved_mean(sd,observations,saved):
 assert observations.ndim==2 and observations.shape[1]==35 and observations.dtype==np.float32
 assert saved.shape==(len(observations),6) and saved.dtype==np.float32 and np.isfinite(observations).all() and np.isfinite(saved).all()
 maxima=dict(torch64_maxabs=0.,numpy64_maxabs=0.,reference_cross_maxabs=0.,original_fp32_maxabs=0.)
 with torch.no_grad():
  for start in range(0,len(observations),4096):
   obs=observations[start:start+4096];actual=saved[start:start+4096];f32=torch.from_numpy(obs);t=f32.double();n=obs.astype(np.float64)
   for k in (0,2,4,6):
    w=sd[f'mlp.{k}.weight'];b=sd[f'mlp.{k}.bias'];assert w.dtype==b.dtype==torch.float32 and w.device.type==b.device.type=='cpu'
    f32=torch.nn.functional.linear(f32,w,b);t=torch.nn.functional.linear(t,w.double(),b.double());n=n@w.numpy().astype(np.float64).T+b.numpy().astype(np.float64)
    if k<6:
     f32=torch.nn.functional.elu(f32);t=torch.nn.functional.elu(t);neg=n<0;n[neg]=np.expm1(n[neg])
   for key,value in [('torch64_maxabs',abs(t.numpy()-actual).max()),('numpy64_maxabs',abs(n-actual).max()),('reference_cross_maxabs',abs(t.numpy()-n).max()),('original_fp32_maxabs',abs(f32.numpy()-actual).max())]:maxima[key]=max(maxima[key],float(value))
 assert maxima['reference_cross_maxabs']<=1e-10
 maxima['strict_same_absolute1e4_pass']=bool(maxima['torch64_maxabs']<=1e-4 and maxima['numpy64_maxabs']<=1e-4)
 maxima['diagnostic_only_never_admission']=True
 return maxima
