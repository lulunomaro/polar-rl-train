"""New observer-transport test: exact existing methods on prescribed dry data.
The mj_step NAME in the extracted body resolves ONLY to a dry clock stub,
never MuJoCo: no model, integration, dynamics or old case/QA is executed.
"""
from pathlib import Path
from types import SimpleNamespace
import ast,json,math,time
import numpy as np
from actuation_telemetry_v1 import ActuationTelemetryMixin
from dr_v2 import FullDR
R=Path(__file__).resolve().parent;W=R.parent;D=R/'ACTUATION_TELEMETRY_V1/check001'
D.mkdir(parents=True,exist_ok=False)
protocol=dict(id='MOD4V2_ACTUATION_OBSERVER_DRY_TRANSPORT_001',
 purpose='Check new observer does not change existing PD/D4/DC/gain/DC/power values or call order on prescribed dry vectors',
 profiles=['free_nominal','first_clip_gain_down','post_gain_clip','signed_overspeed','delayed_targets','power_scale'],
 substeps_per_profile=20,real_model_builds=0,real_physics_steps=0,old_cases_read=0,
 expected_torque_difference=0.,time_tolerance_s=1e-12,
 oracle='Same extracted original V2 apply method and original clip, once bare and once with NEW mixin; not independent actuator accuracy or robot dynamics',
 hardware_qualification=False)
(D/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')

def method(path,cls,name,env):
 tree=ast.parse(path.read_text(encoding='utf-8'));c=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name==cls)
 fn=next(n for n in c.body if isinstance(n,ast.FunctionDef)and n.name==name)
 exec(compile(ast.Module(body=[fn],type_ignores=[]),str(path),'exec'),env)
 return env[name]

# Prescribed states remain constant: no q integration or robot model exists.
def dry_clock_tick(model,data):
 data.time+=model.dt
 data.dry_clock_calls+=1
fake_mujoco=SimpleNamespace(mj_step=dry_clock_tick)
def dry_import(name, *args, **kwargs):
 if name=='RM_ROBUSTNESS_V1.t01_contact_audit':
  return SimpleNamespace(_bucket=lambda:{})
 return __import__(name,*args,**kwargs)
env=dict(np=np,math=math,BOUNDS=(-1.0863195404360622,.49192233306644084),mujoco=fake_mujoco,__import__=dry_import)
apply_original=method(R/'bridge_v2.py','V2Plant','apply_torque_request',env)
clip_original=method(W/'traditional_control_20261101/control_core.py','Plant','clip',dict(np=np))

class DryBase:
 apply_torque_request=apply_original
 clip=clip_original
 def __init__(self,speed,gain=None,lags=(0,0)):
  q=np.array([.2503281103649727,.0503281103649727,0.,.2503281103649727,.0503281103649727,0.])
  self.dt=.0005;self.tick_phys=0;self.KP=60.;self.KD=2.;self.wKD=.6
  self.qids=np.arange(6);self.vids=np.arange(6)
  self.max_tau=np.array([40.,40.,5.775909774436091]*2)
  self.stall=np.array([53.3333333333333,53.3333333333333,28.18532894736838]*2)
  self.no_load=np.array([16.755160819145562,16.755160819145562,55.3557]*2)
  self.d=SimpleNamespace(qpos=q.copy(),qvel=np.asarray(speed,float).copy(),ctrl=np.zeros(6),time=0.,dry_clock_calls=0)
  self.d.sensor=lambda name:SimpleNamespace(data=np.zeros(3))
  self.m=SimpleNamespace(dt=self.dt);self.rate_sum=np.zeros(6)
  self.imu_omega_sum=np.zeros(3);self.imu_acc_sum=np.zeros(3)
  self.imu_window_count=0;self.total_highrate_IMU_samples=0;self.target_projection_calls=0
  self.max_mechanical_power=0.;self.max_applied_tau=np.zeros(6);self.held=[]
  self.dr=None
  if gain is not None:
   # No constructor/sample/model/RNG; use the real queue reset/process routines.
   self.dr=FullDR.__new__(FullDR);self.dr.KP6=np.array([60.,60.,0.,60.,60.,0.])
   self.dr.KD6=np.array([2.,2.,.6,2.,2.,.6]);self.dr.motor_gain6=np.asarray(gain,float)
   self.dr.action_delay_ticks6=np.array([lags[0],lags[0],lags[1]]*2,dtype=int)
   initial=q.copy();initial[[2,5]]=0.;self.dr.reset(initial)
 def _grade_contact_sample(self):
  self.held.append(self.d.ctrl.copy())
 def packet(self):
  return SimpleNamespace(joint_pos4=self.d.qpos[[0,1,3,4]].copy(),joint_vel4=self.d.qvel[[0,1,3,4]].copy(),wheel_vel2=self.d.qvel[[2,5]].copy())

