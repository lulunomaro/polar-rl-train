"""Freeze the new mixed continuation; no model/raw/SDK/GPU/remote access."""
from pathlib import Path
import ast, hashlib, json, shutil, time, traceback
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
S=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
E=T/'E0_82_LITERAL_FUDAN_JUMP72_ONE_HOUR_SOURCE_V198_20261031'
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
OLD=L/'night_frozen_experts_PPO50_gas400_adaptation_20261027/E0_runtime50_gas400_candidate_v1/isaac/mod4'
P=N/'package';REMOTE='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_JUMP32066_GROUND10_400N50_20261031v209/e0_72'
SHA='2df106412ade7c0993f5a51871a4505624600aac7489c011011d9fd24d3ca610'

def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):
 with p.open('x',encoding='utf8',newline='\n') as f:f.write(s)
def replace(s,a,b):
 assert a in s,a[:150]
 return s.replace(a,b)

def main():
 put('SOURCE209_PREPARATION_ONCE_CONSUMED.json',dict(epoch=time.time(),scope='new source only',source_model_reads=0,SDK_GPU_remote=0))
 assert not P.exists();shutil.copytree(S/'primary_package',P)
 shutil.copyfile(N/'mixed209_sdk.py',P/'mixed209_sdk.py')
 original=json.loads((L/'night_frozen_experts_PPO50_gas400_adaptation_20261027/E0_original_run_manifest_frozen_v1.json').read_bytes())
 write(P/'E0_original_run_manifest_frozen_v1.json',json.dumps(original,indent=2,ensure_ascii=False))
 runtime=P/'payload/job0/runtime/isaac/mod4'
 # All task/reward definitions are unchanged between the selected own runtimes;
 # their only module-level physics-clock delta is explicit 50 Hz.
 defs=lambda p:{n.name:ast.dump(n) for n in ast.parse(p.read_bytes()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
 assert all(defs(runtime/'mod4_task.py').get(k)==v for k,v in defs(OLD/'mod4_task.py').items())
 assert H(runtime/'skills_isaac.py')==H(OLD/'skills_isaac.py')
 for name in ('linear_exp','linear_square','linear_gap','yaw_exp','orientation','wheel_positions_body','no_fork','leg_gravity_alignment','wheel_power'):
  assert defs(runtime/'scut_flat_rescue.py')[name]==defs(OLD/'scut_flat_rescue.py')[name],name
 assert H(runtime/'directional_spin_runtime.py')=='8fed717b0d2ba77491c252b183f9462f49457402d96927cc441c88ecd36b1cd8'
 qualified=json.loads((S/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
 assert qualified['passed'] and qualified['roles']['e0_72']['passed'] and qualified['roles']['e0_72']['SHA']==SHA
 task=json.loads((E/'package/TASK198.json').read_bytes())
 task.update(kind='E0_JUMP32066_ORIGINAL_E0_GROUND10_LITERAL_JUMP90_400N50_V209',worker_role='e0_72',
  source_SHA=SHA,source_bytes=17519967,source_iteration=32066,source_Adam_step=642840,
  formal_source_model='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v198/e0_72/production/model_final_complete.pt',
  source_fullstate_CPU_report=str(S/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
  source_fullstate_CPU_report_SHA=H(S/'reports/ROOT197_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json'),
  ground_envs=2000,jump_envs=18000,ground_fraction=.1,ground_task_mode=0,jump_task_mode=1,
  original_frozen_E0_reference_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',
  initialization_scope='Continue latest32066 branch, original frozen E0 immutable; full actor critic STD17Adam LR retained',
  reward_routing='disjoint original E0 reward on ground IDs and original FudanJUMP on jump IDs; unchanged individual reward formulas/scales',
  frozen_E0_original_manifest_SHA='1dbde5972c65baf8842bc82024fe7ddfd6393d73a51137cc9880ed6310ff1af1',
  ground_source_task_SHA=H(OLD/'mod4_task.py'),ground_command_SHA=H(OLD/'directional_spin_runtime.py'),
  ground_rewards_AST_identical_to_frozen_E0=True,one_hour_learning_seconds=3600,max_parent_seconds=3900,
  read_admission=dict(training_GPU_model_read_decode=1,admission_models=0,old_cases_raw_NPZ=0,reset_NPZ='original constructor only',CPU_old_model_reads=0))
 write(P/'TASK209.json',json.dumps(task,indent=2))
 source=(E/'run198_E0_JUMP72_400N50_worker.py').read_text('utf8')
 # Schema/function labels have exact replacements; no global numeric prefix edit.
 for a,b in [('TASK198.json','TASK209.json'),('jump195_sdk','mixed209_sdk'),('sdk.JumpMod4Env','sdk.Mixed209Env'),
  ('e0_jump198_task_protocol','mixed209_task_protocol'),('typed_E0_JUMP198_task','typed_MIX209_task'),
  ('source_E0_SHA','source_parent_branch_SHA'),('real.stats195','real.stats194'),
  ('ACTUAL198','ACTUAL209'),('SOURCE198','SOURCE209'),('ACTUAL_SOURCE198','ACTUAL_SOURCE209'),
  ('source198_config_only_no_old_main','source209_config_only_no_old_main'),
  ('a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',SHA)]:
  source=source.replace(a,b)
 for a,b in [('31984','32066'),('31985','32067'),('641200','642840'),('641220','642860'),('14031973','17519967')]:
  import re
  source=re.sub(r'(?<!\d)'+a+r'(?!\d)',b,source)
 source=replace(source,'n==(20000 if train else 64)','n==(20000 if train else 80)')
 source=replace(source,"if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SPIN_STAGE','RM_SLOPE_INITIAL_ADMISSION')","if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')")
 source=replace(source,"RM_GYRO_CURRICULUM='1'","RM_GYRO_CURRICULUM='0'")
 source=replace(source,"RM_HEIGHT_MIN='.23',RM_HEIGHT_MAX='.33'","RM_HEIGHT_MIN='.25',RM_HEIGHT_MAX='.25'")
 source=replace(source,"original=read(payload/'job0/original_run_manifest.json')['env']","original=read(P/'E0_original_run_manifest_frozen_v1.json')['env']")
 source=replace(source,"import mixed209_sdk as sdk","# Restore the actual frozen E0 command class after the historical H1 import alias.\n sys.modules.pop('directional_spin_runtime',None)\n import mixed209_sdk as sdk")
 source=replace(source,'next_iteration=5000','next_iteration=32067')
 source=replace(source,'num_envs=64,literal_original_reward_calls','num_envs=80,literal_original_reward_calls')
 source=replace(source,'assert ck[\'iter\']==32066 and runner.alg.load(ck,None,True)',"assert ck['iter']==32066 and runner.alg.load(ck,None,True)\n  # Restore learning/sampling RNG from this branch; newly mixed episodes and\n  # command/physical/DR histories are explicitly fresh.\n  prior_rng=ck['target_DR_state']\n  torch.random.set_rng_state(prior_rng['global_CPU_rng'].cpu())\n  torch.cuda.set_rng_state_all([x.cpu() for x in prior_rng['global_CUDA_rng']])")
 source=replace(source,"target_DR_state=fresh_dr_state(),","target_DR_state=fresh_dr_state(),mixed_ground_JUMP_state=mixed_state(),")
 source=replace(source,"def save(label):",'''def mixed_state():
 cmd=real.command_manager.get_term('twist')
 fields=('vel_command_b','time_left','command_counter','is_standing_env','is_heading_env','is_pure_spin','is_moving_spin','is_transition_spin','world_direction','signed_yaw','phase_elapsed','command_uid209')
 command={key:cpu(getattr(cmd,key)) for key in fields if hasattr(cmd,key)}
 command['private_E0_mode_rng']=cmd._mode_rng.get_state().cpu()
 stateful={}
 for name in real.reward_manager.active_terms:
  fn=real.reward_manager.get_term_cfg(name).func
  inner=getattr(fn,'original',None)
  tracker=getattr(inner,'tracker',None)
  if tracker is not None:stateful[name]={k:cpu(v) for k,v in vars(tracker).items()}
 return dict(flat_mask=cpu(real._mixed209_flat),mode=cpu(real._mod4_mode_bit),height=cpu(real._mod4_height_cmd),command=command,
  ground_reward_episode_sums=cpu(real.reward_manager._episode_sums),stateful_ground_rewards=stateful,
  physical_history_scope='Fresh mixed episodes/queues, no exact PhysX checkpoint continuation',frozen_E0_reference_immutable=True)

def save(label):''')
 source=replace(source,"obs=vec.get_observations();assert obs['policy'].shape",'''obs=vec.get_observations()
 flat=real._mixed209_flat;cmd=real.command_manager.get_term('twist')
 assert int(flat.sum())==n//10 and torch.equal(real._mod4_mode_bit,(~flat).long())
 assert torch.equal(obs['policy'][:,28:35].argmax(1),real._mod4_mode_bit)
 assert (real._mod4_height_cmd[flat]==.25).all() and ((real._mod4_height_cmd[~flat]>=.12)&(real._mod4_height_cmd[~flat]<=.15)).all()
 assert (cmd.time_left[~flat]<=20.).all() and not (cmd.is_pure_spin[~flat]|cmd.is_moving_spin[~flat]|cmd.is_standing_env[~flat]).any()
 assert obs['policy'].shape''')
 source=replace(source,"assert real.literal.calls==8",'''assert torch.equal(real._mod4_mode_bit,(~flat).long())
  assert int(flat.sum())==8 and int((~flat).sum())==72
  assert len(real.reward_manager.active_terms)>16 and 'original_jump209' in real.reward_manager.active_terms
  # The actual stateful E0 and literal kernels were both called by the original
  # RewardManager at the existing policy clock; neither is a custom reward.
  assert real.literal.calls==8''')
 source=replace(source,'original_JUMP195_reward_and_plane=True','original_JUMP_reward_and_plane=True,ground_envs=2000,jump_envs=18000,original_E0_ground_reward_and_commands=True')
 source=replace(source,"fresh physics, no exact PhysX resume.","fresh mixed physics, no exact PhysX resume.")
 ast.parse(source)
 write(P/'run209_mixed_E0_JUMP_worker.py',source)
 shutil.copyfile(N/'mixed209_task_protocol.py',P/'mixed209_task_protocol.py')
 # Existing producer integrity for assets, no asset/model/raw rehash for source preparation.
 old_manifest=json.loads((S/'PRIMARY197_COMPLETE_MANIFEST.json').read_bytes())
 old={x['relative']:x for x in old_manifest['files']}
 rows=[]
 for path in sorted(P.rglob('*')):
  if not path.is_file():continue
  rel=path.relative_to(P).as_posix()
  if path.suffix.lower() in ('.usd','.usda','.usdc','.npz','.npy','.stl','.pt'):
   assert rel in old and old[rel]['bytes']==path.stat().st_size,rel
   sha=old[rel]['SHA'];kind='existing_producer_SHA_no_rehash'
  else:sha=H(path);kind='source_UTF8_or_small_metadata_actual'
  rows.append(dict(relative=rel,local_relative='package/'+rel,bytes=path.stat().st_size,SHA=sha,index_kind=kind))
 write(N/'PACKAGE209_MANIFEST.json',json.dumps(dict(kind='FROZEN_MIXED209_COMPLETE_PACKAGE',files=rows),indent=2))
 put('FROZEN209_LATEST32066_GROUND10_JUMP90_SOURCE_HANDOFF.json',dict(epoch=time.time(),passed_source_preparation=True,source_SHA=SHA,source_iteration=32066,source_Adam=642840,
  frozen_original_E0_not_overwritten=True,ground_fraction=.1,jump_fraction=.9,ground_command='exact DirectionalSpinCommand source8fed717b...',
  source_only=True,source_CPU_pending=True,target_admission_and_GO_pending=True,package_manifest_SHA=H(N/'PACKAGE209_MANIFEST.json'),
  no_model_binary_raw_NPZ_decode_SDK_GPU_SSH=True,
  preserved_lookup_errors=['old E0 original_run_manifest.json guessed inside runtime directory absent; exact frozen manifest joined via existing input manifest','scut_rescue_rewards.py guessed absent; actual module is scut_flat_rescue.py','world_drift_runtime.py guessed absent; actual manager module is world_drift_isaac.py'],
  supersedes_202_original_E0_reinitialization_default='human latest continue E0 branch selects latest32066, originalE0 remains frozen reference'))
 print(json.dumps(dict(passed=True,source_files=len(rows),source_only=True)))

if __name__=='__main__':
 try:main()
 except BaseException:
  put('SOURCE209_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
