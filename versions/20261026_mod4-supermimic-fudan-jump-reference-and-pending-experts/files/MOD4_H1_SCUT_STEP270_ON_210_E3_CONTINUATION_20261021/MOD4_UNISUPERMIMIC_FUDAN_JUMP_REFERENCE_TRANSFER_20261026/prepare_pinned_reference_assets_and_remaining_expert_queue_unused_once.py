from pathlib import Path
import json,posixpath,time,urllib.parse,xml.etree.ElementTree as ET
J=Path(__file__).resolve().parent;T=J.parent;R=J/'reports';R.mkdir(exist_ok=True)
revision='8204e853dfd2ed06d85a322e1a998c3d20a3be2c';raw=json.loads((J/'public_sources/github_fetch_2_actual.json').read_bytes());tree=json.loads(raw['structuredContent']['content']);assert not tree['truncated'];rows={x['path']:x for x in tree['tree'] if x['type']=='blob'}
xml='mujoco/assert_now/infantry_binglian_yuntai/infantry_V2/meshes/mjmodel.xml';paths={xml,'mujoco/python_tools/onnx_mj_chuanlian.py','mujoco/python_tools/onnx_mj_binglian.py','README.md','jump/wheel_legged_gym/envs/base/legged_robot_config.py','jump/export_onnx/export_onnx.py','mujoco/actor/yuntai/p60.50.2把urdf中力矩限制为50.onnx','mujoco/actor/yuntai/上台阶3_angz+.onnx'}
for element in ET.parse(J/'source'/xml).getroot().findall('./asset/*'):
 if element.get('file'):
  path=posixpath.normpath(posixpath.join(posixpath.dirname(xml),element.get('file')));assert not path.startswith('../') and path in rows;paths.add(path)
files=[]
for path in sorted(paths):
 x=rows[path];files.append(dict(path=path,bytes=x['size'],Git_blob_SHA1=x['sha'],url='https://raw.githubusercontent.com/yly-true/fudan_rl_wheel_leg/'+revision+'/'+urllib.parse.quote(path,safe='/')))
assert sum(x['bytes'] for x in files)<60*1024**2 and len(files)<=30
plan=dict(epoch=time.time(),repository='https://github.com/yly-true/fudan_rl_wheel_leg',revision=revision,files=files,total_bytes=sum(x['bytes'] for x in files),remote_root='/home/lc01/Zonglin Li/zonglin2/research/MOD4_SUPERMIMIC_FUDAN_REFERENCE_20261026',teacher_jump_policy='mujoco/actor/yuntai/p60.50.2把urdf中力矩限制为50.onnx',teacher_plane_settle_return_policy='mujoco/actor/yuntai/上台阶3_angz+.onnx',mode_selection_source='mujoco/python_tools/onnx_mj_chuanlian.py RUNTIME_PRESETS',policy_duration_s=.55,only_selected_two_small_ONNX_and_XML_referenced_assets_not_full_repository_or_worldmodel_weights=True,download_and_rollout_not_yet_run=True,headless_CPU_reference_on72_only=True,no_local_Windows_policy_or_physics=True)
with (R/'PINNED_FOREIGN_REFERENCE_ASSET_DOWNLOAD_PLAN_SOURCE_ONLY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(plan,f,ensure_ascii=False,indent=2)
queue=[
 dict(expert='H1_step270',priority=1,existing_training='trained_not_graduated',reference='Fudan jump policy on its model then taskspace/closed-chain retargeting',status='source_review_reference_validation_pending'),
 dict(expert='E2_world_moving',priority=2,existing_training='trained_not_graduated',reference='validated original/our own rotation-translation demonstrations',status='demonstration_contract_pending'),
 dict(expert='E3_recovery',priority=2,existing_training='trained_not_graduated',reference='validated fallen-to-upright recovery demonstrations with stable hold',status='demonstration_contract_pending'),
 dict(expert='E1_CURB',priority=3,existing_training='partial_course',reference='validated curb and obstacle passage trajectories',status='demonstration_contract_pending'),
 dict(expert='E1_SLOPE',priority=3,existing_training='partial_course_5deg_seen',reference='validated slope traversal trajectories for required ranges',status='demonstration_contract_pending'),
 dict(expert='E4_low_tunnel',priority=4,existing_training='not_trained',reference='feasible low-posture entry passage and exit demonstrations',status='demonstration_not_yet_available'),
 dict(expert='continuous_stairs',priority=5,existing_training='independent_course_incomplete',reference='multi-step ascent and recovery demonstrations distinct from H1 single step',status='demonstration_not_yet_validated'),
 dict(expert='flyramp_gap_landing',priority=5,existing_training='extended_courses_incomplete',reference='separate takeoff flight crossing landing and stabilization demonstrations',status='demonstration_not_yet_validated')]
with (R/'HUMAN_ALL_REMAINING_EXPERTS_THROUGH_SUPERMIMIC_QUEUE_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),human_latest_instruction='不止是跳跃，其他什么那些我们还没弄得专家都通过supermimic来搞一下',scope='All unfinished expert skills enter the SuperMimic demonstration/retargeting/own-environment learning/acceptance pipeline',preserve_frozen_E0_W35_and_all_current_qualified_models=True,keep_existing_baselines_for_comparison=True,experts=queue,first_validate_H1_reference_and_finalization_protocol_then_parallelize_within_existing_three_GPU_budget=True,no_subagents_no_new_budget_extension=True,queue_is_not_Task_GO_or_graduation=True,foreign_dynamics_transitions_not_groundtruth_for_our_world_model=True),f,ensure_ascii=False,indent=2)
print(json.dumps(dict(prepared_files=len(files),planned_bytes=plan['total_bytes'],remaining_skill_entries=len(queue),no_download_or_rollout_yet=True)))
