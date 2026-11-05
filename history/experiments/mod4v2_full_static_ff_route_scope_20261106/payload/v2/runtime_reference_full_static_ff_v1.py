# Derived M3 runtime ONLY; default runtime_v2.py remains unchanged.
"""Sensor-only MOD4v2 T01 engine; no jump, GUI or real motor binding.
Old public controller settings reused, fresh v2 matrices/DARE/trim actually used.
"""
from pathlib import Path
import sys,json,math
import numpy as np
import mujoco
ROOT=Path(__file__).resolve().parent
V1=ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'
sys.path.insert(0,str(V1))
import physics_bridge as bridge
import model_builder_v2 as terrain
from bridge_v2 import V2Plant as BufferedImuPlant,geometry
from dr_v2 import FullDR
from sensor_core_jump_v1 import StateEstimator,quat_mul,quat_from_rpy
from controller_reference_full_static_ff_v1 import GroundController
# The formal runner counts this exact constructor through runtime.bridge.FullDR.
from types import SimpleNamespace
bridge=SimpleNamespace(FullDR=FullDR,load_gain=bridge.load_gain)

class Engine:
 def __init__(self,scene='latest_rm',difficulty=.5,seed=520110,full_dr=False):
  self.gain=bridge.load_gain(ROOT/'nominal_gain_v2.json')
  self.pack=json.loads((V1/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json').read_text(encoding='utf-8'))
  self.scene_name=scene;self.seed=int(seed);self.full_dr=bool(full_dr)
  model,self.meta=terrain.build_model(scene,difficulty,self.seed)
  self.plant=BufferedImuPlant(model,(.03,0.,.04))
  self.dr_meta=self.plant.attach_dr(bridge.FullDR(self.seed,nominal=not self.full_dr))
  spawn=self.meta['zones'][0]['spawn'];self.spawn_yaw=float(self.meta['zones'][0].get('yaw',0.))
  p=self.plant;p.reset(self.gain['symmetric'],float(spawn[0]))
  p.d.qpos[1]=float(spawn[1]);p.d.qpos[2]+=float(spawn[2])if len(spawn)>2 else 0.
  p.d.qpos[3:7]=quat_mul(quat_from_rpy(0.,0.,self.spawn_yaw),p.d.qpos[3:7])
  mujoco.mj_forward(p.m,p.d);p.initial=p.d.qpos.copy()
  geom=geometry()
  self.estimator=StateEstimator(geom,p.imu_offset,accel_correction=1.5,wheel_std=.065,
   accel_reference='wheel_midpoint',innovation_limit=1.,upright_prior=True)
  self.controller=GroundController(self.gain,self.pack['controller'],geometry=geom)
  # No assignment of old pack.K_6x14: constructor re-solves DARE on fresh v2 Ad/Bd.
  self.meta.update(actual_controller_K_6x14=self.controller.K.tolist(),
   controller_config_source=str(V1/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json'),
   old_pack_K_used=False,actual_controller_mode=self.controller.mode,
   initial_qpos37_grading=p.initial.tolist(),initial_support=p.initial_mesh_support,
   explicit_supported_upright_initialization=True,natural_standup_qualification=False)
  self.meta.update(reference_static_ff_design=self.controller.reference_ff_design,reference_ff_is_not_measured_force=True)
  self.estimate=None;self.packet=None;self.last_tau=np.zeros(6);self.controls=0
  self.fault='';self.paused=False;self.phase='BALANCE';self.target=(0.,0.)
 def tick(self,forward=0.,yaw_rate=0.):
  if self.paused:return
  p=self.plant
  try:
   packet=p.sensor_packet();e=self.estimator.update(packet)
   tau=self.controller.command(e,float(forward),float(yaw_rate))
   if not self.controller.valid_command:raise ValueError('Controller invalid')
   self.packet,self.estimate=packet,e;self.last_tau=np.asarray(tau,float).copy()
   self.target=(float(forward),float(yaw_rate));p.apply_torque_request(self.last_tau,packet)
   self.controls+=1
   if not np.isfinite(p.d.qpos).all()or abs(float(e.state14[2]))>1.3 or abs(float(e.roll))>1.:
    self.fault='FALL_PAUSED';self.paused=True;self.phase='FALL_PAUSED'
  except (ValueError,FloatingPointError)as exc:
   self.fault=str(exc);self.paused=True;self.phase='INHIBIT'
   print('V2_CONTROL_FAULT '+self.fault,flush=True)
