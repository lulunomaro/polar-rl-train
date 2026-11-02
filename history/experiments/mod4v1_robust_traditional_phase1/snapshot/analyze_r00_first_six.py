"""OneCPUread of6ownnewtraces; alignestimatedt withpreviouspost-steptruth.
No rerun/simulation; preserve original result metrics and appendtimingerratum.
"""
from pathlib import Path
import json,hashlib,math
import numpy as np
R=Path(__file__).resolve().parent;out=R/'reports/r00_first_six_analysis.json';assert not out.exists();out.parent.mkdir(exist_ok=True);rows=[]
for name in('r00_stand_nominal_truth_diagnostic','r00_stand_nominal_sensors','r00_stand_fullDR_101','r00_stand_fullDR_102','r00_forward_nominal_sensors','r00_spin_nominal_sensors'):
 d=R/'results'/name;res=json.loads((d/'result.json').read_bytes());raw=(d/'trace.jsonl').read_bytes();data=[json.loads(v)for v in raw.splitlines()];tail=[v for v in data if v['time']>=res['config']['duration_s']-2.];support=float(np.mean([min(v['wheel_support_N2'])>1 for v in tail]));nonwheel=int(sum(v['nonwheel_ground_contact']>0 for v in tail));aligned=[]
 for i in range(1,len(data)):
  cur=data[i];prev=data[i-1]
  if cur['time']<res['config']['duration_s']-2:continue
  gt=prev['ground_truth'];x=cur['estimated14'];aligned.append([x[7]-gt['body_velocity'][0],x[2]-gt['pitch_true']])
 a=np.array(aligned);snap=[]
 for t in(0.01,1.,2.,3.,4.,5.,6.,7.,8.):
  if t>data[-1]['time']+.001:continue
  row=min(data,key=lambda v:abs(v['time']-t));snap.append(dict(t=row['time'],actual_v=row['ground_truth']['body_velocity'][0],estimated_v=row['estimated14'][7],actual_pitch=row['ground_truth']['pitch_true'],estimated_pitch=row['estimated14'][2],actual_yawrate=row['ground_truth']['gyro_true'][2],estimated_yawrate=row['estimated14'][8],raw_accel=row['raw_accel'],raw_gyro=row['raw_gyro'],wheel_rate=row['wheel_rate2'],torques=row['actual_tau'],support=row['wheel_support_N2']))
 row=dict(case=name,mode=res['mode'],nominal=res['nominal'],truth_diagnostic=res['truth_used_for_control'],complete=res['complete'],controls=res['controls'],physical_steps=res['physics_callbacks'],D3_requested_delay_us=res['DR']['D3']['requested_delay_us'],D4_delay_us=res['DR']['D4']['action_delay_us6'],tail_both_wheel_support_fraction=support,tail_nonwheel_contact_controls=nonwheel,old_proposed_gate=res['proposed_gate_passed'],strict_screen_pass=bool(res['proposed_gate_passed']and support>=.95 and nonwheel==0 and not res['truth_used_for_control']),aligned_estimator_v_RMSE=float(np.sqrt(np.mean(a[:,0]**2))),aligned_estimator_pitch_RMSE=float(np.sqrt(np.mean(a[:,1]**2))),tail_v=res['tail_velocity_mean_m_s'],tail_yaw=res['tail_yawrate_mean_rad_s'],v_tracking_RMSE=res['tail_v_tracking_RMSE'],w_tracking_RMSE=res['tail_w_tracking_RMSE'],xy_displacement=res['xy_displacement_m'],snapshot=snap,trace_read_count=1,trace_bytes=len(raw),trace_SHA=hashlib.sha256(raw).hexdigest());rows.append(row)
result=dict(kind='R00_FIRSTSIX_PHYSICAL_FACTS_AND_TIME_ALIGNMENT_ERRATUM',rows=rows,errata=['OriginalestimatorRMSEcomparedpre-commandestimate@twithpost-steptruth@t+.01; alignedmetricsusetruthfrompreviousrow. Originalresultsunchanged.','Originalproposedgateomittedexplicitboth-wheel-bearing/nonwheel-tailcondition; strictscreenadds95percentboth-wheel>1Nandzero-nonwheel-tail withoutnewphysics.','Thesearetrain/diagnosticsamples, notfrozenholdout/fullhardwarequalification.'],physics_reruns=0,controller_inputs_changed=False);out.write_text(json.dumps(result,indent=2),encoding='utf-8')
for r in rows:print(json.dumps({k:v for k,v in r.items()if k!='snapshot'},ensure_ascii=False))
for r in rows[-2:]:print('SAMPLES',r['case'],json.dumps(r['snapshot'],ensure_ascii=False))
print('REPORT',out)
