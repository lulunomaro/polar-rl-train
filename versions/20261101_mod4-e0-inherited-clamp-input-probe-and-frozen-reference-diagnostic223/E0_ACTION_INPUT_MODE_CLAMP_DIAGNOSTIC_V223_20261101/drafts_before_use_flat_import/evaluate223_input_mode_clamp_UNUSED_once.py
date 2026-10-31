"""ROOT-only NEW223 N1 observation/mode/action diagnostic;32 executed controls max.

Current ROOT parent owns authority/resources/locks/wait. No optimizer or GUI.
"""
from pathlib import Path
import argparse,hashlib,io,json,os,runpy,sys,time,traceback
sys.path.insert(0,str(Path(__file__).resolve().parent/'source'))
from contract223 import validate_task,E0_PARENT,KIND
parser=argparse.ArgumentParser();parser.add_argument('--task',type=Path,required=True);args=parser.parse_args()
P=args.task.resolve().parent;TASK=json.loads(args.task.read_bytes());validate_task(TASK)
assert os.environ.get('CUDA_VISIBLE_DEVICES')==TASK['GPU_UUID']
assert TASK['actual_parent_private_EX_and_authority_admitted'] is True
assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest()==TASK['worker_SHA']
ROOT=Path(TASK['qualified197_package_root']);payload=ROOT/'payload'
OUT=P/'actual_capture';OUT.mkdir(exist_ok=False)


def put(n,v):
 with (OUT/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)


