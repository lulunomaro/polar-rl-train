from pathlib import Path
from types import SimpleNamespace as S
import tempfile,json,torch
from e1_terrain_training_health import E1TerrainTrainingHealth,learning_health_pass,declared_truncation_terms
class Manager:
 def __init__(self):
  self.active_terms=['time_out','rough_route_boundary','closure','mimic','bad_orientation','base_contact','low_base','unexpected'];self.flags={n:n in ('time_out','rough_route_boundary') for n in self.active_terms};self.masks={n:torch.zeros(3,dtype=torch.bool) for n in self.active_terms}
 def get_term_cfg(self,n):return S(time_out=self.flags[n])
 def get_term(self,n):return self.masks[n]
 @property
 def terminated(self):return torch.stack([v for n,v in self.masks.items() if not self.flags[n]]).any(0)
 @property
 def time_outs(self):return torch.stack([v for n,v in self.masks.items() if self.flags[n]]).any(0)
class Env:
 def __init__(self,reason=None,missing=False,nan=False):
  self.num_envs=3;self.device='cpu';self.physics_dt=.0025;self.step_dt=.01;self.termination_manager=Manager();self._integrated_contact=S(tick=0);self._mod4_max_closure=.001;self._mod4_max_mimic=.001;self.missing=missing
  data=S(root_state_w=torch.zeros(3,13),joint_pos=torch.zeros(3,30),joint_vel=torch.zeros(3,30));self.scene={'robot':S(data=data)}
  if reason:
   for n in reason:self.termination_manager.masks[n][0]=True
  if nan:data.joint_pos[1,0]=float('nan')
 def step(self,a):self._integrated_contact.tick+=3 if self.missing else 4;return ('original-result',)
def run(reasons=(),missing=False,nan=False,mimic=.001):
 with tempfile.TemporaryDirectory() as folder:
  e=Env(reasons,missing,nan);e._mod4_max_mimic=mimic;h=E1TerrainTrainingHealth(e,folder)
  a=torch.zeros(3,6)
  for _ in range(24):assert e.step(a)==('original-result',)
  v=h.write();return v,(Path(folder)/'STOP_AFTER_SAVE').exists()
def main():
 torch.set_num_threads(1)
 v,stop=run(('rough_route_boundary',));assert learning_health_pass(v) and not stop and v['unknown_task_reset_events']==0 and v['route_boundary_truncation_events']==24 and v['actual_task_reset_events']==0
 v,stop=run(('time_out','rough_route_boundary'));assert learning_health_pass(v) and v['actual_truncation_reset_events']==24 and not stop
 v,stop=run(('closure','rough_route_boundary'));assert learning_health_pass(v) and v['actual_task_reset_events']==v['ordinary_episode_reset_events']==24 and not stop
 v,stop=run(('mimic','rough_route_boundary'));assert not learning_health_pass(v) and v['integrity_task_reset_events']==24 and stop
 v,stop=run(('unexpected',));assert not learning_health_pass(v) and v['unknown_task_reset_events']==24 and stop
 v,stop=run(missing=True);assert not learning_health_pass(v) and stop
 v,stop=run(nan=True);assert not learning_health_pass(v) and stop
 v,stop=run(mimic=.02);assert not learning_health_pass(v) and stop
 m=Manager();m.flags['rough_route_boundary']=False
 try:declared_truncation_terms(m)
 except AssertionError:pass
 else:raise AssertionError('Route must be actual declared truncation')
 m=Manager();m.flags['unexpected']=True
 try:declared_truncation_terms(m)
 except AssertionError:pass
 else:raise AssertionError('Unknown truncation not silently permitted')
 e=Env();e.termination_manager.masks['unexpected'][0]=True;e.termination_manager.flags['unexpected']=False
 # Genuine unnamed terminated flag absent from masks must retain coverage failure.
 class BadManager(Manager):
  @property
  def terminated(self):return torch.ones(3,dtype=torch.bool)
 with tempfile.TemporaryDirectory() as folder:
  e=Env();e.termination_manager=BadManager();h=E1TerrainTrainingHealth(e,folder)
  for _ in range(24):e.step(torch.zeros(3,6))
  assert not learning_health_pass(h.write()) and (Path(folder)/'STOP_AFTER_SAVE').exists()
 assert not torch.cuda.is_initialized();print('CPU11 route truncation / overlap / unknown / integrity / callback / nonfinite / manager coverage contracts passed; no CUDA initialized')
if __name__=='__main__':main()
