"""One-coordinate deterministic pureactor CPU finite difference; no candidate."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import json,time,hashlib,traceback
import torch,numpy as np
import torch.nn.functional as F
torch.set_num_threads(4)
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports'
OUT=R/'E3_ACTUAL_SAVED_VECTOR_GYRO_Z_SENSITIVITY_CPU_ACTUAL.json';assert not OUT.exists()
SOURCE=W/'MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/left_second_ownsave_actual_1791963199228502100/0_model_32825.pt'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def q(x):
 a=np.asarray(x);return dict(min=float(a.min()),mean=float(a.mean()),median=float(np.median(a)),max=float(a.max()),positive_fraction=float((a>0).mean()),negative_fraction=float((a<0).mean()))
try:
 sourceSHA=sha(SOURCE);assert sourceSHA=='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'
 rng=torch.get_rng_state().clone();nprng=np.random.get_state();ck=torch.load(SOURCE,map_location='cpu',weights_only=False);a=ck['actor_state_dict'];assert len(a)==9 and a['mlp.0.weight'].shape==(256,35) and a['mlp.6.weight'].shape==(6,64)
 task=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload/runtime/isaac/mod4/mod4_task.py';arch=W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/payload/runtime/isaac/mod4/frozen_history_policy.py'
 tx=task.read_text(encoding='utf8');assert tx.index('commands = ObsTerm',tx.index('class PolicyCfg'))<tx.index('height_command = ObsTerm',tx.index('class PolicyCfg'))<tx.index('base_ang_vel = ObsTerm',tx.index('class PolicyCfg'))
 assert 'base_ang_vel = ObsTerm(func=base_ang_vel_delayed, scale=0.5' in tx
 assert "'actor',6,[256,128,64],'elu'" in arch.read_text(encoding='utf8')
 rv=json.loads((W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json').read_bytes());raw=Path(rv['raw']['local_path']);assert sha(raw)==rv['raw']['sha256']
 with np.load(raw) as z:obs=z['policy_obs'];ep=z['episode'];reset=z['terminated']|z['truncated']
 assert obs.shape==(1500,80,35) and np.isfinite(obs).all()
 def mlp(x):
  for n in [0,2,4]:x=F.elu(F.linear(x,a[f'mlp.{n}.weight'].double(),a[f'mlp.{n}.bias'].double()))
  return F.linear(x,a['mlp.6.weight'].double(),a['mlp.6.bias'].double())
 rows=[]
 for i in [6,15,69,67,21,72,70]:
  ids=np.flatnonzero(ep[:,i]==0);ev=ids[reset[ids,i]]
  if len(ev):ids=ids[ids<ev[0]]
  x=torch.from_numpy(obs[ids,i].copy()).double();m=mlp(x)
  eps=.005;plus=x.clone();minus=x.clone();plus[:,6]+=eps;minus[:,6]-=eps
  assert torch.equal(plus[:,:6],x[:,:6]) and torch.equal(plus[:,7:],x[:,7:])
  assert torch.equal(minus[:,:6],x[:,:6]) and torch.equal(minus[:,7:],x[:,7:])
  mp=mlp(plus);mm=mlp(minus);grad=(mp-mm)/(2*eps);grad_per_rad_s=grad*.5
  clipgrad=(torch.clamp(mp,-6,6)-torch.clamp(mm,-6,6))/(2*eps)*.5
  rows.append(dict(env=i,primary_valid_prefix_controls=len(ids),fixture_mean6=[q(m[:,k].detach().numpy()) for k in range(6)],d_mean6_d_physical_gyro_z_rad_s=[q(grad_per_rad_s[:,k].detach().numpy()) for k in range(6)],d_clipped6_d_physical_gyro_z_rad_s=[q(clipgrad[:,k].detach().numpy()) for k in range(6)],d_requested_right_minus_left_wheel_d_physical_gyro_z_rad_s=q((grad_per_rad_s[:,5]-grad_per_rad_s[:,4]).detach().numpy()),d_clipped_right_minus_left_wheel_d_physical_gyro_z_rad_s=q((clipgrad[:,5]-clipgrad[:,4]).detach().numpy()),raw_std6=a['distribution.std_param'].tolist(),other34_fixture_columns_exact=True))
 assert torch.equal(torch.get_rng_state(),rng) and not torch.cuda.is_initialized()
 after=np.random.get_state();assert all(np.array_equal(x,y) for x,y in zip(nprng,after));assert sha(SOURCE)==sourceSHA
 out=dict(epoch=time.time(),passed=True,source=dict(path=str(SOURCE),sha256=sourceSHA,bytes=SOURCE.stat().st_size),raw=rv['raw'],frozen_task_SHA=sha(task),frozen_architecture_SHA=sha(arch),gyro_z_observation_column=6,observation_scale=.5,finite_difference_observation_delta=.005,implied_gyro_z_delta_rad_s=.01,actual_saved_fixture_vectors_10500_or_prefix_only=True,results=rows,
  limits=dict(phase='policy_obs copied after vec.step; this is saved-vector mathematics, not actual same-control actorinput replay.',no_causal_or_wrong_sign_verdict='Physical wheel/ground/leg coupling and delayedtargets notreplayed. Differential sign documented numerically; wheel-command yawpolarity must be verified physically beforedeclaring feedbackwrong.',all_other_six_outputs_may_respond='Sharedtrunk naturally changesall6 actoroutputs tooneinput; this is oneobservationfactor, not sixweightupdates.'),
  no_RNGdraw=True,source_weight_file_unchanged=True,no_CUDA_SSH_GPU_PPO_budget_or_new_checkpoint=True,Git_archive_pending_root_owner=True,
  original_exploratory_errors_retained=['Windows rg *.py literal wildcardpath failed before read; rg --files corrected onlyreader.','CPU exploratory checkpointlookup model_state_dict KeyError; actual schema actor_state_dict, critic_state_dict separately. Neithererror initializedGPU orchangedsource.'])
 OUT.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(report=str(OUT),wheelgrad=[dict(env=r['env'],**r['d_clipped_right_minus_left_wheel_d_physical_gyro_z_rad_s']) for r in rows],no_candidate=True)))
except Exception:
 p=R/f'GYRO_CPU_ORIGINAL_READER_ERROR_{time.time_ns()}.json';p.write_text(json.dumps(dict(error=traceback.format_exc(),epoch=time.time(),source_SHA=sha(__file__),no_GPU=True,Git_archive_pending_root_owner=True),indent=2),encoding='utf8');raise
