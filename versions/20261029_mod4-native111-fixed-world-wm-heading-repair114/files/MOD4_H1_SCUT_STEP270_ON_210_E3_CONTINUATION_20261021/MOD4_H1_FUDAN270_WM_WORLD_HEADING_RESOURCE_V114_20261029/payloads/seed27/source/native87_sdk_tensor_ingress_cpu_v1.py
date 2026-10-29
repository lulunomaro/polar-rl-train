"""Portable source/CPU ingress integration; no SDK App, actor or model weights."""
from pathlib import Path
from types import SimpleNamespace as S
import ast,hashlib
import torch
import actual_DR_memory_getter_v1 as getter
from actual_DR_memory_getter_v1 import RuntimeOrderBinding
import actual_DR_memory_getter_v1 as g
from chassis_com_component import ChassisCOM
from explicit_pd_component import ExplicitPD
from spring_pressure_component import SpringPressure
from gas_damping_factor import GasDamping
from sensor_mild_math import SensorCorruption
from action_delay_physics_queue import PhysicsActionQueue
EXPECTED_BASE_SHA='677d500672162d9bdc04b417c726b0d61edc839e0396cb3faf15316fbca28067'
EXPECTED_PHYSX_SHA='43a31992353ad3a500024d0ec908d5b253ada7a0aac9a1cd2261466e10bda4ff'

def _fixture():
    n=3;body=('chassis',)+tuple('body'+str(i) for i in range(1,31));joint=tuple('j'+str(i) for i in range(30))
    binding=g.RuntimeOrderBinding(body,joint,joint[:4],joint[4:6],joint[6:8],5)
    pd=ExplicitPD(n,'cpu',11,True);com=ChassisCOM(n,'cpu',12,True)
    spring=SpringPressure(n,'cpu',13);gas=GasDamping(n,'cpu',14);sensor=SensorCorruption(n,'cpu',15,'noise_bias_mild_v1')
    q=PhysicsActionQueue(n,'cpu',16)
    data=S(joint_armature=torch.full((n,30),.002),joint_friction_coeff=torch.full((n,30),.003),
           joint_stiffness=torch.zeros(n,30),joint_damping=torch.zeros(n,30))
    actuators=dict(legs=S(joint_indices=list(range(4)),episode_scale=torch.ones(n,4),step_scale=torch.ones(n,4),stiffness=torch.zeros(n,4),damping=torch.zeros(n,4)),
       wheels=S(joint_indices=[4,5],episode_scale=torch.ones(n,2),step_scale=torch.ones(n,2),stiffness=torch.zeros(n,2),damping=torch.zeros(n,2)),
       gas_springs=S(joint_indices=[6,7]))
    original=torch.zeros(n,31,7);original[:,:,6]=1;original[:,:,0]=.001
    dr=S(factor=torch.ones(n),mass=torch.arange(1,32,dtype=torch.float32)[None].expand(n,-1).clone(),
         inertia=torch.ones(n,31,9)*.02,materials=torch.ones(n,5,3)*.2,mu=torch.full((n,),.9),
         reset_count=torch.zeros(n,dtype=torch.int64),wheel_shapes=[1,3])
    env=S(num_envs=n,device='cpu',scene={'robot':S(body_names=list(body),joint_names=list(joint),actuators=actuators,data=data)},
       cfg=S(events=S(gas_spring_preload=S(params={'joint_names':list(joint[6:8]),'targets':[.2206,.2206]}))),
       _mild_dr=dr,_chassis_com=S(body_id=0,original_pose=original,component=com),
       _explicit_pd=S(component=pd,leg_ids=[0,1,2,3],wheel_ids=[4,5]),
       _spring_pressure=S(component=spring,nominal=torch.tensor([3500.,3500.]),ids=[6,7],names=list(joint[6:8])),
       _gas_damping=S(component=gas,ids=[6,7]),_sensor_mild=sensor,
       _physics_action_delay=S(queue=q),action_manager=S(action=torch.full((n,6),12345.)))
    neutral=torch.arange(n*6,dtype=torch.float32).reshape(n,6)*.01
    def reset(ids):
        dr.reset_count[ids]+=1;dr.factor[ids]=.95+.01*dr.reset_count[ids].float()
        dr.mu[ids.cpu()]=.7+.01*dr.reset_count[ids].cpu().float()
        for key,width in [('legs',4),('wheels',2)]:
            actuators[key].episode_scale[ids]=1+torch.arange(width)[None]*.01+dr.reset_count[ids,None]*.001
        for component in (pd,com,spring,gas,sensor):component.reset(ids)
        coeff=pd.coefficients();actuators['legs'].stiffness.copy_(coeff['leg_kp']);actuators['legs'].damping.copy_(coeff['leg_kd']);actuators['wheels'].damping.copy_(coeff['wheel_kd'])
        data.joint_stiffness[:,[6,7]]=spring.actual_stiffness(env._spring_pressure.nominal)
        data.joint_damping[:,[6,7]]=gas.actual_damping_Ns_per_m()
        q.reset('legs',ids,neutral[:,:4]);q.reset('wheels',ids,neutral[:,4:])
    reset(torch.arange(n))
    return env,binding,reset,neutral

