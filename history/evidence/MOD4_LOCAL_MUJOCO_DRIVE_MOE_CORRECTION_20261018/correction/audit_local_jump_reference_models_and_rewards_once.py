"""Inspect already downloaded public references; no training or model substitution."""
from pathlib import Path
import hashlib,json,time,ast,shutil,tomllib
import onnx
B=Path(__file__).resolve().parent;W=B.parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=B/'reference_source_snapshots';src.mkdir()
paths={
 'fudan_jump_robot':W/'reference_repos/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot.py',
 'fudan_jump_config':W/'reference_repos/fudan_rl_wheel_leg/jump/wheel_legged_gym/envs/base/legged_robot_config.py',
 'fudan_deploy_params':W/'audits/20260925/fudan_rl_deploy/pseudocode/policy_params_design.hpp',
 'scut_jump_takeoff':W/'reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/jump_takeoff.py',
 'scut_airborne':W/'reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py',
 'scut_V14_cfg':W/'reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py'}
index={}
for key,p in paths.items():
    dest=src/(key+p.suffix);shutil.copy2(p,dest)
    index[key]=dict(original=str(p),bytes=p.stat().st_size,SHA=H(p),snapshot=str(dest))
p=W/'audits/20260925/fudan_rl_deploy/pseudocode/example/onnx/jump/jump_pos0.2_0.4_p6.0_d0.5_0.2.onnx'
m=onnx.load(str(p));onnx.checker.check_model(m)
def shape(v):return [d.dim_value or d.dim_param for d in v.type.tensor_type.shape.dim]
model=dict(path=str(p),bytes=p.stat().st_size,SHA=H(p),valid_ONNX_graph=True,
    inputs=[dict(name=v.name,shape=shape(v)) for v in m.graph.input],outputs=[dict(name=v.name,shape=shape(v)) for v in m.graph.output],
    no_inference_or_execution_on_MOD4=True)
out=dict(epoch=time.time(),user_observation='我测了测跳跃确实不太行',observation_is_qualitative_not_new_formal_skill_score=True,
    found_in_existing_local_downloads=True,fudan_jump_deployed_model=model,source_index=index,
    fudan_jump_reward_config=dict(flight=.15,encourage_jump=1,base_height_flight=6,leg_tuck=1.7,takeoff_extend=.5,line_z=6,orientation=-25,ang_vel_xy=-.1),
    fudan_model_interface_not_dropin_MOD4_35=True,fudan_virtual_leg_kinematics_PD_middle_positions_and_history_required=True,
    scut_jump_types=['takeoff_vel_z','upward_accel_z','release_vel_z_shortfall','release_vel_z_tracking_exp','push_height_tracking_exp','push_vel_z_tracking_exp','peak_height_tracking_exp','leg_retraction','wheel_airtime'],
    scut_airborne_landing_candidates=['wheel_zero_torque_exp','wheel_directional_speed','wheel_directional_speed_shortfall','landing_wheel_max_contact_force','landing_traj_height_exp','landing_traj_vel_z_exp'],
    scut_functions_not_all_enabled_in_default_config=True,scut_state_machine_assist_force_and_terrain_filters_not_authorized_MOD4_features=True,
    no_change_to_live_PPO_reward_LR_STD_geometry_or_guards=True,
    upstream_reference_urls=['https://github.com/chushanxiaodaoshi/XYEGA_RM2026_WheelLeg_Infatry_RLdeploy',
        'https://github.com/yly-true/fudan_rl_wheel_leg','https://github.com/scutrobotlab/wheeled-legged_RL'],
    upstream_page_checked_not_all_repository_HEAD_or_binary_byteexact_claim=True)
(B/'reports/LOCAL_FUDAN_JUMP_MODEL_SCUT_JUMP_REWARDS_RESEARCH_ACTUAL.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
# Verify the existing app update through actual saved TOML, without modifying it.
args=json.loads((W/'MOD4_THREE_GPU_HOUR5_CONTINUATION_20261018/AUTOMATION_FIFTH_HOUR_AND_FULL_RM7V7_V21_ARGS.json').read_text(encoding='utf-8'))
t=tomllib.loads((Path.home()/'.codex/automations/mod4-10/automation.toml').read_text(encoding='utf-8'))
assert t['prompt'].strip()==args['prompt'].strip() and t['target_thread_id']==args['targetThreadId'] and t['status']=='ACTIVE' and t['rrule']==args['rrule']
(B/'reports/V21_AUTOMATION_TOML_ACTUAL_READBACK_VERIFIED.json').write_text(json.dumps(dict(epoch=time.time(),same_original_target=True,ACTIVE=True,hourly_unchanged=True,prompt_SHA=hashlib.sha256(t['prompt'].strip().encode()).hexdigest(),exact_V21_prompt_verified=True,official_docs_checked='https://learn.chatgpt.com/docs/automations?surface=app'),indent=2),encoding='utf-8')
print(json.dumps(dict(fudan_jump_ONNX=model,scut_reward_sources_found=True),ensure_ascii=False))
