"""Verify stop-only causal isolation from existing TRAIN traces. 0 physics."""
from pathlib import Path
import json,struct,hashlib
R=Path(__file__).resolve().parent;A=R/'ROUGH_WORLD_LEG_V3'/'prefix_validation001';A.mkdir(exist_ok=False)
old='r40_world_d0_bar40';new='r42_latched_d0_bar40'
def rows(name):
    with(R/'results'/name/'trace.jsonl').open(encoding='utf-8')as f:return[json.loads(s)for s in f]
a,b=rows(old),rows(new);assert len(a)==len(b)==1300
seen=False;stop=None
for k,r in enumerate(a):
    if abs(r['request'][0])>1e-9:seen=True
    elif seen:stop=k;break
assert stop is not None
fields=['time','estimate_time','request','shaped','estimated14','estimated_roll','sensor_age_s','sensor_timestamp_s','raw_gyro','raw_accel','encoder4','encoder_rate4','wheel_rate2',
        'raw_requested_tau','actual_tau','ground_truth_before','ground_truth','physics_wheel_mean_force_N2','physics_nonwheel_contact_ticks','wheel_support_N2','nonwheel_ground_contact']
count=0;errors=[]
def compare(x,y,path):
    global count
    if isinstance(x,dict):
        if set(x)!=set(y):errors.append((path,'keys'));return
        for k in x:compare(x[k],y[k],path+'.'+k)
    elif isinstance(x,list):
        if len(x)!=len(y):errors.append((path,'length'));return
        for k,(p,q)in enumerate(zip(x,y)):compare(p,q,path+f'[{k}]')
    else:
        count+=1
        equal=type(x)is type(y)and (struct.pack('!d',x)==struct.pack('!d',y)if isinstance(x,float)else x==y)
        if not equal:errors.append((path,x,y))
for k in range(stop):
    for field in fields:compare(a[k][field],b[k][field],f'row{k}.'+field)
# Requests/geometry/acceptance did not change after the stop intervention either.
assert all(x['request']==y['request']for x,y in zip(a,b))
res=json.loads((R/'results'/new/'result.json').read_bytes())
result=dict(kind='R42_NEW_STOP_INTERVENTION_ACTUAL_PHYSICAL_PREFIX_CHECK',source_SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 old_case=old,new_case=new,first_drive_to_stop_control_index=stop,prefix_control_frames=stop,prefix_physics_steps=20*stop,
 compared_leaf_values=count,bit_or_discrete_mismatches=len(errors),first_mismatches=errors[:10],
 new_physics_steps_during_validation=0,new_case_passed_original_rough_gate=res['rough_case_pass'],
 new_progress_m=res['rough_progress_m'],max_abs_y_m=res['rough_max_y_m'],nonwheel_tick_count=res['physics_nonwheel_contact_ticks'],
 tail_pitch_RMS_rad=res['tail_pitch_RMS'],tail_v_RMSE=res['tail_v_tracking_RMSE'],raw_artifact=res['trace_artifact'],
 caveat='one_nominal_4cm_case_not_fullDR_6cm_or_holdout_qualification')
with(A/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2,allow_nan=False)
print(json.dumps(result,indent=2));assert not errors
with(R/'reports/R42_NOMINAL4CM_FACTS.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
