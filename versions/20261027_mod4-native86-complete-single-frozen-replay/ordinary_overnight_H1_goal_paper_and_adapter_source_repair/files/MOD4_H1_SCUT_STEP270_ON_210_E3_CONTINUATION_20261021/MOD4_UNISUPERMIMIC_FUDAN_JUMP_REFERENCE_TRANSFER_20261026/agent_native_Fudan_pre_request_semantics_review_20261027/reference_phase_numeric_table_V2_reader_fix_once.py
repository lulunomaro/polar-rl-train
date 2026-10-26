"""Selected existing-reference rows only. No IK/static261 rerun or actor/model IO."""
from pathlib import Path
import importlib.util,hashlib,json,sys,time,csv
import numpy as np
D=Path(__file__).resolve().parent;T=D.parent.parent;J=D.parent
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
P=B/'source/supermimic_reference_adapter_v1.py'
spec=importlib.util.spec_from_file_location('selected_pre_request_reference_semantics',P);a=importlib.util.module_from_spec(spec);sys.modules[spec.name]=a;spec.loader.exec_module(a)
R=B/'reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json'
data=json.loads(R.read_bytes());ref=a.NativeReference.from_dict(data)
frames=np.array([0,25,49,50,51,75,95,99,100,110,120,130,135,136,140,145,160,179,180,200],dtype=float)
query=frames*.01+ref.metadata['native_frame_zero_reference_time_s'];raw=ref.at_time(query)
goal=ref.goal_frames_numpy(frames,1,.01);mask=ref.conditioning_mask73
names=list(ref.joint_names);ids=[names.index(n) for n in a.ACTION_ORDER[:4]]
phase=ref.metadata['partial_phase_contract'];rows=[]
for f,t,state,g in zip(frames,query,raw,goal):
 clipped=float(np.clip(t,ref.times_s[0],ref.times_s[-1]));idx=int(round(clipped/.01));idx=max(0,min(idx,len(ref.times_s)-1))
 if 0<idx<len(ref.times_s)-1:
  derivative=(ref.states[idx+1]-ref.states[idx-1])/.02
 else:derivative=(ref.states[min(idx+1,len(ref.times_s)-1)]-ref.states[max(idx-1,0)])/(.01 if idx in (0,len(ref.times_s)-1) else .02)
 rows.append(dict(age=int(f),own_time_s=float(f*.01),unclamped_reference_time_s=float(t),reference_time_s=clipped,source_time_s=clipped+1.,
  request=bool(100<=f<180),ascent_active=bool(t<=phase['demo_height_vz_active_through_reference_time_s']),
  raw_root_z_m=float(state[2]),raw_root_vz_m_s=float(state[9]),goal_z=float(g[2]),goal_vz=float(g[9]),
  raw_root_xyz=state[:3].tolist(),raw_quat_wxyz=state[3:7].tolist(),raw_world_omega=state[10:13].tolist(),
  four_motor_q={names[i]:float(state[13+i]) for i in ids},four_motor_qd={names[i]:float(state[43+i]) for i in ids},
  q_abs_masked_max_rad=float(np.max(abs(state[13:43][mask[13:43]]))),
  qd_abs_masked_max_rad_s=float(np.max(abs(state[43:73][mask[43:73]]))),
  interior_derivative_z_error=float(abs(derivative[2]-state[9])),
  interior_derivative_q_error_max=float(np.max(abs(derivative[13:43]-state[43:73]))),
  held_endpoint=bool(t<ref.times_s[0] or t>ref.times_s[-1])))
raw0=raw[0];hold_qdot_max=float(np.max(abs(raw0[43:73][mask[43:73]])))
scale=np.asarray(ref.metadata['joint_position_range_scale30'])
standing_q_cost=2.*np.sum(((raw0[13:43]/scale)**2)*mask[13:43])/np.sum(mask[13:43])
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
value=dict(schema='mod4.Fudan.pre_request.selected_reference_semantics.v1',epoch=time.time(),source_only=True,
 reference=dict(path=str(R),SHA=H(R),metadata=ref.metadata),adapter=dict(path=str(P),SHA=H(P)),
 rows=rows,motor_names=[names[i] for i in ids],clock_scale_dt_source_to_native=1.,
 selected_interior_derivative_z_max_error=max(row['interior_derivative_z_error'] for row in rows if 50<=row['age']<=200),
 selected_interior_derivative_q_max_error=max(row['interior_derivative_q_error_max'] for row in rows if 50<=row['age']<=200),
 held_endpoint_max_masked_qd_rad_s=hold_qdot_max,held_endpoint_vz_m_s=float(raw0[9]),
 held_endpoint_zero_q_normalized_joint_cost=float(standing_q_cost),
 no_PT_raw_NPZ_actor_physics_GPU_SSH_or_training=True,no_old_static261_fixture_rerun=True)
with (D/'reports/SELECTED_NATIVE_REFERENCE_PHASE_NUMBERS_V2_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2,allow_nan=False)
with (D/'reports/SELECTED_NATIVE_REFERENCE_PHASE_NUMBERS_V2.csv').open('x',newline='',encoding='utf8') as stream:
 keys=['age','reference_time_s','source_time_s','request','ascent_active','raw_root_z_m','raw_root_vz_m_s','goal_z','goal_vz','q_abs_masked_max_rad','qd_abs_masked_max_rad_s','held_endpoint']
 writer=csv.DictWriter(stream,fieldnames=keys);writer.writeheader();writer.writerows({k:r[k] for k in keys} for r in rows)
print(json.dumps(dict(phase=phase,metadata_subset={k:ref.metadata.get(k) for k in ['limb_excursion_attenuation','native_frame_zero_reference_time_s','clock_alignment','own_geometry']},
 rows=[{k:r[k] for k in ['age','raw_root_z_m','raw_root_vz_m_s','goal_z','goal_vz','q_abs_masked_max_rad','qd_abs_masked_max_rad_s','four_motor_q','four_motor_qd']} for r in rows],
 derivative_z_max=value['selected_interior_derivative_z_max_error'],derivative_q_max=value['selected_interior_derivative_q_max_error'],hold_qdot_max=hold_qdot_max,hold_vz=float(raw0[9])),ensure_ascii=False))
