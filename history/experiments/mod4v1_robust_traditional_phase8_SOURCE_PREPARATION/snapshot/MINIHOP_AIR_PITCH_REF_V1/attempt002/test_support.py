"""New declared synthetic fixtures, not old trace/QA replay or plant data."""
from pathlib import Path
from types import SimpleNamespace
import copy,json,math
import numpy as np
from sensor_core import LinkageGeometry
from sensor_core_jump_v1 import quat_from_rpy
D=Path(__file__).resolve().parent;R=D.parents[1];O=R.parent/'traditional_control_20261101'
ARRAYS={'q','tau','K','A','B','Ad','Bd','P','Q','R'}
def arrays(g):return{k:np.array(v,float)if k in ARRAYS else copy.deepcopy(v)for k,v in g.items()}
def gains():
    b=json.loads((R/'JUMP270_V1/GAIN_BANK.json').read_bytes())
    return(arrays(b['gains']['crouch']),arrays(json.loads((R/'TALL_ROUGH_BANK_V1/gain_delta20.json').read_bytes())['gain']),arrays(json.loads((R/'TALL_ROUGH_BANK_V1/gain_delta0.json').read_bytes())['gain']))
def geometry():
    x=json.loads((O/'reports/model_manifest.json').read_bytes())['neutral_skeleton_xz_m']
    return LinkageGeometry(x,radius=.0625)
def config():return json.loads((D/'METHOD.json').read_bytes())['synthetic_config'].copy()
def estimate_packet(t,hop):
    x=np.r_[hop.g['q'],np.zeros(7)];x[0]=.7*t;x[7]=.7
    since=t-hop.trigger;flight=bool(hop.enabled and hop.launched and hop.push<=since<hop.push+hop.air)
    if flight:
        j=int(round((since-hop.push)/.01));x[2]=.6 if j<6 else-.6;x[9]=0.
    else:x[2]=.03*math.sin(.8*t);x[9]=.024*math.cos(.8*t)
    age=min(.01,t);q=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]])
    p=SimpleNamespace(joint_pos4=q.copy(),joint_vel4=np.zeros(4),time_s=t-age,arrival_s=t,
                      gyro_body=np.array([0.,x[9],0.]),accel_proper_body=np.array([0.,0.,9.81]),wheel_vel2=np.full(2,.7/.0625))
    e=SimpleNamespace(state14=x,roll=0.,omega_body=np.array([0.,x[9],0.]),sensor_age_s=age,
                      proper_acc_origin=np.array([0.,0.,9.81]),velocity_variance=.01,measured_wheel_forward2=np.array([.7,.7]),
                      estimated_time_s=t,slip_innovation=0.,contact_confidence=0.)
    attitude=quat_from_rpy(0.,float(x[2]-age*x[9]),0.)
    return e,p,attitude

def observer():return SimpleNamespace(wheel_measurement_enabled=True,ground_kinematic_constraint_enabled=True,accel_correction=1.5)
