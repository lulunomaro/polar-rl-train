"""Tiny generic tensors + actual source validators, never a real model read."""
from pathlib import Path
import ast,copy,hashlib,json,sys
import torch
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D))
import review_H1_native87R3_finals_CPU_unused_once as r
from native87R3_event_curve_summary_v1 import summarize_rows
checks=[]
def yes(v,name):
 assert v,name
 checks.append(name)
def refuse(fn,name):
 try:fn()
 except (AssertionError,RuntimeError,ValueError,KeyError,TypeError):checks.append(name);return
 raise AssertionError('unexpected acceptance '+name)
data=b'generic tiny metadata loader fixture';SHA=hashlib.sha256(data).hexdigest();calls=[]
pool=r.OneInitialLoadPool(reader=lambda p:(calls.append(str(p)) or data),loader=lambda raw:dict(tiny=torch.ones(1)))
a=pool.load('synthetic_metadata_input',SHA,'first');b=pool.load('synthetic_metadata_input',SHA,'second_reference')
yes(a is b and len(calls)==1 and len(pool.records)==1,'one_initial_read_and_in_memory_reuse')
calls=[];pool=r.OneInitialLoadPool(reader=lambda p:(calls.append(str(p)) or data),loader=lambda raw:{})
refuse(lambda:pool.load('synthetic','a'*64,'bad'),'bad_INITIAL_SHA_refused')
refuse(lambda:pool.load('synthetic','a'*64,'retry'),'failed_initial_read_not_retried')
yes(len(calls)==1 and pool.records[0]['completed'] is False,'failed_attempt_record_preserved')
yes(not r.exact(dict(flag=1),dict(flag=True)),'strict_contract_bool_integer_types_not_conflated')
refuse(lambda:r.finite(dict(value=torch.tensor([float('nan')]))),'nonfinite_native_tensor_refused')
bootstrap=dict(actor_state_dict={**{f'a{i}':torch.full((1,),float(i)) for i in range(8)},'distribution.std_param':torch.ones(6)},
 critic_state_dict={f'c{i}':torch.full((1,),float(i)) for i in range(8)},
 optimizer_state_dict=dict(state={i:dict(step=torch.tensor(832460.),exp_avg=torch.zeros(1),exp_avg_sq=torch.ones(1)) for i in range(17)},param_groups=[dict(params=list(range(17)))]))
final=copy.deepcopy(bootstrap);yes(r.frozen_bootstrap(final,bootstrap)['passed'],'whole_frozen_actor9_critic8_STD6_17Adam_literal_exact')
final['actor_state_dict']['a0']+=1;refuse(lambda:r.frozen_bootstrap(final,bootstrap),'any_frozen_actor_tensor_change_refused')
final=copy.deepcopy(bootstrap);final['optimizer_state_dict']['state'][0]['exp_avg']+=1
refuse(lambda:r.frozen_bootstrap(final,bootstrap),'frozen_Adam_moment_change_refused_not_just_step')
tiny=torch.nn.Linear(2,1);opt=torch.optim.Adam(tiny.parameters(),lr=.001)
sum(p.square().sum() for p in tiny.parameters()).backward();opt.step()
yes(r.validate_native_optimizer(tiny,opt.state_dict(),.001,(.9,.999))['min_step']==1,'native_positive_step1_not_PPO20_rule')
bad=copy.deepcopy(opt.state_dict());next(iter(bad['state'].values()))['exp_avg']=torch.zeros(7)
refuse(lambda:r.validate_native_optimizer(tiny,bad,.001,(.9,.999)),'native_optimizer_parameter_moment_shape_refused')
T=D.parent.parent;N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';q=json.loads((N/'reports/AVAILABLE_TWO_NATIVE87R3_SOURCE_PREPARED_ACTUAL.json').read_bytes())
pins=r.PinnedSource(q['payloads']['h1'],q['specs']['h1'])
cfg=pins.extract('source/supermimic_wheel_leg_v3/learner.py',('SuperMimicConfig',),dict(dataclass=r.dataclass))
config=pins.extract('source/native_own_fudan87_training.py',('config_for',),dict(SuperMimicConfig=cfg['SuperMimicConfig']))['config_for'](27)
yes(config.horizon==32 and config.utd==.4 and config.buffer_steps==1000 and config.goal_frames==10 and config.hist==10 and config.wm_only_iters==64,'actual_pinned_native_config_source_not_instantiated_as_runtime')
n=2;z=lambda *shape:torch.zeros(*shape);long=lambda:torch.zeros(n,dtype=torch.long);rng=torch.Generator().get_state()
base='job0/runtime/isaac/mod4/';queue=pins.extract(base+'action_delay_physics_queue.py',('WIDTHS','FIELDS','PhysicsActionQueue'),dict(torch=torch))['PhysicsActionQueue'](n,'cpu',0)
phase=dict(version=270,num_envs=n,geometry=dict(height=.270,edge_x=.35,depth=.8,width=1.2),tensors=dict(previous_front=z(n,2)),goal=dict(stable_ticks=long()))
fields=pins.extract('h1_step270_fullstate_checkpoint_candidate_uninstalled.py',('COMMAND_FIELDS',))['COMMAND_FIELDS']
s=dict(sensor_DR_state=dict(version=1,n=n,profile='noise_bias_mild_v1',bias=z(n,4),episode=long(),bias_rng=rng,noise_rng={k:rng for k in ('base_ang_vel','projected_gravity','leg_pos','leg_vel','wheel_vel')},cache={}),
 sensor_global_rng_state=dict(cpu=rng,cuda=[rng]),sensor_command_DR_rng_state=dict(fixture=rng),sensor_physical_DR_rng_state=dict(fixture=rng),
 feedback_delay_state=dict(version=1,n=n,enabled=True,delay=long(),episode=long(),cache={k:dict(last=torch.full((n,),-1,dtype=torch.long),cur=z(n,w),out=z(n,w),sample_tick=long(),ready=torch.zeros(n,dtype=torch.bool)) for k,w in dict(base_ang_vel=3,projected_gravity=3,leg_pos=4,leg_vel=4,wheel_vel=2).items()}),
 physical_action_delay_state=queue.state_dict(),spring_pressure_state=dict(version=1,n=n,enabled=True,rng_device_type='cuda',factor=torch.ones(n,2),episode=long(),rng=[rng,rng]),
 gas_damping_state=dict(physical_parameter='gas_damping_independent_episode_090_110_v1',version=1,n=n,enabled=True,rng_device_type='cuda',factor=torch.ones(n,2),episode=long(),rng=[rng,rng]),
 chassis_PD_state=dict(version=1,rng_device_type='cuda',COM=dict(version=1,profile='chassis_link_local_independent_xyz_5mm_v1',num_envs=n,enabled=True,episode=long(),delta_m=z(n,3),private_xyz_RNG=[rng]*3),PD=dict(version=1,profile='explicit_motor_PD_independent_095_105_v1',num_envs=n,enabled=True,episode=long(),factor={k:torch.ones(n,w) for k,w in dict(leg_kp=4,leg_kd=4,wheel_kd=2).items()},private_group_RNG={k:rng for k in ('leg_kp','leg_kd','wheel_kd')})),
 H1_step270_task_state=dict(version=270,phase=phase,external_command={k:z(n,1) for k in fields},private_command_mode_rng=rng),H1_step270_runtime_contract=dict(original_D0_D7_STD_optimizer_save_chain_retained=True))
