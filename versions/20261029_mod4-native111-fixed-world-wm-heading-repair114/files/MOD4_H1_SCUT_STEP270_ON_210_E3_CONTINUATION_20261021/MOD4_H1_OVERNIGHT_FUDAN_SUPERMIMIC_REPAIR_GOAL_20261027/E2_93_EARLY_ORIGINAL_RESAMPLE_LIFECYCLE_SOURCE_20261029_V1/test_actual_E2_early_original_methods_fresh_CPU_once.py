"""Actual saved source methods on synthetic CPU buffers, no SDK or PT calls."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,math,os,time,traceback,typing
B=Path(__file__).resolve().parent
def H(x):return hashlib.sha256(x).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 import torch as t
 path=B/'e2_early_original_resample_observer_v1.py';s=importlib.util.spec_from_file_location('_freshE2early',path);helper=importlib.util.module_from_spec(s);s.loader.exec_module(helper)
 source=lambda n:(B/('REFERENCE_ORIGINAL_'+n+'.txt')).read_bytes()
 command=(B/'REFERENCE_SAVED_SDK_command_manager.py.txt').read_bytes();velocity=(B/'REFERENCE_SAVED_SDK_velocity_command.py.txt').read_bytes();directional=source('e2_directional_spin_runtime_v1.py');sensor=source('sensor_resume_contract.py');checkpoint=source('e2_command_checkpoint_v1.py');body=source('spin_translation_math.py');contract=json.loads((B/'REQUIRED_ACTUAL_E2_TARGET_METHOD_AND_DOMAIN_SOURCE_CONTRACT.json').read_bytes())
 binding=helper.validate_actual_target_source(command,directional,checkpoint,sensor,contract);rejected=[]
 for label,args in [('changed_CommandTerm', (command.replace(b'self.command_counter[env_ids] += 1',b'self.command_counter[env_ids] += 2'),directional,checkpoint,sensor)),('E0_moving_amplitude_not_E2',(command,directional.replace(b'torch.full_like(u[:, 1], 4.0)',b'torch.full_like(u[:, 1], 1.5)'),checkpoint,sensor))]:
  try:helper.validate_actual_target_source(*args,contract)
  except AssertionError:rejected.append(label)
  else:raise AssertionError('Changed source accepted')
 n=260;scope={'torch':t,'math':math,'os':os,'Sequence':typing.Sequence}
 ct=next(n for n in ast.parse(command).body if isinstance(n,ast.ClassDef) and n.name=='CommandTerm');ut=next(n for n in ast.parse(velocity).body if isinstance(n,ast.ClassDef) and n.name=='UniformVelocityCommand')
 take=lambda cls,names:[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in names]
 init=ast.parse('''def __init__(self,cfg,env):
 self.cfg=cfg;self._env=env;self.num_envs=env.num_envs;self.device=env.device;self.metrics={};self.time_left=torch.zeros(self.num_envs);self.command_counter=torch.zeros(self.num_envs,dtype=torch.long)
def _update_metrics(self):
 pass
''').body
 uinit=ast.parse('''def __init__(self,cfg,env):
 super().__init__(cfg,env);self.robot=env.scene[cfg.asset_name];self.vel_command_b=torch.zeros(self.num_envs,3);self.heading_target=torch.zeros(self.num_envs);self.is_heading_env=torch.zeros(self.num_envs,dtype=torch.bool);self.is_standing_env=torch.zeros_like(self.is_heading_env)
 self._error_xy_sum=torch.zeros(self.num_envs);self._error_yaw_sum=torch.zeros(self.num_envs);self._step_count=torch.zeros(self.num_envs);self.metrics={k:torch.zeros(self.num_envs) for k in ('error_vel_xy','error_vel_yaw','success_rate')}
@property
def command(self):return self.vel_command_b
''').body
 c=ast.ClassDef(name='CommandTerm',bases=[ast.Name(id='object',ctx=ast.Load())],keywords=[],body=init+take(ct,('reset','_resample','compute')),decorator_list=[],type_params=[])
 u=ast.ClassDef(name='UniformVelocityCommand',bases=[ast.Name(id='CommandTerm',ctx=ast.Load())],keywords=[],body=uinit+take(ut,('reset','_resample_command','_update_command')),decorator_list=[],type_params=[])
 d=ast.parse(directional);cls=next(n for n in d.body if isinstance(n,ast.ClassDef) and n.name=='DirectionalSpinCommand');transition=next(n for n in d.body if isinstance(n,ast.FunctionDef) and n.name=='transition_yaw');bodyfn=next(n for n in ast.parse(body).body if isinstance(n,ast.FunctionDef) and n.name=='body_command')
 module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),c,u,bodyfn,transition,cls],type_ignores=[]);exec(compile(ast.fix_missing_locations(module),'selected_saved_CommandTerm_UniformVelocity_and_E2_source_only','exec'),scope)
 e=SimpleNamespace(num_envs=n,device='cpu',cfg=SimpleNamespace(seed=20260928),step_dt=.02,_sim_step_counter=0,extras={},scene={'robot':SimpleNamespace(data=SimpleNamespace(heading_w=SimpleNamespace(torch=t.zeros(n))))})
 cfg=SimpleNamespace(asset_name='robot',heading_command=False,rel_heading_envs=0.,rel_standing_envs=.1,resampling_time_range=(12.,16.),ranges=SimpleNamespace(heading=None,lin_vel_x=(-1.5,1.5),lin_vel_y=(0.,0.),ang_vel_z=(-4*math.pi,4*math.pi)),vel_xy_success_threshold=.1,vel_yaw_success_threshold=.1)
 evidence=json.loads((B/'E2_V4_INITIAL_RESAMPLE_GAP_SAVED_TEXT_AND_SOURCE_ORDER_EVIDENCE.json').read_bytes());actualenv=evidence['old_actual_env']['actual_env'];assert (float(actualenv['RM_CMD_VX_MIN']),float(actualenv['RM_CMD_VX_MAX']))==cfg.ranges.lin_vel_x
 original_env=dict(os.environ)
 try:
  os.environ.update({k:str(v) for k,v in actualenv.items() if k.startswith(('RM_SPIN','RM_PURE','RM_MOVING'))});cmd=scope['DirectionalSpinCommand'](cfg,e)
 finally:os.environ.clear();os.environ.update(original_env)
 globalrng=t.get_rng_state().clone();privaterng=cmd._mode_rng.get_state().clone();ids=t.arange(n);calls=dict(sensor=0,e2=0,reset=0,reset_return=None)
 sensorproof=dict(source_sha256=helper.MODEL,new_physical_episode=True,global_CPU_CUDA_streams_restored=True)
 e2proof=dict(source_SHA=helper.MODEL,source_has_E2_command_state=True,command_CUDA_disk_roundtrip_exact=True,new_physical_episode_not_PhysX_exactresume=True,moving_yaw_cap=4.)
 def reset():calls['reset']+=1;calls['reset_return']=cmd.reset(ids);return calls['reset_return']
 e.reset=reset
 def original_sensor(runner,env,path,log_dir):
  calls['sensor']+=1;t.set_rng_state(globalrng);cmd._mode_rng.set_state(privaterng);env.reset();return sensorproof
 sm=SimpleNamespace(resume_sensor_new_episode=original_sensor)
 def original_e2(runner,env,path,log_dir):
  # This surrogate replaces checkpoint IO ONLY; actual source order proved above.
  calls['e2']+=1;cmd._mode_rng.set_state(privaterng);sm.resume_sensor_new_episode(runner,env,path,log_dir);return e2proof
 em=SimpleNamespace(resume_e2_new_episode=original_e2)
 base=original_e2(None,e,'FRESH_NO_PT','NO_MODEL_IO');baseline={key:getattr(cmd,name).clone() for key,name in helper.FIELDS.items()};gr=t.get_rng_state().clone();pr=cmd._mode_rng.get_state().clone();ret=dict(calls['reset_return'])
 observer=helper.E2EarlyObserver(t,B/'FRESH_CPU_SELECTED_E2_EARLY_OBSERVER',expected_n=n);observer.install(type(cmd),sm,em);value=em.resume_e2_new_episode(None,e,'FRESH_NO_PT','NO_MODEL_IO')
 assert value is base is e2proof and calls['sensor']==calls['e2']==calls['reset']==2 and dict(calls['reset_return'])==ret
 assert all(t.equal(getattr(cmd,name),baseline[key]) for key,name in helper.FIELDS.items()) and t.equal(gr,t.get_rng_state()) and t.equal(pr,cmd._mode_rng.get_state())
 assert observer.verify_current_unchanged(cmd) and bool(cmd.is_moving_spin.any()) and bool((cmd.signed_yaw[cmd.is_moving_spin].abs()==4).all())
 panel=SimpleNamespace(real=e,cmd=cmd,written_phase=t.zeros(n),written_valid=t.zeros(n,dtype=t.bool));adopted=[]
 old=cmd.time_left.clone();cmd.time_left[0]-=.02;assert not observer.adopt_actual_written_start(panel) and not bool(panel.written_valid.any());cmd.time_left.copy_(old);rejected.append('changed_timer_keeps_unknown_no_buffer_write')
 old=cmd.command.clone();cmd.command[0,0]+=.1;assert not observer.verify_current_unchanged(cmd);cmd.command.copy_(old);rejected.append('changed_command_keeps_unknown')
 late=helper.E2EarlyObserver(t,B/'FRESH_CPU_UNUSED_LATE_NO_OUTPUT',expected_n=n);assert not late.adopt_actual_written_start(panel) and not bool(panel.written_valid.any());rejected.append('late_without_real_event_not_adopted')
 assert observer.adopt_actual_written_start(panel,lambda p:adopted.append(p['ids'].clone())) and len(adopted)==1 and panel.written_valid.all() and not panel.written_phase.any()
 assert t.equal(gr,t.get_rng_state()) and t.equal(pr,cmd._mode_rng.get_state())
 for i in range(825):e._sim_step_counter=(i+1)*8;cmd.compute(.02)
 assert (cmd.command_counter==2).all() and not observer.errors
 receipt=observer.finish();assert receipt['diagnostic_valid'] and receipt['initial_start_eligible'] and receipt['ids_count']==n
 C=type(cmd);assert '_resample' not in C.__dict__ and 'reset' not in C.__dict__ and C._write_dynamic.__code__.co_name=='_write_dynamic' and sm.resume_sensor_new_episode is original_sensor and em.resume_e2_new_episode is original_e2
 # Missing actual E2 state receipt cannot be mistaken for E0/ordinary reset.
 e._sim_step_counter=0;e2proof['source_has_E2_command_state']=False;negative=helper.E2EarlyObserver(t,B/'FRESH_CPU_MISSING_E2_STATE',expected_n=n);negative.install(C,sm,em);assert em.resume_e2_new_episode(None,e,'FRESH_NO_PT','NO_MODEL_IO') is e2proof;assert negative.eligible is None;negative.finish();e2proof['source_has_E2_command_state']=True;rejected.append('missing_E2_saved_private_state_scope_not_adopted')
 error=RuntimeError('fresh ORIGINAL sensor failure')
 def fail(*a,**k):raise error
 sm.resume_sensor_new_episode=fail;negative=helper.E2EarlyObserver(t,B/'FRESH_CPU_ORIGINAL_EXCEPTION',expected_n=n);negative.install(C,sm,em)
 try:em.resume_e2_new_episode(None,e,'FRESH_NO_PT','NO_MODEL_IO')
 except RuntimeError as got:assert got is error
 else:raise AssertionError('Original exception swallowed')
 assert negative.eligible is None;negative.finish();rejected.append('original_exception_object_propagated')
 put('ACTUAL_E2_SELECTED_EARLY_ORIGINAL_METHOD_CPU_LIFECYCLE_PROOF.json',dict(passed=True,scope='saved original SDK methods+actual E2 sampler on fresh260 CPU buffers; constructors/metrics/checkpoint IO are explicit stubs; NOT target SDK/GPU/model restoration',local_torch=t.__version__,actual_target_source_binding_still_pending=True,reference_source_contract=binding,E2_moving_signed_abs4_observed_on_fresh_CPU=True,original_timer_commands_flags_phase_counter_literal=True,original_global_private_RNG_literal=True,original_sensor_E2_resume_return_object_identity=True,original_reset_return_values_literal=True,real_original_write_before_phase_increment_observed=True,no_extra_original_reset_resample_write_or_actor=True,first_phase_adoption_changes_only_observer_buffers=True,optional_start_callback_receives_only_true_observed_packet=True,complete_command_instance_accumulator_NOT_implemented=True,original825_compute_methods_executed_without_physics=True,all260_synthetic_initial_timers_reached_original_counter2=True,rejected=rejected,original_exception_object_propagated=True,all_methods_restored=True,no_PT_NPZ_raw_gz_SDK_remote_or_GPU_calls=True))
 print(json.dumps(dict(passed=True,negative_cases=len(rejected),original_RNG_and_returns_equal=True,moving_yaw_abs4=True,no_target_or_model=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('LOCAL_E2_EARLY_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_model_or_remote=True));raise
