"""New synthetic UID/reset conformance only; no model/raw/SDK/remote access."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import json,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
def main():
 put('ROOT222_NEW_OBSERVER_BEHAVIOR_CPU_ONCE_CONSUMED.json',dict(epoch=time.time(),synthetic_cases=3,models_raw_NPZ_SDK_GPU_remote_calls=0,old_child_AST_not_repeated=True))
 import torch as t
 from types import SimpleNamespace as NS
 from rm70_intervals222 import RM70Intervals222
 assert not t.cuda.is_initialized();rng=t.random.get_rng_state().clone();facts=[]
 for case in ('natural_and_reset_failure','unobserved_parameter_break','left_censored_start'):
  out=N/('synthetic_ROOT222_'+case);out.mkdir(exist_ok=False)
  real=NS(_sim_step_counter=0,_e1_episode=t.zeros(2,dtype=t.long),scene=NS(env_origins=t.zeros(2,3)))
  class Command:
   def __init__(self):
    self.num_envs=2;self.device='cpu';self._env=real;self.time_left=t.full((2,),.04);self.command_counter=t.zeros(2,dtype=t.long)
    self.command=t.tensor([[.2,0,0],[.2,0,0]]);self._command_heading=t.zeros(2);self.direction=t.tensor([2.,-1.]);self.is_standing_env=t.zeros(2,dtype=t.bool)
   def _resample(self,ids):
    ids=t.arange(2)if ids is None else ids;self.time_left[ids]=.04;self.command_counter[ids]+=1
   def reset(self,env_ids=None):self._resample(env_ids);return{'original_return':True}
  book=RM70Intervals222(t,2,'cpu',out,'SYNTHETIC_NOT_MODEL');book.install(Command);cmd=Command()
  try:
   if case!='left_censored_start':assert cmd.reset(None)['original_return']
   origin=book.arm(real,cmd);assert origin['initial_start_observed']==(case!='left_censored_start')
   xy=t.tensor([[5.85,6.45],[9.15,6.45]],dtype=t.float32);heading=t.zeros(2)
   masks={k:t.zeros(2,dtype=t.bool)for k in ('closure','time_out')}
   tm=NS(active_terms=list(masks),terminated=t.zeros(2,dtype=t.bool),time_outs=t.zeros(2,dtype=t.bool),get_term=lambda name:masks[name],get_term_cfg=lambda name:NS(time_out=name=='time_out'))
   for i in range(2):
    if i==1 and case=='unobserved_parameter_break':cmd.command[0,0]=.25
    book.begin(i,xy.clone(),heading.clone());xy[:,0]+=cmd.command[:,0]*.02;real._sim_step_counter+=8
    if i==1 and case=='natural_and_reset_failure':masks['closure'][1]=True;tm.terminated[1]=True
    root=t.zeros(2,13);root[:,:2]=xy;root[:,6]=1
    book.terminal(dict(root=root,closure=t.zeros(2),mimic=t.zeros(2)),tm);cmd.time_left-=.02
   cmd.time_left[:]=0
   if case=='natural_and_reset_failure':cmd._resample(t.tensor([0]));cmd.reset(t.tensor([1]))
   else:cmd._resample(t.arange(2))
   f=book.finish();assert not f['diagnostic_errors']and not f['producer']['retention_limited']
   e=f['events']
   if case=='natural_and_reset_failure':assert e['natural_complete_intervals']==1 and e['complete_kinematic_bounds_met']==1 and e['partial_intervals']==1 and f['original_reason_counts']['closure']==1
   elif case=='unobserved_parameter_break':assert e['source_parameter_breaks']==1 and e['natural_complete_intervals']==1 and e['partial_intervals']==2
   else:assert e['natural_complete_intervals']==0 and e['partial_intervals']==2
   facts.append(dict(case=case,events=e,original_reason_counts=f['original_reason_counts'],producer=f['producer']))
  finally:book.uninstall()
 assert t.equal(rng,t.random.get_rng_state())and not t.cuda.is_initialized()
 put('ROOT222_NEW_OBSERVER_BEHAVIOR_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,synthetic_cases=3,facts=facts,global_RNG_unchanged=True,CUDA_initialized=False,physical_or_model_evaluation=False))
 print(json.dumps(dict(passed=True,cases=3,models_raw_NPZ_SDK_GPU_remote_calls=0)))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT222_ORIGINAL_OBSERVER_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
