"""Only saved source text + fresh CPU buffers; no SDK/model/raw/host calls."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,importlib.util,json,math,os,sys,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
S=T/'reports/V98_H1_FAILED_PREFIX_AND_ACTUAL_COMMAND_SDK_SOURCE_RETURNED_ACTUAL.json'
E0=L/'E0_82_NEW86_N20K_LONG_COMMAND_FROZEN_SOURCE_20261029_V1'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 source=json.loads(S.read_bytes());refs={}
 for row in source['actual_installed_SDK_source_texts']:
  raw=row['text'].encode();assert len(raw)==row['bytes'] and H(raw)==row['SHA']
  name=Path(row['path']).name
  if name in ('command_manager.py','velocity_command.py'):
   refs[name]=row
   with (B/('REFERENCE_OLD210_'+name+'.txt')).open('x',encoding='utf8') as f:f.write(row['text'])
 helper=load('_new_early_source_hook',B/'e0_early_original_resample_passthrough_observer_v1.py')
 contract=dict(kind='E0_required_actual_target_CommandTerm_method_AST_binding_v1',reference_capture_path=str(S),reference_not_actual86_proof=True,reference_sources=[{k:r[k] for k in ('path','bytes','SHA')} for r in refs.values()],CommandTerm_method_AST_SHAs={name:H(helper.method_ast(refs['command_manager.py']['text'],'CommandTerm',name).encode()) for name in ('reset','_resample','compute')},actual_target_SDK_method_source_and_receipt_binding='PENDING',no_copy_of_old_SDK_identity_to_new_host=True)
 put('REQUIRED_TARGET_COMMANDTERM_METHOD_SOURCE_CONTRACT_V1.json',contract)
 helper.validate_actual_target_source(refs['command_manager.py']['text'],contract)
 changed=refs['command_manager.py']['text'].replace('self.command_counter[env_ids] += 1','self.command_counter[env_ids] += 2');assert changed!=refs['command_manager.py']['text']
 try:helper.validate_actual_target_source(changed,contract)
 except AssertionError:pass
 else:raise AssertionError('Changed real method source accepted')
 mf=E0/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';manifest=json.loads(mf.read_bytes());rows={r['relative']:r for r in manifest['files']}
 def py(name):
  row=rows['runtime/isaac/mod4/'+name];raw=Path(row['local_path']).read_bytes();assert H(raw)==row['SHA'];return raw
 directional=py('directional_spin_runtime.py');sensor=py('sensor_resume_contract.py');entry=py('train_chassis_pd_resume_ppo.py');body=py('spin_translation_math.py')
 st=ast.parse(sensor);sf=next(x for x in st.body if isinstance(x,ast.FunctionDef) and x.name=='resume_sensor_new_episode')
 envreset=next(x for x in ast.walk(sf) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='env' and x.func.attr=='reset')
 rngrestore=[x for x in ast.walk(sf) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('set_rng_state','set_rng_state_all')]
 assert len(rngrestore)==2 and all(x.lineno<envreset.lineno for x in rngrestore)
 assert len([x for x in ast.walk(sf) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and isinstance(x.func.value,ast.Name) and x.func.value.id=='env' and x.func.attr=='reset'])==1
 # Command sampler/timer is freshly reset after restored RNG. No timer/command load in this source chain.
 assert not any(isinstance(x,ast.Attribute) and x.attr in ('time_left','command_counter') for x in ast.walk(sf))
 main=next(x for x in ast.parse(entry).body if isinstance(x,ast.FunctionDef) and x.name=='main');workcall=next(x for x in ast.walk(main) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='bounded_learn');resumecall=next(x for x in ast.walk(main) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='resume_chassis_pd_new_episode');assert resumecall.lineno<workcall.lineno
 import torch as t
 assert not t.cuda.is_initialized();n=26
 namespace={'torch':t,'math':math,'os':os,'Sequence':__import__('typing').Sequence}
 command=next(x for x in ast.parse(refs['command_manager.py']['text']).body if isinstance(x,ast.ClassDef) and x.name=='CommandTerm')
 uniform=next(x for x in ast.parse(refs['velocity_command.py']['text']).body if isinstance(x,ast.ClassDef) and x.name=='UniformVelocityCommand')
 def methods(cls,names):return [x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name in names]
 base_init=ast.parse('''def __init__(self,cfg,env):
 self.cfg=cfg;self._env=env;self.num_envs=env.num_envs;self.device=env.device
 self.metrics={};self.time_left=torch.zeros(self.num_envs);self.command_counter=torch.zeros(self.num_envs,dtype=torch.long)
def _update_metrics(self):
 pass
''').body
 uniform_init=ast.parse('''def __init__(self,cfg,env):
 super().__init__(cfg,env);self.robot=env.scene[cfg.asset_name]
 self.vel_command_b=torch.zeros(self.num_envs,3);self.heading_target=torch.zeros(self.num_envs)
 self.is_heading_env=torch.zeros(self.num_envs,dtype=torch.bool);self.is_standing_env=torch.zeros_like(self.is_heading_env)
 self._error_xy_sum=torch.zeros(self.num_envs);self._error_yaw_sum=torch.zeros(self.num_envs);self._step_count=torch.zeros(self.num_envs)
 self.metrics={k:torch.zeros(self.num_envs) for k in ('error_vel_xy','error_vel_yaw','success_rate')}
@property
def command(self):return self.vel_command_b
''').body
 c=ast.ClassDef(name='CommandTerm',bases=[ast.Name(id='object',ctx=ast.Load())],keywords=[],body=base_init+methods(command,('reset','_resample','compute')),decorator_list=[],type_params=[])
 u=ast.ClassDef(name='UniformVelocityCommand',bases=[ast.Name(id='CommandTerm',ctx=ast.Load())],keywords=[],body=uniform_init+methods(uniform,('reset','_resample_command','_update_command')),decorator_list=[],type_params=[])
 dc=next(x for x in ast.parse(directional).body if isinstance(x,ast.ClassDef) and x.name=='DirectionalSpinCommand');transition=next(x for x in ast.parse(directional).body if isinstance(x,ast.FunctionDef) and x.name=='transition_yaw');bodyfn=next(x for x in ast.parse(body).body if isinstance(x,ast.FunctionDef) and x.name=='body_command')
 module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),c,u,bodyfn,transition,dc],type_ignores=[]);exec(compile(ast.fix_missing_locations(module),'<actual original command reset/resample/compute and E0 methods, synthetic constructor buffers>','exec'),namespace)
 env=SimpleNamespace(num_envs=n,device='cpu',cfg=SimpleNamespace(seed=20260928),step_dt=.02,_sim_step_counter=0,extras={},scene={'robot':SimpleNamespace(data=SimpleNamespace(heading_w=SimpleNamespace(torch=t.zeros(n))))})
 cfg=SimpleNamespace(asset_name='robot',heading_command=False,rel_heading_envs=0.,rel_standing_envs=.1,resampling_time_range=(12.,16.),ranges=SimpleNamespace(heading=None,lin_vel_x=(-1.5,1.5),lin_vel_y=(0.,0.),ang_vel_z=(-4*math.pi,4*math.pi)),vel_xy_success_threshold=.1,vel_yaw_success_threshold=.1)
 original_env=dict(os.environ);os.environ.update(RM_SPIN_WORLD_PROGRESS_M_S='.5',RM_PURE_SPIN_FRACTION='.30',RM_MOVING_SPIN_FRACTION='.20',RM_SPIN_TRANSITION_WITHIN_PURE=str(1/3),RM_SPIN_MAX_RAD_S=str(4*math.pi),RM_SPIN_BODY_SPEED_LIMIT_M_S='1.5')
 try:cmd=namespace['DirectionalSpinCommand'](cfg,env)
 finally:os.environ.clear();os.environ.update(original_env)
 cls=type(cmd);global_rng=t.get_rng_state().clone();private_rng=cmd._mode_rng.get_state().clone();proof_return=dict(source_sha256=helper.MODEL,new_physical_episode=True,global_CPU_CUDA_streams_restored=True)
 calls={'reset':0,'returned':None};ids=t.arange(n)
 def reset_env():calls['reset']+=1;calls['returned']=cmd.reset(ids);return calls['returned']
 env.reset=reset_env
 def original_resume(runner,env,path,log):
  t.set_rng_state(global_rng);cmd._mode_rng.set_state(private_rng);env.reset();return proof_return
 resume_module=SimpleNamespace(resume_sensor_new_episode=original_resume)
 baseline=original_resume(None,env,'synthetic_no_PT','no_IO');before={k:getattr(cmd,k).clone() for k in ('time_left','command_counter','phase_elapsed','command','world_direction','signed_yaw','is_standing_env','is_pure_spin','is_moving_spin','is_transition_spin')};baselineglobal=t.get_rng_state().clone();baselineprivate=cmd._mode_rng.get_state().clone();basereturn=dict(calls['returned'])
 observer=helper.EarlyResampleObserver(t,B/'FRESH_CPU_EARLY_OBSERVER_ACTUAL',expected_n=n);observer.install(cls,resume_module);value=resume_module.resume_sensor_new_episode(None,env,'synthetic_no_PT','no_IO')
 assert value is baseline is proof_return and calls['reset']==2 and dict(calls['returned'])==basereturn
 assert all(t.equal(getattr(cmd,k),x) for k,x in before.items()) and t.equal(t.get_rng_state(),baselineglobal) and t.equal(cmd._mode_rng.get_state(),baselineprivate)
 assert observer.verify_current_unchanged_at_first_control(cmd)
 # The real original E0 reset chose these timers/commands; observer did not draw them.
 packet=observer.eligible;assert len(packet['ids'])==n and packet['physics_tick']==0
 saved=cmd.time_left.clone();cmd.time_left[0]-=.02;assert not observer.verify_current_unchanged_at_first_control(cmd);cmd.time_left.copy_(saved)
 # Late/no-event observer is never promoted.
 late=helper.EarlyResampleObserver(t,B/'FRESH_CPU_LATE_NO_CAPTURE',expected_n=n);assert not late.verify_current_unchanged_at_first_control(cmd)
 catalog=load('e0_original_profile_catalog_v1',E0/'e0_original_profile_catalog_v1.py');sys.modules['e0_original_profile_catalog_v1']=catalog
 bookmod=load('_actual_frozen_E0_instance_accumulator',E0/'e0_observed_command_instances_v1.py');book=bookmod.CommandInstances(t,n,'cpu')
 context=lambda:dict(key=catalog.classify(t,cmd.is_standing_env,cmd.is_pure_spin,cmd.is_moving_spin,cmd.is_transition_spin,cmd.command,cmd.signed_yaw),command_uid=t.zeros(n,dtype=t.long),episode=t.zeros(n,dtype=t.long),command=cmd.command,direction=cmd.world_direction,signed_yaw=cmd.signed_yaw)
 panel=SimpleNamespace(cmd=cmd,real=env,instances=book,written_phase=t.zeros(n),written_valid=t.zeros(n,dtype=t.bool),instance_context=context)
 try:late.adopt_only_actually_observed_start(panel)
 except AssertionError:pass
 else:raise AssertionError('Late/no-event initial start fabricated')
 assert not book.active.any();observer.adopt_only_actually_observed_start(panel);assert book.active.all() and book.known.all() and panel.written_valid.all()
 # Actual original compute/resample methods run on fresh CPU, no physics. Every original
 # first timer eventually resamples once; it is a SOURCE lifecycle proof, not skill data.
 for i in range(825):env._sim_step_counter=(i+1)*8;cmd.compute(.02)
 assert bool((cmd.command_counter==2).all()) and not observer.errors
 receipt=observer.finish();assert receipt['new_initial_start_eligible'] and receipt['real_initial_sampled_command_JSONL_producer']['rows']==n
 assert '_resample' not in cls.__dict__ and 'reset' not in cls.__dict__ and resume_module.resume_sensor_new_episode is original_resume
 # Producer hash checked ONLY on this new tiny synthetic test file, never originalraw.
 producer=receipt['real_initial_sampled_command_JSONL_producer'];raw=Path(producer['path']).read_bytes();assert H(raw)==producer['SHA'] and len(raw)==producer['bytes']
 # Original error stays original; no event/oldstate is fabricated by observers.
 def bad_resume(*a,**kw):raise RuntimeError('synthetic ORIGINAL resume failure')
 resume_module.resume_sensor_new_episode=bad_resume;negative=helper.EarlyResampleObserver(t,B/'FRESH_CPU_NEGATIVE_ERROR',expected_n=n);negative.install(cls,resume_module)
 try:resume_module.resume_sensor_new_episode(None,env,'no_PT','no_IO')
 except RuntimeError as exc:assert str(exc)=='synthetic ORIGINAL resume failure'
 else:raise AssertionError('Original error swallowed')
 assert negative.eligible is None;negative.finish();assert resume_module.resume_sensor_new_episode is bad_resume
 put('ACTUAL_ORIGINAL_METHOD_CPU_LIFECYCLE_RNG_RETURN_PROOF.json',dict(passed=True,scope='actual saved original methods+E0 class, fresh CPU synthetic constructor/metrics only, NOT targetSDK/GPU',local_versions=dict(torch=t.__version__),target_method_AST_admission_pending=True,reference_contract=contract,real_source_entry_resume_before_work_line=[resumecall.lineno,workcall.lineno],real_sensor_global_RNG_restore_lines=[x.lineno for x in rngrestore],real_sensor_single_env_reset_after_restore_line=envreset.lineno,original_command_timer_not_restored_by_sensor_resume_source=True,source_lineage=dict(directional_SHA=H(directional),sensor_resume_SHA=H(sensor),entry_SHA=H(entry)),original_vs_hook_global_RNG_literal=True,original_vs_hook_private_RNG_literal=True,original_vs_hook_sampled_timer_commands_flags_counter_literal=True,original_resume_return_object_literal_identity=True,original_reset_return_values_literal=True,original_reset_calls_one_each=True,changed_current_timer_rejects_initial_adoption=True,late_no_event_stays_unknown=True,actual_frozen_instance_accumulator_adopt_only_real_observed_start_passed=True,original_reset_resample_methods_actual825_compute_steps=True,all26_initial_commands_reached_next_original_sampler_counter2=True,not_actual_skill_or_GPU_command_exposure=True,original_exception_preserved=True,all_methods_restored=True,typedJSONL_producer_path_bytes_SHA_checked_only_fresh_synthetic=True,no_old_model_PT_raw_NPZ_gz_SDK_host_read=True))
 print(json.dumps(dict(passed=True,scope='SOURCE/fresh CPU only',original_RNG_and_returns_literal=True,target_admission_pending=True,original_initial_timer_completion_synthetic26=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('ORIGINAL_SOURCE_LIFECYCLE_CPU_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_model_SDK_or_remote=True));raise
