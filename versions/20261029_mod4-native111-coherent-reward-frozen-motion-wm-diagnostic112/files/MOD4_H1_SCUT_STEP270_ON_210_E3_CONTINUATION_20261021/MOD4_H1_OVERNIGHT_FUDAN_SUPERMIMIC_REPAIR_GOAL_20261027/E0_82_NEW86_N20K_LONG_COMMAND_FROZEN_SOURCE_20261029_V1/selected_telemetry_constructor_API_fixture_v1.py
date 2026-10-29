"""Fresh CPU API fixture of the actual selected telemetry constructor/methods."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,sys
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def run_selected_constructor_fixture(job,role,t,source_path=None,output=None):
 J=Path(job);assert role=='E0';out=Path(output) if output else J/('CPU_'+role+'_SELECTED_CONSTRUCTOR_FIXTURE');out.mkdir()
 source=Path(source_path) if source_path else J/'runtime/isaac/mod4/mod4_task.py';contract=json.loads((J/'GROUND_PROVIDER_SOURCE_CONTRACT.json').read_bytes())
 provider=load('original_flat_height_provider_v1',J/'original_flat_height_provider_v1.py');snap=load('lossless_snapshot_pinned75d683',J/'lossless_snapshot_pinned75d683.py')
 n=10;checks=[]
 tree=ast.parse(source.read_bytes());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='root_height_above_ground');scope={'torch':t};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),scope);module=SimpleNamespace(TERRAIN='flat',__file__=str(source),root_height_above_ground=scope[fn.name])
 queue_path=source.parent/'action_delay_physics_queue.py';qmod=load('_fresh_constructor_fixture_original_queue_'+role,queue_path);q=qmod.PhysicsActionQueue(n,'cpu',20260928,control_us=20000)
 dr=lambda:SimpleNamespace(state_dict=lambda:dict(value=t.zeros(n),rng=t.arange(16,dtype=t.uint8)))
 robot=SimpleNamespace(data=SimpleNamespace(root_state_w=t.zeros(n,13),root_pos_w=t.zeros(n,3),joint_pos=t.zeros(n,30),joint_vel=t.zeros(n,30),applied_torque=t.zeros(n,30),joint_stiffness=t.full((n,30),2000.),root_lin_vel_b=t.zeros(n,3),root_ang_vel_b=t.zeros(n,3),heading_w=t.zeros(n),projected_gravity_b=t.tensor([[0.,0.,-1.]]).expand(n,3)))
 robot.data.root_pos_w[:,2]=.25;robot.data.root_state_w[:,2]=.25
 original_calls=dict(reset=0,write=0,resample=0)
 def reset(ids):original_calls['reset']+=1
 cmd=SimpleNamespace(_resample_command=lambda ids:original_calls.__setitem__('resample',original_calls['resample']+1),_write_dynamic=lambda ids:original_calls.__setitem__('write',original_calls['write']+1),manual_evaluation_mode=False,progress_goal=.5,pure_max=4*__import__('math').pi,command=t.zeros(n,3),phase_elapsed=t.zeros(n),is_standing_env=t.zeros(n,dtype=t.bool),is_pure_spin=t.zeros(n,dtype=t.bool),is_moving_spin=t.zeros(n,dtype=t.bool),is_transition_spin=t.zeros(n,dtype=t.bool),signed_yaw=t.zeros(n),world_direction=t.zeros(n))
 e=SimpleNamespace(num_envs=n,device='cpu',physics_dt=.0025,step_dt=.02,cfg=SimpleNamespace(decimation=8),scene={'robot':robot},command_manager=SimpleNamespace(get_term=lambda name:cmd),termination_manager=SimpleNamespace(active_terms=('timeout',),terminated=t.zeros(n,dtype=t.bool),time_outs=t.zeros(n,dtype=t.bool),get_term=lambda name:t.zeros(n,dtype=t.bool)),action_manager=SimpleNamespace(action=t.zeros(n,6)),_physics_action_delay=SimpleNamespace(queue=q,state_dict=q.state_dict),_reset_idx=reset,_integrated_contact=SimpleNamespace(tick=0,impulse=t.zeros(n,2,3),history=t.zeros(n,2,3)),_feedback_100hz_tick=0,_own_native_capture=False,e3_capture=False,e3_stepping=False,e3_shapes=list(range(34)),_mod4_mode_bit=t.zeros(n,dtype=t.long),recovery_original_soft={'bad_orientation':t.zeros(n,dtype=t.bool),'base_contact':t.zeros(n,dtype=t.bool)})
 for name in ('_sensor_mild','_feedback_delay_mild','_gas_damping','_chassis_com','_explicit_pd'):setattr(e,name,dr())
 e._spring_pressure=dr();e._spring_pressure.ids=[0,1];e._spring_pressure.nominal=t.tensor([2000.,2000.])
 load('e0_original_profile_catalog_v1',J/'e0_original_profile_catalog_v1.py');load('e0_observed_command_instances_v1',J/'e0_observed_command_instances_v1.py');tele=load('_selected_actual_E0_telemetry_fixture',J/'e0_long_command_domain_telemetry_v1.py');cls=tele.E0Panel
 del e._own_native_capture;del e.e3_capture;del e.e3_stepping;del e.e3_shapes;del e._mod4_mode_bit;del e.recovery_original_soft
 assert not hasattr(e,'_mod4_ground_z') and not hasattr(e,'_own_native_capture');rng=t.get_rng_state().clone();task={'source_SHA':'synthetic_constructor_API_fixture_only','ground_provider_contract':contract}
 panel=cls(e,t,out,task,ground_module=module)
 try:
  assert not hasattr(e,'_mod4_ground_z') and original_calls==dict(reset=0,write=0,resample=0) and t.equal(rng,t.get_rng_state());checks.append('actual selected constructor accepts original flat API WITHOUT ground cache/no injection/no original call/no RNG draw')
  assert bool((panel.ground.height()==.25).all()) and bool((panel.ground.ground_z()==0).all());checks.append('original root-height fallback semantics retained, not injected zero')
  from tensordict import TensorDict
  obs=TensorDict({'policy':t.zeros(n,35),'critic':t.zeros(n,38)},batch_size=[n]);panel.physical();panel.begin(0,obs);panel.requested(t.zeros(n,6))
  for tick in range(8):
   for group in ('legs','wheels'):e._physics_action_delay.queue.apply(group,tick)
  if False:e.recovery.begin();e.recovery.update(-t.ones(n),t.zeros(n),t.zeros(n))
  panel.terminal();e._integrated_contact.tick=8;e._feedback_100hz_tick=2;panel.after(0)
  assert panel.trace_controls==[1] and panel.apply_calls=={'legs':8,'wheels':8};checks.append('actual physical/begin/requested/terminal/after methods cover every new ground reference and real original queue API')
  cmd._resample_command(t.tensor([0,1]));e._reset_idx(t.tensor([0]));assert original_calls==dict(reset=1,write=0,resample=1);checks.append('actual selected command/reset observer hooks call each original exactly once without RNG')
  assert not hasattr(e,'_mod4_ground_z') and t.equal(rng,t.get_rng_state());checks.append('full fixture never injects cache or advances global RNG')
 finally:panel.uninstall()
 rejected=[]
 for name,bad in [('nonflat module',SimpleNamespace(TERRAIN='field')),('wrong source contract SHA',None)]:
  try:
   if bad is not None:provider.OriginalFlatHeightProvider(e,t,contract,bad)
   else:provider.OriginalFlatHeightProvider(e,t,dict(contract,task_source_SHA='0'*64),module)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Bad provider domain accepted')
 p=out/('E0_selected_profile_actual_domain.jsonl.gz' if role=='E0' else 'E3_selected_recipe_actual_domain.jsonl.gz')
 # Actual component E2 file uses its original title; only fresh output is hashed.
 if not p.exists():p=next(out.glob('*.gz'))
 return dict(passed=True,scope='fresh CPU structural constructor/API fixture, NOT real SDK environment or GPU',role=role,checks=checks,rejected=rejected,source_task_SHA=contract['task_source_SHA'],no_ground_attribute_injected=True,no_original_actor_RNG_SDK_raycast_or_physics=True,fresh_synthetic_output=dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
