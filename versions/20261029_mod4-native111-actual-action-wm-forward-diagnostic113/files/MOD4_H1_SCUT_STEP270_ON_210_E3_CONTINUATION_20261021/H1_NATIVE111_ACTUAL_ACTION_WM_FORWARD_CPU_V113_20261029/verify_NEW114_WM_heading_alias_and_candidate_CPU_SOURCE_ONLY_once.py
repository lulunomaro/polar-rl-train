"""Source-only algebra/FK input-visibility proof. No checkpoint/raw/SDK/physics."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import json, hashlib, time, sys, importlib.util, types, ast, traceback
T=Path(__file__).resolve().parent.parent
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
B=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029/payloads_v2/seed27'
D=L/'native114_WM_fixed_world_heading_visibility_source_v1'
OUT=D/'reports'; MARK=OUT/'SOURCE114_CPU_PROOF_CONSUMED.json'
def write(name,value):
 (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def req(v,m):
 if not bool(v):raise ValueError(m)
req(not MARK.exists(),'new source proof entry already consumed')
write(MARK.name,dict(epoch=time.time(),purpose='Source-only fixed-world heading alias and bounded candidate input proof',checkpoint_reads=0,raw_reads=0))
try:
 import torch
 torch.set_num_threads(2)
 sys.path.insert(0,str(B/'source'))
 from supermimic_wheel_leg_v3.augmented_wheel_leg_world_model_v1 import AugmentedWheelLegWorldModel as Old, WheelLegStateLayout
 from supermimic_wheel_leg_v3.geometry import invariant_features, axis_angle_to_mat
 from supermimic_wheel_leg_v3.networks import RunningNorm
 from own_step_differentiable_geometry_v1 import OwnStepWheelGeometry
 spec=importlib.util.spec_from_file_location('NEW114_SOURCE_ONLY',D/'augmented_wheel_leg_world_model_candidate114_v1.py')
 mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
 New=mod.AugmentedWheelLegWorldModel
 def shell(cls):
  obj=types.SimpleNamespace(layout=WheelLegStateLayout(),action_dim=6,context_dim=31,edge_x_m=.35,platform_top_z_m=.27)
  obj.terrain_relative=types.MethodType(cls.terrain_relative,obj)
  return obj
 old,new=shell(Old),shell(New)
 goal=json.loads((B/'source/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json').read_text(encoding='utf-8'))
 geom=OwnStepWheelGeometry(json.loads((B/'job0/assets/import_contract.json').read_text(encoding='utf-8')),
  json.loads((B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json').read_text(encoding='utf-8')),goal['joint_names'])
 q=torch.tensor(goal['neutral_packed73'][13:43],dtype=torch.float32)[None].expand(2,-1).clone()
 R=torch.stack((torch.eye(3),torch.diag(torch.tensor([-1.,-1.,1.]))))
 p=torch.zeros(2,3);p[:,2]=float(goal['neutral_packed73'][2])
 v=torch.zeros(2,3);w=torch.zeros(2,3);dq=torch.zeros(2,30);aux=torch.zeros(2,54)
 state=(p,R,v,w,q,dq,aux)
 g0=geom(state)
 p[:,2]+=.008-g0['low'][...,2].amin(-1)
 front_offsets=geom(state)['high'][...,0].amax(-1)
 p[:,0]=.35-front_offsets.max()-.001
 # Same body velocity; one world +X approaches edge, other world -X departs.
 toward=int(front_offsets.argmax());body_speed=.5 if toward==0 else -.5
 v[:]=(R@torch.tensor([body_speed,0.,0.])[None,:,None]).squeeze(-1)
 action=torch.zeros(2,6);xi=torch.zeros(2,31)
 a=Old.inputs(old,state,action,xi);b=New.inputs(new,state,action,xi)
 req(torch.equal(a[0],a[1]),'exact old input alias not reproduced')
 req(not torch.equal(b[0],b[1]),'candidate must distinguish heading pair')
 g=geom(state);next_state=(p+.01*v,R,v,w,q,dq,aux);gn=geom(next_state)
 initial_gaps=.35-g['high'][...,0].amax(-1);next_gaps=.35-gn['high'][...,0].amax(-1)
 req((initial_gaps>0).all(),'fixture starts before world leading plane')
 req(next_gaps[toward]<0 and next_gaps[1-toward]>0,'constant-velocity geometric projection crossing distinction')
 # Valid SO(3) source grid across yaw seam and tilt, not measured physical states.
 yaw=torch.linspace(-torch.pi,torch.pi,257);pitch=torch.linspace(-.74,.74,11);roll=torch.linspace(-.74,.74,9)
 yy,pp,rr=torch.meshgrid(yaw,pitch,roll,indexing='ij');yy=yy.reshape(-1);pp=pp.reshape(-1);rr=rr.reshape(-1)
 n=len(yy);axisz=torch.tensor([0.,0.,1.]).expand(n,-1);axisy=torch.tensor([0.,1.,0.]).expand(n,-1);axisx=torch.tensor([1.,0.,0.]).expand(n,-1)
 Rs=axis_angle_to_mat(axisz,yy)@axis_angle_to_mat(axisy,pp)@axis_angle_to_mat(axisx,rr)
 ss=(p[:1].expand(n,-1),Rs,torch.zeros(n,3),torch.zeros(n,3),q[:1].expand(n,-1),torch.zeros(n,30),torch.zeros(n,54))
 aa=torch.zeros(n,6);xx=torch.zeros(n,31);f0=Old.inputs(old,ss,aa,xx);f1=New.inputs(new,ss,aa,xx)
 diff=f1-f0;unchanged=torch.ones(167,dtype=torch.bool);unchanged[[1,3]]=False
 req(torch.equal(f0[:,unchanged],f1[:,unchanged]),'only features1/3 may change')
 delta=diff.abs().amax(0);req(delta[1]<=.0100002 and delta[3]<=.0050002,'bounded input cue')
 norm=RunningNorm(167);norm.var.zero_();z=(norm(f1)-norm(f0)).abs().amax(0)
 req(z[1]<=1.00002 and z[3]<=.50002,'unchanged norm eps floor bounded shift')
 yr=torch.tensor([-.4,0.,.4,-3.14159265,3.14159265],requires_grad=True)
 Rr=axis_angle_to_mat(torch.tensor([0.,0.,1.]).expand(len(yr),-1),yr)
 sr=(p[:1].expand(len(yr),-1),Rr,torch.zeros(len(yr),3),torch.zeros(len(yr),3),q[:1].expand(len(yr),-1),torch.zeros(len(yr),30),torch.zeros(len(yr),54))
 fr=New.inputs(new,sr,torch.zeros(len(yr),6),torch.zeros(len(yr),31))
 grads=[torch.autograd.grad(fr[:,k].sum(),yr,retain_graph=True)[0] for k in (1,3)]
 req(all(torch.isfinite(x).all() for x in grads),'finite heading derivatives')
 req(((grads[0].square()+grads[1].square()).sqrt()>.00499).all(),'combined circle cue nonzero yaw derivative')
 req((fr[-1]-fr[-2]).abs().max()<2e-8,'continuous heading seam')
 # Source-level compatibility: inputs only; all other class methods AST unchanged.
 ta=ast.parse((D/'ORIGINAL_augmented_wheel_leg_world_model_v1.py').read_text(encoding='utf-8'))
 tb=ast.parse((D/'augmented_wheel_leg_world_model_candidate114_v1.py').read_text(encoding='utf-8'))
 def funcs(tree):
  cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='AugmentedWheelLegWorldModel')
  return {x.name:ast.dump(x,include_attributes=False) for x in cls.body if isinstance(x,ast.FunctionDef)}
 fa,fb=funcs(ta),funcs(tb);req(fa.keys()==fb.keys(),'same class method set')
 req(all(fa[k]==fb[k] for k in fa if k!='inputs'),'constructor/step/targets/state_error unchanged')
 req(not torch.cuda.is_initialized(),'no CUDA use')
 report=dict(schema='mod4.source114.fixed_world_heading_visibility.CPU.v1',epoch=time.time(),passed_source_CPU=True,
  old_exact_input_alias=True,old_input_width=a.shape[-1],candidate_pair_max_input_difference=float((b[0]-b[1]).abs().max()),
  synthetic_own_FK_pair=dict(world_vx=v[:,0].tolist(),root_xyz=p.tolist(),neutral_own_q=q[0].tolist(),wheel_bottoms_m=g['low'][...,2].tolist(),
   initial_wheel_front_gap_m=initial_gaps.tolist(),constant_velocity_10ms_projected_front_gap_m=next_gaps.tolist()),
  SO3_source_grid_count=n,changed_input_columns=[1,3],other_165_columns_literal_unchanged=True,
  max_raw_cue_shift=delta[[1,3]].tolist(),max_zero_variance_eps_floor_normalized_shift=z[[1,3]].tolist(),
  heading_circle_derivative_norms=(grads[0].square()+grads[1].square()).sqrt().tolist(),
  all_other_class_methods_AST_unchanged=True,model_or_parameter_or_raw_or_SDK_reads=0,MLP_constructs_or_forwards=0,
  context='Same world root, own neutral joint shape, local velocities/actions/torques and vertical/zero contact history may alias yaw in old WM input. Fixed world obstacle geometry is not yaw invariant.',
  limits=['Constructed FK/geometric projection is NOT a PhysX trajectory, collision/manifold proof, mechanical feasibility proof, or unique observed policy failure cause.',
   'Old WM.step rotates outputs by current rotation; equal neural inputs do not imply equal world predictions. This demonstrates missing obstacle-relative heading information, not broken free-space equivariance.',
   'World contact-history forces can carry heading-correlated information in some actual states; zero or vertical forces do not guarantee heading observability.',
   'Valid SO3 grid is synthetic; bounded heading code needs typed payload/fullstate/actual target norm and runtime readback before use.',
   'No reward change or target SDK/GPU/fullstate/Task/GO/training/adapted skill proof. Preserve actual20s and real270 acceptance.'])
 write('SOURCE114_OLD_INPUT_ALIAS_OWN_FK_AND_BOUNDED_CANDIDATE_CPU_ACTUAL.json',report)
 print(json.dumps(report,ensure_ascii=False,allow_nan=False))
except BaseException:
 write('SOURCE114_ORIGINAL_CPU_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),model_or_raw_reads=0))
 raise
