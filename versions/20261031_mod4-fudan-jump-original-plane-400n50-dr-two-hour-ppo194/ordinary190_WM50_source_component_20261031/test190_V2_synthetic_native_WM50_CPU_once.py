from pathlib import Path
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import hashlib,json,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
purpose=json.loads((R/'SOURCE190_V2_BOUNDED_LOCAL_CPU_PURPOSE_FROZEN.json').read_bytes())
with (R/'ROOT190_V2_SYNTHETIC_CPU_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),source_only=True),f)
for row in purpose['inputs']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
sys.path[:0]=[str(N),purpose['source_directory']]
import torch
torch.set_num_threads(2)
from teacher_world_model50_core190_v2 import TeacherWM50
groups=[];started=time.monotonic()
try:
 rng=torch.random.get_rng_state().clone()
 m=TeacherWM50(purpose['source_directory'],'cpu',seed=190,envs=4,window=32,batch=4,hidden=(32,32))
 assert torch.equal(torch.random.get_rng_state(),rng)
 assert m.model.in_dim==167 and m.model.out_dim==126
 groups.append(dict(name='native127_31_6_dimensions_and_rng_isolated_constructor',passed=True))
 def fields(tick):
  s=torch.zeros(4,127);s[:,2]=.25;s[:,6]=1.;s[:,7]=.3;s[:,0]=tick*.006
  s1=s.clone();s1[:,0]+=.006;s1[:,7]+=.001
  xi=torch.tensor([1.,.9]+[1.]*6+[0.]*3+[1.]*10+[1.]*2+[1.]*2+[1.]*2+[0.]*4).expand(4,-1).clone()
  return dict(s=s,s1=s1,a=torch.zeros(4,6),a_prev=torch.zeros(4,6),xi=xi,r=torch.zeros(4),f=torch.zeros(4,dtype=torch.long),ep_step=torch.full((4,),tick,dtype=torch.int32),done=torch.tensor([tick==5,False,tick==11,False]))
 bad=fields(0);before={k:v.clone() for k,v in m.model.state_dict().items()};negative=[]
 for kw in [dict(physics_end_tick=4,physics_us=2500,feedback_samples=1),dict(physics_end_tick=8,physics_us=1000,feedback_samples=2)]:
  try:m.add(bad,**kw)
  except ValueError:negative.append('wrong_physical_clock')
  else:raise AssertionError('100Hz accepted as50Hz')
 wrong=fields(0);wrong['s1'][0,0]=float('nan')
 try:m.add(wrong,physics_end_tick=8,physics_us=2500,feedback_samples=2)
 except ValueError:negative.append('nonfinite_pair')
 else:raise AssertionError('NaN entered RunningNorm')
 assert m.controls==0 and all(torch.equal(v,before[k]) for k,v in m.model.state_dict().items())
 groups.append(dict(name='clock_and_finite_rejections_before_norm_or_replay_mutation',passed=True,rejections=negative))
 for i in range(32):m.add(fields(i),physics_end_tick=8*(i+1),physics_us=2500,feedback_samples=2)
 assert m.controls==32 and m.buffer.size==32 and float(m.model.in_norm.count)==128
 try:m.add(fields(33),physics_end_tick=256,physics_us=2500,feedback_samples=2)
 except ValueError:pass
 else:raise AssertionError('Duplicate clock accepted')
 b=m.sample();expected=torch.cumprod(torch.cat((torch.ones(4,1),1-b['done'].float()[:,:-1]),-1),-1)
 assert torch.equal(b['mask'],expected) and torch.equal(torch.random.get_rng_state(),rng)
 groups.append(dict(name='32step_sequence_terminal_inclusive_mask_and_dedicated_sampling_rng',passed=True,real_transitions=0,synthetic_transitions=128))
 out=m.update();assert out['world_updates']==1 and out['policy_updates']==0 and out['preclip_grad_L2']>0
 assert torch.equal(torch.random.get_rng_state(),rng)
 groups.append(dict(name='one_finite_native_autoregressive_WM_only_gradient_update',passed=True,value=out))
 ck=m.checkpoint();assert ck['world_updates']==1 and ck['physical_controls']==32 and ck['last_physics_tick']==256
 assert ck['protocol']['policy_us']==20000 and ck['complete_native_policy_conversion'] is False and len(ck['world_optimizer']['state'])>0
 assert not torch.cuda.is_initialized()
 groups.append(dict(name='full_WM_norm_optimizer_rng_counter_checkpoint_in_memory_only',passed=True,no_checkpoint_written=True))
 report=dict(epoch=time.time(),passed=True,groups=groups,elapsed_seconds=time.monotonic()-started,model_raw_SDK_GPU_remote_reads=0,
  scope='synthetic source component only, no actual expert transitions or native policy training;512production memory not tested')
except BaseException:
 report=dict(epoch=time.time(),passed=False,groups=groups,elapsed_seconds=time.monotonic()-started,error=traceback.format_exc(),actual_expert_or_GPU_failure=False);raise
finally:
 with (R/'ROOT190_V2_SYNTHETIC_NATIVE_WM50_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,groups=len(groups),elapsed_seconds=report['elapsed_seconds'])))
