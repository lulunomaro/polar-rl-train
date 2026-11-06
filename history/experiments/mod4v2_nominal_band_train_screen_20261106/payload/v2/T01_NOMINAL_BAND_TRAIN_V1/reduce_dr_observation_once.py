"""One pass on TWO new DR traces, diagnostic only; no old/raw contact/motor, replay or SDK."""
from pathlib import Path
import json,math
D=Path(__file__).resolve().parent
CASES=['v2_t01_band_stand_dr_520182_001','v2_t01_band_slow_dr_520183_001']
BOUNDS=[('2_3',2.,3.),('3_7',3.,7.),('7_8',7.,8.),('8_9',8.,9.),('9_12',9.,12.)]
def stats(v):
 return dict(n=len(v),mean=None if not v else math.fsum(v)/len(v),rms=None if not v else math.sqrt(math.fsum(x*x for x in v)/len(v)),
  minimum=None if not v else min(v),maximum=None if not v else max(v))
def main():
 out=D/'DR_OBSERVATION_REDUCTION001'
 if out.exists():raise RuntimeError('New DR trace once budget already consumed')
 out.mkdir(exist_ok=False)
 (out/'PREEXEC.json').write_text(json.dumps(dict(cases=CASES,max_control_rows_per_case=1200,passes_per_trace=1,
  contact_and_motor_payload_reads=0,old_raw_reads=0,controller_replay=0,model_compile=0,forward=0,physics=0,
  source_contract='sensor_core_jump_v1._predict_view propagates first7 state elements to arrival,holds velocity and roll;report command-epoch residual and held-roll sensor-epoch separately',
  no_calibrated_bias_or_unique_cause_claim=True,original_controller_and_gates_unchanged=True),indent=2),encoding='utf-8')
 results=[]
 for name in CASES:
  path=D/'runs'/name/'trace.jsonl';truth={};rows=0;matches=0;rollmatches=0;maxstamperror=0.
  groups={key:dict(true_vx_at_command=[],used_estimated_vx=[],used_vx_minus_command_true=[],used_pitch_minus_command_true=[],
    held_roll_minus_sensor_true=[],requested_wheel_common_Nm=[],contact_low_points=0,contact_windows_missing=0,source_age_s=[])for key,_,_ in BOUNDS}
  examples=[]
  with path.open(encoding='utf-8')as f:
   for line in f:
    r=json.loads(line);rows+=1
    if rows>1200:raise RuntimeError('Unexpected trace length')
    now=float(r['command_time_s']);stamp=r.get('sensor_time_s');x=r.get('estimated14');roll=r.get('estimated_roll')
    at=truth.get(round(now*1e6));sample=None if stamp is None else truth.get(round(float(stamp)*1e6))
    if at is not None:matches+=1;maxstamperror=max(maxstamperror,abs(at['time']-now))
    if sample is not None:rollmatches+=1
    for key,lo,hi in BOUNDS:
     if not lo<=now<hi:continue
     g=groups[key];cw=r.get('contact_window')
     if cw is None:g['contact_windows_missing']+=1
     elif cw.get('whole_body_unsupported_ticks')is None:g['contact_windows_missing']+=1
     else:g['contact_low_points']+=int(cw['whole_body_unsupported_ticks'])
     if stamp is not None:g['source_age_s'].append(now-float(stamp))
     tau=r.get('requested_tau6_Nm')
     if tau is not None:g['requested_wheel_common_Nm'].append(.5*(tau[2]+tau[5]))
     if at is not None and x is not None:
      v=float(at['g']['body_velocity'][0]);g['true_vx_at_command'].append(v);g['used_estimated_vx'].append(float(x[7]))
      g['used_vx_minus_command_true'].append(float(x[7])-v)
      g['used_pitch_minus_command_true'].append(math.atan2(math.sin(float(x[2])-at['g']['pitch_true']),math.cos(float(x[2])-at['g']['pitch_true'])))
     if sample is not None and roll is not None:
      g['held_roll_minus_sensor_true'].append(math.atan2(math.sin(float(roll)-sample['g']['roll_true']),math.cos(float(roll)-sample['g']['roll_true'])))
    if r['control_index']in(800,900,1000,1100,1199):
     examples.append(dict(k=r['control_index'],command_time_s=now,sensor_time_s=stamp,used_vx=None if x is None else x[7],
      truth_at_command=None if at is None else dict(vx=at['g']['body_velocity'][0],pitch=at['g']['pitch_true']),
      post_tick_vx=r['post_truth']['body_velocity'][0],requested_tau6=r['requested_tau6_Nm']))
    truth[round(float(r['time_s'])*1e6)]=dict(time=float(r['time_s']),g=r['post_truth'])
  if rows!=1200:raise RuntimeError('Partial trace requires explicit partial analysis')
  results.append(dict(case=name,rows=rows,arrival_command_truth_matches=matches,held_roll_sensor_truth_matches=rollmatches,
   max_command_truth_epoch_difference_s=maxstamperror,
   regions={k:{field:stats(value)if isinstance(value,list)else value for field,value in g.items()}for k,g in groups.items()},examples=examples))
 result=dict(cases=results,control_rows_read=2400,passes_per_trace=1,contact_motor_payload_reads=0,old_raw_reads=0,
  models=0,forward=0,physics=0,controller_replay=0,raw_hash_reread=0,truth_used_only_diagnostic=True,
  limits='Pipeline residuals on sampled/held/delayed estimates,not a hardware calibration or proof that delay/noise/model variation uniquely caused failure;no controller correction or force authority created.')
 (out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
 for r in results:print(json.dumps(dict(case=r['case'],matches=r['arrival_command_truth_matches'],final=r['regions']['9_12'],examples=r['examples']),indent=2))
 print('NEW_DR_ONCE_DONE rows=2400;models/physics/replay/oldraw/contactmotorpayload=0')
if __name__=='__main__':main()
