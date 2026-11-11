"""Exact 35D encoder and50Hz policy/100Hz PD; ONNX Runtime+NumPy only."""
from pathlib import Path
import json,numpy as np
B=Path(__file__).resolve().parents[1]
CONTRACT=json.loads((B/'config/deployment_contract.json').read_text(encoding='utf-8'))
Q0=np.asarray(CONTRACT['observation_default_joint_positions_rad'],dtype=np.float32)
def array(value,n):
 a=np.asarray(value,dtype=np.float32).reshape(-1)
 if a.size!=n or not np.isfinite(a).all():raise ValueError(f'Expected {n} finite float values')
 return a

def build_observation(command,q,qd,gyro_b,gravity_b,previous_action):
 command=array(command,4);q=array(q,6);qd=array(qd,6);relative=q-Q0;relative[4:]=0.
 values=dict(command=command[:3],height_cmd=command[3:4],root_ang_vel_b=array(gyro_b,3),projected_gravity_b=array(gravity_b,3),joint_pos=relative,joint_vel_leg=qd[:4],joint_vel_wheel=qd[4:],actions=array(previous_action,6),ctrl_mode_obs=np.asarray(CONTRACT['mode_vector'],dtype=np.float32));parts=[]
 for block in CONTRACT['input']['blocks']:
  v=values[block['name']];limit=block['clip_raw']
  if limit is not None:
   low,high=limit if isinstance(limit,list) else (-abs(limit),abs(limit));v=np.clip(v,low,high)
  parts.append(v*np.asarray(block['scale'],dtype=np.float32))
 return np.concatenate(parts).astype(np.float32)

def decode_targets(action,current_q):
 a=np.clip(array(action,6),-6.,6.);q=array(current_q,6);target=Q0.copy();target[:4]+=np.float32(.5)*a[:4];twopi=np.float32(2*np.pi)
 for side,front,rear in [(0,0,1),(1,2,3)]:
  delta=target[front]-target[rear];delta+=np.rint((q[front]-q[rear]-delta)/twopi)*twopi;delta=np.clip(delta,*CONTRACT['controller']['front_rear_delta_bounds_rad'][side]);hip=target[rear]+np.rint((q[rear]-target[rear])/twopi)*twopi;target[rear]=hip;target[front]=hip+delta
 target[4:]=np.float32(10.)*a[4:];return target.astype(np.float32)

def pd_torque(target,q,qd):
 t=array(target,6);q=array(q,6);v=array(qd,6);raw=np.concatenate([60.*(t[:4]-q[:4])-2.*v[:4],.6*(t[4:]-v[4:])]).astype(np.float32)
 e=CONTRACT['motor_envelope'];stall=np.asarray(e['stall_Nm'],np.float32);no=np.asarray(e['no_load_rad_s'],np.float32);peak=np.asarray(e['plateau_Nm'],np.float32);hi=np.minimum(peak,np.maximum(0,stall*(1-v/no)));lo=np.maximum(-peak,np.minimum(0,-stall*(1+v/no)));return np.clip(raw,lo,hi).astype(np.float32)

def limit_torque(held_torque,current_qd):
 tau=array(held_torque,6);v=array(current_qd,6);e=CONTRACT['motor_envelope'];stall=np.asarray(e['stall_Nm'],np.float32);no=np.asarray(e['no_load_rad_s'],np.float32);peak=np.asarray(e['plateau_Nm'],np.float32)
 return np.clip(tau,np.maximum(-peak,np.minimum(0,-stall*(1+v/no))),np.minimum(peak,np.maximum(0,stall*(1-v/no)))).astype(np.float32)

class Controller:
 def __init__(self,policy=None):
  import onnxruntime as ort
  self.session=ort.InferenceSession(str(policy or B/'model/policy.onnx'),providers=['CPUExecutionProvider']);self.reset()
 def reset(self):self.previous_action=np.zeros(6,np.float32);self.target=None
 def policy_tick(self,state):
  cmd=array(state['command'],4)
  if abs(cmd[0])>2.2 or cmd[1]!=0 or abs(cmd[2])>14.137168 or not .2<=cmd[3]<=.4:raise ValueError('Command outside packaged task scope')
  obs=build_observation(cmd,state['joint_position_rad'],state['joint_velocity_rad_s'],state['gyro_b_rad_s'],state['gravity_b'],self.previous_action);action=self.session.run(['action'],{'observation':obs[None]})[0][0];target=decode_targets(action,state['joint_position_rad']);self.previous_action=action.copy();self.target=target.copy();return dict(observation=obs.tolist(),action=action.tolist(),target=target.tolist(),torque_Nm=pd_torque(target,state['joint_position_rad'],state['joint_velocity_rad_s']).tolist())
 def PD_tick(self,q,qd):
  if self.target is None:raise RuntimeError('Call a valid policy_tick before enabling PD')
  return pd_torque(self.target,q,qd)
