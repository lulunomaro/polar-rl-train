from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;D=N/'train_package';D.mkdir()
old=T/'DELIVERED_JUMP4999_TOTAL_PLAN_400N50_DR_270_CHECK_V187_20261031/V2_EXISTING_NORMALIZED_CLOCK_AND_FEEDBACK_SOURCE'
shutil.copytree(old/'payload',D/'payload')
for p in (N/'package_v2').glob('*.py'):shutil.copyfile(p,D/p.name)
for name in ['stairs3_heightfield_sdk_bridge188.py','stairs3_measured_boundary188.py','stairs3_sdk188.py','run188_literal_stairs3_40050_worker.py','zonglin2_app_launcher.py']:
 shutil.copyfile(N/name,D/name)
for name in ['legged_robot.py','legged_robot_config.py','wheel_legged_config.py']:
 p=N/'upstream/plane/logs/wheel_legged/上台阶3'/name;q=D/'original_source'/name;q.parent.mkdir(exist_ok=True);shutil.copyfile(p,q)
p=N/'upstream/plane/wheel_legged_gym/utils/terrain.py';shutil.copyfile(p,D/'original_source/terrain.py')
proof=json.loads((N/'reports/ROOT188_NEW_LITERAL_STAIRS3_REWARD_TERRAIN_CPU_RETURNED_ACTUAL.json').read_bytes());assert proof['passed']
oldtask=json.loads((T/'MOD4_DELIVERED_FUDAN_JUMP4999_REUSE_RESOURCE_V186_20261031/TASK186.json').read_bytes())
task=dict(schema='mod4.literal-original-STAIRS3.own400N50.D0-D7.fullstate4999.v188',
 kind='FUDAN_STAIRS3_LITERAL_400N50_D0_D7_REUSE4999',literal_reward_snapshot='plane/logs/wheel_legged/上台阶3',
 upstream='yly-true/fudan_rl_wheel_leg',commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',
 source_SHA=oldtask['input_SHA'],formal_source_model=oldtask['formal_source_model'],source_bytes=1244341,
 source_iteration=4999,source_Adam_step=100020,learned_STD6=oldtask['learned_STD6'],
 preserve_actor_critic_all17Adam_and_STD=True,source_trained_policy_hz=100,source_gas_nominal_k=3500,
 actor_obs=35,critic_obs=38,action_dim=6,learned_obs_normalizer_tensors=0,
 num_envs=20000,admission_num_envs=64,admission_controls=8,physics_dt=.0025,policy_hz=50,feedback_hz=100,
 decimation=8,TGS=[32,4],gas_nominal_k=2000,nominal_gas_each_N_engineering=400,
 DR_profiles='Approved original D0white_v3,D1D2sensor,D3feedback100Hz,D4physicaldelay,D5spring,D6damping,D7COMexplicitPD',
 discount_gamma=.9801,discount_lam=.9025,raw_action_clip=6,episode_seconds=20,
 reward_core_source=str(N/'package_v2/literal_stairs3_original_methods.py'),reward_weights_and_functions_no_edits=True,
 reward_source_CPU_report_SHA=hashlib.sha256((N/'reports/ROOT188_NEW_LITERAL_STAIRS3_REWARD_TERRAIN_CPU_RETURNED_ACTUAL.json').read_bytes()).hexdigest(),
 reward_selected16=proof['groups'][1]['scales'],single_reward_clip=1,original_total_positive_clip=False,
 source_reward_dt_once=True,terrain_mesh_type='trimesh',terrain_rows=10,terrain_cols=20,initial_max_level=5,
 terrain_proportions=[0.,0.,0.,.5,.5,0.],terrain_step_width=.7,terrain_step_height_formula='.05+.18*difficulty',
 terrain_physical_vertical_quantization=.005,original_Fudan_terrain_class_literal=True,
 terrain_CPU_raw_heightfield_SHA=proof['groups'][-1]['heightfield_SHA'],
 no_custom270_bonus_or_h1_event_reward=True,ultimate270_success_not_inferred_from_curriculum=True,
 motor_PD_hardware_closure_perenv2mm_and_mimic01_retained=True,
 only_standard_ground_reset_on_original_own_feasible_pose_bank=True,
 no_scripted_force_velocity_or_mid_episode_state_injection=True,
 source4999_finite_CPU_admission_reused_without_new_PT_CPU_read=True,
 target_DR_rng_sensor_queue_and_curriculum_states_explicitly_new=True,
 fresh_physics_not_exact_original_simulation_resume=True,
 maximum_parent_seconds=3900,save_deadline_seconds=3600,exit_headroom_seconds=300,
 single_forwarded4090_only=True,sole72_original_writer=True,
 no_plain186_or_cold_comparison=True)
(D/'TASK188.json').write_text(json.dumps(task,ensure_ascii=False,indent=2),encoding='utf8')
rows=[]
oldm=json.loads((old/'FROZEN_EVAL187_COMPLETE_MANIFEST.json').read_bytes());known={r['relative']:r for r in oldm['files'] if r['relative'].startswith('payload/')}
for p in sorted(D.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(D).as_posix()
 if p.suffix.lower() in ('.usd','.usda','.npz','.npy'):
  k=known[rel];assert p.stat().st_size==k['bytes'];sha=k['SHA']
 else:
  raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
  if p.suffix=='.py':ast.parse(raw)
 rows.append(dict(relative=rel,local_relative='train_package/'+rel,bytes=p.stat().st_size,SHA=sha))
manifest=dict(schema=task['schema'],files=rows,model_files=0,task_SHA=hashlib.sha256((D/'TASK188.json').read_bytes()).hexdigest())
(N/'TRAIN188_COMPLETE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(dict(files=len(rows),bytes=sum(r['bytes'] for r in rows),task_SHA=manifest['task_SHA'],reward_functions_unchanged=True)))
