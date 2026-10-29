"""Actual SDK SOURCE method lifecycle using fresh CPU API buffers, no SDK scene."""
from pathlib import Path
from types import SimpleNamespace
import ast,json,math,os

def run_fixture(J,t,command_raw,velocity_raw,out):
    J=Path(J);out=Path(out);out.mkdir(exist_ok=False)
    from e0_early_original_resample_passthrough_observer_v1 import EarlyResampleObserver,validate_actual_target_source,MODEL
    from e0_original_profile_catalog_v1 import classify
    from e0_observed_command_instances_v1 import CommandInstances
    contract=json.loads((J/'REQUIRED_TARGET_COMMANDTERM_METHOD_SOURCE_CONTRACT_V1.json').read_bytes())
    actual_proof=validate_actual_target_source(command_raw,contract)
    directional=(J/'runtime/isaac/mod4/directional_spin_runtime.py').read_bytes();body=(J/'runtime/isaac/mod4/spin_translation_math.py').read_bytes()
    namespace={'torch':t,'math':math,'os':os}
    command=next(x for x in ast.parse(command_raw).body if isinstance(x,ast.ClassDef) and x.name=='CommandTerm')
    uniform=next(x for x in ast.parse(velocity_raw).body if isinstance(x,ast.ClassDef) and x.name=='UniformVelocityCommand')
    def selected(cls,names):return [x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name in names]
    base_init=ast.parse('''def __init__(self,cfg,env):
 self.cfg=cfg;self._env=env;self.num_envs=env.num_envs;self.device=env.device
 self.metrics={};self.time_left=torch.zeros(self.num_envs);self.command_counter=torch.zeros(self.num_envs,dtype=torch.long)
def _update_metrics(self):pass
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
    c=ast.ClassDef(name='CommandTerm',bases=[ast.Name(id='object',ctx=ast.Load())],keywords=[],body=base_init+selected(command,('reset','_resample','compute')),decorator_list=[],type_params=[])
    u=ast.ClassDef(name='UniformVelocityCommand',bases=[ast.Name(id='CommandTerm',ctx=ast.Load())],keywords=[],body=uniform_init+selected(uniform,('reset','_resample_command','_update_command')),decorator_list=[],type_params=[])
    tree=ast.parse(directional);dc=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='DirectionalSpinCommand');transition=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='transition_yaw');bodyfn=next(x for x in ast.parse(body).body if isinstance(x,ast.FunctionDef) and x.name=='body_command')
    module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),c,u,bodyfn,transition,dc],type_ignores=[]);exec(compile(ast.fix_missing_locations(module),'<actual installed method/E0 source; fresh CPU constructor buffers>','exec'),namespace)
    n=26;env=SimpleNamespace(num_envs=n,device='cpu',cfg=SimpleNamespace(seed=20260928),step_dt=.02,_sim_step_counter=0,extras={},scene={'robot':SimpleNamespace(data=SimpleNamespace(heading_w=SimpleNamespace(torch=t.zeros(n))))})
    cfg=SimpleNamespace(asset_name='robot',heading_command=False,rel_heading_envs=0.,rel_standing_envs=.1,resampling_time_range=(12.,16.),ranges=SimpleNamespace(heading=None,lin_vel_x=(-1.5,1.5),lin_vel_y=(0.,0.),ang_vel_z=(-4*math.pi,4*math.pi)),vel_xy_success_threshold=.1,vel_yaw_success_threshold=.1)
    saved_env=dict(os.environ)
    try:
        os.environ.update(RM_SPIN_WORLD_PROGRESS_M_S='.5',RM_PURE_SPIN_FRACTION='.30',RM_MOVING_SPIN_FRACTION='.20',RM_SPIN_TRANSITION_WITHIN_PURE=str(1/3),RM_SPIN_MAX_RAD_S=str(4*math.pi),RM_SPIN_BODY_SPEED_LIMIT_M_S='1.5')
        cmd=namespace['DirectionalSpinCommand'](cfg,env)
    finally:os.environ.clear();os.environ.update(saved_env)
    global_rng=t.get_rng_state().clone();private_rng=cmd._mode_rng.get_state().clone();calls={'reset':0,'result':None};ids=t.arange(n)
    def reset():calls['reset']+=1;calls['result']=cmd.reset(ids);return calls['result']
    env.reset=reset;original_proof=dict(source_sha256=MODEL,new_physical_episode=True,global_CPU_CUDA_streams_restored=True)
    def resume(*a):t.set_rng_state(global_rng);cmd._mode_rng.set_state(private_rng);env.reset();return original_proof
    resume_module=SimpleNamespace(resume_sensor_new_episode=resume);baseline=resume(None,env,'synthetic_no_PT','no_IO')
    initial={k:getattr(cmd,k).clone() for k in ('time_left','command_counter','phase_elapsed','command','world_direction','signed_yaw','is_standing_env','is_pure_spin','is_moving_spin','is_transition_spin')};expected_rng=t.get_rng_state().clone();expected_private=cmd._mode_rng.get_state().clone();expected_return=dict(calls['result'])
    observer=EarlyResampleObserver(t,out/'early',expected_n=n);observer.install(type(cmd),resume_module);returned=resume_module.resume_sensor_new_episode(None,env,'synthetic_no_PT','no_IO')
    assert returned is baseline is original_proof and calls['reset']==2 and dict(calls['result'])==expected_return
    assert all(t.equal(getattr(cmd,k),v) for k,v in initial.items()) and t.equal(t.get_rng_state(),expected_rng) and t.equal(cmd._mode_rng.get_state(),expected_private)
    book=CommandInstances(t,n,'cpu');context=lambda:dict(key=classify(t,cmd.is_standing_env,cmd.is_pure_spin,cmd.is_moving_spin,cmd.is_transition_spin,cmd.command,cmd.signed_yaw),command_uid=t.zeros(n,dtype=t.long),episode=t.zeros(n,dtype=t.long),command=cmd.command,direction=cmd.world_direction,signed_yaw=cmd.signed_yaw)
    panel=SimpleNamespace(cmd=cmd,real=env,instances=book,written_phase=t.zeros(n),written_valid=t.zeros(n,dtype=t.bool),instance_context=context)
    late=EarlyResampleObserver(t,out/'late',expected_n=n)
    try:late.adopt_only_actually_observed_start(panel)
    except AssertionError:pass
    else:raise AssertionError('Unobserved initialstart adopted')
    assert not book.active.any();observer.adopt_only_actually_observed_start(panel);assert book.active.all() and book.known.all() and panel.written_valid.all()
    timer=cmd.time_left.clone();cmd.time_left[0]-=.02;assert not observer.verify_current_unchanged_at_first_control(cmd);cmd.time_left.copy_(timer)
    for i in range(825):env._sim_step_counter=(i+1)*8;cmd.compute(.02)
    assert bool((cmd.command_counter==2).all());receipt=observer.finish();assert receipt['diagnostic_valid'] and receipt['new_initial_start_eligible']
    assert '_resample' not in type(cmd).__dict__ and 'reset' not in type(cmd).__dict__ and resume_module.resume_sensor_new_episode is resume
    # Exact new acted/zero-control/complete denominator lifecycle on selected class.
    acc=CommandInstances(t,10,'cpu');z=t.zeros(10);ctx=dict(key=t.arange(10),command_uid=t.zeros(10,dtype=t.long),episode=t.zeros(10,dtype=t.long),command=t.zeros(10,3),direction=z,signed_yaw=t.ones(10),written_phase_valid=t.ones(10,dtype=t.bool),written_phase=z)
    acc.open(t.arange(10),ctx,True);error=dict(errors=[t.ones(10)]*3);acc.observe(ctx,error);acc.close(t.arange(5),'resample');acc.close(t.arange(5,8),'reset')
    ctx['command_uid']+=1;acc.open(t.arange(5),ctx,True)
    out2=out/'instances';out2.mkdir(parents=True);summary=acc.finish(out2,MODEL);ps=summary['profiles']
    assert sum(x['closed_instance_events'] for x in ps)==15 and sum(x['acted_instance_events'] for x in ps)==10 and sum(x['zero_control_instance_events'] for x in ps)==5
    assert sum(x['fully_observed_resample_to_resample_instance_events'] for x in ps)==5 and sum(x['acted_reset_ended_events'] for x in ps)==3 and sum(x['acted_window_end_events'] for x in ps)==2
    assert summary['typed_JSONL_producer_index']['rows']==15
    return dict(passed=True,scope='actual installed source methods and selected E0 constructor/API using fresh26 CPU buffers, NOT real SDK environment/model/GPU',actual_target_command_source=actual_proof,original_global_private_RNG_literal=True,original_commands_timer_flags_counter_literal=True,original_resume_return_object_identity=True,original_reset_return_literal=True,actual_observed_start_adoption_positive=True,late_and_changed_timer_negative=True,original_method825_compute_source_fixture=True,model_or_saved_tensor_decode=0,acted10_zero5_complete5_reset3_window2_fresh_fixture=True,typed_JSONL_producer_index=summary['typed_JSONL_producer_index'],full20k_GPU_native24_still_pending=True)
