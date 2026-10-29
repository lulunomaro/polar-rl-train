from pathlib import Path
import ast,json,time,hashlib
import torch
B=Path(__file__).resolve().parent;test=B/'verify_reward_counterexamples_domain_and_unloaded_crossing_CPU_V4_UNUSED_once.py'
raw=test.read_text(encoding='utf8');tree=ast.parse(raw.split("try:\n rng=",1)[0]);tree.body=[n for n in tree.body if not isinstance(n,ast.Assert)]
ns={'__file__':str(test)};exec(compile(tree,str(test),'exec'),ns);evaluate=ns['evaluate']
# New algebraic purpose: flight-scale velocities/forces/height and numeric gradients.
states=torch.cartesian_prod(torch.tensor([-.1,.2,.27,.35,.43,.75,1.2]),torch.tensor([0.,.005,.1,.27,.5]),torch.tensor([0.,1.,10.,100.,1000.]),
 torch.tensor([-3.5,-2.3,-.5,0.,.5,2.3,3.5]),torch.tensor([-1.,0.,.5,1.]),torch.tensor([-.5,0.,.5]),torch.tensor([.185,.25,.31,.346]))
x=states[:,0].clone().requires_grad_();zlow=states[:,1];force=states[:,2];vz=states[:,3].clone().requires_grad_();vx=states[:,4].clone().requires_grad_();vy=states[:,5].clone().requires_grad_();leg=states[:,6].clone().requires_grad_()
r,mo,m=evaluate('candidate110v4',x,vx=vx,vy=vy,vz=vz,leg=leg,force=force,z=.3824462629854679+zlow,lowz=zlow)
grad=torch.autograd.grad(r['total'].sum(),(x,vx,vy,vz,leg))
assert torch.isfinite(r['total']).all() and all(torch.isfinite(g).all() for g in grad) and r['total'].max()<=.15+2e-6
assert r['mode_advantage'].min()>=-1e-7 and r['nonpositive_recovery_extra'].max()<=1e-7 and r['nonnegative_jump_bonus'].max()<=.0985+1e-7
p0=mo['top_support']==0
gx=grad[1][p0]*(m['task_command_planar_velocity'][p0,0]-vx[p0]);gy=grad[2][p0]*(-vy[p0])
assert gx.min()>=-1e-7 and gy.min()>=-1e-7
report=dict(passed=True,epoch=time.time(),kind='EXTENDED_SOURCE_ALGEBRA_NOT_PHYSICS_OR_SAVEDMODEL',
 measurements=len(states),vertical_velocity_values_m_s=[-3.5,-2.3,-.5,0.,.5,2.3,3.5],wheel_bottom_values_m=[0.,.005,.1,.27,.5],force_values_N=[0.,1.,10.,100.,1000.],
 reward_max=float(r['total'].max()),all_five_input_gradients_finite=True,zero_top_support_measurements=int(p0.sum()),
 forward_gradient_times_command_error_min=float(gx.min()),lateral_gradient_times_zero_error_min=float(gy.min()),
 candidate_reward_SHA=hashlib.sha256((B/'mod4_fudan_contact_phase_reward_candidate_v2.py').read_bytes()).hexdigest(),
 limits='Independent measurement tuples include dynamically inconsistent poses/contact forces. This checks source bounds/numeric/axis behavior, not reachable motion, model accuracy, roll/pitch velocity coupling tradeoffs or empirical27cm success.',
 no_model_raw_SDK_remote_or_training=True)
with (B/'reports/EXTENDED_FLIGHT_VELOCITY_CONTACT_DOMAIN_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(report))

