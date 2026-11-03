"""One-pass NEW V2 saved control diagnosis, no physics/raw hashes or reruns."""
from pathlib import Path
import json,math
R=Path(__file__).resolve().parent;O=R/'STARTUP_STAND_V2/saved_diagnosis001';O.mkdir(exist_ok=False)
D=R/'results/startup_front065_coupled_v2_nominal1';result=json.loads((D/'result.json').read_bytes());rows=[]
with (D/'trace.jsonl').open(encoding='utf-8')as f:
    for line in f:rows.append(json.loads(line))
assert len(rows)==result['controls']==601 and result['physics_steps']==12020
sel=[]
for t in(0.,.31,1.,2.,2.31,3.,4.,5.,5.99,6.):
    x=min(rows,key=lambda v:abs(v['command_time_s']-t));p=x['phase'];q=x['encoder_q4'];ref=p.get('reference_q4')
    sel.append(dict(command_s=x['command_time_s'],phase=p['phase'],estimated_pitch=x['estimated14'][2],true_pitch_post=x['grade_after']['pitch_true'],
        rootXYZ_post=x['grade_after']['xyz'],encoder_q4=q,reference_q4=ref,
        maximum_ref_error=None if ref is None else max(abs(a-b)for a,b in zip(q,ref)),
        requested_tau6=x['requested_tau6'],wheel_rate2=x['wheel_rate_mean2'],
        main_Fn_min2=x['main_contact_min_N2'],no_other=x['no_other_contact_in_control']))
out=dict(status='SAVED_NEW_V2_CONTROL_DIAGNOSIS_NOT_NEW_TRIAL',trace_opens=1,control_rows=len(rows),physics_raw_opens=0,raw_hashes=0,new_model_FK_PHY_QA=0,
    original_result_unchanged=True,complete=result['complete'],controller_fault=result['controller_fault_reason'],
    max_root_xy_displacement_m=result['max_root_xy_displacement_m'],body_height_gain_m=result['body_height_gain_m'],
    max_abs_requested_tau6=[max(abs(x['requested_tau6'][i])for x in rows)for i in range(6)],
    max_abs_wheel_rate2=[max(abs(x['wheel_rate_mean2'][i])for x in rows)for i in range(2)],samples=sel,
    interpretation='Encoder/reference and requested torque only. No applied-drive/collision identity inferred. Entire failed case remains failed; no gait or threshold modified.')
with (O/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(out,f,indent=2,allow_nan=False)
print(json.dumps(dict(status=out['status'],controls=len(rows),max_root_xy_displacement_m=out['max_root_xy_displacement_m'],body_height_gain_m=out['body_height_gain_m'],max_abs_requested_tau6=out['max_abs_requested_tau6'],max_abs_wheel_rate2=out['max_abs_wheel_rate2'],samples=[sel[i]for i in(0,5,8,9)]),indent=2,allow_nan=False))
