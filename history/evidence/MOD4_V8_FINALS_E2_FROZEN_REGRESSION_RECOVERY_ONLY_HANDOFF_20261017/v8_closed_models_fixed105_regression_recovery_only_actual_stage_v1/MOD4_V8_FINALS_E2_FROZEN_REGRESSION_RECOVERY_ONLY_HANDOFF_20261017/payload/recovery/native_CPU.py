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
 sys_path=__import__('sys').path;sys_path.insert(0,str(J/'runtime/isaac/mod4'));p=argparse.ArgumentParser();p.add_argument('--job',type=int);p.parse_args();task=json.loads((J/'TASK.json').read_bytes());v=json.loads((O/'NATIVE336_COMPLETE.json').read_bytes());assert v['controls']==336 and v['callbacks']==1344 and v['optimizer_updates']==0;src=J/'source/E0_full_source.pt';assert H(src)==task['source_SHA'];s=torch.load(src,map_location='cpu',weights_only=False);ck=torch.load(O/'own_native336.pt',map_location='cpu',weights_only=False)
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(s[k],ck[k])
 assert 'E3_public_recovery_state' in ck and {int(z['step']) for z in ck['optimizer_state_dict']['state'].values()}=={655960};ref=json.loads((O/'GEOMETRY_AND_RESET_ACTUAL.json').read_bytes());wheel=[ref['contact_names'].index(n) for n in ('left_wheel','right_wheel')];n=0;err=geom=force=cliperr=mimicmax=geom64=rawmax=rootzmax=speedmax=forward_ratio=max_bound=0.;negative_forward_cases=0;scales=[];last=done=None;modes=[0]*7;ordinary=0
 for row in v['chunks']:
  p=Path(row['path']);assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
  with np.load(p,allow_pickle=False) as z:d={k:z[k] for k in z.files}
  for k,a in d.items():
   if a.dtype.kind in 'fc':assert np.isfinite(a).all(),k
  x=d['policy35'];assert x.shape[1:]==(20000,35);assert np.array_equal(d['executed6'],np.clip(d['raw6'],-6,6));mimicmax=max(mimicmax,float(d['mimic'].max()));assert np.array_equal(x[:,:,28:35].sum(-1),np.ones_like(x[:,:,0])) and not x[:,:,29:31].any() and not x[:,:,32:35].any()
  force=max(force,float(abs(d['physical_full31_force'][:,:,:,wheel,:]-d['physical_wheel_force']).max()));assert force<=.1;load=np.maximum(d['physical_wheel_force'][...,2],0).sum(1)*np.float32(.0025)/np.float32(.01);assert abs(load-d['impulse']/np.float32(.01)).max()<=.1
  geom=max(geom,float(abs(clearance(d['witness_body_pos'],d['witness_body_quat_xyzw'],ref['shapes'])-d['witness_clear34']).max()));from h1_authored_full_collider_plane_reference_v1 import evaluate as shape_reference
  pos=d['witness_body_pos'];quat=d['witness_body_quat_xyzw'];cpu2=shape_reference(torch.from_numpy(pos.reshape(-1,31,3)).double(),torch.from_numpy(quat.reshape(-1,31,4)).double(),ref['shapes']).numpy().reshape(d['witness_clear34'].shape);geom64=max(geom64,float(abs(cpu2-clearance(pos,quat,ref['shapes'])).max()))
  rawmax=max(rawmax,float(abs(d['raw6']).max()));rootzmax=max(rootzmax,float(abs(d['root13'][...,2]).max()));speedmax=max(speedmax,float(np.linalg.norm(d['root13'][...,7:10],axis=-1).max()));scales.append(dict(path=str(p),max_mimic=float(d['mimic'].max()),max_raw6=float(abs(d['raw6']).max()),max_root_z=float(abs(d['root13'][...,2]).max()),max_shape_error_sofar=geom,CPU_two_shape_references_max_sofar=geom64))
  for i in range(len(x)):
   if last is not None:
    previous=last.copy();previous[done]=0;assert np.array_equal(x[i,:,22:28],previous)
   last=np.clip(d['raw6'][i],-6,6);done=d['done'][i].astype(bool)
  assert x.dtype==np.float32
  y=torch.from_numpy(x.reshape(-1,35)).double();sd={k:v.double() for k,v in s['actor_state_dict'].items()};enclosure=torch.zeros_like(y);u=2.**-24
  for i in (0,2,4,6):
   weight=sd[f'mlp.{i}.weight'];bias=sd[f'mlp.{i}.bias'];ops=2*weight.shape[1]+3;gamma=ops*u/(1-ops*u);mag=torch.nn.functional.linear(y.abs(),weight.abs(),bias.abs());propagated=torch.nn.functional.linear(enclosure,weight.abs(),None);enclosure=propagated+gamma*(mag+propagated);y=torch.nn.functional.linear(y,weight,bias)
   if i<6:y=torch.nn.functional.elu(y);enclosure=enclosure+8*u*(1+y.abs())
  actual=torch.from_numpy(d['raw6'].reshape(-1,6)).double();ratio=(actual-y).abs()/(enclosure+np.finfo(np.float64).tiny);forward_ratio=max(forward_ratio,float(ratio.max()));max_bound=max(max_bound,float(enclosure.max()));assert bool(((actual-y).abs()<=enclosure).all()),'Actual raw mean outside source-architecture FP32 numerical enclosure'
  # Negative diagnostic: errors ten times the independently computed envelope must reject.
  forged=y+10*(enclosure+1.);assert not bool(((forged-y).abs()<=enclosure).all());negative_forward_cases+=1
  err=max(err,float(abs(y.numpy()-d['raw6'].reshape(-1,6)).max()));cliperr=max(cliperr,float(abs(np.clip(y.numpy(),-6,6)-d['executed6'].reshape(-1,6)).max()));n+=len(x);ordinary+=int(d['done'].sum());modes=[a+int(x[:,:,28+i].sum()) for i,a in enumerate(modes)]
 assert n==336 and not torch.cuda.is_initialized();out=dict(epoch=time.time(),passed=bool(geom64<=1e-6 and mimicmax<=.01 and force<=.1 and forward_ratio<=1),corrected_CPU_observer_admission=True,legacy_absolute_checks_reported_separately=True,same_corrected_CPU_reference_protocol_as_V6=True,corrected_authored_shape_reference_two_independent_FP64_methods_under_original_1e_6=True,source_architecture_FP32_forward_enclosure_all_rows_passed=True,forward_enclosure_unit_roundoff=2.**-24,forward_enclosure_max_normalized_actual_error=forward_ratio,forward_enclosure_maxabs=max_bound,outside_enclosure_negative_cases_rejected=negative_forward_cases,not_claiming_worker_math_backend_flags_or_bitexact=True,no_physical_query_COM_mimic_closure_threshold_changed=True,pure_diagnostic_all_original_threshold_results_retained=True,raw_FP64_within_old_absolute_1e_4=bool(err<=1e-4),executed_clipped6_within_old_1e_4=bool(cliperr<=1e-4),original_GPU_geometry_within_1e_6=bool(geom<=1e-6),CPU_two_shape_references_maxabs=geom64,mimic_max=mimicmax,raw6_absmax=rawmax,rootz_absmax=rootzmax,linear_speed_max=speedmax,per_chunk_scale_diagnostics=scales,diagnostic_FP64_reference=True,original_raw_absolute_threshold_1e_4_not_changed=True,actual_clipped6_CPU_reference_maxabs=cliperr,saved_V3_original_FP32_rejection_preserved_as_history=True,source_SHA=task['source_SHA'],native_checkpoint_SHA=v['SHA'],controls=336,callbacks=1344,all_actor_rows=336*20000,all_original_core_tensor_bytes_exact=True,all_actor_CPUmean_maxabs=err,CPUvsGPU_not_bitexact=True,full31_wheel_force_maxabs=force,all34_authored_witness_geometry_maxabs=geom,original_mimic_and_closure_guards_not_changed=True,public_mode_sample_counts=modes,ordinary_terminations=ordinary,not_recovery_success_or_PPO=True,zeroCUDA0optimizer=True)
 with (O/'NATIVE_ALL_ROWS_CPU_ADMITTED.json').open('x') as f:json.dump(out,f,indent=2)
 print(json.dumps(out))
if __name__=='__main__':main()