deadline=time.time()+840;real=ns=None
try:
 original=json.loads((payload/'job0/original_run_manifest.json').read_bytes())['env']
 for key in list(os.environ):
  if key.startswith('RM_') or key in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[key]
 os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SPIN_STAGE','RM_SLOPE_INITIAL_ADMISSION')})
 os.environ.update(RM_MOD4_USD=str(payload/'job0/assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',
  RM_KEEP_STD='1',RM_JUMP_SCRIPT_PROB='0',RM_GYRO_CURRICULUM='1',RM_HEADING_CMD='0',
  RM_HEIGHT_MIN='.23',RM_HEIGHT_MAX='.33',RM_EPISODE_S='20',RM_HIDDEN_DIMS='256,128,64',
  RM_VALUE_LOSS_COEF='2.0',RM_SCHEDULE='adaptive',RM_ENTROPY_COEF='.005',RM_DESIRED_KL='.01',
  RM_RESCUE_DEADLINE=str(deadline),RM_RESCUE_STOP_FILE=str(OUT/'UNREQUESTED_STOP.json'))
 os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
 kit=OUT/'kit_isolation';kit.mkdir();(kit/'data').mkdir();(kit/'DerivedDataCache').mkdir();(kit/'data/user.config.json').write_text('{}')
 os.environ['MOD4_188_OWN_KIT_ROOT']=str(kit);os.environ['MOD4_188_JOB_ROOT']=str(P)
 runtime=payload/'job0/runtime/isaac/mod4'
 sys.path[:0]=[str(P),str(ROOT),str(payload/'lib'),str(runtime),str(payload/'job0/runtime')]
 entry=runtime/'train_H1_ground_prelaunch_fullstate_v2.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','27','--log_root',str(OUT/'unused_learning_logs')]
 ns=runpy.run_path(str(entry),run_name='capture223_config_only_no_old_main')
 import numpy as np
 import torch
 from spring_nominal_sdk_readback import tensor
 import jump194_sdk as sdk
 cfg=ns['Mod4EnvCfg']();cfg.scene.num_envs=1;cfg.seed=27;cfg.sim.device='cuda:0';sdk.configure(cfg)
 cfg.commands.twist.ranges.ang_vel_z=(0.,0.)  #207 controlled eval-only factor;reward unchanged.
 real=sdk.JumpMod4Env(cfg=cfg);real._physics_action_delay.queue.control_us=20000
 vec=ns['RslRlVecEnvWrapper'](real,clip_actions=6.);obs=vec.get_observations();robot=real.scene['robot']
 assert real.physics_dt==.0025 and real.step_dt==.02 and real.cfg.decimation==8
 assert obs['policy'].shape==(1,35) and real.spring_pressure_recipe()['nominal_stiffness_N_m']==2000
 assert real.cfg.terminations.closure.params['threshold']==.002 and real.cfg.terminations.mimic.params['threshold']==.01
 assert tuple(cfg.commands.twist.ranges.lin_vel_x)==(-2.1,2.1)
 put('ACTUAL223_LITERAL_PLANT_BEFORE_MODEL.json',dict(passed=True,physics_dt=real.physics_dt,policy_dt=real.step_dt,nominal_spring=real.spring_pressure_recipe(),original_literal_reward_and_DR_binding=real.binding_receipt(),eval_yaw_only0=True,original_MOD4_guards_unchanged=True))
 source=Path(TASK['model_path'])
 with source.open('rb') as f:raw=f.read()
 assert len(raw)==TASK['model_bytes'] and hashlib.sha256(raw).hexdigest()==TASK['model_SHA']
 ck=torch.load(io.BytesIO(raw),map_location='cuda:0',weights_only=False);del raw
 assert ck['iter']==TASK['model_iteration'] and ck['source_parent_branch_SHA']==E0_PARENT
 typed=ck['typed_MIX210_task'];assert typed['source_SHA']==E0_PARENT and typed['reward_weights_and_functions_no_edits']
 assert typed['learning_seconds']==10800 and typed['ground_envs']==2000 and typed['jump_envs']==18000
 assert ck['actual_new_PPO_updates']==TASK['actual_training_new_PPO_updates']
 actor=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6)).to(real.device)
 weights={k.removeprefix('mlp.'):v for k,v in ck['actor_state_dict'].items() if k.startswith('mlp.')}
 actor.load_state_dict(weights,strict=True);actor.eval()
 assert all(torch.equal(v,actor.state_dict()[k]) for k,v in weights.items())
 parameter=ck['actor_state_dict']['distribution.std_param'].detach().cpu().tolist()
 put('ACTUAL223_ONE_NEW_GPU_MODEL_MEAN_RESTORE.json',dict(passed=True,model_SHA=TASK['model_SHA'],model_iteration=TASK['model_iteration'],model_byte_reads=1,model_decodes=1,actor_exact=True,learned_distribution_STD_parameter6=parameter,STD_parameter_semantics_not_reinterpreted=True,no_optimizer_Critic_WM_or_budget_write=True))
 from input_counterfactual223 import diagnose,SLOTS
 for p in actor.parameters():p.requires_grad_(False)
 pending={};old_compute=real.termination_manager.compute;old_reward=real.original_jump_once
 names=list(real.termination_manager.active_terms)
 def capture_term(*a,**kw):
  value=old_compute(*a,**kw)
  pending['root13']=tensor(robot.data.root_state_w)[0].detach().cpu().tolist()
  pending['q30']=tensor(robot.data.joint_pos)[0].detach().cpu().tolist()
  pending['flags']={n:bool(real.termination_manager.get_term(n)[0])for n in names}
  return value
 def capture_reward(*a,**kw):
  value=old_reward(*a,**kw)
  pending['reward_motor_actions6']=real.literal.actions[0].detach().cpu().tolist()
  pending['reward_commands4']=real.literal.commands[0].detach().cpu().tolist()
  return value
 real.termination_manager.compute=capture_term;real.original_jump_once=capture_reward
 tick0=int(real._integrated_contact.tick);fb0=int(real._feedback_100hz_tick);calls0=real.literal.calls;rows=[]
 for control in range(TASK['controls_max']):
  assert time.time()<deadline
  pobs=obs['policy'].detach().clone();before=pobs.clone()
  assert pobs.shape==(1,35)and torch.isfinite(pobs).all()
  assert int(pobs[0,28:35].argmax())==1
  numeric=diagnose(actor,pobs,gradient=control==0)
  with torch.inference_mode():action=actor(pobs)
  raw=action.detach().cpu().clone()
  assert torch.equal(pobs,before)
  pending.clear();obs,reward,done,extra=vec.step(action)
  executed=torch.tensor(pending['reward_motor_actions6']);expected=raw[0].clamp(-6,6)[[0,1,4,2,3,5]]
  residual=float((executed-expected).abs().max());assert residual<=1e-6
  assert all(torch.equal(v,actor.state_dict()[k])for k,v in weights.items())
  rows.append(dict(control=control+1,policy_observation35=before[0].cpu().tolist(),raw_mean6=raw[0].tolist(),numeric_counterfactual=numeric,pre_reset=pending.copy(),clip6_motor_reorder_residual=residual))
  if bool(done[0]):break
 controls=len(rows);assert int(real._integrated_contact.tick)-tick0==controls*8 and int(real._feedback_100hz_tick)-fb0==controls*2 and real.literal.calls-calls0==controls
 left=[r['raw_mean6'][0]for r in rows]
 result=dict(passed=True,kind=KIND,model_SHA=TASK['model_SHA'],controls=controls,physics_callbacks=controls*8,feedback_samples=controls*2,
  first_episode_only=True,actual_action_uses_untouched_original_observation_and_mean=True,source_actor_tensors_unchanged=True,
  input_slots_fixedSI=SLOTS,learned_STD_parameter6=parameter,rows=rows,
  actual_left_crank_mean_min=min(left),actual_left_crank_mean_max=max(left),actual_left_crank_negative_clip_count=sum(x < -6 for x in left),
  no_reward_STD_guard_physics_or_actor_repair_selected=True,no_skill_or_population_cause_claim=True,
  model_byte_reads=1,model_decodes=1,optimizer_steps=0,account_writes=0,old_control_NPZ_or_raw_reads=0)
 put('CAPTURE223_ACTUAL_RESULT.json',result)
 print(json.dumps(dict(passed=True,controls=controls,left_crank_range=[min(left),max(left)])),flush=True)
except BaseException:
 put('ORIGINAL223_ERROR.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
finally:
 if real is not None:
  try:real.close();put('ENV223_CLOSE_RETURNED.json',dict(closed=True))
  except BaseException:put('ENV223_CLOSE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()))
 if ns is not None:
  put('APP223_CLOSE_REQUESTED.json',dict(close_call_next=True,post_return_marker_not_required_or_fabricated=True))
  ns['app'].close()
  put('APP223_CLOSE_RETURNED_IF_REACHED.json',dict(returned=True))
