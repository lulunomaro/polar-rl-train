"""All saved native rows; original actor mean/action/reset and physical impulse."""
from pathlib import Path
import os,argparse,hashlib,json,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,numpy as np
torch.set_num_threads(4);B=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.contiguous().numpy().tobytes()==b.contiguous().numpy().tobytes()
 if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(v,b[k]) for k,v in a.items())
 if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def main():
 p=argparse.ArgumentParser();p.add_argument('--job',type=int,required=True);a=p.parse_args();j=B/('job'+str(a.job));out=j/'native';report=out/'NATIVE_ALL_ROWS_CPU_ADMITTED.json';assert not report.exists();task=json.loads((j/'TASK.json').read_bytes());v=json.loads((out/'NATIVE144_COMPLETE.json').read_bytes());assert v['controls']==144 and v['callbacks']==576
 src=j/'source/E2_final58.pt';assert H(src)==task['source_SHA'];s=torch.load(src,map_location='cpu',weights_only=False);ck=torch.load(v['saved']['path'],map_location='cpu',weights_only=False)
 for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(s[k],ck[k]),k
 n=0;last=done=None;err=impulse_err=0.;moving4=0
 for r in v['chunks']:
  q=Path(r['path']);assert q.stat().st_size==r['bytes'] and H(q)==r['SHA']
  with np.load(q,allow_pickle=False) as z:d={k:z[k] for k in z.files}
  for k,x in d.items():
   if x.dtype.kind in 'fc':assert np.isfinite(x).all(),k
  x=d['policy35'];S=x.shape[0];assert x.shape[1:]==(task['per_GPU_envs'],35);mode=np.zeros_like(x[:,:,28:35]);mode[:,:,0 if a.job==0 else 4]=1;assert np.array_equal(mode,x[:,:,28:35]);assert abs(d['ground']).max()<=1e-6 and d['mimic'].max()<=.01
  assert np.array_equal(np.clip(d['raw6'],-6,6),d['executed6'])
  for i in range(S):
   if last is not None:
    previous=last.copy();previous[done]=0;assert np.array_equal(x[i,:,22:28],previous)
   last=np.clip(d['raw6'][i],-6,6);done=d['done'][i].astype(bool)
  impulse_err=max(impulse_err,float(abs(np.maximum(d['physical_wheel_force'][:,:,:,:,2],0).sum(axis=1)*.0025-d['impulse']).max()));assert impulse_err<=1e-6
  if a.job==0:moving4+=int(((abs(d['command'][:,:,2])==4)&(abs(d['command'][:,:,0])>1e-6)).sum())
  else:assert d['full_robot_contact_force'].shape[2]==len(v['actual_full_sensor_body_names']) and d['all_body_pos'].shape[2]==len(v['body_names'])
  y=torch.from_numpy(x.reshape(-1,35));sd=s['actor_state_dict']
  for i in (0,2,4,6):
   y=torch.nn.functional.linear(y,sd[f'mlp.{i}.weight'],sd[f'mlp.{i}.bias'])
   if i<6:y=torch.nn.functional.elu(y)
  err=max(err,float(abs(y.numpy()-d['raw6'].reshape(-1,6)).max()));assert err<=1e-4;n+=S
 assert n==144 and (a.job!=0 or moving4>0) and not torch.cuda.is_initialized()
 report.write_text(json.dumps(dict(epoch=time.time(),passed=True,job=a.job,source_SHA=task['source_SHA'],native_checkpoint_SHA=v['saved']['SHA'],controls=n,callbacks=576,all_saved_actor_CPUmeans_maxabs=err,CPU_GPU_not_bitexact=True,physical_wheel_impulse_maxabs=impulse_err,source_actor9_critic8_STD17Adam_literal_bytes_exact=True,policy35_mode_history_selectedreset_clipped6_exact=True,all_query_mimic_finite_guard_checked=True,actual_moving4_samples=moving4,H1_native_only_not_airborne_or_PPO_admission=a.job==1,full20k_original_source_restore=a.job==0,CPU_no_optimizer_or_CUDA=True),indent=2));print(report.read_text(),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  (B/('NATIVE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(error=traceback.format_exc(),no_GPU_replay=True),indent=2));raise
