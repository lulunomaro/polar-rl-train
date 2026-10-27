"""One whole NEW W35 fixed92 formal model CPU load; saved input witnesses only."""
from pathlib import Path
from types import SimpleNamespace
import copy,hashlib,importlib.util,json,math,os,sys,time,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent;CLOSE=L/'W35_fixed92_correct_normal900_collector_v1_source';MODEL=CLOSE/'current_qualified_candidate/formal/model_final.pt';COLLECTED=CLOSE/'reports/W35_FIXED92_COMPLETE_FINAL_OR_PARTIAL_ORIGINAL_COST_RETURNED_ACTUAL.json'
SOURCE_SHA='36825921fb3e4a368791be7802c8ff16977e899240ac21ed2c067b2287bb9393';NAME='W35_FIXED92_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V2'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def emit(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def imported(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def walk(value,torch,path=''):
 if torch.is_tensor(value):yield path,value
 elif isinstance(value,dict):
  for k,x in value.items():yield from walk(x,torch,path+'/'+str(k))
 elif isinstance(value,(tuple,list)):
  for k,x in enumerate(value):yield from walk(x,torch,path+'/'+str(k))
 elif isinstance(value,float):assert math.isfinite(value),path

def compare_recipe_summary(actual,summary,path=''):
 # Existing metadata summaries keep list prefixes/counts and nested key sets.
 # They are not fabricated full tensor/value fingerprints.
 if isinstance(summary,dict) and summary.get('kind') in ('dict','list','tuple','tensor'):
  if summary['kind']=='dict':assert isinstance(actual,dict) and set(map(str,actual))==set(summary['keys']),path
  elif summary['kind'] in ('list','tuple'):
   assert isinstance(actual,(list,tuple)) and len(actual)==summary['count'],path
   for a,b in zip(actual,summary['entries']):compare_recipe_summary(a,b,path)
  return
 if isinstance(summary,dict):
  assert set(actual)==set(summary),path
  for k,x in summary.items():
   if path=='sensor_recipe' and k in ('max_abs_actual_bias_rad','noise_draw_counts'):continue
   compare_recipe_summary(actual[k],x,path+'/'+k)
 else:assert actual==summary,path

def review_model(ck,n,b,torch):
 meta=b['original_metadata'];expected=set(meta)|{'PPO50_gas400_adaptation','PPO50_gas400_new_updates','PPO50_gas400_clock'}
 assert set(ck)==expected and ck['PPO50_gas400_adaptation']==b['adaptation_original_provenance']
 assert ck['PPO50_gas400_new_updates']==n and ck['iter']==32259+n-1
 assert ck['PPO50_gas400_clock']==dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)
 for name,count in [('actor_state_dict',9),('critic_state_dict',8)]:
  assert len(ck[name])==count and set(ck[name])==set(meta[name])
  for k,x in ck[name].items():assert list(x.shape)==meta[name][k]['shape'] and str(x.dtype)==meta[name][k]['dtype']
 assert ck['actor_state_dict']['distribution.std_param'].shape==(6,)
 opt=ck['optimizer_state_dict'];assert len(opt['state'])==17 and len(opt['param_groups'])==1
 assert {int(x['step']) for x in opt['state'].values()}=={646800+20*n}
 group=opt['param_groups'][0];original=b['original_optimizer_param_group']
 assert set(group)==set(original) and math.isfinite(group['lr']) and 1e-5<=group['lr']<=.01
 # Adaptive LR is expected to evolve; other optimizer settings remain original.
 for k,x in original.items():
  if k!='lr':assert json.loads(json.dumps(group[k]))==x,k
 parameter_shapes=[x.shape for name in ('actor_state_dict','critic_state_dict') for x in ck[name].values()]
 for key,shape in zip(group['params'],parameter_shapes):
  state=opt['state'][key]
  assert set(state)=={'step','exp_avg','exp_avg_sq'} and state['exp_avg'].shape==state['exp_avg_sq'].shape==shape
 for key in meta:
  if key.endswith('_resume_contract'):assert ck[key]==meta[key],key
 for key in ('sensor_recipe','feedback_delay_recipe','physical_action_delay_recipe','spring_pressure_recipe','gas_damping_recipe','chassis_PD_recipe'):
  summary=copy.deepcopy(meta[key])
  if key=='physical_action_delay_recipe':summary['control_period_us']=20000
  if key=='spring_pressure_recipe':summary['nominal_stiffness_N_m']=2000;summary['actual_stiffness_bounds_N_m']['entries']=[1800,2200]
  compare_recipe_summary(ck[key],summary,key)
 def rng(x,width=16):assert torch.is_tensor(x) and x.dtype==torch.uint8 and x.shape==(width,) and x.device.type=='cpu'
 s=ck['sensor_DR_state'];channels={'base_ang_vel':3,'projected_gravity':3,'leg_pos':4,'leg_vel':4,'wheel_vel':2}
 assert s['version']==1 and s['n']==20000 and s['profile']=='noise_bias_mild_v1'
 assert s['bias'].shape==(20000,4) and bool((s['bias'].abs()<=.0075).all())
 assert s['episode'].shape==(20000,) and s['episode'].dtype==torch.long and bool((s['episode']>=0).all())
 assert set(s['noise_rng'])==set(s['cache'])==set(s['draw_counts'])==set(channels);rng(s['bias_rng'])
 for k,width in channels.items():
  rng(s['noise_rng'][k]);last,noise=s['cache'][k]
  assert last.shape==(20000,) and last.dtype==torch.long and noise.shape==(20000,width)
  assert type(s['draw_counts'][k])is int and s['draw_counts'][k]>=0
 assert ck['sensor_recipe']['raw_pre_scale_uniform_bounds']==dict(base_ang_vel=.125,projected_gravity=.025,leg_pos=.005,leg_vel=.25,wheel_vel=.5)
 assert ck['sensor_recipe']['raw_units']==dict(base_ang_vel='rad/s',projected_gravity='dimensionless',leg_pos='rad',leg_vel='rad/s',wheel_vel='rad/s')
 assert ck['sensor_recipe']['noise_draw_counts']==s['draw_counts'] and ck['sensor_recipe']['max_abs_actual_bias_rad']==float(s['bias'].abs().max())
 assert ck['feedback_delay_recipe']['actor_feedback_channels']==list(channels)
 global_rng=ck['sensor_global_rng_state'];rng(global_rng['cpu'],5056);assert len(global_rng['cuda'])==1;rng(global_rng['cuda'][0])
 assert set(ck['sensor_command_DR_rng_state'])=={'_mode_rng'};rng(ck['sensor_command_DR_rng_state']['_mode_rng'])
 assert set(ck['sensor_physical_DR_rng_state'])=={'generator','cpu_generator'}
 rng(ck['sensor_physical_DR_rng_state']['generator']);rng(ck['sensor_physical_DR_rng_state']['cpu_generator'],5056)
 from feedback_delay_checkpoint import validate_delay_state
 validate_delay_state(SimpleNamespace(n=20000,enabled=True),ck['feedback_delay_state']);rng(ck['feedback_delay_state']['rng'])
 from action_delay_physics_queue import PhysicsActionQueue
 adapter=imported('E0_original_CPU_structure_adapter',Path(b['queue_CPU_adapter']['path']))
 queue=PhysicsActionQueue.__new__(PhysicsActionQueue);queue.n=20000;queue.device=torch.device('cpu');queue.enabled=True;queue.control_us=20000
 queue_proof=adapter.validate_original_CUDA_queue_structure_CPU(queue,ck['physical_action_delay_state'])
 from spring_pressure_checkpoint import validate_saved_pressure
 from gas_damping_checkpoint import validate_saved_damping
 from chassis_pd_checkpoint import validate_saved_chassis_pd
 validate_saved_pressure(ck['spring_pressure_state'],20000);validate_saved_damping(ck['gas_damping_state'],20000);validate_saved_chassis_pd(ck['chassis_PD_state'],20000)
 for state in ('spring_pressure_state','gas_damping_state'):
  for x in ck[state]['rng']:rng(x)
 for x in ck['chassis_PD_state']['COM']['private_xyz_RNG']:rng(x)
 for x in ck['chassis_PD_state']['PD']['private_group_RNG'].values():rng(x)
 from g3_terrain_checkpoint import validate as validate_g3
 from retention_command_state import validate as validate_command,PROFILE
 validate_g3(ck['E1_terrain_state'],20000);validate_command(ck['E1_retained_flat_command_state'],20000)
 assert ck['E1_retained_flat_command_state']['rng_device_type']=='cuda' and ck['E1_current_command_profile']==PROFILE
 assert ck['E1_terrain_state']['G3_profile_sha256']==H(Path(b['runtime_mod_path'])/'g3_cad_profile.json')
 tensors=list(walk(ck,torch));assert tensors and all(x.device.type=='cpu' for _,x in tensors)
 assert all(bool(torch.isfinite(x).all()) for _,x in tensors if x.is_floating_point() or x.is_complex())
 fingerprints=[dict(path=p,shape=list(x.shape),dtype=str(x.dtype),SHA=hashlib.sha256(x.detach().contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()).hexdigest()) for p,x in tensors]
 return dict(all_whole_model_tensors_finite=True,tensor_count=len(tensors),new_final_tensor_fingerprints=fingerprints,
  actor9_critic8_STD6_actor35_critic38=True,Adam_states=17,Adam_step=646800+20*n,stored_RSL_iteration=ck['iter'],
  final_adaptive_optimizer_LR=group['lr'],D1_D7_factors_and_rng_CPU_structure_passed=True,queue_structure=queue_proof,
  final_factors_RNG_weights_and_STD_not_required_equal_to_pretraining_values=True)
def closure_gate(v,first):
 assert v['actual_finite_returned'] and v['canonical_None'] and v['original_owner_private_shared_locks_free']
 assert v['cohort']['original_cost_settled'] and v['owner_exit']['original_cost_settled']
 t=v['terminal'];assert t['terminal_all_own_children_waited'] and t['returncode']==0 and not t['original_error'] and not t['errors']
 assert t['actual_exit']['actual_waited'] and t['actual_exit']['returncode']==0 and v['node_exit']['actual_all_own_children_waited']
 go=v['cohort']['go']['w35'];assert go==first['go'] and go['source_SHA']==SOURCE_SHA and set(v['cohort']['scheduled_experts'])=={'w35'}
 assert go['save_deadline']==go['learning_started_epoch']+3600 and go['nominal_end_epoch']==go['learning_started_epoch']+3900
 seg=v['unique_original_segment'];assert seg['owner_parent_pid']==go['original_owner_pid'] and set(seg['experts'])=={'w35'}
 fee=seg['experts']['w35'];assert fee['started_epoch']==go['learning_started_epoch'] and fee['duration_bound_passed'] and fee['actual_returncode']==0 and 0<fee['charged_seconds']<=3900
 assert v['original_fee_seconds']==seg['charged_expert_seconds']==fee['charged_seconds']
 assert len(v['own_processes'])==3 and all(x.get('original_out') or x.get('original_nonexecuting_zombie') or x.get('out_PID_recycled_no_foreign_identity_read') for x in v['own_processes'])
 f=v['W35_formal'];assert f['passed'] and f['source_SHA']==SOURCE_SHA and f['original_frozen_label_unchanged'] and not f['new_branch_skill_qualified']
 row=f['final'];n=row['new_updates'];assert type(n)is int and n>0 and row['Adam_step']==646800+20*n and row['not_skill_qualified']
 p=v['published'];assert p and p['original_producer']==row and p['source_stat_unchanged'] and p['twohost_complete_SHA'] and p['NEW_formal_transfer_count']==1 and Path(p['local_path']).resolve()==MODEL.resolve()
 return n,p

def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 b=read(HERE/'W35_SAVED_INPUT_BINDINGS_V1.json');v=read(COLLECTED);first=read(b['first_PPO']['path']);assert H(b['first_PPO']['path'])==b['first_PPO']['SHA'];n,p=closure_gate(v,first)
 for r in b['dependencies']:assert H(r['path'])==r['SHA']
 assert first['passed_first_W35_real_PPO'] and first['positive_PPO']['Adam_step']==646820 and first['fullrestore']['actual_algorithm_learning_rate']==.00001
 for name in ('CLOCK_GAS400_NATIVE24_ACTUAL.json','SOURCE_FULLRESTORE_ZERO_VERIFIED.json','APP_CLOSING.json'):
  rows=[r for r in v['all_original_texts_full_case_safe'] if r['relative']=='w35_slot/w35/adaptation/'+name];assert len(rows)==1;r=rows[0];assert H(r['local_path'])==r['SHA']
  q=read(r['local_path'])
  if name.startswith('CLOCK_'):assert q['passed'] and q['controls']==24 and q['physics_callbacks']==192 and q['feedback_samples']==48 and q['actual_RewardManager_dt_s']==.02 and q['reward_dt_applied_once_no_manual_rescale']
  if name.startswith('SOURCE_'):assert q['source_SHA']==SOURCE_SHA and q['W35_retained_command_and_G3_state_restored'] and q['original_actor9_critic8_STD_17Adam_LR_D1_D7_exact']
 report=HERE/(NAME+'.json');start=HERE/(NAME+'_STARTED.json');assert not report.exists() and not start.exists()
 emit(start,dict(epoch=time.time(),purpose='One NEW full formal initial CPU load',model_SHA=p['SHA'],new_updates=n,no_original_input_PT_reload=True))
 assert MODEL.is_file() and not MODEL.is_symlink();before=MODEL.stat();assert before.st_size==p['bytes'] and H(MODEL)==p['SHA']
 import torch
 torch.set_num_threads(2);rng=torch.get_rng_state().clone();assert not torch.cuda.is_initialized();sys.path.insert(0,b['runtime_mod_path'])
 ck=torch.load(MODEL,map_location='cpu',weights_only=False)
 result=review_model(ck,n,b,torch)
 after=MODEL.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 emit(report,dict(kind='MOD4_W35_FIXED92_FORMAL_FULLSTATE_INITIAL_CPU_V1',passed=True,epoch=time.time(),model=p,new_updates=n,review=result,one_NEW_formal_initial_CPU_load=True,source_SHA=SOURCE_SHA,original_fee_seconds=v['original_fee_seconds'],canonical_None_allownout_and_original_locksfree=True,base_actual_source_CPU=b['base_actual_source_CPU'],actual_GPU_initial_restore_and_native24_proof=b['first_PPO'],new_branch_format_qualified=True,new_branch_skill_qualified=False,WM_transition_data_collection_executed=False,no_input_PT_Actor_SDK_GPU_remote_or_account_IO=True))
 print(json.dumps(dict(passed=True,report=str(report),SHA=H(report),model_SHA=p['SHA'],updates=n,Adam=646800+20*n,new_branch_skill_qualified=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  emit(HERE/(NAME+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_model_retry_or_promotion=True));raise
