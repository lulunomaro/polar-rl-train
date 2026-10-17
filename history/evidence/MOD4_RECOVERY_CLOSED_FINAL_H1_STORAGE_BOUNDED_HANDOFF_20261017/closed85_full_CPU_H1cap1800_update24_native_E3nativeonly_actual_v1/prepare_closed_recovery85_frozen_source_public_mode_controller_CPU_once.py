"""Prepare source-bound E3 frozen actor/public-mode components; no target package or GPU evaluation."""
from pathlib import Path
import os,sys,time,json,hashlib,shutil,copy,ast
os.environ['CUDA_VISIBLE_DEVICES']=''
import torch
B=Path(__file__).resolve().parent;R=B/'reports';E=B/'recovery_closed85_frozen_components_CPU_v1';Q=B.parent/'MOD4_TWO72_CLOSED_SOURCES_HEALTHY_NEXT_BLOCK_20261017/e2_closed109_frozen_prepared_v6/payload'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();v=json.loads((R/'RECOVERY_CLOSED85_COMPLETE_MODEL_CPU_COST_EXIT_ORIGINAL_HANDOFF_ACTUAL.json').read_bytes());row=v['complete_final'];assert v['passed_full_model_CPU'] and row['SHA']=='8043c7fbcd8abf2690672aa956fcfae0c17c24172fc6baaef0e75e5e44a1c208';src=Path(row['local_path']);assert H(src)==row['SHA'] and not E.exists();E.mkdir();dst=E/'E3_actual_closed85_Adam657660.pt';shutil.copy2(src,dst)
 guard='''"""E3 actual closed85 full-source guard; no E2/E1 metadata fabrication."""
import torch
def validate_E3_source(ck):
 assert ck['E3_phase']=='production' and ck['E3_production_updates']==85 and ck['E3_task']['kind']=='E3_PUBLIC_RECOVERY'
 assert ck['E3_task']['num_envs']==20000 and ck['E3_public_recovery_state']['version']==1
 assert len(ck['actor_state_dict'])==9 and len(ck['critic_state_dict'])==8 and len(ck['optimizer_state_dict']['state'])==17
 assert {int(v['step']) for v in ck['optimizer_state_dict']['state'].values()}=={657660}
 sd=ck['actor_state_dict'];assert [list(sd[k].shape) for k in ('mlp.0.weight','mlp.2.weight','mlp.4.weight','mlp.6.weight')]==[[256,35],[128,256],[64,128],[6,64]]
 assert ck['critic_state_dict']['mlp.0.weight'].shape[1]==38 and sd['distribution.std_param'].shape==(6,) and torch.isfinite(sd['distribution.std_param']).all() and (sd['distribution.std_param']>0).all()
 for name in ('sensor_DR_state','sensor_global_rng_state','sensor_command_DR_rng_state','sensor_physical_DR_rng_state','feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state','chassis_PD_state'):assert name in ck,name
 def finite(x):
  if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for v in x.values():finite(v)
  elif isinstance(x,(tuple,list)):
   for v in x:finite(v)
 finite(ck);return True
'''
 component='''"""Frozen source85 actor9 only; caller supplies the actual declared public mode0 or3."""
from pathlib import Path
import hashlib,torch
from hard_top1_frozen_expert_CPU_component_v1 import FrozenMean35
from recovery_closed85_source_guard_v1 import validate_E3_source
EXPECTED='8043c7fbcd8abf2690672aa956fcfae0c17c24172fc6baaef0e75e5e44a1c208'
class Single35:
 def __init__(self,path,n,device):
  assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==EXPECTED and isinstance(n,int) and n>0
  ck=torch.load(path,map_location='cpu',weights_only=False);validate_E3_source(ck)
  self.model=FrozenMean35(ck['actor_state_dict']).to(device).eval();self.model.requires_grad_(False);self.source={k:v.detach().cpu().clone() for k,v in ck['actor_state_dict'].items()};self.n=n;self.device=torch.device(device);self.last=torch.zeros(n,6,device=device);self.tick=-1;self.pending=None;self.calls=0;self.controls=0
 def begin(self,tick,provider,public_mode):
  if self.pending is not None:assert self.tick==tick;return self.pending
  assert self.tick<0 or tick==self.tick+1
  x=provider();assert x.shape==(self.n,35) and x.dtype==torch.float32 and x.device==self.device and torch.isfinite(x).all() and torch.equal(x[:,22:28],self.last)
  assert isinstance(public_mode,int) and public_mode in (0,3);mode=torch.zeros_like(x[:,28:35]);mode[:,public_mode]=1;assert torch.equal(x[:,28:35],mode)
  a=self.model(x);assert a.shape==(self.n,6) and torch.isfinite(a).all();self.pending=dict(shared_obs=x.detach().clone(),raw_action=a.detach().clone(),clipped_action=a.detach().clamp(-6,6),declared_actual_public_mode=public_mode);self.tick=tick;self.calls+=1;return self.pending
 def finish(self,actual,ended):
  assert self.pending is not None and actual.shape==(self.n,6) and ended.shape==(self.n,) and ended.dtype==torch.bool and torch.equal(actual,self.pending['clipped_action'])
  self.last=actual.detach().clone();self.last[ended]=0;self.pending=None;self.controls+=1
 def exact(self):
  assert all(torch.equal(v.detach().cpu(),self.source[k]) for k,v in self.model.snapshot().items());return True
'''
 for n,s in [('recovery_closed85_source_guard_v1.py',guard),('recovery_closed85_single35_public03_CPU_v1.py',component)]:
  ast.parse(s)
  with (E/n).open('x',encoding='utf8',newline='\n') as f:f.write(s)
 sys.path[:0]=[str(E),str(Q)];from recovery_closed85_source_guard_v1 import validate_E3_source
 from recovery_closed85_single35_public03_CPU_v1 import Single35
 ck=torch.load(dst,map_location='cpu',weights_only=False);assert validate_E3_source(ck);controller=Single35(dst,104,'cpu');assert controller.exact();calls=[0]
 def provider(mode):
  calls[0]+=1;x=torch.zeros(104,35);x[:,22:28]=controller.last;x[:,28+mode]=1;return x
 first=controller.begin(0,lambda:provider(3),3);assert controller.begin(0,lambda:provider(3),3) is first and calls[0]==1;ended=torch.zeros(104,dtype=torch.bool);ended[[1,3]]=True;controller.finish(first['clipped_action'],ended);assert not controller.last[ended].any();second=controller.begin(1,lambda:provider(0),0);controller.finish(second['clipped_action'],torch.zeros(104,dtype=torch.bool));assert controller.exact() and controller.calls==2
 wrong=[]
 for name in ('wrong_step','wrong_updates','wrong_phase','wrong_kind','wrong_public_version','wrong35','wrong38','nonfinite_STD','negative_STD'):
  x=copy.deepcopy(ck)
  if name=='wrong_step':next(iter(x['optimizer_state_dict']['state'].values()))['step']+=1
  elif name=='wrong_updates':x['E3_production_updates']=86
  elif name=='wrong_phase':x['E3_phase']='native'
  elif name=='wrong_kind':x['E3_task']['kind']='E2_WORLD_MOVING_SIGNED4'
  elif name=='wrong_public_version':x['E3_public_recovery_state']['version']=99
  elif name=='wrong35':x['actor_state_dict']['mlp.0.weight']=x['actor_state_dict']['mlp.0.weight'][:,:34]
  elif name=='wrong38':x['critic_state_dict']['mlp.0.weight']=x['critic_state_dict']['mlp.0.weight'][:,:37]
  elif name=='nonfinite_STD':x['actor_state_dict']['distribution.std_param'][0]=float('nan')
  else:x['actor_state_dict']['distribution.std_param'][0]=-1
  try:validate_E3_source(x)
  except AssertionError:wrong.append(name)
  else:raise AssertionError(name)
 for name in ('bad_previous_actual','bad_declared_mode','bad_mode_observation','bad_tick','nonfinite_input'):
  cc=Single35(dst,104,'cpu');x=torch.zeros(104,35);x[:,31]=1;tick=0;mode=3
  if name=='bad_previous_actual':x[:,22]=1
  elif name=='bad_declared_mode':mode=2
  elif name=='bad_mode_observation':x[:,31]=0;x[:,28]=1
  elif name=='bad_tick':cc.tick=0;tick=2
  else:x[:,0]=float('nan')
  try:cc.begin(tick,lambda:x,mode)
  except AssertionError:wrong.append(name)
  else:raise AssertionError(name)
 assert len(wrong)==14 and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 recipe=dict(source=dict(path=str(dst),bytes=dst.stat().st_size,SHA=H(dst),closed_updates=85,Adam=657660),CPU_components_only=True,planned_num_envs=104,planned_13groups_each8=True,pose_scope='Original approved normal plus roll/pitch +/-30/60/90 legal-q30 collision bank; actual original restore then explicit newfallreset required, not fabricated here',public_request='Original publicmode3 for300control thennormal; exact actual runtime phase must supply mode03 to controller',actual_DR_profile_and_fresh_seed_must_be_explicit=True,original_hardguards=dict(query=1e-6,COM=1e-5,mimic=.01,closure=.002,whole6clip=6,unknown_nonfinite_missingcallbacks='own durable failedprefix saved-stop'),no_qualification_threshold_or_success_claim=True,needs_complete_target_package_current_resource_desktop_MSVCRT_source_SDK_and_fresh_unused_native_full_allrow_CPU=True,existing_new_native336_on72_is_technical_admission_not3060_frozen_or_selfrescue_skill=True)
 with (E/'E3_CLOSED85_PUBLIC03_FROZEN_REVIEW_RECIPE_CPU_PREPARED.json').open('x',encoding='utf8') as f:json.dump(recipe,f,indent=2)
 out=dict(epoch=time.time(),passed_source_controller_CPU_components_only=True,source=recipe['source'],actor9inclSTD_initial_final_exact=True,two_tick_once_whole6_clip_selectedreset_public3_then0_CPU_fixture_pass=True,negative_cases=wrong,CPU_RNG_unchanged0CUDA0optimizer=True,no_target_package_or_GPU_Task_native_full_or_physical_skill_result=True,recipe=recipe)
 with (R/'E3_CLOSED85_FROZEN_PUBLIC03_COMPONENTS_SOURCE_AND14NEG_CPU_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(dict(passed_CPU_components=True,source85=True,Adam657660=True,negative_cases=14,no_3060_dispatch_or_skill_PASS=True)),flush=True)
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('E3_FROZEN_COMPONENT_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=__import__('traceback').format_exc(),CPU_only_no_remote_changes=True),f,indent=2)
  raise
