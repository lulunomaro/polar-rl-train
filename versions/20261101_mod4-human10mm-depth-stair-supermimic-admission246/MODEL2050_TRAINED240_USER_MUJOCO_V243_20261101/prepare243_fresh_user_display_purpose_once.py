"""Bind fresh user display to completed242; no pose/model/SDK read."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports';R.mkdir(exist_ok=True);T=N.parent
X=T/'MODEL2050_NEW240_CLOSED_MEAN_REGRESSION_SOURCE_V242_20261101/reports'
x=json.loads((X/'ROOT242_COMPACT_ACTUAL_WHEEL_AIR_CLOSURE_AND_SHORT_GROUND_REGRESSION.json').read_bytes())
full=json.loads((X/'ROOT242_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json').read_bytes())
assert x['execution_passed']and x['source_model_SHA']=='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'
names=None
for row in full['full_UTF8']:
 if Path(row['path']).name=='ACTUAL242_ORIGINAL_MIXED_REWARD_AND_PLANT.json':names=json.loads(row['UTF8'])['binding']['original_jump_binding']['body_names']
assert names and len(names)==31
old=json.loads((T/'H1_NATIVE178_LATEST_USER_MUJOCO_MOTION_WM_V180_20261031/CPU_DISPLAY180_ACTUAL_V2/USER180_DISPLAY_DATA_COMPLETE.json').read_bytes())['visual_assets']
value=dict(epoch=time.time(),human_exact='放mujoco让我看看',read_purpose='Fresh user-requested visible display of latest trainedmodel240 iteration2135 actual242 four first episodes; not statistics/Git/learning or live replay.',model_iteration=2135,selected_model_SHA=x['source_model_SHA'],body_names=names,body_order_binding='Actual242 SDK binding_receipt body_names; xyzw SDK quaternion, convert wxyz for MuJoCo only.',cases=x['cases'],visual_assets=old,npz_members_selected=['body_position_w','body_quat_xyzw','root13','wheel_contact_xyz','authored_wheel_bottom'],remote_pose_byte_open_and_transfer_per_case=1,local_pose_byte_open_and_integrity_per_case=1,npz_member_reads_each_per_case=1,model_reads=0,new_SDK_GPU_controls=0,local_neural_CUDA=False,no_mj_step=True,display_only=True,window_seconds_max=7200,default_case='literal_jump',default_speed=.1,old_windows='Preserve; fresh new user request, no old237 window actions.',labels='RECORDED242 / trained MODEL2050 adaptation240 / iteration2135 /400N50fullDR / original closure reset / NOT LIVE / no stablelanding or270 claim.')
paths=[N/'collect243_selected242_poses_for_fresh_user_once.py',N/'view243_trained240_actual242_true_MOD4.py',N/'launch243_fresh_user_trained240_once.py',Path(__file__).resolve()]
for p in paths:ast.parse(p.read_text('utf8'),filename=str(p))
value['source_AST_passed']=len(paths);value['source_files']=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in paths]
with (R/'FROZEN243_FRESH_USER_DISPLAY_PURPOSE_BEFORE_IO.json').open('x',encoding='utf8')as f:json.dump(value,f,indent=2,allow_nan=False)
print(json.dumps(dict(passed=True,model_iteration=2135,cases=[c['name']for c in value['cases']],pose_or_model_reads=0,source_AST=len(paths))))
