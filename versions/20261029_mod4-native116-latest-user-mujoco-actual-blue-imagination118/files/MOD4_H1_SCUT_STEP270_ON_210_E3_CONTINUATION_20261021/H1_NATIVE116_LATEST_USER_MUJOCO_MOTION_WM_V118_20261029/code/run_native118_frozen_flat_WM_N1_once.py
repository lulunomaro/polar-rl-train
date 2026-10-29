"""One NEW qualified116 frozen actual270mm step episode and paired WM diagnostic.

No learner, optimizer, learning GO, budget writer or training-state restore.
Requires no active learning account; this new frozen case never registers a learning owner.
"""
from pathlib import Path
import os,sys,json,time,hashlib,traceback,argparse,importlib.util,importlib.metadata
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from fudan118_eval_contract_v1 import require
from fudan118_eval_environment_v1 import bind_private_job_root,environment
from fudan118_frozen_diag_driver_v1 import literal,run_single_case,termination_cache_contract

def H(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(root,name,value):
 with (Path(root)/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)

def main():
 import fcntl,psutil,subprocess,shutil
 args=argparse.ArgumentParser();args.add_argument('--binding',required=True);a=args.parse_args();q=read(a.binding)
 root=Path(q['eval_root']);B=Path(q['source_job_root']);J=B/'job0';out=root/'case'
 require(str(root).startswith('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_NATIVE116_FUDAN270_FROZEN_MOTION_WM_DIAG_') and not out.exists(),'unused owned frozen case root')
 out.mkdir();put(out,'ENTRY_STARTED_BEFORE_APP_ACTUAL.json',dict(epoch=time.time(),one_case=True,no_learning_or_account_write=True))
 C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')
 handles=[];env=None;app=None
 def authority():
  c=read(C);require(c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return' and c['remaining_training_seconds']>86412.86069250107,'sole finite72 authority')
  require(c['active_segment'] is None,'NEW118 requires original116 closed and no new learning owner')
  return dict(remaining_snapshot=c['remaining_training_seconds'],canonical_None=True,no_account_write=True)
 try:
  require(q['source_model']['SHA']=='78f5840ec3db38a3fe2c8c16852b81a5bc7f02b445acd4a7901dafc7078d9976' and q['source_model']['bytes']==256240073,'qualified116 formal source exact')
  require(q['fixed_seed']==20260928 and q['max_controls']==2000 and q['max_callbacks']==8000,'one fixed20s case no retry')
  require(H(root/'source_qualified116_CPU.json')==q['qualification_SHA'],'source wholeCPU receipt pin')
  qualified=read(root/'source_qualified116_CPU.json');require(qualified['passed'] and qualified['model']['SHA']==q['source_model']['SHA'] and qualified['original_normal_duration_account_settled_and_allout'],'formal/initialCPU/oldaccount settlement')
  for name,SHA in q['eval_code_SHAs'].items():require(H(HERE/name)==SHA,'exact eval source '+name)
  require(q['resource_policy']==dict(schema='mod4.user_allowed_light_compute.20261029.v1',free_MiB_strictly_above=15669,utilization_percent_max=30,compute_UUID_rows_allowed=True,other_processes_untouched=True),'exact human shared-GPU policy')
  authority()
  for path,mode in [('/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',fcntl.LOCK_EX),('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock',fcntl.LOCK_SH)]:
   h=open(path,'rb+');fcntl.flock(h,mode|fcntl.LOCK_NB);handles.append(h)
  gpu='GPU-c27eecbd-6838-7290-1cd2-37e34522213d';line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip().split(',');users=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)
  require(line[0].strip()==gpu and '4090' in line[1] and int(line[2])>15669 and int(line[3])<=30,'user-authorized light occupation with original VRAM headroom')
  put(out,'FRESH_USER_LIGHT_GPU_RESOURCE_ACTUAL.json',dict(line=line,compute_UUID_rows=users.splitlines(),no_unknown_PID_read=True,policy=q['resource_policy']))
  require(psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(root).free>25*1024**3,'original frozen-case memory/disk headroom')
  sys.path[:0]=[str(B),str(B/'source'),str(B/'source/sm_deps'),str(B/'lib'),str(J/'runtime/isaac/mod4'),str(HERE)]
  from native_flat90_source_guard_v1 import check_payload
  checked=check_payload(B,verify_model_bytes=False);require(checked['manifest_SHA']==q['runtime_manifest_SHA'],'exact admitted116 coherent-reward runtime for qualified116 output')
  c=read(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json');sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
  require({k:importlib.metadata.version(k) for k in ('isaaclab','rsl-rl-lib','torch')}==c['expected_installed_versions'],'fresh exact SDK/RSL/torch')
  require(H(sdk/'utils/math.py')==c['expected_actual_SDK_math_SHA'],'fresh SDK math')
  for row in c['expected_actual_RSL_sources']:require(H(rsl/row['relative'])==row['SHA'],'fresh RSL source')
  source=Path(q['source_model']['path']);qualified_output=Path(q['qualified_training_job_root'])/'job0/production'
  require(source.resolve().is_relative_to(qualified_output.resolve()) and source.stat().st_size==q['source_model']['bytes'] and H(source)==q['source_model']['SHA'],'published qualified model input')
  for k in list(os.environ):
   if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
  os.environ.update({k:str(v) for k,v in read(J/'original_run_manifest.json')['env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
  bind_private_job_root(out/'private');os.environ.update(environment({'GPU_UUID':gpu}))
  os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_KEEP_STD='1',RM_RESCUE_STOP_FILE=str(out/'UNUSED_STOP.json'),OWN_E2_H1_KIND='FROZEN_NATIVE116_FUDAN270_MOTION_WM_DIAGNOSTIC')
  import runpy
  entry=J/'runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','20260928','--steps_per_env','24','--init_checkpoint',str(source),'--log_root',str(out/'UNUSED_training_logs')]
  ns=runpy.run_path(str(entry),run_name='native118_frozen_N1_configuration_only');app=ns['app']
  import h1_scut_fudan_jump_reward_v1 as scut,h1_step270_sdk_runtime_candidate as terrain
  original_rewards=scut.configure;scut.configure=lambda cfg:terrain.configure_rewards(cfg,original_rewards)
  original_cfg=ns['Mod4EnvCfg'];factory=ns['build_env']
  def config():
   cfg=original_cfg();cfg.scene.num_envs=1;cfg.seed=20260928;cfg.episode_length_s=20.;cfg.sim.device='cuda:0'
   require(float(cfg.terminations.closure.params['threshold'])==.002 and float(cfg.terminations.mimic.params['threshold'])>=.01,'original per-env reset thresholds')
   return cfg
  factory.__globals__.update(Mod4Env=terrain.H1Step270Env,Mod4EnvCfg=config)
  env=factory();vec=ns['RslRlVecEnvWrapper'](env,clip_actions=6.)
  import torch,inspect
  from types import SimpleNamespace
  from actual_DR_memory_getter_v1 import RuntimeOrderBinding,indices,tensor
  from native_fudan_step_bridge_v1 import FudanStepBridge,install_fudan_step_request_and_command
  from native_fudan_step_adapter_candidate_v2 import OwnFudanStepReference,OwnFudanStepMdp
  from native87_encoder_actual_sdk_adapter_v1 import actual_encoder_joint_names
  from gas400_sdk_admission_candidate_v1 import check_actual_new_gas
  from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source
  from supermimic_wheel_leg_v3.networks import Policy,Critic
  from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel
  from supermimic_wheel_leg_v3.geometry import unflatten_state
  from native88C_to_flat_migration_v1 import NATIVE_CONTRACT,verify_saved_migration,observe_first_original_preload_write
  require(env.num_envs==1 and env.physics_dt==.0025 and env.step_dt==.01 and env.cfg.decimation==4 and env._sim_step_counter==0 and env.cfg.episode_length_s==20.,'fresh coherent20s N1 numerical clock')
  props=env.cfg.scene.robot.spawn.articulation_props;require(props.solver_position_iteration_count==32 and props.solver_velocity_iteration_count==4 and env.cfg.sim.physics.solver_type==1,'TGS32/4')
  require(env._physics_action_delay.queue.control_us==10000 and env._rescue_reset_bank[0].shape==(74,30) and env._rescue_reset_q.shape==(1,30),'actual original reset and100Hz delay')
  robot=env.scene['robot'];names=tuple(robot.joint_names);bodies=tuple(robot.body_names)
  require(list(names)==c['expected_runtime_joint_names'] and len(bodies)==31,'actual named order30/31')
  def group(k):return tuple(names[i] for i in indices(robot.actuators[k].joint_indices,30))
  binding=RuntimeOrderBinding(bodies,names,group('legs'),group('wheels'),group('gas_springs'),int(env._mild_dr.materials.shape[1]))
  require(env._mild_dr.audit()['actual_parameters_pass'],'fresh D0-D7 physical backend')
  provider=OwnFudanStepReference(read(B/'source/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'),env.device).bind_named_order(names,scope='actual_SDK_readback')
  mdp=OwnFudanStepMdp(provider,read(J/'assets/import_contract.json'),read(B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'),actual_encoder_joint_names(env,names))
  command=install_fudan_step_request_and_command(env)
  from private_phase_frame_v1 import STRIDE,PUBLIC_EPISODE_MAX_TICKS
  require(STRIDE==4096 and PUBLIC_EPISODE_MAX_TICKS==2000 and command['request_control_interval']==[200,2000],'actual20s phase/frame/source binding')
  class OriginalCounter:
   def __init__(self):self.last=None
   def record(self,state):self.last=state
   def snapshot(self):return dict(actual_terminal_before_autoreset=None if self.last is None else {k:self.last[k] for k in ('takeoff_count','landing_count','recovery_count','success','stable_callback_ticks')},one_episode_only=True,original270_counter_unchanged=True)
  counter=OriginalCounter()
  bridge=FudanStepBridge(SimpleNamespace(env=vec),SimpleNamespace(frame=None),mdp,binding,lambda:None)
  gas=check_actual_new_gas(env,expected_joint_names=names,tensor=tensor,require_active_preload=False);bank=check_runtime_source(J/'runtime/isaac/mod4')
  preload=SimpleNamespace(preload_evidence=None);observe_first_original_preload_write(env,preload,expected_joint_names=names,emit=lambda value:put(out,'ORIGINAL_PRELOAD_BEFORE_WRITE_ACTUAL.json',value))
  term=termination_cache_contract(inspect.getsourcefile(type(env.termination_manager)))
  put(out,'FRESH_N1_SOURCE_SDK_RESET_GAS_BEFORE_FORWARD_ACTUAL.json',dict(passed=True,source_SHA=q['source_model']['SHA'],actual_names=list(names),actual_body_names=list(bodies),actual_gas400=gas,reset_bank_source=bank,command=command,actual_Fudan270_task=True,no_forward_before_admission=True))
  saved=torch.load(source,map_location='cpu',weights_only=False);publication=saved['UniSuperMimic_publication'];native=saved['UniSuperMimic_H1_test']
  verify_saved_migration(saved,publication);require(literal(saved['UniSuperMimic_test_contract'],NATIVE_CONTRACT) and native['iteration']==20809 and publication['world_updates']==208090 and publication['policy_updates']==19977,'qualified116 output lineage and exact global counters')
  torch.backends.cuda.matmul.allow_tf32=True;torch.backends.cudnn.allow_tf32=True
  with torch.random.fork_rng(devices=[]):
   pi=Policy(86,1460,hist=10,z_dim=32,num_joints=6,hidden=native['args']['policy_hidden'])
   wm=AugmentedWheelLegWorldModel(context_dim=31,hidden=native['args']['wm_hidden'],num_joints=30,auxiliary_dim=54,action_dim=6)
   critic=Critic(1625,hidden=native['args']['critic_hidden'])
  for module,key in [(pi,'pi'),(wm,'wm'),(critic,'critic')]:
   module.load_state_dict(native[key],strict=True);require(literal(module.state_dict(),native[key]),'literal saved model/norm load '+key);module.to(env.device);module.eval()
   for p in module.parameters():p.requires_grad_(False)
  del saved
  put(out,'ACTUAL_RENDER_GEOMETRY.json',dict(body_names=list(bodies),shapes=env.h1_shapes,geometry=terrain.GEOMETRY))
  result=run_single_case(vec,bridge,pi,unflatten_state,tensor,out/'episode',seed=20260928,source_identity=q['source_model'],term_contract=term,authority_check=authority,wm=wm,critic=critic,model_args=native['args'],original_counter=counter)
  require(preload.preload_evidence is not None,'actual original preload observed')
  put(out,'FROZEN_DIAGNOSTIC_FUNCTION_RETURNED_ACTUAL.json',dict(passed=True,result=result,authority=authority(),no_learning_GO_optimizer_or_budget_writer=True,not_bestcase_or_population_success_rate=True))
 except BaseException:
  put(out,'PRIMARY_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_retry=True));raise
 finally:
  if env is not None:
   try:env.close()
   except BaseException:put(out,'ENV_CLOSE_ORIGINAL_ERROR.json',dict(traceback=traceback.format_exc()))
  for h in reversed(handles):h.close()
  if app is not None:app.close()

if __name__=='__main__':main()
