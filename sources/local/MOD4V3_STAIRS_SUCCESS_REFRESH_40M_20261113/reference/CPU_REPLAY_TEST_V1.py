from pathlib import Path
import sys,json,types,copy,time
import torch
from tensordict import TensorDict
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.success_replay import SuccessfulStairReplay
from mod4v3_ppo_v1.teacher_retention import TeacherRetention

def env():
 n=4;z=torch.zeros(n);return types.SimpleNamespace(device='cpu',continuous_stair_mask=torch.ones(n,dtype=torch.bool),stair_up=torch.ones(n,dtype=torch.bool),stair_initial_stage=torch.tensor([0,0,1,0]),episode_length_buf=torch.full((n,),150),step_dt=.02,stair_stage=torch.zeros(n,dtype=torch.long),stair_goal_hold=z.clone(),stair_height=torch.full((n,),.4),stair_speed=torch.full((n,),2.2),stair_first_time=torch.full((n,),3.2),stair_second_time=torch.full((n,),4.4),full_dr=types.SimpleNamespace(nominal_env_mask=torch.tensor([False,True,False,True])))
spec=dict(max_episode_frames=6,capacity_per_stratum=8,new_fraction=.5,transition_fraction=.5)
e=env();pool=SuccessfulStairReplay(e,spec);ob=TensorDict({'policy':torch.arange(140).float().reshape(4,35)/100},batch_size=[4]);act=torch.full((4,6),8.)
for k,new_stage in enumerate([0,1,2,2]):
 with torch.inference_mode():
  pool.before_step(e,ob,act,25076);e.stair_stage.fill_(new_stage);e.episode_length_buf+=1;e.stair_goal_hold.fill_(.3 if k==3 else 0.)
  pool.after_step(e,torch.tensor([False,False,False,k==3]),torch.zeros(4,dtype=torch.bool))
assert pool.accepted==2 and pool.counts==[2,2,2,2] and pool.rejected_done==1
assert {r['env'] for r in pool.episodes}=={0,1}
x,y=pool.sample(100);assert x.shape==(100,35) and y.shape==(100,6) and y.abs().max()==6
assert pool.sampled==[25,25,25,25]
with torch.inference_mode():pool.before_step(e,ob,act,25077);pool.after_step(e,torch.zeros(4,dtype=torch.bool),torch.zeros(4,dtype=torch.bool))
assert pool.accepted==2
restored=SuccessfulStairReplay(env(),spec);restored.load_state_dict(copy.deepcopy(pool.state_dict()));assert restored.counts==pool.counts and torch.equal(restored.bank_obs,pool.bank_obs)
# A failed/overflowing physical episode cannot supply a later successful label.
e2=env();e2.stair_initial_stage[:]=0;overflow=SuccessfulStairReplay(e2,spec)
for k in range(8):
 with torch.inference_mode():
  overflow.before_step(e2,ob,act,25076);e2.episode_length_buf+=1;e2.stair_goal_hold.fill_(.3 if k==7 else 0.);overflow.after_step(e2,torch.zeros(4,dtype=torch.bool),torch.zeros(4,dtype=torch.bool))
assert overflow.accepted==0 and overflow.overflows==4
class Actor(torch.nn.Module):
 def __init__(self):
  super().__init__();self.mlp=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6))
 def forward(self,obs,stochastic_output=False):return self.mlp(obs['policy'])
p=json.loads((T/'PLAN.json').read_text());p['teacher_retention']['keep_teacher']=str(T/'weights/teacher_parent_iter24692.pt');p['teacher_retention']['dataset']=str(T/'reference/native_stair_success_demos.pt')
a=types.SimpleNamespace(device='cpu',actor=Actor());r=TeacherRetention(a,p);r.success_replay=pool
batch=TensorDict({'policy':ob['policy'],'teacher_keep':torch.ones(4,1)},batch_size=[4]);loss=r.compute(a,batch);loss.backward();metrics=r.finish_update()
assert torch.isfinite(loss) and metrics['teacher_new_success_samples']==512 and metrics['teacher_new_success_mse']>0
assert sum(float(v.grad.abs().sum()) for v in a.actor.parameters() if v.grad is not None)>0 and all(v.grad is None for v in r.keep_teacher.parameters())
report=dict(epoch=time.time(),pass_all=True,checks=['whole successes admitted','failed reset excluded','mid-start excluded','phase and DR balanced','execution clipping6','no duplicate success','overflow discarded','complete replay state roundtrip','new success contributes actual actor gradients','frozen teacher no gradients'],accepted=pool.accepted,frames_by_stratum=pool.counts,losses=metrics,teacher_change=r.summary()['keep_teacher_max_parameter_change'])
(T/'evidence/CPU_REPLAY_CHECK.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
