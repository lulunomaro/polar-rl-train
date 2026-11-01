from pathlib import Path
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports';p=json.loads((R/'FROZEN255_NEW_CONTEXT40_SYNTHETIC_CPU_PURPOSE.json').read_bytes())
with(R/'ROOT255_NEW_SYNTHETIC_NATIVE_WM40_CPU_ONCE_CONSUMED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),old190_fixture_replayed=False,real_model_or_data=0),f)
sys.path[:0]=[str(N),p['native_source_directory']]
import torch
torch.set_num_threads(2)
from native_depth_world_model50_v255 import DepthTeacherWM50
groups=[]
try:
 rng=torch.get_rng_state().clone();m=DepthTeacherWM50(p['native_source_directory'],'cpu',seed=255,envs=2,window=32,batch=2,hidden=(32,32));assert m.model.in_dim==176 and m.model.out_dim==126
 groups.append(dict(name='new_native_context40_input176_output126',passed=True))
 def row(t):
  s=torch.zeros(2,127);s[:,2]=.25;s[:,6]=1.;s[:,7]=.25;s[:,0]=t*.005;s1=s.clone();s1[:,0]+=.005
  xi31=torch.tensor([1.,.9]+[1.]*6+[0.]*3+[1.]*10+[1.]*2+[1.]*2+[1.]*2+[0.]*4).expand(2,-1).clone()
  d=torch.tensor([1.25-t*.005,.27,0.,0.,1.5,1.5,.9,.02,1.]).expand(2,-1).clone()
  return dict(s=s,s1=s1,a=torch.zeros(2,6),a_prev=torch.zeros(2,6),xi=torch.cat((xi31,d),-1),r=torch.zeros(2),f=torch.zeros(2,dtype=torch.long),ep_step=torch.full((2,),t,dtype=torch.int32),done=torch.tensor([t==9,False]))
 producer=dict(kind='SYNTHETIC_CPU_INTERFACE_ONLY',plant='own_MOD4_live_USD',run_id='synthetic255',generation=1,source_admission_SHA='syntheticonly',max_depth_age_seconds=.02)
 before={k:v.clone()for k,v in m.model.state_dict().items()};rejected=0
 for producer0,clock in[(dict(producer,plant='foreign_Fudan'),8),(dict(producer,max_depth_age_seconds=-.01),8),(producer,4)]:
  try:m.add(row(0),physics_end_tick=clock,physics_us=2500,feedback_samples=2,producer=producer0,synthetic_CPU_test=True)
  except ValueError:rejected+=1
  else:raise AssertionError('Bad input accepted')
 assert m.controls==0 and all(torch.equal(v,before[k])for k,v in m.model.state_dict().items())
 groups.append(dict(name='producer_depth_clock_rejected_before_norm_or_replay',passed=True,rejections=rejected))
 for i in range(32):m.add(row(i),physics_end_tick=(i+1)*8,physics_us=2500,feedback_samples=2,producer=producer,synthetic_CPU_test=True)
 value=m.update();assert value['world_updates']==1 and value['policy_updates']==0 and value['preclip_grad_L2']>0
 ck=m.checkpoint();assert ck['protocol']['context40']and ck['protocol']['depth9']and ck['complete_native_policy_conversion']is False
 assert torch.equal(rng,torch.get_rng_state())and not torch.cuda.is_initialized()
 groups.append(dict(name='new_native_autoregressive_H32_WM_only_update_and_full_in_memory_state',passed=True,value=value,synthetic_pairs=64,no_checkpoint_written=True))
 report=dict(passed=True,epoch=time.time(),groups=groups,old190fixture0=True,real_data_model_SDK_GPU_remote=0,actualPi_or_WM_learning=False,scope='New context40 source/synthetic only, not actual expert transitions, literalFudan reward adapter or fullSuperMimic conversion.')
except BaseException:report=dict(passed=False,epoch=time.time(),groups=groups,error=traceback.format_exc(),actual_model_or_physics_failure=False);raise
finally:
 with(R/'ROOT255_NEW_NATIVE_CONTEXT40_WM50_CPU_RETURNED.json').open('x',encoding='utf8')as f:json.dump(report,f,indent=2)
files=list(N.glob('*.py'))+list(R.glob('*.json'));index=N/'INDEX255_NATIVE_DEPTH_WM50_SOURCE_FROZEN.json'
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='FROZEN_NEW_NATIVE_DEPTH_CONTEXT40_SOURCE_ONLY',files=[dict(path=str(f),bytes=f.stat().st_size,SHA=hashlib.sha256(f.read_bytes()).hexdigest())for f in files],actual_learning=False),f,indent=2)
print(json.dumps(dict(passed=True,groups=len(groups),index_SHA=hashlib.sha256(index.read_bytes()).hexdigest(),synthetic_WM_updates=1,real_updates=0)))
