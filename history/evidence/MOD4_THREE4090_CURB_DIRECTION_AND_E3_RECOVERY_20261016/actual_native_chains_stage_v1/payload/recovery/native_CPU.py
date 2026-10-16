"""Independent CPU consumption of complete new recovery native rows, no GPU replay."""
from pathlib import Path
import argparse,os,json,time,hashlib
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
torch.set_num_threads(4);B=Path(__file__).resolve().parent;J=B/'job0';O=J/'native'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.shape==b.shape and a.dtype==b.dtype and a.contiguous().numpy().tobytes()==b.contiguous().numpy().tobytes()
 if isinstance(a,dict):return a.keys()==b.keys() and all(exact(v,b[k]) for k,v in a.items())
 if isinstance(a,(list,tuple)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def clearance(pos,q,shapes):
 xyz=q[...,:3].astype(np.float64);qw=q[...,3:4].astype(np.float64);basis=np.zeros_like(xyz);basis[...,2]=1;localz=basis+2*np.cross(xyz,np.cross(xyz,basis)-qw*basis);values=[]
 for s in shapes:
  rz=localz[...,s['body_index'],:];r=rz@np.asarray(s['linear_body_from_shape']);center=pos[...,s['body_index'],2]+np.einsum('...i,i->...',rz,np.asarray(s['origin_body_m']));kind=s['type'];norm=np.linalg.norm(r,axis=-1)
  if kind=='Cube':v=center-abs(r).sum(-1)*s['size']*.5
  elif kind in ('Capsule','Cylinder'):
   axial=abs(r[...,s['axis']]);v=center-axial*s['height']*.5-s['radius']*(norm if kind=='Capsule' else np.sqrt(np.maximum(0,norm**2-axial**2)))
  elif kind=='Sphere':v=center-norm*s['radius']
  elif kind=='Mesh':v=center+(r@np.asarray(s['points']).T).min(-1)
  else:raise ValueError(kind)
  values.append(v)
 return np.stack(values,-1)
def main():
 p=argparse.ArgumentParser();p.add_argument('--job',type=int);p.parse_args();task=json.loads((J/'TASK.json').read_bytes());v=json.loads((O/'NATIVE336_COMPLETE.json').read_bytes());assert v['controls']==336 and v['callbacks']==1344 and v['optimizer_updates']==0;src=J/'source/E0_full_source.pt';assert H(src)==task['source_SHA'];s=torch.load(src,map_location='cpu',weights_only=False);ck=torch.load(O/'own_native336.pt',map_location='cpu',weights_only=False)
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(s[k],ck[k])
 assert 'E3_public_recovery_state' in ck and {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={639560};ref=json.loads((O/'GEOMETRY_AND_RESET_ACTUAL.json').read_bytes());wheel=[ref['contact_names'].index(n) for n in ('left_wheel','right_wheel')];n=0;err=geom=force=0.;last=done=None;modes=[0]*7;ordinary=0
 for row in v['chunks']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
  with np.load(p,allow_pickle=False) as z:d={k:z[k] for k in z.files}
  for k,a in d.items():
   if a.dtype.kind in 'fc':assert np.isfinite(a).all(),k
  x=d['policy35'];assert x.shape[1:]==(20000,35);assert np.array_equal(d['executed6'],np.clip(d['raw6'],-6,6));assert d['mimic'].max()<=.01;assert np.array_equal(x[:,:,28:35].sum(-1),np.ones_like(x[:,:,0])) and not x[:,:,29:31].any() and not x[:,:,32:35].any()
  force=max(force,float(abs(d['physical_full31_force'][:,:,:,wheel,:]-d['physical_wheel_force']).max()));assert force<=.1;load=np.maximum(d['physical_wheel_force'][...,2],0).sum(1)*np.float32(.0025)/np.float32(.01);assert abs(load-d['impulse']/np.float32(.01)).max()<=.1
  geom=max(geom,float(abs(clearance(d['witness_body_pos'],d['witness_body_quat_xyzw'],ref['shapes'])-d['witness_clear34']).max()));assert geom<=1e-6
  for i in range(len(x)):
   if last is not None:
    previous=last.copy();previous[done]=0;assert np.array_equal(x[i,:,22:28],previous)
   last=np.clip(d['raw6'][i],-6,6);done=d['done'][i].astype(bool)
  y=torch.from_numpy(x.reshape(-1,35));sd=s['actor_state_dict']
  for i in (0,2,4,6):
   y=torch.nn.functional.linear(y,sd[f'mlp.{i}.weight'],sd[f'mlp.{i}.bias'])
   if i<6:y=torch.nn.functional.elu(y)
  err=max(err,float(abs(y.numpy()-d['raw6'].reshape(-1,6)).max()));assert err<=1e-4;n+=len(x);ordinary+=int(d['done'].sum());modes=[a+int(x[:,:,28+i].sum()) for i,a in enumerate(modes)]
 assert n==336 and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed=True,source_SHA=task['source_SHA'],native_checkpoint_SHA=v['SHA'],controls=336,callbacks=1344,all_actor_rows=336*20000,all_original_core_tensor_bytes_exact=True,all_actor_CPUmean_maxabs=err,CPUvsGPU_not_bitexact=True,full31_wheel_force_maxabs=force,all34_authored_witness_geometry_maxabs=geom,original_mimic_and_closure_guards_not_changed=True,public_mode_sample_counts=modes,ordinary_terminations=ordinary,not_recovery_success_or_PPO=True,zeroCUDA0optimizer=True)
 with (O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json').open('x') as f:json.dump(out,f,indent=2)
 print(json.dumps(out))
if __name__=='__main__':main()
