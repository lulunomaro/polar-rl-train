"""One NEW off-source ABI CPU purpose. No Torch/SDK/model/old fixtures."""
from pathlib import Path
from types import SimpleNamespace as NS
import ast,json,time,traceback
from dr0_contract import ENV,KIND,validate_snapshot
N=Path(__file__).resolve().parent;R=N/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 assert json.loads((R/'CPU_DR0_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 put(R/'CPU_DR0_ONCE_CONSUMED.json',dict(epoch=time.time(),old_fixtures=0))
 names=['dr0_contract.py','derive_dr0_off_modules.py','mild_dr.py','action_delay_training_env.py','spring_pressure_training_env.py','dr0_actual_readback.py','check_new_dr0_off_interface_once.py']
 sources={x:(N/x).read_text(encoding='utf8') for x in names}
 for s in sources.values():ast.parse(s)
 enabled=[]
 class Base:
  def __init__(self,*a,**kw):self.cfg=NS(seed=20260928)
 def adapter(env,on,seed,**kw):enabled.append(on);assert on is False;return NS()
 for name,cls,base,adaptername in [('action_delay_training_env.py','ActionDelayMod4Env','DelaySensorMod4Env','PhysicalActionDelayAdapter'),('spring_pressure_training_env.py','SpringPressureMod4Env','ActionDelayMod4Env','LearningSpringPressure')]:
  tree=ast.parse(sources[name]);node=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==cls)
  ns={'os':NS(environ=dict(ENV)),base:Base,adaptername:adapter,'PROFILE':'gas_stiffness_independent_episode_090_110_v1'}
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<new OFF constructor>','exec'),ns);ns[cls]()
 assert enabled==[False,False]
 tree=ast.parse(sources['mild_dr.py']);parents={}
 for p in ast.walk(tree):
  for child in ast.iter_child_nodes(p):parents[child]=p
 random_calls=[x for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('rand','randint','uniform_')]
 assert len(random_calls)==4
 for call in random_calls:
  a=call
  while a in parents and not isinstance(a,ast.IfExp):a=parents[a]
  assert isinstance(a,ast.IfExp) and ast.unparse(a.test)=='self.dr0' and call in list(ast.walk(a.orelse))
 assert "self.mass[ids] * factor" in sources['mild_dr.py'] and "self.inertia[ids] * factor" in sources['mild_dr.py']
 assert "torch.tensor([.9])" in sources['mild_dr.py'] and "self.profile == 'all_off_nominal_v1'" in sources['mild_dr.py']
 snap=dict(kind=KIND,actual_SDK_readback=False,synthetic_only=True,closure_m=.002,mimic_rad=.01)
 for k in ('mass_inertia_authored_baseline','motor_gains_one','wheel_mu_original_nominal09','nonwheel_material_authored_baseline','ground_cfg_unchanged_from_source','sensor_noise_and_bias_off','feedback_added_delay_zero','physical_target_added_delay_zero','gas_stiffness_nominal2000','gas_damping_nominal3','COM_delta_zero_AUTHORED_absolute_preserved','PD_nominal','new_DR0_streams_not_old_DR_restore'):snap[k]=True
 assert validate_snapshot(json.loads(json.dumps(snap)),synthetic=True)
 rejects=0
 for value,synthetic in [(snap,False),(dict(snap,motor_gains_one=False),True),(dict(snap,mimic_rad=.05),True)]:
  try:validate_snapshot(value,synthetic=synthetic)
  except AssertionError:rejects+=1
  else:raise AssertionError('New DR0 admission refusal did not reject')
 put(R/'CPU_DR0_NEW_OFF_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,source_AST=7,D4_D5_actual_new_off_constructor_arguments=[False,False],
  D0_random_sites_all_guarded_off_branches=4,nominal_mu09_from_original_bucket0=True,new_JSON_synthetic_snapshot=1,new_refusals=rejects,
  actual_SDK_readback=False,model_asset_raw_Torch_SDK_network_Git=0,old_fixture_replays=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'CPU_DR0_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
