"""One human-requested frozen native attempt. No learner/optimizer or budget write."""
from pathlib import Path
import hashlib,json,os,sys,time,traceback
HERE=Path(__file__).resolve().parent;Q=json.loads((HERE/'BINDING.json').read_bytes());B=Path(Q['source_root']);J=B/'job0';OUT=HERE/'attempt'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,value):
 p=HERE/name
 with p.open('x',encoding='utf8') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False)
def main():
 import fcntl,subprocess,psutil
 handles=[];app=None;env=None
 try:
  assert not OUT.exists() and H(HERE/'driver.py')==Q['driver_SHA']
  for raw in Q['locks']:
   f=open(raw,'rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);handles.append(f)
  c=json.loads(Path(Q['canonical']).read_bytes());assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
  assert c['remaining_training_seconds']>86412.86069250107 and c['new_authority_budget_extensions']==[] and c['budget_mode']=='finite_original_limits_restored_after_single4090_return'
  canonical_SHA=H(Q['canonical'])
  for p in psutil.process_iter(['pid','cmdline']):
   try:assert not any(a.startswith(Q['source_root']+'/') or a.startswith(Q['old_owner_root']+'/') for a in (p.info['cmdline'] or []))
   except psutil.Error:pass
  info=subprocess.check_output(['nvidia-smi','-i',Q['GPU_UUID'],'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip().split(',')
  assert info[0].strip()==Q['GPU_UUID'] and '4090' in info[1] and int(info[2])>15669
  apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True).strip()
  assert Q['GPU_UUID'] not in apps,'Selected replay GPU has an existing compute user; do not inspect or stop it'
  import shutil
  assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(HERE).free>25*1024**3
  source=Path(Q['model']['path']);assert source.stat().st_size==Q['model']['bytes'] and H(source)==Q['model']['SHA']
  final=json.loads((B/'job0/production/FINAL.json').read_bytes());assert final['passed'] and final['final']['SHA']==Q['model']['SHA']
  manifest=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
  for row in manifest['files']:
   p=B/row['relative']
   if p.suffix in ('.py','.json','.txt','.yaml','.yml','.sh'):
    assert p.stat().st_size==row['bytes'] and H(p)==row['SHA'],'Closed runtime source changed: '+row['relative']
  original=json.loads((J/'original_run_manifest.json').read_bytes())['env']
  for k in list(os.environ):
   if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
  os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')})
  os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_KEEP_STD='1',RM_RESCUE_STOP_FILE=str(HERE/'UNUSED_STOP_FILE.json'),OWN_E2_H1_KIND='FROZEN_NATIVE86_SINGLE_REPLAY')
  for k,rel in [('HOME','home'),('TMPDIR','tmp'),('XDG_CACHE_HOME','home/.cache'),('CUDA_CACHE_PATH','home/.cache/cuda')]:
   p=HERE/rel;p.mkdir(parents=True,exist_ok=True);os.environ[k]=str(p)
  sys.path[:0]=[str(B/'source'),str(B/'source/sm_deps'),str(B/'lib'),str(J/'runtime/isaac/mod4'),str(HERE)]
  import runpy
  entry=J/'runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py'
  sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','20260928','--steps_per_env','24','--init_checkpoint',str(source),'--log_root',str(HERE/'unused_training_logs')]
  ns=runpy.run_path(str(entry),run_name='native_frozen_replay_sdk_configuration_only');app=ns['app']
  import h1_scut_fudan_jump_reward_v1 as scut,h1_step270_sdk_runtime_candidate as terrain
  configure=scut.configure;scut.configure=lambda cfg:terrain.configure_rewards(cfg,configure)
  original_cfg=ns['Mod4EnvCfg'];factory=ns['build_env']
  def cfg():
   c=original_cfg();c.scene.num_envs=1;c.seed=20260928;c.sim.device='cuda:0'
   assert float(c.terminations.closure.params['threshold'])==.002 and float(c.terminations.mimic.params['threshold'])>=.01
   c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};return c
  factory.__globals__.update(Mod4Env=terrain.H1Step270Env,Mod4EnvCfg=cfg)
  env=factory();env._physics_action_delay.queue.control_us=10000
  assert env.num_envs==1 and not env.h1_capture and float(env.physics_dt)==.0025 and float(env.step_dt)==.01 and env.cfg.decimation==4
  props=env.cfg.scene.robot.spawn.articulation_props
  assert props.solver_position_iteration_count==32 and props.solver_velocity_iteration_count==4
  assert env.cfg.sim.physics.solver_type==1
  vec=ns['RslRlVecEnvWrapper'](env,clip_actions=6.)
  import torch
  assert not env.h1_phase.age_control.any()
  import mod4_task as task
  closure=torch.stack(list(task.closure_errors(env).values())).amax(0);mimic=torch.stack(list(task.mimic_errors(env).values())).amax(0)
  assert torch.isfinite(closure).all() and torch.isfinite(mimic).all() and float(closure.max())<=.002 and float(mimic.max())<=.01
  from types import SimpleNamespace
  from h1_supermimic_bridge_v1 import H1Bridge
  from supermimic_reference_adapter_v1 import read_json_reference,PartialReferenceImitationMdp
  bridge=H1Bridge(SimpleNamespace(env=vec),HERE,dict(save_deadline=float('inf')))
  rb=json.loads((B/'MIXED84_REFERENCE_BINDING_ACTUAL.json').read_bytes());rp=B/rb['reference']['artifact_relative']
  assert H(rp)==rb['reference']['reference_artifact_SHA']
  names=list(env.scene['robot'].joint_names);assert names==Q['ordered_joint_names'] and len(set(names))==30
  reference=read_json_reference(rp).for_sdk_joint_order(names)
  bridge.mdp=PartialReferenceImitationMdp(bridge.mdp,reference.torch_provider(env.device));contract=bridge.mdp.contract_manifest()
  contract_raw=(json.dumps(contract,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
  contract_SHA=hashlib.sha256(contract_raw).hexdigest();assert contract_SHA==Q['runtime_objective_contract_SHA']
  put('ACTUAL_SINGLE_N1_SDK_AND_REFERENCE_ADMISSION.json',dict(passed=True,epoch=time.time(),source=Q['model'],actual_joint_names=names,
   closure_max_m=float(closure.max()),mimic_max_m=float(mimic.max()),num_envs=1,clock=dict(physics_dt=.0025,decimation=4,policy_hz=100),
   solver=dict(type='TGS',position32=32,velocity4=4),runtime_objective_contract_SHA=contract_SHA,new_fresh_episode_not_20k_D0_D7_restore=True,
   no_policy_forward_yet=True,no_training_or_budget_mutation=True))
  from driver import make_frozen_native_policy,run_frozen_single_attempt
  from supermimic_vendor_v2.networks import Policy
  from supermimic_vendor_v2.geometry import unflatten_state
  from h1_takeoff_progress_environment_v2 import tensor
  saved=torch.load(source,map_location='cpu',weights_only=False)
  assert saved['UniSuperMimic_publication']['producer']==Q['producer']
  pi=make_frozen_native_policy(saved,Policy,env.device);del saved
  def json_default(v):
   if hasattr(v,'tolist'):return v.tolist()
   raise TypeError(type(v).__name__)
  with (HERE/'ACTUAL_RENDER_GEOMETRY.json').open('x',encoding='utf8') as f:json.dump(dict(body_names=list(env.scene['robot'].body_names),shapes=env.h1_shapes,geometry=terrain.GEOMETRY,source_asset=str(J/'assets/robot.usd')),f,default=json_default)
  result=run_frozen_single_attempt(vec,bridge.mdp,pi,bridge.current,unflatten_state,tensor,OUT,
   source_identity=dict(model=Q['model'],native_policy_only=True,source_run_id=Q['source_run_id'],source_qualification=Q['source_CPU_report_SHA']),
   actual_joint_order=names,learned_joint_order=Q['ordered_joint_names'],runtime_objective_SHA=contract_SHA,
   expected_runtime_objective_SHA=Q['runtime_objective_contract_SHA'],action_mode='deterministic_native_mean',seed=20260928,max_seconds=10.)
  assert H(Q['canonical'])==canonical_SHA
  put('FROZEN_REPLAY_FUNCTION_RETURNED_ACTUAL.json',dict(passed=True,result=result,not_training=True,no_budget_write=True,canonical_bytes_unchanged=True))
 finally:
  if env is not None:
   try:env.close()
   except BaseException:put('ENV_CLOSE_ERROR.json',dict(error=traceback.format_exc()))
  if app is not None:
   try:app.close()
   except BaseException:put('APP_CLOSE_ERROR.json',dict(error=traceback.format_exc()))
  for f in reversed(handles):f.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('FROZEN_NATIVE_REPLAY_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_same_once_retry=True));raise
