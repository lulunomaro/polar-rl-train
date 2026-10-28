from pathlib import Path
import ast,hashlib,importlib.util,json,math,os,sys,time,traceback
S=Path(__file__).resolve().parent;T=S.parent;B=T/'MOD4_H1_FUDAN270_NATIVE_RESOURCE_V103_20261028/payloads_v4/seed27';R=S/'reports'
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized();sys.path[:0]=[str(S/'code'),str(B/'source')]
 from fudan105_frozen_diag_driver_v1 import frozen_first_action_sensitivity,nested_finite,literal
 assert nested_finite(dict(total=torch.ones(1),parts=dict(a=torch.zeros(1)),metadata=('absent_prior_prior_action',True,None,1.)))
 assert not nested_finite(dict(parts=dict(bad=torch.tensor([float('nan')])))) and not nested_finite(dict(value=float('inf')))
 class Pi(torch.nn.Module):
  def __init__(self):super().__init__();self.register_buffer('unchanged',torch.tensor(1.))
  def forward(self,h,g):return h[:,-1,:6]*0
 class WM:
  def step(self,state,action,context):return (state[0]+.01*action[...,:3],*state[1:])
 class Critic(torch.nn.Module):
  def forward(self,x):return x[...,0]
 class MDP:
  def normalize_context(self,x):return x
  def critic_features(self,s,f,c):return torch.cat((s[0],torch.zeros(s[0].shape[0],162)),-1)
  def goal(self,f,n):return torch.zeros(f.shape[0],1460)
  def objective_terms(self,s,f,a,p):return dict(total=s[0][...,0],contact_step_modes=dict(jump=s[0][...,0]*0))
  def soft_termination(self,s,f):return s[0][...,0]*0
  def wheel_geometry(self,s):return dict(low=s[0].unsqueeze(-2).expand(-1,2,-1))
  def obs(self,s,a,c,f):return torch.cat((s[0],a,torch.zeros(s[0].shape[0],77)),-1)
  def add_noise(self,o):return o
 class Bridge:mdp=MDP()
 pi=Pi().eval();critic=Critic().eval();before={k:v.clone() for k,v in pi.state_dict().items()};rng=torch.get_rng_state().clone()
 with torch.inference_mode():
  state=torch.zeros(1,127);state[:,3]=1;row=(state,torch.zeros(1,31),torch.zeros(1,6),state.clone(),torch.zeros(1,dtype=torch.long),torch.zeros(1,10,86),torch.zeros(1,6))
 rows=frozen_first_action_sensitivity([row],Bridge(),pi,WM(),critic,dict(gamma=.99,no_critic=False));assert len(rows)==1 and len(rows[0]['predicted32'])==32 and rows[0]['all_values_finite']
 gr=torch.tensor(rows[0]['first_action_reward_gradient6']);gt=torch.tensor(rows[0]['first_action_critic_tail_gradient6']);expected_r=torch.zeros(1,6);expected_r[:,0]=.01*sum(.99**i for i in range(32));expected_t=torch.zeros(1,6);expected_t[:,0]=.01*.99**32
 assert torch.allclose(gr,expected_r,atol=2e-6,rtol=0) and torch.allclose(gt,expected_t,atol=2e-6,rtol=0)
 assert literal(pi.state_dict(),before) and torch.equal(torch.get_rng_state(),rng) and not torch.cuda.is_initialized()
 for p in (S/'code').glob('*.py'):ast.parse(p.read_bytes())
 entry=S/'run_NEW105_qualified104_fixed_Fudan270_motion_WM_case_UNUSED_once.py';tree=ast.parse(entry.read_bytes())
 for n in tree.body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('PRE','RUN') for t in n.targets):ast.parse(ast.literal_eval(n.value))
 value=dict(epoch=time.time(),passed=True,purpose='New105 SOURCE synthetic equations and nested reader only',analytic32_first_action_reward_gradient=gr.tolist(),analytic32_first_action_critic_tail_gradient=gt.tolist(),closedform_expected_reward=expected_r.tolist(),closedform_expected_tail=expected_t.tolist(),nested_finite_accepts_declared_metadata_rejects_nonfinite=True,inference_origin_tensors_cloned_for_gradient=True,fixture_parameters_norm_RNG_unchanged=True,AST_and_embedded_remote_AST=True,actual_saved104_model_loads=0,actual_saved_WM_Pi_Critic_forward=False,SDK_scene_CUDA_or_SSH=False,not_learning_or_physical_accuracy_or_gradient_direction_proof=True)
 with (R/'NEW105_SOURCE_SYNTHETIC_GRADIENT_NESTED_FINITE_CPU_V2_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 print(json.dumps(value))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_model_or_SSH=True),f,indent=2)
  raise
