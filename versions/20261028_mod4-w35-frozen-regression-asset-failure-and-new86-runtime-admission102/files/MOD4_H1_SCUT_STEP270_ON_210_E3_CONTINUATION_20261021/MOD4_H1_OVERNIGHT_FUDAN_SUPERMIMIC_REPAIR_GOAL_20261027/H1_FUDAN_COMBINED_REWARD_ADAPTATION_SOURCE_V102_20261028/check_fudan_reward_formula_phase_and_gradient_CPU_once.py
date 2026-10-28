from pathlib import Path
from types import SimpleNamespace
import hashlib,importlib.util,json,os,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports'
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
 import torch
 torch.set_num_threads(2);assert not torch.cuda.is_initialized();torch.manual_seed(102)
 a=mod('candidate_fudan102_v2',B/'mod4_fudan_contact_phase_reward_candidate_v2.py');J=mod('oracle_jump_v3',B/'upstream_jump_enabled_reward_oracle_v3.py');S=mod('oracle_stair_v3',B/'upstream_stair_enabled_reward_oracle_v3.py')
 n=64;root=torch.randn(n,13);root[:,2]=torch.rand(n);commands=torch.randn(n,3);commands[:,2]=.2;vel=torch.randn(n,3);ang=torch.randn(n,3);L=.12+torch.rand(n,2)*.24;theta=torch.randn(n,2);actions=torch.randn(n,6);old=torch.randn(n,6,2);tau=torch.randn(n,6);gravity=torch.randn(n,3);dq=torch.randn(n,6);q=torch.randn(n,6);limits=torch.tensor([[-.4,.4]]*6);contact=torch.rand(n,2)>.5;flight=~contact.any(-1);takeoff=contact.any(-1)&(root[:,9]>.15)
 p=a.BoundOwnStepReward(.31,.16,.2,.65,.35,1.15,.27,.75)
 idx=[0,1,3,4];limit_violation=(limits[idx,0]-q[:,idx]).clamp_min(0).sum(-1)+(q[:,idx]-limits[idx,1]).clamp_min(0).sum(-1)
 m=dict(flight=flight.float(),takeoff=takeoff.float(),virtual_leg_length=L,virtual_leg_angle=theta,world_vertical_velocity=root[:,9],body_forward_velocity=vel[:,0],body_vertical_velocity=vel[:,2],body_yaw_velocity=ang[:,2],command_forward_velocity=commands[:,0],command_yaw_velocity=commands[:,1],root_height=root[:,2],relative_base_height=root[:,2],action=actions,previous_action=old[:,:,0],actuated_torque=tau,projected_gravity=gravity,body_angular_velocity=ang,actuated_leg_dq=dq[:,idx],actuated_soft_limit_violation=limit_violation,root_planar_velocity=vel[:,:2])
 cfg=SimpleNamespace(rewards=SimpleNamespace(tracking_sigma=.25));maxerr={}
 for name,klass,fn in [('jump',J.UpstreamJumpRewardOracleV3,a.instantaneous_jump_terms),('stair',S.UpstreamStairRewardOracleV3,a.instantaneous_stair_recovery_terms)]:
  oracle=klass();oracle.cfg=cfg;oracle.device='cpu';oracle.dt=.01;oracle.commands=commands;oracle.base_lin_vel=vel;oracle.base_ang_vel=ang;oracle.L0=L;oracle.theta0=theta;oracle.root_states=root;oracle.was_in_flight=flight;oracle.contact_filt=contact;oracle.last_actions=old;oracle.actions=actions;oracle.torques=tau;oracle.projected_gravity=gravity;oracle.base_height=root[:,2];oracle.reward_scales={'nominal_state':-1.,'base_height':1.};oracle.dof_vel=dq;oracle.dof_pos=q;oracle.dof_pos_limits=limits
  terms=fn(m,p);errs={}
  for key,value in terms.items():
   if key=='encourage_jump_upward_only':expect=.15*root[:,9].clamp_min(0)
   else:expect=getattr(oracle,'_reward_'+key)().float()
   error=(value-expect).abs().max().item();assert torch.allclose(value,expect,rtol=2e-6,atol=2e-6),(name,key,error);errs[key]=error
  maxerr[name]=errs
 # Demonstrate why the upstream historical accumulator cannot be silently
 # treated as real flight duration in native127 (no such state field).
 oracle=J.UpstreamJumpRewardOracleV3();oracle.device='cpu';oracle.dt=.01;oracle.base_air_time=torch.zeros(1);oracle.was_in_flight=torch.tensor([False]);oracle.root_states=torch.zeros(1,13);oracle.root_states[:,2]=.2
 history=[float(oracle._reward_encourage_jump()) for _ in range(4)];assert history[-1]>history[1]>history[0]
 # Real completion is deliberately not certified by the planning blend.
 low=torch.tensor([[[.1,0.,0.],[.1,0.,0.]],[[.6,0.,.27],[.6,0.,.27]],[[.1,0.,.65],[.1,0.,.65]]]);high=low.clone();high[...,0]+=.1
 modes=a.contact_and_step_modes(low,high,torch.tensor([[100.,100.],[100.,100.],[0.,0.]]),torch.tensor([.1,.75,.1]),torch.zeros(3),p)
 assert modes['top_support'][1]>.99 and modes['top_support'][0]<.001 and modes['top_support'][2]<.001
 assert modes['command_forward_velocity'][1]<.005 and modes['command_forward_velocity'][0]>.49
 # Finite, nonzero height/leg gradients using only synthetic tensors, no model.
 z=torch.tensor([.50,.55],requires_grad=True);leg=torch.tensor([[.22,.23],[.24,.25]],requires_grad=True);gm={k:v[:2].clone() if torch.is_tensor(v) else v for k,v in m.items()};gm.update(root_height=z,virtual_leg_length=leg,flight=torch.ones(2),takeoff=torch.ones(2));raw=a.instantaneous_jump_terms(gm,p);objective=raw['base_height_flight'].sum()+raw['leg_tuck'].sum();objective.backward();assert torch.isfinite(z.grad).all() and z.grad.abs().min()>0 and torch.isfinite(leg.grad).all() and leg.grad.abs().min()>0
 put('FUDAN102_INSTANTANEOUS_FORMULAS_MODES_AND_SYNTHETIC_GRADIENT_CPU_ACTUAL.json',dict(epoch=time.time(),passed=True,source_SHA=hashlib.sha256((B/'mod4_fudan_contact_phase_reward_candidate_v2.py').read_bytes()).hexdigest(),upstream_commit=a.UPSTREAM_COMMIT,instantaneous_source_formula_max_errors=maxerr,upstream_grounded_history_counterexample=history,upstream_history_not_carried_or_called_in_candidate=True,platform_support_and_stop_command_negative_scopes_passed=True,synthetic_height_and_leg_gradients_finite_nonzero=True,unavailable_original_terms_explicit=a.NATIVE_UNAVAILABLE_OR_STATEFUL_ORIGINAL_TERMS,no_saved_model_actor_WM_forward_or_SDK_GPU_network_or_physics=True,not_training_admission_or_physical_success=True))
 print(json.dumps(dict(passed=True,source_formula_profiles=list(maxerr),grounded_history_counterexample=history,source_only_no_GPU_or_models=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('FUDAN102_MATH_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_GPU_or_physics=True));raise
