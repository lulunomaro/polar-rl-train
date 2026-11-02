"""SYNTHETIC software contract, original C113 source binder; never SDK/native."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch,types,json,sys,random,hashlib
import numpy as np
from pathlib import Path
from original_role_command_binding_candidate_v2 import bind_original_command_after_fresh_reset as bind
import independent_expert_axis_v1 as original
assert not torch.cuda.is_initialized();torch.set_num_threads(1)
S=types.SimpleNamespace;checks=[]
def ok(name,value):
 assert value,name
 checks.append(name)
def generated_commands(*a,**kw):raise AssertionError('No observation sampling')
class Term:
 def __init__(self):
  self.vel_command_b=torch.tensor([[.11,.02,.03]]*4);self.linear_vx=self.vel_command_b[:,0].clone();self.is_standing_env=torch.tensor([False,False,False,True]);self.manual_evaluation_mode=False;self.calls=0
 def _write_dynamic(self,ids):
  self.calls+=1
  if self.manual_evaluation_mode:return
  self.vel_command_b[ids]=torch.tensor([.11,.02,.03]);self.vel_command_b[ids[self.is_standing_env[ids]]]=0;self.linear_vx[ids]=self.vel_command_b[ids,0]
 @property
 def command(self):return self.vel_command_b
class Env:
 def __init__(self):
  self.num_envs=4;self.device=torch.device('cpu');family=torch.zeros(40,40,dtype=torch.long);family[20,20]=4
  self.scene=S(env_origins=torch.tensor([[1.,1.,0.],[1.,1.,0.],[10.,1.,0.],[1.,1.,0.]]),terrain=S(retention_family=family))
  self._rough_spawn_xy=torch.tensor([[3.7,4.5],[5.3,4.5],[13.5,4.5],[5.3,4.5]])
  self.term=Term();self.command_manager=S(get_term=lambda name:self.term)
  command=S(func=generated_commands,params={'command_name':'twist'},noise=None,clip=None,scale=None,modifiers=None)
  self.cfg=S(observations=S(policy=S(commands=command)));self.observation_manager=S(active_terms={'policy':['commands','height_command'],'critic':['commands','height_command']})
 def reset(self):raise AssertionError('Additional reset forbidden')
e=Env();obs={'policy':torch.randn(4,35),'critic':torch.randn(4,38),'extra':'unknown field retained'}
rng=torch.get_rng_state().clone();py=random.getstate();nr=np.random.get_state();before={k:v.clone()if torch.is_tensor(v)else v for k,v in obs.items()}
new,receipt=bind(e,'CURB_INDEPENDENT113',obs,original)
ok('source original binder called once',e.term.calls==1)
ok('target reset direction toward center +.3/-.3',torch.allclose(new['policy'][:2,:3],torch.tensor([[.3,0.,0.],[-.3,0.,0.]])))
ok('non-target command unchanged',torch.equal(new['policy'][2,:3],torch.tensor([.11,.02,.03])))
ok('standing remains zero',torch.equal(new['policy'][3,:3],torch.zeros(3)))
ok('critic same current original command',torch.equal(new['critic'][:,:3],new['policy'][:,:3]))
ok('all sensor previous_action mode slots unchanged',torch.equal(new['policy'][:,3:],before['policy'][:,3:])and torch.equal(new['critic'][:,3:],before['critic'][:,3:]))
ok('original observation input not overwritten',torch.equal(obs['policy'],before['policy'])and new['extra']=='unknown field retained')
ok('all CPU random states unchanged',torch.equal(rng,torch.get_rng_state())and py==random.getstate()and all(np.array_equal(a,b)for a,b in zip(nr,np.random.get_state())))
ok('no reset or extra observation compute',receipt['extra_reset_or_physics_or_model_operations']==0)
try:bind(e,'CURB_INDEPENDENT113',obs,original)
except RuntimeError:ok('duplicate bind rejected',e.term.calls==1)
else:raise AssertionError('duplicate accepted')
other,other_receipt=bind(Env(),'E0',obs,original);ok('other role identity and no extra binding',other is obs and not other_receipt['extra_axis_binding_required'])
bad=Env();bad.cfg.observations.policy.commands.scale=2.
try:bind(bad,'CURB_INDEPENDENT113',obs,original)
except ValueError:ok('unknown command transform rejected before binding',bad.term.calls==0)
else:raise AssertionError('unknown transform accepted')
ok('source binder native library not imported',not any(k.startswith(('isaaclab','omni','pxr'))for k in sys.modules)and not torch.cuda.is_initialized())
result=dict(kind='SYNTHETIC_ORIGINAL_C113_BINDING_SOFTWARE_ONLY',passed=True,checks=checks,checks_count=len(checks),receipt=receipt,original_axis_source_SHA=hashlib.sha256(Path(original.__file__).read_bytes()).hexdigest(),native_expert_BPTT_updates=0,SDK_GPU_PT_C_GO_operations=0)
out=Path(sys.argv[1]);assert not out.exists();out.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
