"""Compare ONNX/C/NumPy against frozen PyTorch and real R1 runtime vectors."""
from pathlib import Path
import json,sys,ctypes as ct,hashlib,time,subprocess
import numpy as np,torch,onnxruntime as ort
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'runtime'));from control import build_observation,decode_targets,pd_torque
v=np.load(B/'evidence/RUNTIME_VECTORS.npz');N=len(v['observation']);q0=json.loads((B/'config/deployment_contract.json').read_text())['observation_default_joint_positions_rad'];so=ort.InferenceSession(str(B/'model/policy.onnx'),providers=['CPUExecutionProvider']);dll=ct.CDLL(str(B/'bin/windows-x64/mod4_runtime.dll'));F=ct.c_float;P=ct.POINTER(F)
class State(ct.Structure):_fields_=[('q',F*6),('qd',F*6),('gyro',F*3),('gravity',F*3)]
class Command(ct.Structure):_fields_=[('command',F*4)]
class Memory(ct.Structure):_fields_=[('previous_action',F*6),('target',F*6),('target_valid',ct.c_int)]
dll.mod4_build_observation.argtypes=[ct.POINTER(State),ct.POINTER(Command),ct.POINTER(Memory),P];dll.mod4_forward.argtypes=[P,P];dll.mod4_decode_targets.argtypes=[P,P,P];dll.mod4_pd_torque.argtypes=[P,ct.POINTER(State),P]
def ptr(a):return a.ctypes.data_as(P)
obs=[];targets=[];torques=[];c_obs=[];c_actions=[];c_targets=[];c_torques=[]
for i in range(N):
 cmd=np.r_[v['command'][i],v['height'][i]].astype(np.float32);q=v['q'][i].astype(np.float32);qd=v['qd'][i].astype(np.float32);prev=v['previous_action'][i]
 obs.append(build_observation(cmd,q,qd,v['gyro'][i],v['gravity'][i],prev));targets.append(decode_targets(v['action'][i],q));torques.append(pd_torque(v['target'][i],q,qd))
 s=State((F*6)(*q),(F*6)(*qd),(F*3)(*v['gyro'][i]),(F*3)(*v['gravity'][i]));c=Command((F*4)(*cmd));m=Memory((F*6)(*prev),(F*6)(),0);o=np.zeros(35,np.float32);a=np.zeros(6,np.float32);t=np.zeros(6,np.float32);tau=np.zeros(6,np.float32)
 assert dll.mod4_build_observation(ct.byref(s),ct.byref(c),ct.byref(m),ptr(o));assert dll.mod4_forward(ptr(o),ptr(a));assert dll.mod4_decode_targets(ptr(v['action'][i].astype(np.float32)),ptr(q),ptr(t));assert dll.mod4_pd_torque(ptr(v['target'][i].astype(np.float32)),ct.byref(s),ptr(tau));c_obs.append(o);c_actions.append(a);c_targets.append(t);c_torques.append(tau)
obs=np.asarray(obs);targets=np.asarray(targets);torques=np.asarray(torques);c_obs=np.asarray(c_obs);c_actions=np.asarray(c_actions);nom=v['nominal'];on=so.run(['action'],{'observation':v['observation'].astype(np.float32)})[0]
metric=dict(runtime_samples=N,nominal_PD_samples=int(nom.sum()),python_observation_max_abs=float(abs(obs-v['observation']).max()),C_observation_max_abs=float(abs(c_obs-v['observation']).max()),ONNX_vs_runtime_action_max_abs=float(abs(on-v['action']).max()),C_vs_runtime_action_max_abs=float(abs(c_actions-v['action']).max()),python_target_max_abs=float(abs(targets-v['target']).max()),C_target_max_abs=float(abs(np.asarray(c_targets)-v['target']).max()),python_nominal_PD_max_abs=float(abs(torques[nom]-v['torque'][nom]).max()),C_nominal_PD_max_abs=float(abs(np.asarray(c_torques)[nom]-v['torque'][nom]).max()))
state=torch.load(B/'model/training_checkpoint.pt',map_location='cpu',weights_only=False)['actor_state_dict'];net=torch.nn.Sequential(torch.nn.Linear(35,256),torch.nn.ELU(),torch.nn.Linear(256,128),torch.nn.ELU(),torch.nn.Linear(128,64),torch.nn.ELU(),torch.nn.Linear(64,6)).eval();net.load_state_dict({k[4:]:x for k,x in state.items() if k.startswith('mlp.')});rng=np.random.default_rng(121112);random=rng.uniform(-4,4,(4096,35)).astype(np.float32)
with torch.inference_mode():expected=net(torch.from_numpy(random)).clamp(-6,6).numpy()
actual=so.run(['action'],{'observation':random})[0];cc=[]
for row in random:
 a=np.empty(6,np.float32);assert dll.mod4_forward(ptr(row),ptr(a));cc.append(a)
metric['synthetic_actor_vectors']=4096;metric['ONNX_vs_Torch_synthetic_max_abs']=float(abs(actual-expected).max());metric['C_vs_Torch_synthetic_max_abs']=float(abs(np.asarray(cc)-expected).max());metric['all_outputs_finite']=bool(np.isfinite(actual).all() and np.isfinite(cc).all());metric['action_clip_observed']=bool((abs(actual)<=6).all());metric['C_nonfinite_rejected']=not bool(dll.mod4_forward(ptr(np.full(35,np.nan,np.float32)),ptr(np.empty(6,np.float32))))
metric['checkpoint_sha256']=hashlib.sha256((B/'model/training_checkpoint.pt').read_bytes()).hexdigest();metric['CPU_platform_only']=True
metric['status']='PASS' if metric['python_observation_max_abs']<2e-5 and metric['C_observation_max_abs']<2e-5 and max(metric['ONNX_vs_runtime_action_max_abs'],metric['C_vs_runtime_action_max_abs'])<2e-4 and max(metric['python_target_max_abs'],metric['C_target_max_abs'])<2e-5 and max(metric['python_nominal_PD_max_abs'],metric['C_nominal_PD_max_abs'])<1e-3 and max(metric['ONNX_vs_Torch_synthetic_max_abs'],metric['C_vs_Torch_synthetic_max_abs'])<2e-4 and metric['all_outputs_finite'] and metric['C_nonfinite_rejected'] else 'FAIL'
(B/'evidence/NUMERICAL_PARITY.json').write_text(json.dumps(metric,indent=2)+'\n',encoding='utf-8')
golden=[]
for i in range(16):golden.append(dict(command=np.r_[v['command'][i],v['height'][i]].tolist(),joint_position_rad=v['q'][i].tolist(),joint_velocity_rad_s=v['qd'][i].tolist(),gyro_b_rad_s=v['gyro'][i].tolist(),gravity_b=v['gravity'][i].tolist(),previous_action=v['previous_action'][i].tolist(),observation=v['observation'][i].tolist(),action=v['action'][i].tolist(),target=v['target'][i].tolist(),torque_Nm=v['torque'][i].tolist() if bool(nom[i]) else None))
(B/'examples/golden_vectors.json').write_text(json.dumps(dict(source='Actual frozen R1 runtime capture',vectors=golden),indent=2)+'\n',encoding='utf-8');print(json.dumps(metric,indent=2));assert metric['status']=='PASS'
