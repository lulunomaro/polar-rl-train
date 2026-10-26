"""Lossless-to-randomized-parameters static xi31 for the pinned MOD4 recipe.

Full typed DR snapshots remain admission/save evidence. This projection retains
all episode-varying degrees of freedom; nominal constants/order are source-pinned.
It never reads the robot, changes parameters or synthesizes missing fields.
"""
import torch
FIELDS=(('mass_inertia_factor',1),('wheel_friction',1),('motor_gain6',6),
        ('chassis_COM_delta3',3),('PD_factor10',10),('spring_factor2',2),
        ('gas_damping_factor2',2),('action_lag_steps2',2),('leg_encoder_bias4',4))
DIM=sum(n for _,n in FIELDS)

def compact_static_snapshot(snapshot, *, nominal_mass, nominal_inertia,
    original_body_com, body_id, leg_ids, wheel_ids, gas_ids,
    wheel_shape_ids, nominal_gas_stiffness):
    v=snapshot
    n=v['body_mass'].shape[0]
    d=v['body_mass'].device
    def require(ok,msg):
        if not bool(ok):raise ValueError(msg)
    def positive(x):
        require(torch.isfinite(x).all() and (x>0).all(),'positive finite nominal parameter required')
    mass=nominal_mass
    positive(mass)
    factor=v['body_mass'][:,body_id:body_id+1]/mass[:,body_id:body_id+1]
    # These exact recipe reconstruction tests are engineering float32 comparisons,
    # not a new physical/skill gate or sub-resolution world-point audit.
    require(torch.allclose(v['body_mass'],mass*factor,rtol=2e-6,atol=1e-7),'nonuniform mass DR not represented by factor1')
    require(torch.allclose(v['body_inertia'],nominal_inertia*factor[...,None],rtol=2e-6,atol=1e-8),'inertia DR not represented by factor1')
    mu=v['material_static_friction'][:,wheel_shape_ids[:1]]
    for name in ['material_static_friction','material_dynamic_friction']:
        require(torch.equal(v[name][:,wheel_shape_ids],mu.expand(n,len(wheel_shape_ids))),'wheel friction not shared scalar')
    require(torch.equal(v['material_restitution'][:,wheel_shape_ids],torch.zeros_like(v['material_restitution'][:,wheel_shape_ids])),'wheel restitution outside pinned recipe')
    com_delta=v['body_com'][:,body_id]-original_body_com[:,body_id]
    other=[i for i in range(v['body_com'].shape[1]) if i!=body_id]
    require(torch.equal(v['body_com'][:,other],original_body_com[:,other]),'nonchassis COM variation not represented')
    pd=torch.cat((v['joint_stiffness'][:,leg_ids]/60.,
                  v['joint_damping'][:,leg_ids]/2.,
                  v['joint_damping'][:,wheel_ids]/.6),-1)
    positive(nominal_gas_stiffness)
    spring=v['joint_stiffness'][:,gas_ids]/nominal_gas_stiffness
    gas=v['joint_damping'][:,gas_ids]/3.
    values=(factor,mu,v['motor_episode_scale'],com_delta,pd,spring,gas,
            v['action_lag_steps'],v['leg_encoder_episode_bias'])
    for (name,width),x in zip(FIELDS,values):
        require(x.shape==(n,width) and x.device==d and x.dtype==torch.float32 and torch.isfinite(x).all(),name+' wrong shape/device/type/nonfinite')
    out=torch.cat(values,-1).detach().clone()
    require(out.shape==(n,31),'explicit xi31 required')
    return out

def normalize_static31(x):
    if x.shape[-1]!=31:raise ValueError('explicit MOD4 static xi31 required')
    # Fixed feature scales, no future dynamic labels or per-step parameter query.
    center=x.new_tensor([1.,.9]+[1.]*6+[0.]*3+[1.]*10+[1.]*2+[1.]*2+[1.]*2+[0.]*4)
    scale=x.new_tensor([.1,.3]+[.1]*6+[.005]*3+[.05]*10+[.1]*2+[.1]*2+[1.]*2+[.02]*4)
    return (x-center)/scale

