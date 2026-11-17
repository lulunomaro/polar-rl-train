from pathlib import Path
import ast,importlib.util,json,math,sys,tempfile
import numpy as np
import torch
T=Path(__file__).resolve().parent;S=T/'support/mod4v3_ppo_v1'
def load(name):
 spec=importlib.util.spec_from_file_location(name,S/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
reward=load('dense_top_reward');maths=load('fixed200_reward_math');replay=load('success_replay')
upper=torch.tensor([[False,False],[True,False],[True,True],[True,True],[True,True],[True,True]])
z=torch.zeros(6);active=torch.ones(6,dtype=torch.bool);pitch=z.clone();pitch[3]=math.radians(30);speed=torch.full((6,),.47);speed[4]=2.;hold=torch.tensor([0,0,0,0,0,.4]);limit=torch.full((6,),1.5)
dense,parts=reward.dense_top_support(upper,active,pitch,z,pitch,torch.zeros(6,dtype=torch.bool),speed,limit,hold,.02)
assert torch.allclose(dense,torch.tensor([0.,.1,.4,0.,0.,.8])),dense
base=torch.zeros(6);cmd=torch.full((6,),.47);vx=z;landed=upper.all(1)
net,breakdown=maths.fixed200_reward(base,dense,active,cmd,vx,speed,pitch,z,z,torch.zeros(6,dtype=torch.bool),landed,landed,z,torch.zeros(6,2),limit,.02,height_aux_active=active)
assert net[0]<0 and net[1]>0 and net[2]>0 and net[5]>net[2]
assert torch.equal(maths.fixed200_reward(base,dense,~active,cmd,vx,speed,pitch,z,z,~active,landed,landed,z,torch.zeros(6,2),limit,.02,height_aux_active=active)[0],base)
pool=replay.SuccessReplayPool(max_frames=100)
frames=np.zeros((20,461),np.float32);phases=np.arange(20,dtype=np.int64)%3;meta=dict(accepted_native_success=True,stable_hold_s=.4,source_model_sha256='a55eeaed11ed7c7471444e1369153824b3fe79544e59296c911a3235507bd7a4')
pool.add(frames,phases,meta);sample=pool.sample(128,'cpu');assert sample['policy'].shape==(128,35)and sample['obs_history'].shape==(128,420)and sample['actions'].shape==(128,6)
rejected=False
try:pool.add(frames,phases,dict(accepted_native_success=False,stable_hold_s=.4))
except AssertionError:rejected=True
assert rejected
for f in list(S.glob('*.py'))+[T/'remote_control.py']:ast.parse(f.read_text(encoding='utf-8-sig'))
train=(S/'route2_train.py').read_text(encoding='utf8');opt=(S/'route2_optimizer.py').read_text(encoding='utf8')
assert "raw['settle_anchor']"in train and 'torch.full_like(coefficient,8.)'in opt
assert "success_recorder.push(obs"in train and "success_recorder.finish(term|timeout)"in train
out=dict(passed=True,reward_vector=dense.tolist(),net_vector=net.tolist(),normal_reward_exact=True,false_success_rejected=True,replay_shapes_correct=True,training_authorized=False,PPO_updates=0,optimizer_updates=0)
(T/'evidence/LOCAL_REPAIR_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf8');print(json.dumps(out))
