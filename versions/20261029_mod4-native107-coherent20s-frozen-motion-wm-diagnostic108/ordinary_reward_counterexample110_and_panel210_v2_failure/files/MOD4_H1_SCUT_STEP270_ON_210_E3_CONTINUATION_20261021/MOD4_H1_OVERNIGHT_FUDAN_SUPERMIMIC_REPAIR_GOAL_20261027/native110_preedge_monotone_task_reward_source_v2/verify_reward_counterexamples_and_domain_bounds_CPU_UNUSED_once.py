"""Deterministic CPU reward tests; no checkpoint, raw case, SDK or GPU."""
from pathlib import Path
import importlib.util,sys,json,hashlib,time,traceback,math
import torch
torch.set_num_threads(4)
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;R=B/'reports'
OUT=R/'REWARD_COUNTEREXAMPLES_DOMAIN_AND_BOUND_CPU_ACTUAL.json';assert not OUT.exists()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
src=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029/payloads_v2/seed27/source'
dirs=dict(original107=src,unselected109=L/'native109_ground_supported_extension_calibration_source_v1',unselected110v1=L/'native110_preedge_monotone_reward_blend_source_v1',candidate110v2=B)
mods={k:load('reward_cpu_'+k,p/'mod4_fudan_contact_phase_reward_candidate_v2.py') for k,p in dirs.items()}
ps={k:m.BoundOwnStepReward(**json.loads((dirs[k]/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_bytes())['metadata']['bound_own_step_reward']) for k,m in mods.items()}
def evaluate(k,x,*,vx=0.,vy=0.,vz=0.,yaw=0.,leg=.346,theta=0.,force=100.,z=None,lowz=0.,torque=0.,actiondiff=0.,active=True):
 mod=mods[k];p=ps[k]
 x=torch.as_tensor(x,dtype=torch.float32)
 def a(v):return torch.as_tensor(v,dtype=x.dtype).expand_as(x)
 zz=torch.zeros_like(x);vx,vy,vz,yaw,leg,theta,force=map(a,(vx,vy,vz,yaw,leg,theta,force))
 low=torch.stack((torch.stack((x-.08,zz-.1,a(lowz)),-1),torch.stack((x-.08,zz+.1,a(lowz)),-1)),-2)
 high=low+low.new_tensor([.16,0.,.16])
 modes=mod.contact_and_step_modes(low,high,torch.stack((force,force),-1),x,vz,p)
 if not active:
  modes['jump']=zz;modes['recovery']=zz+1;modes['command_forward_velocity']=zz
 q=torch.stack((torch.sin(theta),zz,-torch.cos(theta)),-1)
 m=dict(flight=modes['flight'],takeoff=modes['takeoff'],virtual_leg_length=torch.stack((leg,leg),-1),virtual_leg_angle=torch.stack((theta,theta),-1),
  world_vertical_velocity=vz,body_vertical_velocity=vz,body_forward_velocity=torch.cos(yaw)*vx+torch.sin(yaw)*vy,body_yaw_velocity=zz,
  command_forward_velocity=modes['command_forward_velocity'],command_yaw_velocity=zz,
  root_height=a(p.standing_body_height_m if z is None else z),
  relative_base_height=a(p.standing_body_height_m if z is None else z)-modes['support_surface_height'],
  action=torch.stack([a(actiondiff)]*6,-1),previous_action=torch.stack([zz]*6,-1),actuated_torque=torch.stack([a(torque)]*6,-1),
  projected_gravity=q,body_angular_velocity=torch.stack([zz]*3,-1),actuated_leg_dq=torch.stack([zz]*4,-1),actuated_soft_limit_violation=zz,
  root_planar_velocity=torch.stack((vx,vy),-1),
  task_planar_velocity=torch.stack((vx,vy),-1),task_command_planar_velocity=torch.stack((modes['command_forward_velocity'],zz),-1))
 return mod.combined_reward(m,p,modes),modes,m
try:
 rng=torch.get_rng_state().clone();counter={}
 for k in mods:
  rr,mm,_=evaluate(k,torch.tensor([.056,.20,.25,.27]))
  counter[k]=dict(x_m=[.056,.20,.25,.27],reward=rr['total'].tolist(),jump_weight=mm['jump'].tolist(),jump_total=rr['jump_reward'].tolist(),recovery_total=rr['recovery_reward'].tolist(),
                  far_to_x20_delta=float((rr['total'][1]-rr['total'][0]).item()))
 assert counter['original107']['far_to_x20_delta']<-.001
 assert counter['unselected109']['far_to_x20_delta']<-.001
 assert counter['candidate110v2']['far_to_x20_delta']>=-1e-7
 # Exhaustive tensor product of these explicit synthetic measurement values.
 states=torch.cartesian_prod(torch.tensor([-.5,0.,.25,.5,1.]),torch.tensor([-.2,0.,.15,.5]),torch.tensor([.185,.25,.31,.346,.36]),torch.tensor([-.3,0.,.3]),torch.tensor([10.,100.]))
 nx=257;x=torch.linspace(-.1,.27,nx).repeat(len(states)).requires_grad_()
 vel=states[:,0].repeat_interleave(nx);vzs=states[:,1].repeat_interleave(nx);legs=states[:,2].repeat_interleave(nx);tilts=states[:,3].repeat_interleave(nx);forces=states[:,4].repeat_interleave(nx)
 args=dict(vx=vel,vz=vzs,leg=legs,theta=tilts,force=forces,torque=(torch.arange(len(states))%4).float().repeat_interleave(nx)*20.,actiondiff=(torch.arange(len(states))%3).float().repeat_interleave(nx)*.2)
 r,mo,_=evaluate('candidate110v2',x,**args)
 grad=torch.autograd.grad(r['total'].sum(),x)[0]
 d=r['total'].detach().reshape(-1,nx).diff(dim=1)
 assert torch.isfinite(grad).all() and grad.min()>=-2e-7 and d.min()>=-2e-7
 assert r['mode_advantage'].min()>=-1e-7 and r['nonnegative_jump_bonus'].min()>=0 and r['nonnegative_jump_bonus'].max()<=.0985+1e-7 and r['nonpositive_recovery_extra'].max()<=1e-7
 assert r['total'].max()<=.15+2e-6 and (mo['jump']+mo['top_support']).max()<=1+2e-7
 grid=dict(synthetic_measurement_states=len(states),preedge_positions_per_state=nx,total_evaluations=len(x),minimum_position_derivative=float(grad.min()),minimum_adjacent_reward_delta=float(d.min()),maximum_reward=float(r['total'].max()),mode_advantage_min=float(r['mode_advantage'].min()),no_dynamic_reachability_claim=True)
 old,_,_=evaluate('original107',x.detach(),**args);oldbad=int((old['total'].reshape(-1,nx).diff(dim=1)<-1e-7).any(dim=1).sum())
 # At request-off, exact recovery reward is preserved.
 off,_,_=evaluate('candidate110v2',torch.tensor([.056,.20]),vx=.3,vz=.2,active=False)
 assert torch.allclose(off['total'],off['recovery_reward'],atol=1e-7,rtol=0)
 # Explicit frame and lateral counterexamples; source actual command/observations unchanged.
 heading={};lateral={}
 for k in ('original107','candidate110v2'):
  hh,_,_=evaluate(k,torch.tensor([.056,.056,.056]),vx=torch.tensor([.5,-.5,.5]),yaw=torch.tensor([0.,math.pi,math.pi]))
  heading[k]=hh['total'].tolist()
  ll,_,_=evaluate(k,torch.tensor([.056,.056]),vx=.5,vy=torch.tensor([0.,.5]));lateral[k]=ll['total'].tolist()
 assert abs(heading['original107'][0]-heading['original107'][1])<1e-7
 assert heading['candidate110v2'][0]>heading['candidate110v2'][1]+.001
 assert abs(heading['candidate110v2'][0]-heading['candidate110v2'][2])<1e-7
 assert abs(lateral['original107'][0]-lateral['original107'][1])<1e-7 and lateral['candidate110v2'][0]>lateral['candidate110v2'][1]+.001
 # Quiet supported top dominates a rigorous zero-top-support upper bound.
 top={};quiet={}
 for k in ('original107','unselected110v1','candidate110v2'):
  p=ps[k];tt,tm,_=evaluate(k,.75,z=p.standing_body_height_m+.27,lowz=.27)
  top[k]=dict(reward=float(tt['total']),P=float(tm['top_support']),zero_top_support_upper_bound_for_new_decomposition=.1285)
 assert top['candidate110v2']['reward']>.1285+.02
 for vz in (0.,.15,.5,1.):
  tt,_,_=evaluate('candidate110v2',.75,z=ps['candidate110v2'].standing_body_height_m+.27,lowz=.27,vz=vz)
  quiet[str(vz)]=float(tt['total'])
 assert quiet['0.0']>quiet['0.15']>quiet['0.5']>=quiet['1.0']-1e-7
 # Separate branch derivative certificate holds for all finite valid measurements:
 # C<=.02, E<=0, J<=.0985, 0<=w<=1-P, 0<=quiet<=1.
 assert .03+.0985<=.15 and .03+.12==.15
 assert torch.equal(rng,torch.get_rng_state())
 # Nonfinite state must still be rejected, no negative test exception hidden.
 rejected=False
 try:evaluate('candidate110v2',torch.tensor(float('nan')))
 except AssertionError:rejected=True
 assert rejected
 report=dict(passed=True,epoch=time.time(),kind='DETERMINISTIC_SOURCE_CPU_NOT_MODEL_OR_PHYSICS',
   user_counterexample_reproduced=counter,original107_adverse_position_states_in_grid=oldbad,
   preedge_monotonic_grid=grid,heading_counterexample_rewards=heading,lateral_counterexample_rewards=lateral,perfect_quiet_top=top,top_vertical_speed_sweep=quiet,
   proof=['At fixed supported floor state before leading-edge crossing, C,E,J,command andP=0 do not change with translation. New near andw are nondecreasing.',
          'd reward/dw = J-E >=0, so the old negative baseline mixing term is removed over this domain, not only at one selected stance.',
          'total=C+dt+(1-w)E+wJ+.12Pquiet <=.03+.0985(1-P)+.12P <=.15.',
          'At zero top support, reward<=.1285. Ideal quiet supported top is approximately.15; coefficient12 is an explicit engineering selection above Jmax/dt9.85, not an optimal measured weight.'],
   tests=dict(recovery_exact_when_request_off=True,task_world_XY_velocity_frame_explicit=True,lateral_velocity_penalized=True,vertical_quiet_includes_vz=True,RNG_literal_unchanged=True,nonfinite_rejected=True),
   unselected={'109':'Unchanged whole-total blend reproduces adverse translation; NOT_ADMITTED/NOT_SELECTED.',
      '110v1':'Preedge monotonic source exists, but top-state reward is below a non-top upper bound and quiet omits vertical velocity; insufficient task certificate, NOT_SELECTED.'},
   source_SHA={k:hashlib.sha256((p/'mod4_fudan_contact_phase_reward_candidate_v2.py').read_bytes()).hexdigest() for k,p in dirs.items()},
   limitations=['Synthetic inputs are algebraic checks, not measured reachable dynamic rollouts or successful270mm trajectories.',
     'Proof excludes contact/command changes, real landing/reset, postedge decay, collision/model error and soft-contact false positives.',
     'Top optimum is a measurement-domain certificate, not proof of optimal learned policy or dynamic feasibility.',
     'Original extension0.31 and old positive-vz selfgate remain here; the geometry/calibration proposal is not bundled into this priority repair.',
     'No GPU/sourceSDK/fullstate/payload/producer/Task/GO/resource admission; source passing alone must not launch training.'],
   saved_model_reads=0,raw_reads=0,remote_calls=0,actual_training_started=False)
except BaseException:
 with OUT.open('x',encoding='utf8') as f:json.dump(dict(passed=False,epoch=time.time(),error=traceback.format_exc(),no_model_raw_or_remote=True),f,indent=2)
 raise
with OUT.open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed=True,counterexample=counter,grid=grid,quiet_top=top['candidate110v2'],heading=heading,lateral=lateral)))

