"""Read actual D6 scene COM and explicit motor PD; no parameter setter or RNG draw."""
import torch
from gas_damping_sdk_adapter import tensor

def quat_rotate_xyzw(q,v):
    q=q[..., [1,2,3,0]]
    xyz=q[...,:3]; w=q[...,3:4]
    uv=torch.cross(xyz,v,dim=-1)
    return v+2*(w*uv+torch.cross(xyz,uv,dim=-1))

def joint_indices(a,total):
    value=a.joint_indices
    if isinstance(value,slice):return list(range(total))[value]
    if hasattr(value,'torch'):value=value.torch
    if torch.is_tensor(value):return value.detach().cpu().tolist()
    return list(value)

def read_chassis_pd(env):
    cpu=torch.get_rng_state().clone(); cuda=torch.cuda.get_rng_state_all()
    r=env.scene['robot']; names=list(r.body_names); joints=list(r.joint_names)
    assert names.count('chassis')==1
    chassis=names.index('chassis')
    direct=tensor(r.root_view.get_coms()).clone()
    local=tensor(r.data.body_com_pose_b).clone().to(direct.device)
    assert direct.shape==(env.num_envs,len(names),7) and torch.equal(direct,local)
    mass=tensor(r.root_view.get_masses()).clone()
    inertia=tensor(r.root_view.get_inertias()).clone()
    links=tensor(r.data.body_link_pose_w).clone()
    world=tensor(r.data.body_com_pos_w).clone()
    estimated=links[...,:3].double()+quat_rotate_xyzw(links[...,3:7].double(),local[...,:3].to(links.device).double())
    frame_error=float((estimated-world.double()).abs().max())
    assert frame_error<1e-5,frame_error
    assert bool((mass>0).all()) and bool(torch.isfinite(inertia).all())
    weighted=(world.double()*mass.to(world.device).double()[...,None]).sum(1)/mass.to(world.device).double().sum(1)[:,None]
    drive_k=tensor(r.root_view.get_dof_stiffnesses()).clone()
    drive_d=tensor(r.root_view.get_dof_dampings()).clone()
    pd={}
    for name,width,kp,kd in (('legs',4,60.,2.),('wheels',2,0.,.6)):
        a=r.actuators[name]; ids=joint_indices(a,len(joints)); assert len(ids)==width
        k=tensor(a.stiffness).clone(); d=tensor(a.damping).clone()
        assert bool((k==kp).all()) and bool((d==kd).all()),(name,k,d)
        assert bool((drive_k[:,ids]==0).all()) and bool((drive_d[:,ids]==0).all()),name
        pd[name]=dict(joint_indices=ids,joint_names=[joints[i] for i in ids],
                      explicit_model_stiffness=k.cpu().tolist(),explicit_model_damping=d.cpu().tolist(),
                      PhysX_implicit_drive_stiffness=drive_k[:,ids].cpu().tolist(),
                      PhysX_implicit_drive_damping=drive_d[:,ids].cpu().tolist())
    assert torch.equal(cpu,torch.get_rng_state()) and all(torch.equal(a,b) for a,b in zip(cuda,torch.cuda.get_rng_state_all()))
    static=dict(body_names=names,chassis_index=chassis,chassis_name=names[chassis],
                local_COM_pose_xyz_xyzw=local.cpu().tolist(),mass_kg=mass.cpu().tolist(),inertia_kg_m2=inertia.cpu().tolist(),
                explicit_PD=pd,body_count=len(names),joint_names=joints)
    return dict(static=static,actual_PhysX_and_buffer_local_COM_exact=True,COM_frame='each body link-local meters, quaternion xyzw',
                independent_link_to_world_COM_formula_max_error_m=frame_error,
                chassis_mass_fraction=(mass[:,chassis]/mass.sum(1)).cpu().tolist(),
                root_COM_point_world=tensor(r.data.root_com_pos_w).cpu().tolist(),
                calculated_whole_robot_mass_weighted_COM_world=weighted.cpu().tolist(),
                root_COM_point_is_not_claimed_whole_robot_COM=True,explicit_model_PD_separate_from_zero_motor_implicit_drive=True,
                parameter_setter_calls=0,global_CPU_CUDA_RNG_unchanged=True,D7_randomization=False,hardware_calibrated=False)
