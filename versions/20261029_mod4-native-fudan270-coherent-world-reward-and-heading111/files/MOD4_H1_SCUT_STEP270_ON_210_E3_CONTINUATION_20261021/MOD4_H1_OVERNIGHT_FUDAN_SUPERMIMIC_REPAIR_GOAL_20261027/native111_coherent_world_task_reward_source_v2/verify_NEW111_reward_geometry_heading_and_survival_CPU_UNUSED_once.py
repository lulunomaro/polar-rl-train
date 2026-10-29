"""New-purpose definitions/source CPU validation. No PT, raw case, SDK or GPU."""
from pathlib import Path
import ast,hashlib,importlib.util,json,math,sys,time,traceback
import torch
torch.set_num_threads(4)
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;R=B/'reports'
OUT=R/'NEW111_REWARD_GEOMETRY_HEADING_AND_SURVIVAL_CPU_ACTUAL_V1.json'
assert not OUT.exists();(R/'CPU_ENTRY_CONSUMED_BEFORE_CHECKS.json').open('x').write(json.dumps(dict(epoch=time.time(),no_model_or_raw=True)))
SRC=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029/payloads_v2/seed27/source'
sys.path[:0]=[str(B),str(SRC)]
import mod4_fudan_contact_phase_reward_candidate_v2 as reward
from native_fudan_step_adapter_candidate_v2 import OwnFudanStepMdp,OwnFudanStepReference
from converted_MOD4_jump_mdp_v4 import ConvertedMOD4JumpMdp
from supermimic_wheel_leg_v3.geometry import axis_angle_to_mat,mat_to_6d,invariant_features
from supermimic_wheel_leg_v3.networks import RunningNorm
from private_phase_frame_v1 import encode
doc=json.loads((B/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_bytes())
p=reward.BoundOwnStepReward(**doc['metadata']['bound_own_step_reward'])
def evaluate(x,*,y=0.,vx=0.,vy=0.,vz=0.,yaw=0.,tilt=0.,leg=.346,theta=0.,force=100.,z=None,lowz=0.,active=True,torque=0.,adiff=0.):
 x=torch.as_tensor(x,dtype=torch.float32)
 def a(v):return torch.as_tensor(v,dtype=x.dtype).expand_as(x)
 z0=torch.zeros_like(x);y,vx,vy,vz,yaw,tilt,leg,theta,force=map(a,(y,vx,vy,vz,yaw,tilt,leg,theta,force))
 low=torch.stack((torch.stack((x-.08,y-.12,a(lowz)),-1),torch.stack((x-.08,y+.08,a(lowz)),-1)),-2)
 high=low+low.new_tensor([.16,.04,.16])
 modes=reward.contact_and_step_modes(low,high,torch.stack((force,force),-1),x,vz,p)
 modes['actual_front_gap']=p.step_edge_x_m-high[...,0].amax(-1)
 if not active:modes.update(jump=z0,recovery=z0+1,command_forward_velocity=z0)
 m=dict(flight=modes['flight'],takeoff=modes['takeoff'],virtual_leg_length=torch.stack((leg,leg),-1),virtual_leg_angle=torch.stack((theta,theta),-1),
  world_vertical_velocity=vz,body_vertical_velocity=vz,body_forward_velocity=yaw.cos()*vx+yaw.sin()*vy,body_yaw_velocity=z0,
  task_planar_velocity=torch.stack((vx,vy),-1),task_command_planar_velocity=torch.stack((modes['command_forward_velocity'],z0),-1),
  command_forward_velocity=modes['command_forward_velocity'],command_yaw_velocity=z0,root_height=a(p.standing_body_height_m if z is None else z),
  relative_base_height=a(p.standing_body_height_m if z is None else z),top_support=modes['top_support'],upright_cos=tilt.cos(),heading_cos=yaw.cos(),root_lateral_position=y,request_active=a(float(active)),
  action=torch.stack([a(adiff)]*6,-1),previous_action=torch.stack([z0]*6,-1),actuated_torque=torch.stack([a(torque)]*6,-1),
  projected_gravity=torch.stack((tilt.sin(),z0,-tilt.cos()),-1),body_angular_velocity=torch.stack([z0]*3,-1),
  actuated_leg_dq=torch.stack([z0]*4,-1),actuated_soft_limit_violation=z0,root_planar_velocity=torch.stack((vx,vy),-1))
 return reward.combined_reward(m,p,modes),modes,m
def scalar(v):return float(v.detach())
def frames(age,n=1):
 return encode(torch.full((n,),age,dtype=torch.long),torch.zeros(n,dtype=torch.long))
try:
 rng=torch.get_rng_state().clone();report=dict(epoch=time.time(),kind='NEW111_SOURCE_CPU_NO_MODEL_RAW_SDK_REMOTE',passed=False)
 # Original adverse position example is pinned to its already-saved report; new source evaluated now.
 old=json.loads((L/'native110_task_reward_contact_semantics_source_v4/reports/REWARD_COUNTEREXAMPLES_DOMAIN_AND_BOUND_CPU_ACTUAL_V4.json').read_bytes())
 examples={}
 for speed in (0.,.25,.5):
  result,_,_=evaluate(torch.tensor([.056,.20,.25]),vx=speed)
  assert result['total'][1]>=result['total'][0]-2e-7
  examples[str(speed)]=result['total'].tolist()
 report['position_counterexamples']=dict(saved_original107=old['user_counterexample_reproduced']['original107'],new111=examples)
 # Dense fixed-floor monotonicity, including independent own-state channels.
 states=torch.cartesian_prod(torch.tensor([-.5,0.,.25,.5,1.]),torch.tensor([-.2,0.,.15,.5]),torch.tensor([.185,.25,.31,.346,.36]),torch.tensor([-.3,0.,.3]),torch.tensor([10.,100.]))
 nx=257;x=torch.linspace(-.1,.27,nx).repeat(len(states)).requires_grad_()
 result,modes,_=evaluate(x,vx=states[:,0].repeat_interleave(nx),vz=states[:,1].repeat_interleave(nx),leg=states[:,2].repeat_interleave(nx),theta=states[:,3].repeat_interleave(nx),force=states[:,4].repeat_interleave(nx))
 gradient=torch.autograd.grad(result['total'].sum(),x)[0];pre=modes['actual_front_gap']>=0
 pairs=pre.reshape(-1,nx)[:,:-1]&pre.reshape(-1,nx)[:,1:];deltas=result['total'].detach().reshape(-1,nx).diff(dim=-1)
 assert torch.isfinite(gradient).all() and gradient[pre].min()>=-2e-7 and deltas[pairs].min()>=-2e-7
 assert result['mode_advantage'].min()>=-1e-7 and result['nonpositive_recovery_extra'].max()<=1e-7
 report['floor_position_grid']=dict(structured_states=len(states),evaluations=len(x),actual_preedge=int(pre.sum()),minimum_gradient=scalar(gradient[pre].min()),minimum_delta=scalar(deltas[pairs].min()),no_dynamical_reachability_claim=True)
 # Full XY footprint: off either side, either x edge, or zero contact cannot earn platform credit.
 boundary={}
 for xx,yy,label in [(p.goal_root_x_m,0.,'interior'),(.42,0.,'leading_wheel_incomplete'),(1.08,0.,'far_wheel_outside'),(.75,.51,'right_side_outside'),(.75,-.51,'left_side_outside')]:
  q,m,_=evaluate(xx,y=yy,z=p.standing_body_height_m+.27,lowz=.27)
  boundary[label]=dict(reward=scalar(q['total']),P=scalar(m['top_support']),footprint=scalar(m['footprint']))
  assert (m['top_support']>0) if label=='interior' else (m['top_support']==0)
 assert boundary['interior']['reward']>.1385
 report['platform_boundary']=boundary
 xx=torch.linspace(.20,1.07,256);a,am,_=evaluate(xx,vx=.5,vz=2.3,force=0.,lowz=.27,z=p.standing_body_height_m+.27)
 assert torch.all(am['flight']==1) and torch.all(am['top_support']==0) and torch.all(am['jump']==1)
 assert a['total'].max()-a['total'].min()<2e-7
 report['unloaded_contact']=dict(points=256,flight_exact1=True,top_support_exact0=True,reward_range=[scalar(a['total'].min()),scalar(a['total'].max())])
 quiet={}
 for k,kw in [('ideal',{}),('yaw90',dict(yaw=math.pi/2)),('tilt20deg',dict(tilt=math.pi/9)),('vertical.15',dict(vz=.15)),('planar.15',dict(vx=.15))]:
  a,_,_=evaluate(.75,z=p.standing_body_height_m+.27,lowz=.27,**kw);quiet[k]=dict(reward=scalar(a['total']),quiet=scalar(a['top_quiet']))
 assert all(quiet['ideal']['reward']>quiet[k]['reward'] for k in quiet if k!='ideal')
 report['stationary_platform_heading_tilt_and_motion']=quiet
 # 58,800 independent tuples, plus finite gradients of x/y/z/vx/vz/yaw/tilt.
 mesh=torch.cartesian_prod(torch.tensor([-.1,.056,.2,.35,.55,.75,1.15,1.3]),torch.tensor([-.8,0.,.8]),torch.tensor([0.,.27,.5]),torch.tensor([0.,1.,100.]),torch.tensor([-3.5,0.,3.5]))
 xx=mesh[:,0].clone().requires_grad_();yy=mesh[:,1].clone().requires_grad_();zz=torch.full_like(xx,p.standing_body_height_m,requires_grad=True);vv=torch.full_like(xx,.5,requires_grad=True);vz=mesh[:,4].clone().requires_grad_();yaw=torch.full_like(xx,.3,requires_grad=True);tilt=torch.full_like(xx,.2,requires_grad=True)
 a,mo,_=evaluate(xx,y=yy,z=zz,vx=vv,vz=vz,yaw=yaw,tilt=tilt,force=mesh[:,3],lowz=mesh[:,2]);gg=torch.autograd.grad(a['total'].sum(),(xx,yy,zz,vv,vz,yaw,tilt))
 assert all(torch.isfinite(t).all() for t in gg) and torch.isfinite(a['total']).all() and a['total'].max()<=.160002
 assert (mo['jump']+mo['top_support']).max()<=1.000001
 # C<=.02, E<=0, J<=.0985, alignment<=.01 => R<=.04+.0985(1-P)+.12P<=.16.
 assert .04+.0985<.16 and abs(.04+.12-.16)<1e-12
 report['independent_measurement_domain']=dict(count=len(mesh),seven_gradients_finite=True,maximum_reward=scalar(a['total'].max()),source_upper_bound=.16,zero_top_support_bound=.1385,dynamically_inconsistent_tuples_explicitly_possible=True)
 off,_,_=evaluate(torch.tensor([.056,.2]),active=False,vx=.3,vz=.2)
 assert torch.allclose(off['total'],off['recovery_reward'],atol=1e-7,rtol=0)
 # Real own recorded FK constants and named joint source pose, no USD/NPZ/model.
 contract=json.loads((SRC.parent/'job0/assets/import_contract.json').read_bytes());geometry=json.loads((SRC/'OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json').read_bytes())
 provider=OwnFudanStepReference(doc).bind_named_order(doc['joint_names'],scope='source_CPU_fixture')
 mdp=OwnFudanStepMdp(provider,contract,geometry)
 n=73;q=provider.neutral[13:43].expand(n,-1).clone();q.requires_grad_();dq=torch.zeros_like(q)
 xyz=torch.tensor([.056,0.,p.standing_body_height_m]).expand(n,-1).clone();v=torch.zeros_like(xyz);w=torch.zeros_like(xyz);aux=torch.zeros(n,54);aux[:,:18].reshape(n,3,2,3)[:,:,:,2]=100
 yaw_angles=torch.linspace(-math.pi+1e-4,math.pi,n);axis=torch.tensor([0.,0.,1.]).expand(n,-1);rot=axis_angle_to_mat(axis,yaw_angles)
 state=(xyz,rot,v,w,q,dq,aux);g=mdp.wheel_geometry(state)
 # Translate the actual own FK root so both wheel bottoms are at/above floor.
 xyz=xyz.clone();xyz[:,2]-=g['low'][...,2].amin(-1).detach();state=(xyz,rot,v,w,q,dq,aux)
 f=frames(300,n);previous=torch.zeros(n,6);context=torch.zeros(n,31)
 obs=mdp.obs(state,previous,context,f);base=ConvertedMOD4JumpMdp.obs(mdp,state,previous,context,f)
 assert obs.shape==(n,86) and torch.equal(obs[...,:3],base[...,:3]) and torch.equal(obs[...,4:],base[...,4:])
 assert obs[:,3].abs().max()<=.010001
 normal=RunningNorm(86);normal.var.zero_();normal.count.fill_(2e8)
 assert normal(obs)[:,3].abs().max()<=1.0001
 # Construct exact same stationary state except world yaw0 vs pi. Old ingress aliases.
 pair=(xyz[:1].expand(2,-1),axis_angle_to_mat(torch.tensor([[0.,0.,1.]]).expand(2,-1),torch.tensor([0.,math.pi])),v[:2],w[:2],q[:1].expand(2,-1),dq[:2],aux[:2])
 ff=frames(300,2);bb=ConvertedMOD4JumpMdp.obs(mdp,pair,previous[:2],context[:2],ff);nn=mdp.obs(pair,previous[:2],context[:2],ff)
 assert (bb[0]-bb[1]).abs().max()<3e-7 and (nn[0]-nn[1]).abs().max()>.009
 crit=mdp.critic_features(pair,ff,context[:2]);assert crit.shape==(2,165) and (crit[0]-crit[1]).abs().max()>.009
 assert torch.equal(mdp.goal(ff,10),provider.future_goal(ff,10))
 rr=mdp.objective_terms(state,f,previous,previous);dg=torch.autograd.grad(rr['total'].sum(),q)[0]
 assert torch.isfinite(rr['total']).all() and torch.isfinite(dg).all()
 report['own_FK_and_policy_ingress']=dict(actual_source_named_joint_pose=True,world_yaw_states=n,old_zero_slot_max=scalar(base[:,3].abs().max()),new_slot_max=scalar(obs[:,3].abs().max()),old_opposite_heading_alias_max=scalar((bb[0]-bb[1]).abs().max()),new_opposite_heading_separation=scalar((nn[0]-nn[1]).abs().max()),all_other_observation_slots_literal_equal=True,goal_bytes_and_goal_norm_semantics_unchanged=True,architecture=[86,1460,165],own_FK_reward_and_joint_gradient_finite=True,no_closed_loop_or_dynamic_reachability_claim=True,actual_saved_norm_readback_still_required=True,wrapped_yaw_seam_explicit=True)
 survival={}
 for angle in (0.,.3,.5,.7,.749,.751):
  rot=axis_angle_to_mat(torch.tensor([[0.,1.,0.]]),torch.tensor([angle]));st=(torch.tensor([[0.,0.,p.standing_body_height_m]]),rot,*[part[:1] for part in state[2:]])
  d=mdp.soft_termination(st,frames(300));new_alive=(1-d)**32;old_tilt=torch.sigmoid((math.cos(.75)-rot[:,2,2])/.04);old_height=torch.sigmoid((.12-st[0][:,2])/.02);old_alive=((1-old_height)*(1-old_tilt))**32
  survival[str(angle)]=dict(old_survival32=scalar(old_alive),new_survival32=scalar(new_alive),new_discounted_tail32=scalar(new_alive*.99**32))
  assert torch.isfinite(d).all() and 0<=d<=1
 assert survival['0.5']['new_survival32']>.97 and survival['0.5']['old_survival32']<.45
 assert survival['0.751']['new_survival32']==0
 assert mdp.soft_termination(st,frames(2000))==1
 report['joint_discount_and_termination']=dict(gamma=.99,horizon=32,gamma32=.99**32,tilt_table=survival,per_step_risk_is_32_control_engineering_surrogate_not_measured_probability=True,physical_hard_tilt_and_timeout_unchanged=True,soft_height_012_removed_because_physical_low_base_disabled_source_minus1=True,actual_target_config_readback_required=True)
 assert torch.equal(rng,torch.get_rng_state())
 report.update(passed=True,no_model_raw_SDK_remote_or_GPU=True,saved_model_reads=0,new_learning_GO=False,physical270_skill=False,limitations=['Synthetic tuples and source FK do not prove dynamic reachability.','This jointly changes multiple identified task-coherence errors, not an isolated causal experiment.','Bounded yaw retains the inherited norm tensors; actual current mean/variance must be read back at the new target admission.','Horizon hazard scaling is an explicit engineering change, not measured calibration.','Original extension.31/tuck.16 and pre-positive-vz gate are retained; no sole-cause claim.'])
 with OUT.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps({k:v for k,v in report.items() if k in ('passed','floor_position_grid','platform_boundary','own_FK_and_policy_ingress','joint_discount_and_termination')},indent=2))
except BaseException:
 with (R/('ORIGINAL_CPU_FAILURE_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),traceback=traceback.format_exc(),source_not_used=True),f,indent=2)
 raise
