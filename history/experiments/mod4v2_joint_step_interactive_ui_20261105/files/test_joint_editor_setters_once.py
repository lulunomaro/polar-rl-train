"""Bounded hidden editor-API check in separate metadata folder; never reset/reopen the user's session."""
from pathlib import Path
import sys,json,math,traceback
import numpy as np
D=Path(__file__).resolve().parent;T=D/'functional_check';OUT=D/'FUNCTIONAL_CHECK.json';assert not T.exists()and not OUT.exists();T.mkdir();(T/'interactive_scene.xml').write_bytes((D/'interactive_scene.xml').read_bytes());sys.path.insert(0,str(D));from joint_step_viewer import JointStepViewer
checks={};errors=[];details={};app=None
try:
 app=JointStepViewer(T/'interactive_scene.xml');app.window.withdraw()
 def ck(k,v):
  checks[k]=bool(v)
  if not v:raise AssertionError(k)
 def q(name):return float(app.data.qpos[app.model.joint(name).qposadr[0]])
 app.set_joint_target('left_hip',1.2);ck('hip_beyond_old_half_rad_and_delta_preserved',abs(q('left_hip')-1.2)<1e-9 and abs(q('left_crank')-1.2)<1e-9)
 knee=app.ik.leg_configuration(1.2,1.4,side='left')[0]['knee'];app.set_joint_target('left_knee',knee);ck('passive_joint_inverse_preserves_closure_branch',abs(q('left_knee')-knee)<1e-7 and abs(q('left_crank')-1.4)<1e-7)
 app.set_joint_target('left_drive_hip_spin',1.2+2*math.pi);ck('follower_maps_to_continuous_leader',abs(q('left_hip')-(1.2+2*math.pi))<1e-8 and abs(q('left_drive_hip_spin')-q('left_hip'))<1e-9)
 before=app.data.qpos.copy();rejected=False
 try:app.set_joint_target('right_gas_slide',.14-float(app.ik.PARAMS['neutral_gas_eye_length_m']['right']))
 except ValueError as exc:rejected=True;details['gas_lower_rejection']=str(exc)
 ck('hardware140_but_mechanism_stop_rejects_without_mutation',rejected and np.array_equal(before,app.data.qpos))
 app.set_joint_target('right_wheel_spin',math.pi);app.set_joint_target('guide_roller_00',.4);ck('wheel_and_free_roller_adjustable',abs(q('right_wheel_spin')-math.pi)<1e-9 and abs(q('guide_roller_00')-.4)<1e-9)
 app.set_root_pose(x=.1,z=.5,yaw=.2);ck('root_pose_adjustable_without_auto_lift',abs(float(app.data.qpos[0])-.1)<1e-9 and abs(float(app.data.qpos[2])-.5)<1e-9)
 metrics=app._metrics();details['metrics']=metrics;ck('closed_chain_still_closed',metrics['closure_max_m']<1e-6)
 ck('all30_controls_exist',len(app.joint_names)==30 and len(app.controls)>=30)
except BaseException:errors.append(traceback.format_exc())
finally:
 if app is not None:app.close()
r=dict(passed=not errors and all(checks.values()),checks=checks,details=details,errors=errors,user_GUI_metadata_or_pose_changed=False,visible_second_window_or_policy_or_integration=False)
OUT.write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf8');print(json.dumps(dict(receipt=str(OUT),passed=r['passed'],failed=[k for k,v in checks.items()if not v],errors=errors),indent=2,ensure_ascii=False));raise SystemExit(0 if r['passed']else 1)
