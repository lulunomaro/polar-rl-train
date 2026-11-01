from pathlib import Path
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import ast,hashlib,json,time
import numpy as np
import torch
from depth_supermimic249 import validate_transition,policy_observation,imagine32
from d435i_profile249 import calibrated_packet
N=Path(__file__).resolve().parent;R=N/'reports';R.mkdir(exist_ok=True);rng=torch.get_rng_state().clone()
row=dict(producer_kind='SYNTHETIC_INTERFACE_ONLY',plant='own_MOD4_live_USD',run_id='synthetic_not_actual',generation=1,source_admission_SHA='synthetic_source_only',physics_us=2500,physics_callbacks=8,feedback_samples=2,policy_us=20000,control_index=10,control_time=1.,depth_control_time=.98,s=np.zeros((2,127),np.float32),s1=np.zeros((2,127),np.float32),xi=np.zeros((2,31),np.float32),depth=np.zeros((2,9),np.float32),a=np.zeros((2,6),np.float32))
assert validate_transition(row,9,synthetic_interface_test=True)
rejects=0
for changes in[dict(physics_callbacks=4),dict(depth_control_time=1.1),dict(plant='foreign_Fudan_plant'),dict(s1=np.zeros((2,35),np.float32))]:
 try:validate_transition(dict(row,**changes),9,synthetic_interface_test=True)
 except ValueError:rejects+=1
 else:raise AssertionError(changes)
try:validate_transition(row,9)
except ValueError:rejects+=1
else:raise AssertionError('Synthetic data accepted as real producer')
assert policy_observation(np.zeros((2,35)),np.zeros((2,9))).shape==(2,44)
assert policy_observation(np.zeros((2,38)),np.zeros((2,9))).shape==(2,47)
q=calibrated_packet(np.array([[1000,0]],dtype=np.uint16),depth_scale_m=.001,K=np.eye(3),T_heading_optical=np.eye(4),sensor_time_in_control_clock=.9,control_time=1.)
assert np.isclose(q['depth_m'][0,0],1.)and np.isnan(q['depth_m'][0,1])
w=torch.full((6,),.1,requires_grad=True);s=torch.zeros(2,1);depth=torch.zeros(2,9)
out=imagine32(s,depth,actor=lambda obs:w[None,:].expand(2,6),world_step=lambda x,a,d:x+.02*a[:,:1],context=lambda x,d:d,policy_obs=lambda x,d:torch.cat((x,d),-1),literal_reward_step=lambda x,a,y,m:(-((y[:,0]-.5)**2)*.02,m),terminal_value=lambda x,d:torch.zeros(2),reward_memory=None)
out['objective'].sum().backward();assert torch.isfinite(w.grad).all()and w.grad.norm()>0
assert torch.equal(rng,torch.get_rng_state())and not torch.cuda.is_initialized()
files=list(N.glob('*.py'))+[N/'HANDOFF249_CURRENT_MAIN_DEPTH_SUPERMIMIC.md']
for p in N.glob('*.py'):ast.parse(p.read_text('utf8'))
report=R/'ROOT249_NEW_SYNTHETIC_INTERFACE_H32_CPU_RETURNED.json'
with report.open('x',encoding='utf8')as f:json.dump(dict(passed=True,epoch=time.time(),new_interface_rejects=rejects,H32_synthetic_callback_gradient_norm=float(w.grad.norm()),optimizer_steps=0,model_raw_SDK_remote_or_GPU=0,old190_fixture_replay=0,RNG_unchanged=True,actual_Fudan_or_native_actor_gradient=False,actual_camera_or_WM_or_Pi_training=False,scope='Synthetic protocol and differentiable callback kernel only; no completeSuperMimic/runtime claim.'),f,indent=2)
index=N/'INDEX249_DEPTH_SUPERMIMIC_SOURCE_FROZEN.json'
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='FROZEN_SOURCE_COMPONENTS_NOT_RUNTIME_READY',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in files+[report]],actual_learning=False),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=hashlib.sha256(index.read_bytes()).hexdigest(),H32_gradient=float(w.grad.norm()),real_model_or_camera_or_learning=0)))
