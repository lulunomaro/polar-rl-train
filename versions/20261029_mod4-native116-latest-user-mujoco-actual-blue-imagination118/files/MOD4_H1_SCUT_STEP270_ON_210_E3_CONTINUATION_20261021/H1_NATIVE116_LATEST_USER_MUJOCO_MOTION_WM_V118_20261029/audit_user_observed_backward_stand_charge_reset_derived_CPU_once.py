"""New necessary purpose: explain user's observed116 action sequence.
One read of derived display NPZ, three actual-pose arrays; no PT/physics raw/GPU.
"""
from pathlib import Path
import csv,hashlib,io,json,math,time
import numpy as np
S=Path(__file__).resolve().parent;D=S/'user_action_sequence_review';assert not D.exists();D.mkdir()
proof=json.loads((S/'display/reports/USER_DISPLAY_DATA_COMPLETE.json').read_bytes());row=proof['pose_file'];p=Path(row['path'])
(D/'DERIVED_POSE_DIAGNOSTIC_PURPOSE_CONSUMED.json').write_text(json.dumps(dict(epoch=time.time(),purpose='User observed backward-lean-stand-charge-reset sequence; determine motion timing versus request and original termination',derived_NPZ_reads_planned=1,arrays=['actual_position','actual_rotation','actual_wheel_bottom'],checkpoint_physics_raw_GPU_network_reads=0,not_an_extra_training_or_model_stats_read=True),indent=2),encoding='utf8')
raw=p.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
with np.load(io.BytesIO(raw),allow_pickle=False) as z:pos=z['actual_position'];rot=z['actual_rotation'];bottom=z['actual_wheel_bottom']
root=pos[:,0];x=root[:,0];height=root[:,2];tilt=np.arccos(np.clip(rot[:,0,2,2],-1,1));n=len(x);t=(np.arange(n)+1)*.01
def event(k):return dict(control=int(k+1),seconds=float(t[k]),root_x=float(x[k]),root_z=float(height[k]),root_tilt_degrees=float(tilt[k]*180/math.pi),wheel_bottom_m=[float(y) for y in bottom[k]],request_active=bool(k>=200))
case=json.loads((S/'reports/FROZEN118_SINGLE_CASE_AND_WM_DIAGNOSTIC_RETURNED_ACTUAL.json').read_bytes())['case']['result']
value=dict(epoch=time.time(),source_latest116_SHA=proof['actual_source_SHA'],derived_NPZ_read_count=1,actual_pose_arrays_read_once=3,source_bytes=row['bytes'],source_SHA=row['SHA'],
    case_controls=n,start=event(0),most_backward=event(int(x.argmin())),highest_body=event(int(height.argmax())),maximum_forward=event(int(x.argmax())),maximum_tilt=event(int(tilt.argmax())),bothwheel_highest_control_endpoint=event(int(bottom.min(axis=1).argmax())),last=event(n-1),
    first2s_standing_request_off=dict(root_dx=float(x[199]-x[0]),body_z_rise=float(height[:200].max()-height[0]),max_both_wheel_bottom=float(bottom[:200].min(axis=1).max())),
    exact_cached_termination=case['last_termination_terms'],one_episode_original_termination_then_viewer_replays=True,not_multiple_independent_trials=True,
    body_rise_is_not_wheel_clearance=True,only_100Hz_control_endpoints_not_full400Hz_peak=True,no_contact_airborne_proof_from_pose_alone=True,not_unique_reward_or_mechanical_cause=True)
(D/'USER_OBSERVED_SEQUENCE_AND_ORIGINAL_CLOSURE_ACTUAL.json').write_text(json.dumps(value,indent=2),encoding='utf8')
with (D/'ACTUAL118_DERIVED_ROOT_HEIGHT_TILT_WHEEL_TIMELINE.csv').open('w',newline='',encoding='utf8') as f:
    w=csv.writer(f);w.writerow(['control','seconds','request','root_x_m','root_z_m','tilt_deg','left_wheel_bottom_m','right_wheel_bottom_m'])
    for i in range(n):w.writerow([i+1,t[i],int(i>=200),x[i],height[i],tilt[i]*180/math.pi,*bottom[i]])
print(json.dumps({k:v for k,v in value.items() if k in ('start','most_backward','highest_body','maximum_forward','first2s_standing_request_off','last')}))
