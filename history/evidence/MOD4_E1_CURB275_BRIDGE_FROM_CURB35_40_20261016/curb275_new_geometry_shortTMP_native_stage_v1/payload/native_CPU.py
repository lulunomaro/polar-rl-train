"""Separate process CPU-only admission of each new GPU native, no learner step."""
from pathlib import Path
import os,argparse,hashlib,json,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
torch.set_num_threads(4)
B=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.contiguous().numpy().tobytes()==b.contiguous().numpy().tobytes()
 if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(v,b[k]) for k,v in a.items())
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def main():
 p=argparse.ArgumentParser();p.add_argument('--job',type=int,required=True);a=p.parse_args();j=B/('job'+str(a.job));out=j/'native20k_then_production';report=out/'INDEPENDENT_NATIVE_CPU_ADMITTED.json';assert not report.exists();task=json.loads((j/'TASK_CURB35.json').read_bytes());v=json.loads((out/'NATIVE144_COMPLETE.json').read_bytes());assert v['controls']==144 and v['callbacks']==576 and v['updates']==0 and v['no_optimizer_updates'];src=j/'source/CURB140.pt';assert H(src)==task['source_SHA'];source=torch.load(src,map_location='cpu',weights_only=False);ckp=Path(v['path']);assert H(ckp)==v['SHA'];ck=torch.load(ckp,map_location='cpu',weights_only=False)
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(source[k],ck[k]),k
 assert ck['E1_terrain_state']['CURB_height_m']==.0275 and source['E1_terrain_state']['CURB_height_m']==.035
 assert ck['E1_terrain_state']['CURB_strip_width_m']==source['E1_terrain_state']['CURB_strip_width_m']==.15
 assert len(ck['optimizer_state_dict']['state'])==17 and {int(s['step']) for s in ck['optimizer_state_dict']['state'].values()}=={task['source_Adamstep']}
 def finite(x):
  if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for z in x.values():finite(z)
  elif isinstance(x,(tuple,list)):
   for z in x:finite(z)
 finite(ck);n=0;last=None;done=None;err=0.
 for r in v['chunks']:
  q=Path(r['path']);assert q.stat().st_size==r['bytes'] and H(q)==r['SHA']
  with np.load(q,allow_pickle=False) as z:d={k:z[k] for k in z.files}
  for k,x in d.items():
   if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
  assert np.array_equal(d['executed6'],np.clip(d['raw6'],-6,6));load=np.maximum(d['physical_wheel_force'][...,2],0).sum(1)*np.float32(.0025)/np.float32(.01);assert float(abs(load-d['impulse']/np.float32(.01)).max())<=.1
  x=d['policy35'];assert x.shape[1:]==(20000,35);S=x.shape[0];expected=np.zeros_like(x[:,:,28:35]);expected[:,:,0]=1;assert np.array_equal(x[:,:,28:35],expected);assert d['independent_query_error'].max()<=1e-6 and d['mimic'].max()<=.01
  for i in range(S):
   if last is not None:
    previous=last.copy();previous[done]=0;assert np.array_equal(x[i,:,22:28],previous)
   last=np.clip(d['raw6'][i],-6,6);done=d['done'][i].astype(bool)
  y=torch.from_numpy(x.reshape(-1,35));sd=source['actor_state_dict']
  for i in (0,2,4,6):
   y=torch.nn.functional.linear(y,sd[f'mlp.{i}.weight'],sd[f'mlp.{i}.bias'])
   if i<6:y=torch.nn.functional.elu(y)
  err=max(err,float(abs(y.numpy()-d['raw6'].reshape(-1,6)).max()));assert err<=1e-4;n+=S
 assert n==144 and not torch.cuda.is_initialized();report.write_text(json.dumps(dict(epoch=time.time(),passed=True,job=a.job,source_SHA=task['source_SHA'],native_checkpoint_SHA=v['SHA'],warmup_controls=24,timed_controls=120,controls=n,callbacks=576,source_actor9_critic8_STD_all17Adam_literal_bytes_exact=True,all_native_controls_finite_query_history_reset_normal35_CPU_checked=True,explicit_source35_new27p5_geometry_bridge_validated=True,all_native_actor_CPUmeans_maxabs=err,CPUvsGPU_not_bitexact=True,new_task_scope_explicit=True,CPU_optimizer_updates=0),indent=2));print(report.read_text(),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (B/('NATIVE_CPU_GATE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_optimizer_or_CUDA=True),indent=2));raise
