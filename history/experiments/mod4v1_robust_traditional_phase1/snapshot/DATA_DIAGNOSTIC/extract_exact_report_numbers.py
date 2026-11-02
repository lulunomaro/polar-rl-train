"""Print exact report evidence for final numerical QA; no simulation imports."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent
p=json.loads((H/'PACKET_QUICK_SUMMARY.json').read_text(encoding='utf-8'));c=json.loads((H/'CONDITIONED_QUICK_SUMMARY.json').read_text(encoding='utf-8'));s=json.loads((H/'STATIC_FRAME_GEOMETRY.json').read_text(encoding='utf-8'))
r={}
for case,v in p.items():
 t=v['tail'];cc=c[case]
 r[case]={'pitch_error':t['aligned_est_pitch_error'],'vx_error':t['aligned_est_vx_error'],'rawaccnorm':t['raw_accel_norm'],'gyrointegrations':t['gyro_only_integrations'],'gyro_interval':t['interval_gyro_minus_root_SO3_average'],'v_std':cc['source_velocity_std'],'radius_delta':cc['radius_change_vx_delta'],'stagger_rms':cc['stagger_norm_RMS_before_after_m'],'yawcentripetalactual':cc['yaw_only_origin_centripetal_at_actual_omega'],'total_correction':cc['total_correction_body_omega_integral']}
r['initial_static_FK']=s['actual_model_FK_geometry_samples'][0]
(H/'EXACT_SOURCE_NUMBERS.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(r,ensure_ascii=False,indent=2))
