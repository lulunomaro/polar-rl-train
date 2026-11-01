"""Fresh user visual purpose. Reuse230 actual poses; no new physics or model."""
from pathlib import Path
import hashlib,json,time
T=Path(__file__).resolve().parent;N=T/'E0_CANDIDATE225_USER_MUJOCO_V237_20261101'
assert not N.exists();N.mkdir();R=N/'reports';R.mkdir()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
r230=T/'E0_CANDIDATE225_CONTROLLED_PHYSICAL_REGRESSION_V230_20261101/reports/ROOT230_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json'
r220=T/'E0_NEW210_FORMAL_MEAN_PLANE_FLIGHT_SOURCE_V220_20261101/reports/ROOT220V2_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json'
x=read(r230);y=read(r220)
rows230={Path(a['path']).name:json.loads(a['UTF8']) for a in x['full_UTF8'] if a['path'].endswith('.json')}
rows220={Path(a['path']).name:json.loads(a['UTF8']) for a in y['full_UTF8'] if a['path'].endswith('.json')}
assert x['passed_execution'] and rows230['CAPTURE230_ACTUAL_RESULT.json']['passed']
task230=rows230['TASK230_ADMITTED_ACTUAL.json'];task220=rows220['TASK220_ADMITTED_ACTUAL.json']
assert task230['qualified197_package_root']==task220['qualified197_package_root']
names=rows220['CAPTURE220_ACTUAL_RESULT.json']['body_names'];assert len(names)==31 and names[0]=='chassis' and len(set(names))==31
case=next(z for z in rows230['CAPTURE230_ACTUAL_RESULT.json']['cases'] if z['name']=='literal_jump')
assert case['controls']==500 and case['seconds']==10. and case['requested_window_complete']
assert not any(case['first_episode_original_terminal_flags'].values())
visual=read(T/'H1_NATIVE178_LATEST_USER_MUJOCO_MOTION_WM_V180_20261031/CPU_DISPLAY180_ACTUAL_V2/USER180_DISPLAY_DATA_COMPLETE.json')['visual_assets']
put('FROZEN237_FRESH_USER_E0_DISPLAY_PURPOSE_BEFORE_IO.json',dict(epoch=time.time(),human_exact='e0分支mujoco让我看看',
 selected_case=case,selected_model_SHA=task230['model_SHA'],model_iteration=32341,
 independent225_repaired_copy_not_new_learned_policy=True,original_frozen_E0_and_parent210_unchanged=True,
 remote_pose_transfers=1,remote_pose_physical_byte_opens=1,stream_integrity_passes=1,
 local_view_pose_byte_open=1,local_view_integrity_passes=1,npz_members_selected=['body_position_w','body_quat_xyzw','root13','wheel_contact_xyz','authored_wheel_bottom'],
 local_npz_member_reads_selected_each=1,model_reads=0,other_raw_reads=0,new_SDK_GPU_neural_controls=0,
 body_names=names,body_order_binding=dict(actual220_report=str(r220),same_exact_qualified_payload_root=task230['qualified197_package_root'],
   same_original_robot_asset_and_SDK_order_unchanged=True,actual230_wheel_names=[a['name'] for a in rows230['ACTUAL230_OWN_ALREADY_LOADED_WHEEL_GEOMETRY.json']['wheels']],
   before_render_chassis_root_pose_consistency_required=True),
 visual_assets=visual,window_seconds_max=7200,display_only=True,no_mj_step=True,no_PPO_WM_prediction=True,
 labels='E0 branch / trained32341 independent225 repair copy / recorded230 literal_jump / NOT LIVE / not stablejump or270',
 read_purpose_not_for_stats_or_Git=True,old_windows_preserved_new_user_request=True))
print(json.dumps(dict(source_purpose_frozen=True,selected=case['producer'],body_names=31,model_or_raw_reads=0)))
