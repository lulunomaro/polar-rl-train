"""Initial whole NEW formal FINAL CPU load only after original closure; no SDK/actor."""
from pathlib import Path
from types import SimpleNamespace
import copy,hashlib,importlib.util,json,math,os,sys,time,traceback
HERE=Path(__file__).resolve().parent
N=HERE.parents[1]/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027'
SOURCE_SHA='54f53453a3f793cea990f0608c0a2c3bd3e5d37aecf41bb8817691af5fea0371'
ORIGINAL_SHA='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'
REMOTE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d'
MODEL=N/'current_qualified_candidate/formal/model_final.pt'
COLLECTED=N/'reports/E0_89D_COMPLETE_FINAL_OR_PARTIAL_ORIGINAL_COST_RETURNED_ACTUAL.json'
NAME='E0_89D_FORMAL_FINAL_WHOLE_INITIAL_CPU_REVIEW_ACTUAL_V1'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def emit(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def imported(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def closure_gate(v,first,model_path):
 # Called before model stat/hash/open, torch import or any model load.
 assert v['actual_normal_finite_ending_returned'] and v['actual_finite_transport_returned']
 assert v['canonical_None'] and v['all_original_locks_free']
 assert v['owner_exit']['original_cost_settled'] and v['owner_cohort_final']['original_cost_settled']
 terminal=v['terminal'];assert terminal['terminal_all_own_children_waited'] and terminal['returncode']==0
 assert terminal['original_error'] is False and terminal['errors']==[]
 assert terminal['actual_exit']['actual_waited'] and terminal['actual_exit']['returncode']==0
 cohort=v['owner_cohort_final'];assert set(cohort['go'])==set(cohort['rows'])=={'e0'}
 go=cohort['go']['e0'];assert go==first['go'] and go['source_SHA']==SOURCE_SHA
 assert go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
 assert go['save_deadline']==go['learning_started_epoch']+3600 and go['nominal_end_epoch']==go['learning_started_epoch']+3900
 seg=v['unique_original_segment'];assert seg['owner_parent_pid']==go['original_owner_pid'] and set(seg['experts'])=={'e0'}
 expert=seg['experts']['e0'];assert expert['started_epoch']==go['learning_started_epoch'] and expert['actual_returncode']==0
 assert expert['duration_bound_passed'] and 0<expert['charged_seconds']<=3900
 assert v['original_fee_seconds']==seg['charged_expert_seconds']==expert['charged_seconds']
 assert math.isfinite(v['closed_remaining_snapshot'])
 own=v['own_process_out_or_nonexecuting_zombie'];assert len(own)==len(first['snapshot']['known_own_processes'])==3
 assert {x['pid'] for x in own}=={x['pid'] for x in first['snapshot']['known_own_processes']}
 assert all(x.get('original_out') or x.get('original_nonexecuting_zombie') or x.get('original_out_PID_recycled_no_foreign_identity_read') for x in own)
 formal=v['formal'];assert formal and formal['passed'] and formal['source_SHA']==SOURCE_SHA
 assert formal['original_frozen_label_unchanged'] and formal['new_branch_skill_qualified'] is False
 row=formal['final'];n=row['new_updates'];assert type(n)is int and n>0 and row['Adam_step']==639560+20*n
 assert row['path']==REMOTE+'/e0/adaptation/final_valid_update'+str(n)+'.pt'
 published=v['published_complete_FINAL_model'];assert published and published['twohost_fullSHA_verified']
 assert published['source_stat_before_after_unchanged'] and published['original_producer']==row
 assert published['path']==row['path'] and published['SHA']==row['SHA'] and published['bytes']==row['bytes']
 assert Path(published['local_path']).resolve()==Path(model_path).resolve()
 assert len(published['SHA'])==64 and published['bytes']>0
 return n,published

def closed_text(v,relative):
 rows=[x for x in v['all_original_ending_texts'] if x['relative']==relative];assert len(rows)==1
 row=rows[0];p=Path(row['local_path']);assert p.resolve().is_relative_to((N/'actual_closed_text').resolve())
 assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and H(p)==row['SHA']
 return read(p),row

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
 assert ck['PPO50_gas400_new_updates']==n and ck['iter']==31903+n-1
 assert ck['PPO50_gas400_clock']==dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)
 for name,count in [('actor_state_dict',9),('critic_state_dict',8)]:
  assert len(ck[name])==count and set(ck[name])==set(meta[name])
  for k,x in ck[name].items():assert list(x.shape)==meta[name][k]['shape'] and str(x.dtype)==meta[name][k]['dtype']
 assert ck['actor_state_dict']['distribution.std_param'].shape==(6,)
 opt=ck['optimizer_state_dict'];assert len(opt['state'])==17 and len(opt['param_groups'])==1
 assert {int(x['step']) for x in opt['state'].values()}=={639560+20*n}
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
 tensors=list(walk(ck,torch));assert tensors and all(x.device.type=='cpu' for _,x in tensors)
 assert all(bool(torch.isfinite(x).all()) for _,x in tensors if x.is_floating_point() or x.is_complex())
 fingerprints=[dict(path=p,shape=list(x.shape),dtype=str(x.dtype),SHA=hashlib.sha256(x.detach().contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()).hexdigest()) for p,x in tensors]
 return dict(all_whole_model_tensors_finite=True,tensor_count=len(tensors),new_final_tensor_fingerprints=fingerprints,
  actor9_critic8_STD6_actor35_critic38=True,Adam_states=17,Adam_step=639560+20*n,stored_RSL_iteration=ck['iter'],
  final_adaptive_optimizer_LR=group['lr'],D1_D7_factors_and_rng_CPU_structure_passed=True,queue_structure=queue_proof,
  final_factors_RNG_weights_and_STD_not_required_equal_to_pretraining_values=True)

def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 bindings=read(HERE/'E0_89D_INPUT_WITNESS_BINDINGS_v1.json')
 # First JSON gate; partial/error returns never touch a PT or import torch.
 v=read(COLLECTED);first=read(bindings['first_PPO']['path']);assert H(bindings['first_PPO']['path'])==bindings['first_PPO']['SHA']
 n,published=closure_gate(v,first,MODEL)
 report=N/'reports'/(NAME+'.json');started=N/'reports'/(NAME+'_STARTED.json')
 assert not report.exists() and not started.exists()
 emit(started,dict(epoch=time.time(),purpose='One NEW formal FINAL initial whole CPU load',collector_SHA=H(COLLECTED),model_SHA=published['SHA'],new_updates=n,no_input_PT_or_normal86_read=True))
 for r in bindings['frozen_small_dependencies']:assert H(r['path'])==r['SHA']
 clock,clockrow=closed_text(v,'e0/adaptation/CLOCK_GAS400_NATIVE24_ACTUAL.json')
 assert clock['passed'] and [clock[k] for k in ('controls','physics_callbacks','feedback_samples','actual_reward_compute_calls')]==[24,192,48,24]
 assert clock['actual_RewardManager_dt_s']==.02 and clock['reward_dt_applied_once_no_manual_rescale'] and clock['no_optimizer_update']
 restored,restorerow=closed_text(v,'e0/adaptation/SOURCE_FULLRESTORE_ZERO_VERIFIED.json')
 assert restored['source_SHA']==SOURCE_SHA and restored['original_source_SHA']==ORIGINAL_SHA and restored['original_actor9_critic8_STD_17Adam_LR_D1_D7_exact']
 assert len(restored['receipts'])==6 and restored['own0']['Adam_step']==639560 and restored['own0']['new_updates']==0
 closed_text(v,'e0/adaptation/APP_CLOSED.json');node_exit,_=closed_text(v,'node_e0/NODE_EXIT_ACTUAL.json');assert node_exit['actual_all_own_children_waited']
 assert first['passed_first_PPO'] and first['actual_restore_and_24control_clock_gas_readback'] and first['positive']['Adam_step']==639580 and first['positive']['new_updates']==1
 assert MODEL.is_file() and not MODEL.is_symlink();before=MODEL.stat();assert before.st_size==published['bytes'] and H(MODEL)==published['SHA']
 import torch
 torch.set_num_threads(2);cpu_rng=torch.get_rng_state().clone();assert not torch.cuda.is_initialized()
 sys.path.insert(0,bindings['runtime_mod_path'])
 ck=torch.load(MODEL,map_location='cpu',weights_only=False)  # The single NEW model initial load.
 result=review_model(ck,n,bindings,torch)
 after=MODEL.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 assert torch.equal(cpu_rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
 emit(report,dict(kind='MOD4_E0_89D_PPO50_GAS400_FORMAL_FINAL_WHOLE_CPU_V1',epoch=time.time(),passed=True,
  model=dict(path=str(MODEL),bytes=published['bytes'],SHA=published['SHA'],producer_twohost_fullSHA_verified=True),new_updates=n,
  source_SHA=SOURCE_SHA,original_source_SHA=ORIGINAL_SHA,collector=dict(path=str(COLLECTED),SHA=H(COLLECTED)),
  original_fee_seconds=v['original_fee_seconds'],original_finite_duration_bound_passed=True,canonical_None_and_all_original_locks_free=True,
  all_original_own_processes_out_or_nonexecuting_zombie=True,actual_native24_receipt=clockrow,actual_initial_restore_receipt=restorerow,
  previous_source_CPU_witness=bindings['base_source_CPU'],first_PPO242=bindings['first_PPO'],review=result,
  original_bank_and_nominal400_recipe_evidence=bindings['base_reset_bank_evidence'],
  no_input_checkpoint_normal86_Actor_SDK_GPU_remote_or_account_IO=True,one_NEW_model_initial_CPU_load=True,
  new_adaptation_branch_format_qualified=True,original_frozen_label_unchanged=True,new_branch_skill_qualified=False,
  WM_transition_data_collection_executed=False,Git_status='ordinary_supplement_existing89trial_pending_root'))
 print(json.dumps(dict(report=str(report),SHA=H(report),passed=True,model_SHA=published['SHA'],new_updates=n,not_skill_qualification=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  emit(N/'reports'/(NAME+'_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),traceback=traceback.format_exc(),no_promotion_or_retry=True));raise
