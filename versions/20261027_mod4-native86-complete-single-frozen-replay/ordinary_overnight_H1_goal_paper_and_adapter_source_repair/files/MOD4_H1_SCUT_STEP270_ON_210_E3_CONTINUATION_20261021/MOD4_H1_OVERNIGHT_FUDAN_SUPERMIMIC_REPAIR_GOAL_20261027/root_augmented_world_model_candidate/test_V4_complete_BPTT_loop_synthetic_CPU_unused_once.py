"""One synthetic CPU integration step of the actual candidate loop; no robot policy or checkpoint."""
from pathlib import Path
import json,sys,traceback,types
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
REPORT=ROOT/'reports/V4_SEVEN_STATE_BPTT_WORLD_POLICY_CRITIC_SYNTHETIC_CPU_ACTUAL.json'
assert not REPORT.exists()
sys.path.insert(0,str(HERE/'v4'))
checks=[]
try:
 import torch
 from supermimic_wheel_leg_v3.learner import SuperMimicConfig,SuperMimicLearner
 from supermimic_wheel_leg_v3.geometry import unflatten_state,invariant_features
 from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY
 torch.set_num_threads(2)
 class SyntheticMdp:
  num_joints=30;action_dim=6;auxiliary_dim=54;packed_state_dim=127
  context_dim=4;obs_dim=86;goal_frame_dim=73;max_step_reward=1.
  step_edge_x_m=.35;platform_top_z_m=.27
  def normalize_context(self,c):return c
  def add_noise(self,o):return o
  def obs(self,s,a,c,f):
   assert len(s)==7
   rel=torch.stack((.35-s[0][...,0],.27-s[0][...,2],f.float()*.01,
     f.float()*0,f.float()*0,f.float()*0,f.float()*0),-1)
   return torch.cat((invariant_features(s[:6]),a,rel),-1)
  def goal(self,f,k):
   return torch.cat([torch.zeros((*f.shape,73)) for _ in range(k)],-1)
  def reward(self,s,f,a,p):
   assert len(s)==7
   return 1-(s[0][...,2]-.4).square()-.01*s[4].square().mean(-1)-.001*s[6].square().mean(-1)-.001*(a-p).square().mean(-1)
  def soft_termination(self,s,f):return torch.zeros_like(f,dtype=torch.float32)
  def critic_features(self,s,f,c):
   assert len(s)==7
   return torch.cat((invariant_features(s[:6]),s[6],c,f.float()[...,None]/200),-1)
  def valid_imagination_start(self,f,h):return torch.ones_like(f,dtype=torch.bool)
 n=4
 packed=torch.zeros(n,127);packed[:,2]=.3377423;packed[:,3]=1
 info=dict(s=packed,xi=torch.zeros(n,4),f=torch.zeros(n,dtype=torch.long),
  a_prev=torch.zeros(n,6),ep_step=torch.zeros(n,dtype=torch.int32))
 env=types.SimpleNamespace(device='cpu',num_envs=n,supermimic_mdp=SyntheticMdp(),state=types.SimpleNamespace(info={SUPERMIMIC_STATE_KEY:info}))
 cfg=SuperMimicConfig(iterations=1,buffer_steps=16,utd=.4,horizon=3,goal_frames=2,hist=3,
  wm_window=2,wm_batch=4,pi_batch=4,wm_batches=1,critic_epochs=1,critic_minibatches=1,
  wm_hidden=(16,16),policy_hidden=(16,16),critic_hidden=(16,16),
  test_hidden_dims=(16,16),amp='none',compile=False,log_backend='none')
 learner=SuperMimicLearner(env,cfg,HERE/'synthetic_cpu_integration_only',device='cpu')
 checks.append('actual candidate learner initializes with explicit30 joints / aux54 / static fixture4')
 with torch.no_grad():
  learner.wm.net[-1].weight.normal_(0,.001)
 for i in range(8):
  learner.buffer.add(dict(s=packed,s1=packed.clone(),a=torch.zeros(n,6),a_prev=torch.zeros(n,6),
   xi=info['xi'],r=torch.ones(n),f=torch.full((n,),i,dtype=torch.long),
   ep_step=torch.full((n,),i,dtype=torch.int32),done=torch.zeros(n,dtype=torch.bool)))
 wm_loss,wm_error=learner.wm_update()
 assert torch.isfinite(wm_loss) and torch.isfinite(wm_error).all()
 checks.append('actual8-compatible-window world fitting call and optimizer completes with seven state parts')
 result=learner.policy_update()
 assert all(torch.isfinite(x).all() for x in result)
 checks.append('actual candidate BPTT policy+critic update completes including both seven-state batches')
 for name,opt in [('WM',learner.opt_wm),('Pi',learner.opt_pi),('Critic',learner.opt_v)]:
  steps={int(x['step']) for x in opt.state.values()}
  assert steps=={1},(name,steps)
  checks.append('synthetic '+name+' optimizer stepped exactly once')
 assert not torch.cuda.is_initialized()
 checks.append('no CUDA initialized')
 out={'passed':True,'checks':checks,'scope':'NEW synthetic CPU gradient/integration fixture, not MOD4 policy inference/training/evaluation','saved_robot_models_loaded':False,'actual_SDK':False,'GO_or_fee':False,'stage':'source-only V4','prior_V2_incomplete_policy_batch_copy':'Preserved original failure: initial AST verifier expected one range(6) but found two; V2 had changed first only. V3 builder literal expected wrong suffix count and failed pre-runtime; V4 changes both state batches. All partials and errors retained.'}
except BaseException:
 out={'passed':False,'checks_before_failure':checks,'error':traceback.format_exc(),'partial_source_and_synthetic_logs_preserved':True}
 REPORT.write_text(json.dumps(out,indent=2),'utf8');raise
REPORT.write_text(json.dumps(out,indent=2),'utf8')
print(json.dumps({'passed':True,'checks':len(checks),'scope':out['scope']}))

