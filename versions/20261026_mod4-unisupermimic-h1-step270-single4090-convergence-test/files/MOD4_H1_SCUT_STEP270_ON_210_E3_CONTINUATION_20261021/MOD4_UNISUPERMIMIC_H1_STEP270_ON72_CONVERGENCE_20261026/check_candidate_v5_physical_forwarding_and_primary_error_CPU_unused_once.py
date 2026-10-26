"""Exercise actual bridge methods on synthetic tensor holders, not a simulator."""
from pathlib import Path
import ast
import json
import sys
import time
import traceback
import types
import torch

H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'candidate_source_v5'))
from h1_supermimic_bridge_v1 import H1Bridge,BridgeState
from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY,SUPERMIMIC_TRANSITION_KEY
from supermimic_vendor_v2.replay import ReplayBuffer

torch.set_num_threads(2);rng=torch.get_rng_state().clone();n=2
out=H/'reports/CANDIDATE_V5_PHYSICAL_TENSOR_FIXTURE';assert not out.exists();out.mkdir()
root=torch.zeros(n,13);root[:,6]=1
data=types.SimpleNamespace(root_state_w=root,joint_pos=torch.zeros(n,30),joint_vel=torch.zeros(n,30),applied_torque=torch.zeros(n,30))
robot=types.SimpleNamespace(data=data)
scene={'robot':robot}
class Scene(dict):pass
scene=Scene(scene);scene.env_origins=torch.zeros(n,3)
real=types.SimpleNamespace(scene=scene,_integrated_contact=types.SimpleNamespace(history=torch.zeros(n,3,2,3)),h1_phase=types.SimpleNamespace(age_control=torch.zeros(n,dtype=torch.long),public_request=lambda:torch.zeros(n,dtype=torch.bool)))
b=object.__new__(H1Bridge);b.real=real;b.num_envs=n;b.device=torch.device('cpu');b.out=out;b.go={'save_deadline':time.time()+100};b.ep_step=torch.zeros(n,dtype=torch.int32)
b.trace=types.SimpleNamespace(frame=None);b.learner=types.SimpleNamespace(iteration=0);b.last_curve=0
calls=[];actions=torch.tensor([[9.,0,1,2,3,4],[0.,1,2,3,4,5]]);original_actions=actions.clone()
obs={'policy':torch.zeros(n,35),'critic':torch.zeros(n,38)}
def audited_act(value):
    assert torch.is_inference_mode_enabled() and value is obs;calls.append('audit_before_policy')
def fake_step(value):
    assert torch.is_inference_mode_enabled() and value is actions and torch.equal(value,original_actions)
    calls.append('same_original_action_object')
    b.trace.frame=dict(root13=root.clone(),q30=data.joint_pos.clone(),joint_velocity=data.joint_vel.clone(),executed6=value.clamp(-6,6))
    return obs,torch.ones(n),torch.zeros(n,dtype=torch.bool),{}
b.vec=types.SimpleNamespace(get_observations=lambda:obs,step=fake_step)
b.runner=types.SimpleNamespace(alg=types.SimpleNamespace(act=audited_act))
b.init_state();b.before_action();state=b.step(actions)
assert calls==['audit_before_policy','same_original_action_object']
assert torch.equal(actions,original_actions)
transition=state.info[SUPERMIMIC_TRANSITION_KEY]
assert torch.equal(transition['a'],actions.clamp(-6,6)) and transition['s'].shape==(n,73)
replay=ReplayBuffer(4,n,'cpu',num_joints=30,context_dim=49,action_dim=6)
replay.add(transition)
assert not torch.is_inference(replay.data['s']) and not torch.is_inference(replay.data['a'])
linear=torch.nn.Linear(73,1);loss=linear(replay.data['s'][0]).square().mean();loss.backward();assert torch.isfinite(linear.weight.grad).all()

tree=ast.parse((H/'candidate_source_v5/h1_supermimic_bridge_v1.py').read_text('utf8'))
run=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='run');outer=next(x for x in run.body if isinstance(x,ast.Try) and x.finalbody);inner=outer.finalbody[-1]
record=[]
class Primary(Exception):pass
class SaveFailure(Exception):pass
fn=ast.parse('def fixture(failed):\n try:\n  raise Primary("original learning error")\n finally:\n  pass\n').body[0]
fn.body[0].finalbody=[inner]
scope=dict(Primary=Primary,BaseException=BaseException,save=lambda p:(_ for _ in ()).throw(SaveFailure('secondary fullsave error')),path=out/'partial.pt',out=out,time=time,traceback=traceback,put=lambda p,v:record.append((p,v)))
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'actual_bridge_error_handler','exec'),scope)
try:scope['fixture'](True)
except Primary:primary_preserved=True
else:raise AssertionError('Primary error lost')
assert primary_preserved and record[-1][1]['original_primary_learning_error_preserved']
try:scope['fixture'](False)
except SaveFailure:success_save_failure_not_masked=True
else:raise AssertionError('Success-path save failure masked')
assert not torch.cuda.is_initialized()
result=dict(epoch=time.time(),passed=True,synthetic_tensor_only_no_robot_or_policy_rollout=True,actual_candidate_bridge_init_before_action_step_methods_executed=True,original_action_object_and_values_retained=True,original_execution_clip6_recorded=True,physical_audit_sampler_inference_context=True,replay_tensors_normal_for_training_backward=True,actual_finally_handler_preserves_primary_and_secondary_errors=True,success_path_fullsave_error_not_masked=True,CUDA_initialized=False,prospective_context_change_not_an_observed81O_error=True)
with (H/'reports/CANDIDATE_V5_PHYSICAL_FORWARDING_AND_SAVE_FAILURE_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(result))