class Observed(ActuationTelemetryMixin,DryBase):pass
cases=[
 dict(name='free_nominal',tau=[1.,-1.,.1]*2,speed=[0.]*6,gain=None,lags=(0,0),limit=None),
 dict(name='first_clip_gain_down',tau=[100.,-100.,25.]*2,speed=[0.]*6,gain=[.9]*6,lags=(0,0),limit=None),
 dict(name='post_gain_clip',tau=[38.,38.,5.4]*2,speed=[0.]*6,gain=[1.2]*6,lags=(0,0),limit=None),
 dict(name='signed_overspeed',tau=[0.]*6,speed=[20.,20.,70.]*2,gain=[1.]*6,lags=(0,0),limit=None),
 dict(name='delayed_targets',tau=[3.,-3.,.3]*2,speed=[.4,.4,2.]*2,gain=[.8,1.15,.95]*2,lags=(5,10),limit=None),
 dict(name='power_scale',tau=[10.,10.,2.]*2,speed=[1.,1.,3.]*2,gain=[1.]*6,lags=(0,0),limit=5.)]
rows=[];start=time.perf_counter();maxdiff=0.;assertions=0;dry_total=0
for case in cases:
 kw={k:case[k]for k in ['speed','gain','lags']}
 bare=DryBase(**kw);on=Observed(**kw,motor_telemetry=True);off=Observed(**kw,motor_telemetry=False)
 for obj in [bare,on,off]:obj.apply_torque_request(np.array(case['tau']),obj.packet(),dt=.01,mechanical_power_limit=case['limit'])
 dry_total+=sum(obj.d.dry_clock_calls for obj in [bare,on,off])
 assert np.array_equal(np.asarray(bare.held),np.asarray(on.held));assertions+=1
 assert np.array_equal(np.asarray(bare.held),np.asarray(off.held));assertions+=1
 assert bare.tick_phys==on.tick_phys==off.tick_phys==20;assertions+=1
 assert bare.d.dry_clock_calls==on.d.dry_clock_calls==off.d.dry_clock_calls==20;assertions+=1
 assert on.motor_telemetry_summary['complete']and len(on.motor_telemetry_window)==20;assertions+=1
 assert not off.motor_telemetry_summary['enabled']and off.motor_telemetry_window==[];assertions+=1
 for k,rec in enumerate(on.motor_telemetry_window):
  a,b=rec['clip_stages'];assert a['stage']=='first_signed_DC'and b['stage']=='post_gain_signed_DC';assertions+=1
  expected=np.asarray(a['after_tau6'])*(np.asarray(case['gain'])if case['gain']is not None else 1.)
  assert np.array_equal(expected,np.asarray(b['before_tau6']));assertions+=1
  assert np.array_equal(np.asarray(rec['held_ctrl_tau6']),bare.held[k]);assertions+=1
  assert rec['physics_tick_pre']==k and abs(rec['time_s_pre']-k*.0005)<=1e-12;assertions+=1
  for stage in [a,b]:
   changed=np.not_equal(stage['before_tau6'],stage['after_tau6']).tolist()
   assert changed==stage['changed6'];assertions+=1
 maxdiff=max(maxdiff,float(np.max(np.abs(np.asarray(bare.held)-np.asarray(on.held)))))
 rows.append(dict(name=case['name'],summary=on.motor_telemetry_summary,
  positive_power_scaling_observed=any(not np.array_equal(r['clip_stages'][1]['after_tau6'],r['held_ctrl_tau6'])for r in on.motor_telemetry_window)))
by={r['name']:r for r in rows}
assert any(by['first_clip_gain_down']['summary']['first_dc_changed_ticks6']);assertions+=1
assert not any(by['first_clip_gain_down']['summary']['post_gain_dc_changed_ticks6']);assertions+=1
assert any(by['post_gain_clip']['summary']['post_gain_dc_changed_ticks6']);assertions+=1
assert by['power_scale']['positive_power_scaling_observed'];assertions+=1
# Disabled-after-enabled must not publish the prior window as current data.
on.motor_telemetry_enabled=False;on.apply_torque_request(np.array(cases[-1]['tau']),on.packet(),dt=.01)
assert not on.motor_telemetry_summary['enabled']and on.motor_telemetry_window==[];assertions+=1
out=dict(status='NEW_OBSERVER_DRY_TRANSPORT_CHECK_PASSED',passed=True,assertions=assertions,profiles=rows,
 max_held_tau_difference_Nm=maxdiff,prescribed_dry_substeps_per_arm=120,
 total_dry_clock_calls_all_arms=dry_total+20,additional_disabled_toggle_dry_substeps=20,real_model_builds=0,real_physics_steps=0,old_cases_read=0,
 original_clip_and_PD_D4_DC_gain_DC_power_methods_extracted_unchanged=True,
 full_robot_integration_verified=False,physical_saturation_of_old_M1_known=False,
 wall_s_includes_test_process_work=time.perf_counter()-start,
 limitations='Prescribed inconsistent synthetic q/dq for data transport only; not robot trajectories, dynamic validity, actuator calibration, physical delivery or WCET')
(D/'result.json').write_text(json.dumps(out,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps(out,indent=2),flush=True)
