"""Execute exact archived velocity expressions and stair bonus on tensors, no simulator/update."""
from pathlib import Path
from types import SimpleNamespace
import ast,json,torch,numpy as np,hashlib
T=Path(__file__).resolve().parent;S=T.parent/'MOD4V3_SCUT_STAIR_LIFT_20M_20261112';E=T/'evidence';raw=(E/'pinned_source/base_env.py').read_text(encoding='utf8');tree=ast.parse(raw);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef));method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_get_rewards');wanted={'forward_lin_vel_horizontal','lin_vel_err','rew_track_lin_vel_xy','rew_track_lin_vel_xy_square'}
nodes=[]
for n in method.body:
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in wanted for t in n.targets):nodes.append(n)
 if isinstance(n,ast.If) and 'self.cfg.lin_vel_err_constraint' in ast.unparse(n.test):nodes.append(n)
compiled=compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<exact_pinned_velocity_reward>','exec')
cfg=SimpleNamespace(lin_vel_err_constraint=1.,lin_vel_xy_sigma=.5,lin_vel_xy_square_sigma=1.)
def rate(v,c):
 env=SimpleNamespace(cfg=cfg,robot=SimpleNamespace(data=SimpleNamespace(root_lin_vel_b=torch.stack((v,torch.zeros_like(v),torch.zeros_like(v)),-1))))
 ns=dict(self=env,torch=torch,vel_reward_gate=torch.ones_like(v),pitch=torch.zeros_like(v),tracking_command=torch.stack((torch.full_like(v,c),torch.zeros_like(v),torch.zeros_like(v)),-1));exec(compiled,ns);return 1.2*ns['rew_track_lin_vel_xy']-1.5*ns['rew_track_lin_vel_xy_square']
source=S/'support/mod4v3_ppo_v1/scut_rough_stair_lift_env.py';tr=ast.parse(source.read_text());cl=next(n for n in tr.body if isinstance(n,ast.ClassDef));cl.body=[n for n in cl.body if isinstance(n,ast.FunctionDef) and n.name in ('_get_rewards','_center','_count')]
class Base:
 def _get_rewards(self):return self.base_value
ns=dict(ScutUnifiedRoughV1Env=Base,torch=torch,euler_xyz_from_quat=lambda x:(torch.zeros(x.shape[0]),torch.zeros(x.shape[0]),torch.zeros(x.shape[0])))
exec(compile(ast.fix_missing_locations(ast.Module(body=[cl],type_ignores=[])),str(source),'exec'),ns);C=ns['ScutRoughV1StairLiftEnv']
def bonus(v,c):
 n=len(v);s=C();s.num_envs=n;s._stair_lift_ready=True;s.device='cpu';s.terrain=SimpleNamespace(terrain_origins=torch.tensor([[[0.,0.,.33]]]),terrain_levels=torch.zeros(n,dtype=torch.long),terrain_types=torch.zeros(n,dtype=torch.long));s.terrain_family=torch.zeros(n,dtype=torch.long);s.view=SimpleNamespace(data=SimpleNamespace(root_pos_w=torch.stack((3.75-v*.02,torch.zeros_like(v),torch.full_like(v,.38)),-1),root_quat_w=torch.tensor([1.,0.,0.,0.]).repeat(n,1)));s.stair_approach=torch.ones(n,dtype=torch.bool);s.reset_terminated=torch.zeros(n,dtype=torch.bool);s.stair_start_abs_x=torch.full_like(v,3.75);s.stair_best_progress=torch.zeros_like(v);s.step_dt=.02;s.snapshots={'height_obs':torch.full_like(v,.38)};s.height=torch.full_like(v,.38);s.reward=SimpleNamespace(ground_z_est=torch.zeros_like(v));s.stair_platform_z=torch.full_like(v,.33);s.stair_best_step=torch.zeros(n,dtype=torch.long);s.stair_counts=torch.zeros(2,11,10,4,dtype=torch.long);s.full_dr=SimpleNamespace(nominal_env_mask=torch.zeros(n,dtype=torch.bool));s.stair_top_seen=torch.zeros(n,dtype=torch.bool);s.stair_reward_sum=torch.zeros(());s.stair_height_error_sum=torch.zeros(());s.stair_height_samples=torch.zeros(());s.base_value=rate(v,c)*.02;ans=s._get_rewards();return (ans-s.base_value)/.02
v=torch.linspace(0.,3.5,35001);rows=[]
for c in (1.5,1.8,2.,2.1,2.2):
 rv=rate(v,c);b=bonus(v,c);j=int((rv+b).argmax());rows.append(dict(command=c,pure_tracking_optimum=float(v[rv.argmax()]),tracking_plus_progress_optimum=float(v[j]),tracking_at_optimum=float(rv[j]),extra_at_optimum=float(b[j])))
basecheck=json.loads((E/'SPEED_RESPONSE.json').read_text());penalties=[]
for r in basecheck['rows']:
 if r['delay_ms']==5 and r['cmd_vx']==2.2 and r['model'] in ('parent','005m','010m'):
  vv=r['tail_reward_projected_vx'];err=vv-2.2;penalties.append(dict(model=r['model'],height=r['height'],projected_speed=vv,error=err,square_rate=-1.5*err**2,exponential_rate=1.2*np.exp(-min(err**2,1.)/.5),combined_tracking_rate=float(rate(torch.tensor([vv]),2.2)[0])))
result=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),formula='R_v=1.2*exp(-min(e^2,1)/0.5)-1.5*e^2; e=c-v_body_x*cos(pitch)',extra_flat_approach_rate='min(new_inward_progress_speed,2.2)*exp(-((height-height_cmd)/0.05)^2)',applies_to_regular_flat=False,applies_on_pre_stair_flat_approach=True,optimum_sweep=rows,actual_point_penalties=penalties,one_step_bonus_at_speed1p8=float(bonus(torch.tensor([1.8]),1.8)[0]*.02),discount_per_policy_step=.99,discount_per_second=.99**50,frontier_step_reward_discount_factor_gain_for_0p2s_earlier=.99**(-10),scope='Analytical local reward comparison; isolated exact AST expressions and bonus; no PPO training; not a causal ablation of training updates')
(E/'REWARD_AUDIT.json').write_text(json.dumps(result,indent=2),encoding='utf8');np.savez_compressed(E/'REWARD_LANDSCAPE.npz',speed=v.numpy(),tracking_c1p8=rate(v,1.8).numpy(),tracking_plus_progress_c1p8=(rate(v,1.8)+bonus(v,1.8)).numpy());print(json.dumps(result))

