"""OriginalE2Cycles213 onnewfresh80 owncommand/naturalpre-resetframes. Noactor/RNG/physics/timers writes."""
import types
from e2_cycles213 import E2Cycles213
from e2_original_profile_catalog_candidate_v1 import classify
class E2FreshCycleBridge:
 def __init__(self,env,t,tensor,out):
  self.env=env;self.t=t;self.tensor=tensor;self.robot=env.scene['robot'];self.cmd=env.command_manager.get_term('twist');self.cycles=E2Cycles213(t,env.num_envs,env.device,out);self.episode=t.zeros(env.num_envs,dtype=t.long,device=env.device);self.uid=self.episode.clone();self.context=None;self.old_reset=env._reset_idx;self.old_sample=self.cmd._resample_command;book=self
  def ids(v):return t.arange(env.num_envs,device=env.device)if v is None else t.arange(env.num_envs,device=env.device)[v]if isinstance(v,slice)else t.as_tensor(v,device=env.device,dtype=t.long)
  def reset(this,selected):
   selected=ids(selected);book.cycles.close(selected,'original_reset');book.episode[selected]+=1;return book.old_reset(selected)
  def resample(this,selected):
   selected=ids(selected);book.cycles.close(selected,'original_resample');result=book.old_sample(selected);book.uid[selected]+=1;return result
  env._reset_idx=types.MethodType(reset,env);self.cmd._resample_command=types.MethodType(resample,self.cmd)
 def begin(self,i):
  e=self.env;t=self.t;c=self.cmd;r=self.robot;heading=self.tensor(r.data.heading_w).clone();direction=c.world_direction.clone();command=c.command.clone();angle=heading-direction
  self.context=dict(key=classify(t,c.is_standing_env,c.is_pure_spin,c.is_moving_spin,c.is_transition_spin,command,c.signed_yaw),phase=0 if i<100 else 1,episode=self.episode.clone(),command_uid=self.uid.clone(),before_xy=self.tensor(r.data.root_pos_w)[:,:2].clone(),heading=heading,direction=direction,command=command,signed_yaw=c.signed_yaw.clone(),reference_projection=command[:,0]*t.cos(angle)-command[:,1]*t.sin(angle));self.cycles.begin(i,self.context,int(e._integrated_contact.tick))
 def terminal(self):
  c=self.context;t=self.t;e=self.env;tm=e.termination_manager;heading=self.tensor(self.robot.data.heading_w);delta=t.atan2(t.sin(heading-c['heading']),t.cos(heading-c['heading']));after=dict(xy=self.tensor(self.robot.data.root_pos_w)[:,:2],heading_delta=delta);self.cycles.observe(c,after,tm.terminated,tm.time_outs,{k:tm.get_term(k).bool()for k in tm.active_terms},int(e._integrated_contact.tick))
 def finish(self):
  result=self.cycles.finish();self.env._reset_idx=self.old_reset;self.cmd._resample_command=self.old_sample;return result
