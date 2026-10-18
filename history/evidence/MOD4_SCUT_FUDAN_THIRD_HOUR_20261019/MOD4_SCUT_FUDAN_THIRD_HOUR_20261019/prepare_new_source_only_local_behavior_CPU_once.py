"""Reuse the recorded local diagnostic protocol only for the new complete source."""
from pathlib import Path
import ast,json,time
B=Path(__file__).resolve().parent;Q=B.parent/'MOD4_SCUT_FUDAN_SECOND_HOUR_20261019';R=B/'reports'
f=json.loads((Q/'reports/THREE_HOUR_ALL_CLOSED_FINAL_MODELS_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert f['passed_all_three_whole_final_models_CPU']
s=(Q/'review_first_reward_hour_local_mujoco_behavior_V2_once.py').read_text('utf8').replace("P=W/'MOD4_SCUT_FUDAN_JUMP_REWARD_20261019'","P=W/'MOD4_SCUT_FUDAN_SECOND_HOUR_20261019'")
a=s.index(" sources={'before_reward':");z=s.index('\n dest=',a)
s=s[:a]+" sources={'after_reward_hour2':(Path(finals['experts']['h1']['final']['local_path']),finals['experts']['h1']['final']['SHA'])}"+s[z:]
s=s.replace('FIRST_SCUT_FUDAN_HOUR_LOCAL_MUJOCO_BEHAVIOR_V2_ACTUAL.json','SECOND_SCUT_FUDAN_HOUR_NEW_SOURCE_LOCAL_MUJOCO_BEHAVIOR_ACTUAL.json').replace('local_first_reward_hour_trajectories_v2','local_second_reward_hour_new_source_trajectories').replace('scut-fudan-first-hour-local-flat-mujoco-prefix','scut-fudan-second-hour-new-source-local-flat-mujoco-prefix')
ast.parse(s)
with (B/'review_second_reward_hour_new_source_local_behavior_once.py').open('x',encoding='utf8') as p:p.write(s)
with (R/'SECOND_HOUR_LOCAL_BEHAVIOR_PROTOCOL_PREPARED_CPU_ACTUAL.json').open('x',encoding='utf8') as p:json.dump(dict(epoch=time.time(),new_source=f['experts']['h1']['final'],original_recorded_local_protocol_reused=True,only_new_checkpoint_four_normal_jump_yaw0pi_trajectories=True,prior_case_replay=False,phase_thresholds_physics_reset_control_config_unchanged=True,previous_first_hour_results_read_only_reference=str(Q/'reports/FIRST_REWARD_LOCAL_TRAJECTORY_READINESS_AND_CLEARANCE_CPU_ACTUAL.json'),no_PhysX_or_skill_PASS_or_player_write=True),p,indent=2)
print('New-source-only local diagnostic prepared; old cases will not replay.')
