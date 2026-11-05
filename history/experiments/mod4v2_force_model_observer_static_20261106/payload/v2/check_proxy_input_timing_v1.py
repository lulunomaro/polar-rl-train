"""NEW input-contract check, not another nominal FK/static/physics QA.
Exercise frozen ContactProxy.step time guards with a deliberately inert model.
No packet converter, alignment/resampling, force estimate or controller is built.
"""
from pathlib import Path
from dataclasses import asdict
import json,sys
from CONTACT_PROXY_V2.contact_proxy import ContactProxy,Config,SensorInput,ALL_VALID,TorqueDomain
R=Path(__file__).resolve().parent;D=R/'PROXY_INPUT_TIME_V1/check001';D.mkdir(parents=True,exist_ok=False)
protocol=dict(id='MOD4V2_PROXY_INPUT_TIME_CONTRACT_001',
 source_example='Existing20-point PRE mean: center approximately endpoint-5.25ms; encoder q endpoint; held torque endpoint-.5ms. Pipeline-time example, not measured timestamp calibration.',
 max_skew_s=Config().max_channel_skew_s,max_age_s=Config().max_age_s,
 actual_old_raw_reads=0,real_model_compiles=0,real_forwards=0,real_physics_steps=0,
 source_contact_proxy_modified=False,force_model_evaluation_permitted=False,
 warning='Passing declared equal timestamps is not evidence that measurements were aligned; encoder qd also needs its own producer coherence with q')
(D/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
class InertBoundaryModel:
 def __init__(self):self.joint_checks=0;self.force_evaluations=0
 def joint_values(self,q):
  # Intentionally NOT the real geometric model: timing tests end before force.
  self.joint_checks+=1;return {}
 def terms(self,*a,**k):
  self.force_evaluations+=1;raise AssertionError('This new boundary test must not evaluate force/FK')

def observer():
 p=ContactProxy.__new__(ContactProxy);p.c=Config();p.model=InertBoundaryModel()
 p.previous=None;p.good_samples=0;p._history_updated_this_call=False;return p

def fixture(qtime,imutime,tautime):
 return SensorInput(timestamp_s=qtime,imu_timestamp_s=imutime,torque_timestamp_s=tautime,
  valid_bits=ALL_VALID,encoder_q4=(.2503281103649727,.0503281103649727)*2,
  encoder_qd4=(0.,)*4,output_motor_tau4=(3.021463108983351,-4.065098484664146,3.001951054893838,-4.0493720973547696),
  proper_root_B_m_s2=(0.,0.,9.81),omega_B_rad_s=(0.,)*3,alpha_B_rad_s2=(0.,)*3,
  torque_domain=TorqueDomain.NOMINAL_DESIGN_OUTPUT_FIXTURE,torque_binding_id='time_gate_synthetic_not_calibrated',
  proper_reference='chassis_origin')

cases=[
 ('missing_IMU_timestamp',1.,None,.9995,'NONFINITE_TIME'),
 ('nominal_mixed_source_epochs',1.,.99475,.9995,'STALE_FUTURE_OR_UNALIGNED_CHANNELS'),
 ('same_public_10ms_feedback_delay',.99,.98475,.9895,'STALE_FUTURE_OR_UNALIGNED_CHANNELS'),
 ('stale_public_sample',.96,.95475,.9595,'STALE_FUTURE_OR_UNALIGNED_CHANNELS'),
 ('future_public_sample',1.01,1.01,1.01,'STALE_FUTURE_OR_UNALIGNED_CHANNELS'),
 ('hypothetical_equal_metadata_NOT_proven_alignment',.99475,.99475,.99475,'DERIVATIVE_WARMUP')]
rows=[];n=0
for name,qtime,imutime,tautime,expected in cases:
 p=observer();r=p.step(fixture(qtime,imutime,tautime),1.)
 assert r.common_reasons==(expected,);n+=1
 assert r.normal_proxy_N2==(None,None)and r.confidence2==(0.,0.);n+=1
 assert p.model.force_evaluations==0;n+=1
 rows.append(dict(name=name,declared_encoder_time_s=qtime,declared_imu_time_s=imutime,declared_torque_time_s=tautime,
  reason=r.common_reasons,normal_proxy_N2=r.normal_proxy_N2,confidence2=r.confidence2,
  inert_joint_validation_calls=p.model.joint_checks,real_FK_calls=0,force_evaluations=0))
out=dict(status='CURRENT_TIME_GATES_RETAINED_MIXED_WINDOW_REJECTED_NO_ALIGNMENT_CLAIM',
 assertions=n,cases=rows,real_model_compiles=0,real_forwards=0,real_physics_steps=0,
 old_raw_reads=0,real_FK_calls=0,force_evaluations=0,
 source_runtime_imports_mujoco='mujoco'in sys.modules,source_runtime_imports_dr_v2='dr_v2'in sys.modules,
 production_resampler_or_packet_adapter_created=False,controller_connected=False,
 default_skew_or_confidence_changed=False,
 decision='Do not copy the single packet endpoint epoch into all proxy channels. A producer alignment/uncertainty contract is still required; no force estimate or contact identity gained.')
(D/'result.json').write_text(json.dumps(out,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps(out,indent=2),flush=True)
