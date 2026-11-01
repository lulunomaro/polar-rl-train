"""One LOCAL source derivation;copies only three Python modules,never assets/PT."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
M=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/package/payload/job0/runtime/isaac/mod4'
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
 assert json.loads((R/'DERIVE_DR0_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 put(R/'DERIVE_DR0_ONCE_CONSUMED.json',dict(epoch=time.time(),model_asset_raw_reads=0))
 source={x:(M/x).read_text(encoding='utf8') for x in ('mild_dr.py','action_delay_training_env.py','spring_pressure_training_env.py')}
 s=source['mild_dr.py']
 s=once(s,"        self.recipe = DR_PROFILES[self.profile]", "        self.dr0 = self.profile == 'all_off_nominal_v1'\n        if self.dr0:\n            assert os.environ.get('RM_ALL_RANDOMIZATION_OFF')=='1'\n            self.recipe = dict(mass=(1.,1.),motor=(1.,1.),friction=(.9,.9))\n        else:self.recipe = DR_PROFILES[self.profile]")
 s=once(s,"nominal = torch.rand(len(ids), device=env.device, generator=self.generator) < .2", "nominal = torch.ones(len(ids),device=env.device,dtype=torch.bool) if self.dr0 else torch.rand(len(ids), device=env.device, generator=self.generator) < .2")
 s=once(s,"factor = torch.empty(len(ids), device=env.device).uniform_(*self.recipe['mass'], generator=self.generator)", "factor = torch.ones(len(ids),device=env.device) if self.dr0 else torch.empty(len(ids), device=env.device).uniform_(*self.recipe['mass'], generator=self.generator)")
 s=once(s,"gains[ids] = torch.empty_like(gains[ids]).uniform_(*self.recipe['motor'], generator=self.generator)", "gains[ids] = 1. if self.dr0 else torch.empty_like(gains[ids]).uniform_(*self.recipe['motor'], generator=self.generator)")
 s=once(s,"bucket = torch.randint(1, 33, (len(ids),), device='cpu', generator=self.cpu_generator)", "bucket = torch.zeros(len(ids),device='cpu',dtype=torch.long) if self.dr0 else torch.randint(1, 33, (len(ids),), device='cpu', generator=self.cpu_generator)")
 s=once(s,"    if profile not in DR_PROFILES:", "    if profile=='all_off_nominal_v1':\n        assert os.environ.get('RM_ALL_RANDOMIZATION_OFF')=='1'\n    elif profile not in DR_PROFILES:")
 source['mild_dr.py']=s
 s=source['action_delay_training_env.py'];s=once(s,"assert profile=='physical_target_0_2500_5000us_v1'", "assert profile in ('off','physical_target_0_2500_5000us_v1')")
 s=once(s,'PhysicalActionDelayAdapter(self,True,int(self.cfg.seed),collect=False)',"PhysicalActionDelayAdapter(self,profile!='off',int(self.cfg.seed),collect=False)");source['action_delay_training_env.py']=s
 s=source['spring_pressure_training_env.py'];s=once(s,"assert os.environ.get('RM_SPRING_PRESSURE_PROFILE')==PROFILE", "profile=os.environ.get('RM_SPRING_PRESSURE_PROFILE');assert profile in ('off',PROFILE)")
 s=once(s,'LearningSpringPressure(self,True,int(self.cfg.seed))',"LearningSpringPressure(self,profile!='off',int(self.cfg.seed))");source['spring_pressure_training_env.py']=s
 rows=[]
 for name,s in source.items():
  ast.parse(s);p=N/name
  with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
  r=ref(p);rows.append(dict(relative='runtime/isaac/mod4/'+name,local_path=str(p),bytes=r['bytes'],SHA=r['SHA']))
 put(R/'INSTALL_DR0_OFF_MODULES.json',dict(kind='DR0_NEW_NAMESPACE_THREE_OFF_MODULES',files=rows,
  install_only_into_NEW_owned_runtime=True,old_frozen_sources_immutable=True,base_runtime_other_bytes_unchanged=True,
  original_inputs=[ref(M/x) for x in source],model_asset_raw_reads=0,actual_target_SDK_pending=True))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'DERIVE_DR0_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