class SDKProxyStyleView:
 def __init__(self,value):self._existing_tensor=value
 @property
 def torch(self):return self._existing_tensor
 # Existing Tensor protocol delegation explains why a wrapper can be valid
 # elsewhere while failing torch.is_tensor. No backend query or copy is used.
 def __getattr__(self,key):return getattr(self._existing_tensor,key)

def check(B,actual_sdk_root,*,expected_base_SHA,expected_physx_SHA):
    B=Path(B).resolve();actual_sdk_root=Path(actual_sdk_root).resolve()
    if expected_base_SHA!=EXPECTED_BASE_SHA or expected_physx_SHA!=EXPECTED_PHYSX_SHA:raise ValueError('actual SDK source contract SHA differs')
    paths=dict(base=actual_sdk_root/'assets/articulation/base_articulation_data.py',
        physx=actual_sdk_root.parents[1]/'isaaclab_physx/isaaclab_physx/assets/articulation/articulation_data.py')
    sources={}
    for key,SHA in [('base',EXPECTED_BASE_SHA),('physx',EXPECTED_PHYSX_SHA)]:
        raw=paths[key].read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('actual SDK '+key+' data source SHA mismatch')
        tree=ast.parse(raw)
        props=[n for cls in tree.body if isinstance(cls,ast.ClassDef) for n in cls.body if isinstance(n,ast.FunctionDef) and n.name in ('root_state_w','joint_pos','joint_vel','applied_torque')]
        if len(props)!=4 or any(ast.unparse(p.returns)!='ProxyArray' for p in props):raise ValueError('pinned four ProxyArray properties missing')
        sources[key]=dict(path=str(paths[key]),bytes=len(raw),SHA=SHA,properties={p.name:[p.lineno,p.end_lineno] for p in props})
    from native_wheel_leg_bridge_v4 import NativeWheelLegBridge
    from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY as SK
    rng_before=torch.random.get_rng_state().clone();checks=[]
    def yes(v,name):
        if not v:raise AssertionError(name)
        checks.append(name)
    def refuse(fn,name):
        try:fn()
        except (ValueError,AttributeError,TypeError,KeyError):checks.append(name);return
        raise AssertionError('unexpected acceptance '+name)
    e,binding,reset,neutral=_fixture();n=e.num_envs;robot=e.scene['robot']
    torch.set_num_threads(2)
    root=torch.zeros(n,13);root[:,2]=.3377423;root[:,6]=1.
    joint=torch.arange(n*30,dtype=torch.float32).reshape(n,30)*.001
    velocity=joint*.1;torque=joint*.2
    e.scene=type('Scene',(dict,),{})(e.scene);e.scene.env_origins=torch.tensor([[0.,0.,0.],[2.,3.,0.],[4.,6.,0.]])
    root[:,:3]+=e.scene.env_origins
    for name,value in [('root_state_w',root),('joint_pos',joint),('joint_vel',velocity),('applied_torque',torque)]:setattr(robot.data,name,SDKProxyStyleView(value))
    e._integrated_contact=S(history=torch.ones(n,3,2,3)*.002)
    e._sim_step_counter=0;e.physics_dt=.0025;e.step_dt=.01;e.cfg.decimation=4
    e.h1_phase=S(age_control=torch.zeros(n,dtype=torch.long));e.termination_manager=S(compute=lambda:'unused_original_no_physics')
    trace=S(frame=None);vec=S(unwrapped=e)
    mdp=S(num_joints=30,auxiliary_dim=54,packed_state_dim=127,context_dim=31,action_dim=6)
    bridge=NativeWheelLegBridge(S(env=vec),trace,mdp,binding,lambda:None)
    bridge.install_exact_pre_reset_aux_hook();state=bridge.init_state();packed=state.info[SK]['s'];xi=state.info[SK]['xi']
    yes(packed.shape==(n,127) and xi.shape==(n,31),'real_bridge_constructor_initial_static_capture_and_init_state_accept_four_proxy_views')
    yes(torch.equal(packed[:,91:121],torque) and torch.equal(packed[:,121:127],neutral),'real_current_dynamic54_contains_torque_view_and_original_queue_applied6')
    yes(torch.equal(packed[:,:3],root[:,:3]-e.scene.env_origins) and torch.equal(packed[:,3:7],root[:,[6,3,4,5]]),'original_pack_frame_and_xyzw_wxyz_unchanged')
    yes(torch.equal(packed[:,13:43],joint) and torch.equal(packed[:,43:73],velocity),'real_current_joint_and_velocity_views_exact')
    for name,value in [('root_state_w',root),('joint_pos',joint),('joint_vel',velocity),('applied_torque',torque)]:
     yes(getter.tensor(getattr(robot.data,name)) is value,name+'_normalizer_returns_existing_view_no_copy')
    rows=bridge.static.reader.friction_transfer_rows;current,unchanged=bridge.current()
    yes(torch.equal(current,packed) and torch.equal(unchanged,xi) and bridge.static.reader.friction_transfer_rows==rows,'nonreset_current_does_not_transfer_friction_or_resample_static_context')
    before_xi=xi.clone();before_packed=current.clone();reset(torch.tensor([1]));root[1,2]=.3377423;torque[1]=0;e._integrated_contact.history[1]=0
    bridge.static.refresh_after_resets(torch.tensor([1]));current,new_xi=bridge.current()
    yes(torch.equal(new_xi[[0,2]],before_xi[[0,2]]) and not torch.equal(new_xi[1],before_xi[1]),'real_selected_reset_static_cache_changes_only_selected_row')
    yes(torch.equal(current[[0,2]],before_packed[[0,2]]) and torch.all(current[1,91:121]==0),'postreset_current_reads_selected_proxy_row_and_preserves_other_rows')
    original=robot.data.applied_torque;robot.data.applied_torque=SDKProxyStyleView(torch.zeros(n,29));refuse(bridge.current,'wrong_torque_width_rejected_by_original_dynamic_shape_guard');robot.data.applied_torque=original
    robot.data.applied_torque=SDKProxyStyleView(torch.zeros(n,30,dtype=torch.float64));refuse(bridge.current,'wrong_torque_dtype_not_cast_or_relaxed');robot.data.applied_torque=original
    robot.data.applied_torque=S(torch=None);refuse(bridge.current,'nonTensor_proxy_view_refused_no_as_tensor_fallback');robot.data.applied_torque=original
    original=robot.data.joint_pos;robot.data.joint_pos=SDKProxyStyleView(torch.zeros(n,29));refuse(bridge.current,'wrong_joint_width_original_pack_guard');robot.data.joint_pos=original
    original=robot.data.applied_torque;bad=torque.clone();bad[0,0]=float('nan');robot.data.applied_torque=SDKProxyStyleView(bad);refuse(bridge.current,'nonfinite_torque_original_finite_guard_retained');robot.data.applied_torque=original
    yes(torch.equal(rng_before,torch.random.get_rng_state()),'global_CPU_RNG_unchanged_private_fixture_generators_only')
    yes(not torch.cuda.is_initialized(),'no_CUDA_context_created')
    return dict(passed=True,checks=checks,count=len(checks),fixture_only=True,fixture_num_envs=n,
        actual_source_SHA_checks=sources,source_layout_supplied_by_caller=True,
        actual_GPU_runtime_readback_passed=False,actual_SDK_instance_or_scene_created=False,
        actual_Warp_ProxyArray_instance_created=False,SDK_proxy_style_existing_tensor_view_fixture=True,
        actual_bridge_constructor_current_init_state_selected_reset_checked=True,
        no_real_actor_model_weights_physics_rollout_or_network=True,old_fixture_cases_not_rerun=True)
