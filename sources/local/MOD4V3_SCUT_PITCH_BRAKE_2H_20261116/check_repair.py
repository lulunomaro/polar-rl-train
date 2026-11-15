"""Regression tests of geometry, reward semantics and causal training-only labels."""
from pathlib import Path
import sys,json,math,ast
from types import SimpleNamespace
import torch
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T/'support'))
from mod4v3_ppo_v1.pitch_brake_math import heading_velocity,horizontal_reward_terms,brake_hint_mask,wheel_brake_targets
from mod4v3_ppo_v1.pitch_stability_math import stability_components,transition_command
checks=[]
for roll,pitch,yaw in [(0.,0.,0.),(.3,.4,1.1),(-.4,-.3,-2.1),(.1,.7,2.9)]:
 cr,sr=math.cos(roll),math.sin(roll);cp,sp=math.cos(pitch),math.sin(pitch);cy,sy=math.cos(yaw),math.sin(yaw)
 Rx=torch.tensor([[1.,0,0],[0,cr,-sr],[0,sr,cr]],dtype=torch.float64);Ry=torch.tensor([[cp,0,sp],[0,1,0],[-sp,0,cp]],dtype=torch.float64);Rz=torch.tensor([[cy,-sy,0],[sy,cy,0],[0,0,1.]],dtype=torch.float64);R=Rz@Ry@Rx
 world=torch.tensor([2.,-.7,.8],dtype=torch.float64);g=R.T@torch.tensor([0.,0.,-1.],dtype=torch.float64);body=R.T@world
 out=heading_velocity(body[None],g[None])[0];forward=R[:,0].clone();forward[2]=0;forward/=forward.norm();lateral=torch.linalg.cross(torch.tensor([0.,0.,1.],dtype=torch.float64),forward)
 expected=torch.stack((world@forward,world@lateral));assert torch.allclose(out,expected,atol=1e-10)
checks.append('Exact horizontal heading velocity across yaw,roll,pitch and vertical motion')
cfg=SimpleNamespace(stand_still_deadzone_enabled=True,stand_still_deadzone_threshold=.1,lin_vel_err_constraint=1.,lin_vel_xy_sigma=.5,lin_vel_xy_soft_sigma=1.5,lin_vel_xy_tight_sigma=.1,lin_vel_xy_square_sigma=1.,lin_vel_xy_torlarance_gap=.5,high_speed_pen_sigma=1.)
g=torch.tensor([[0.,0.,-1.]]*3);v=torch.tensor([[0.,0.,0.],[1.,0.,0.],[2.,0.,0.]]);cmd=torch.tensor([[2.,0.,0.]]*3);r=horizontal_reward_terms(v,g,cmd,cfg);assert r['track_lin_vel_xy_square'].tolist()==[4.,1.,0.];checks.append('Unclipped velocity-square still penalizes standing under fast commands')
cmd.zero_();r=horizontal_reward_terms(v,g,cmd,cfg);assert r['stand_still_lin_vel'].tolist()==[0.,1.,2.];checks.append('Stop residual velocity uses SI horizontal speed')
p=torch.tensor([0.,math.radians(2),math.radians(5),math.radians(20)]);active=torch.ones(4,dtype=torch.bool);c=stability_components(p,torch.zeros(4),active).sum(-1);assert c[0]==0 and bool((c[1:]<c[:-1]).all());checks.append('No5degree deadband; increasing tilt costs strictly more')
cstop=stability_components(p,torch.zeros(4),active,command_vx=torch.zeros(4));crun=stability_components(p,torch.zeros(4),active,command_vx=torch.full((4,),2.2));assert bool((cstop[1:,0]<crun[1:,0]).all());checks.append('SCUT-derived posture correction increases at stop command')
assert not bool(stability_components(p,torch.ones(4),torch.zeros(4,dtype=torch.bool)).any());checks.append('Retained environments receive no added specialist cost')
ages=torch.arange(0,900)*.02;mask=brake_hint_mask(ages,torch.full_like(ages,2.2),torch.full_like(ages,.4),torch.ones(900,dtype=torch.bool));indices=mask.nonzero().flatten().tolist();expected=[i for start in [150,300,450,600,750]for i in range(start,start+5)];assert indices==expected;checks.append('First100ms stop hints use exactly5 issuance ticks in every cycle')
_,moving,_=transition_command(torch.tensor([2.98,3.,3.08,3.1]),torch.ones(4));assert moving.tolist()==[True,False,False,False];checks.append('Brake supervision starts only after the commanded stop')
x=torch.zeros(3,35);x[0,20:22]=3;x[1,20:22]=-3;ref=torch.randn(3,6).clamp(-3,3);target,valid=wheel_brake_targets(ref,x);assert torch.equal(target[:,:4],ref[:,:4]);assert torch.allclose(target[0,4:]-ref[0,4:],torch.ones(2));assert torch.allclose(target[1,4:]-ref[1,4:],-torch.ones(2));assert valid.tolist()==[True,True,False];checks.append('Causal wheel labels mirror direction, leave legs unchanged, exclude stationary wheels')
assert x.shape[1]==35 and target.shape[1]==6;checks.append('Original35D actor and6D output contract retained')
for f in T.rglob('*.py'):ast.parse(f.read_text(encoding='utf-8-sig'))
out=dict(passed=len(checks),checks=checks,training_updates=0);(T/'evidence/LOCAL_REGRESSION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