yes(r.original_physical_state(s,pins,n=2)['passed'],'original_D3_D7_and_phase_validators_tiny_population_only')
bad=copy.deepcopy(s);bad['spring_pressure_state']['n']=20000
refuse(lambda:r.original_physical_state(bad,pins,n=2),'source20k_component_population_cannot_reshape')
def events(c,t=0,l=0,re=0,cross=0):return dict(schema='completed_control_goal_events_v1',num_envs=4096,complete_control_rows=c,environment_control_transitions=c*4096,events=dict(takeoff_count=t,landing_count=l,recovery_count=re),both_leading_edges_cross_event_count=cross,diagnostic_valid=True,initial_counter_snapshot_sums=dict(takeoff_count=0,landing_count=0,recovery_count=0))
rows=[dict(native_iteration=i,world_updates=i*10,policy_updates=i,completed_control_rows=c,environment_transitions=c*4096,events=e) for i,c,e in ((0,0,events(0)),(1,7,events(7,1)),(2,19,events(19,2,1)),(3,23,events(23,2,1,1)))]
summary=summarize_rows(rows)
yes(summary['diagnostic_passed'] and summary['latest_complete_snapshot']['control']==23 and summary['event_increment_intervals'][1]['left_control_exclusive']==7 and summary['event_increment_intervals'][1]['right_control_inclusive']==19,'event_intervals_use_actual_controls_not_iterations_times24')
bad=copy.deepcopy(rows);bad[-1]['events']['events']['takeoff_count']=0
yes(not summarize_rows(bad)['diagnostic_passed'],'regressing_event_counter_diagnostic_preserved_false')
bad=copy.deepcopy(rows);bad[-1]['events']['diagnostic_valid']=False
yes(not summarize_rows(bad)['diagnostic_passed'] and bad[-1]['events']['diagnostic_valid'] is False,'raw_event_false_not_repaired')
tree=ast.parse((D/'review_H1_native87R3_finals_CPU_unused_once.py').read_bytes())
loader=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='OneInitialLoadPool')
shared=next(n for n in loader.body if isinstance(n,ast.FunctionDef) and n.name=='load_qualified_shared_source')
yes(sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='load' for n in ast.walk(shared))==1,'shared_source_exactly_one_torch_load_call_no_rehash')
for f in D.glob('*.py'):ast.parse(f.read_bytes())
yes(not torch.cuda.is_initialized(),'tiny_fixture_CPU_no_CUDA')
with (D/'REVIEWER_SOURCE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,count=len(checks),checks=checks,
 evidence='tiny synthetic generic tensors and pinned original source validators',fixture_population=2,actual4096_runtime_or_checkpoint=False,actual_model_or_network_or_physics_executed=False,source_only_validator_lineage=pins.extracted),f,indent=2)
print(json.dumps(dict(passed=True,count=len(checks))))
