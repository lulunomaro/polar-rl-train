"""One pass of NEW M1 control telemetry only; no old raw, physics or regrading."""
from pathlib import Path
import json,math
D=Path(__file__).resolve().parent;R=D.parent;O=D/'M1_REDUCTION001.json'
assert not O.exists(),'M1 telemetry already consumed: read compact result instead'
C=D/'runs/v2_t01_roll_force_nominal_slow_520121_001'
B=R/'T01_V2/runs/v2_t01_nominal_slow_520111_001'
a=json.loads((B/'result.json').read_text(encoding='utf-8'));b=json.loads((C/'result.json').read_text(encoding='utf-8'))
meta=json.loads((C/'meta.json').read_text(encoding='utf-8'))
n=scaled=packet_count=0;f=[];mx=[];extra=[0.]*6;minscale=1.
with (C/'trace.jsonl').open(encoding='utf-8')as handle:
 for line in handle:
  r=json.loads(line);d=r['roll_force_diagnostic'];n+=1
  f.append(float(d['requested_ground_force_couple_N'])*float(d['applied_scale']))
  mx.append(float(d['filtered_roll_moment_Nm']));s=float(d['applied_scale']);minscale=min(minscale,s);scaled+=int(s<1.-1e-12)
  extra=[max(old,abs(float(v)))for old,v in zip(extra,d['extra_joint_tau6_Nm'])]
  packet_count+=int(isinstance(r.get('sensor_packet_100Hz'),dict)and r.get('estimated_omega_body')is not None)
assert n==1200
out=dict(status='M1_NEW_NOMINAL_CASE_COLLECTED_CONTACT_GATES_FAILED_NOT_ADOPTED',
 baseline_result=str(B/'result.json'),candidate_result=str(C/'result.json'),old_raw_read=0,new_control_trace_passes=1,
 physics_in_this_reduction=0,new_model_builds_in_this_reduction=0,
 actual_case=dict(controls=b['controls'],physics_steps=b['physics_steps'],wall_s=b['total_case_wall_s'],complete=b['complete']),
 design=meta.get('roll_force_design'),telemetry=dict(rows=n,full_packet_and_gyro_rows=packet_count,
  requested_force_couple_abs_peak_N=max(map(abs,f)),requested_force_couple_rms_N=math.sqrt(math.fsum(v*v for v in f)/n),
  filtered_roll_moment_abs_peak_Nm=max(map(abs,mx)),max_abs_extra_joint_tau6_Nm=extra,headroom_scaled_calls=scaled,min_headroom_scale=minscale,
  forces_are_requests_not_measured_support=True,physical_2kHz_motor_saturation_duty='still_not_logged'),
 comparison={key:dict(baseline=a['metrics'][key],M1=b['metrics'][key])for key in ['roll_abs_peak_rad','roll_rms_rad','pitch_abs_peak_rad','slow_vx_rmse_m_s','slow_progress_m','slow_max_lateral_m','final_stop_body_vx_rms_m_s']},
 main_support_duty=dict(baseline=a['contact_metrics']['mainwheel_support_duty2'],M1=b['contact_metrics']['mainwheel_support_duty2']),
 whole_unsupported_ticks=dict(baseline=a['contact_metrics']['whole_body_unsupported_ticks'],M1=b['contact_metrics']['whole_body_unsupported_ticks']),
 guide_hard_M1=[b['contact_metrics']['guide_support_duty'],b['contact_metrics']['hard_contact_ticks']],
 false_checks=[k for k,v in b['checks'].items()if v is False],candidate_case_screen_pass=b['case_screen_pass'],
 decision='Not adopted; keep original runtime/controls/gates, no second mechanism or DR launched in this stage',
 confidence='One nominal case per controller, not reliability/causality or real-hardware qualification')
with O.open('x',encoding='utf-8')as handle:json.dump(out,handle,indent=2,allow_nan=False)
print(json.dumps(out,indent=2),flush=True)
