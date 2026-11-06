"""Optional Newton sampling fusion; install only at a saved boundary.

This only translates the existing solver buffers to the task's wxyz tensors.
Task fusion preserves400Hz checks and acceptance, plus the50Hz Fudan16 terms.
"""
import torch
import warp as wp
from .warp_kernels import acceptance


@wp.func
def rotate(q: wp.vec4, v: wp.vec3):
    xyz=wp.vec3(q[1],q[2],q[3])
    t=2.0*wp.cross(xyz,v)
    return v+q[0]*t+wp.cross(xyz,t)


@wp.kernel(enable_backward=False)
def read_state(q: wp.array2d[float],v: wp.array2d[float],
               bodies: wp.array[wp.transform],velocities: wp.array[wp.spatial_vector],
               com: wp.array[wp.vec3],qadr: wp.array[wp.int64],vadr: wp.array[wp.int64],
               joint_pos: wp.array2d[float],joint_vel: wp.array2d[float],
               body_pos: wp.array3d[float],body_quat: wp.array3d[float],
               body_velocity: wp.array3d[float],world_velocity: wp.array2d[float],
               local_velocity: wp.array2d[float],local_omega: wp.array2d[float],
               gravity: wp.array2d[float]):
    env,b=wp.tid()
    if b<30:
        joint_pos[env,b]=q[env,qadr[b]]
        joint_vel[env,b]=v[env,vadr[b]]
    i=env*31+b
    t=bodies[i]
    xyz=wp.transform_get_translation(t)
    xyzw=wp.transform_get_rotation(t)
    wxyz=wp.vec4(xyzw[3],xyzw[0],xyzw[1],xyzw[2])
    omega=wp.spatial_bottom(velocities[i])
    linear=wp.spatial_top(velocities[i])-wp.cross(omega,rotate(wxyz,com[i]))
    for k in range(3):
        body_pos[env,b,k]=xyz[k]
        body_velocity[env,b,k]=linear[k]
    for k in range(4):body_quat[env,b,k]=wxyz[k]
    if b==0:
        inverse=wp.vec4(wxyz[0],-wxyz[1],-wxyz[2],-wxyz[3])
        local=rotate(inverse,linear)
        angular=rotate(inverse,omega)
        down=rotate(inverse,wp.vec3(0.0,0.0,-1.0))
        for k in range(3):
            world_velocity[env,k]=linear[k]
            local_velocity[env,k]=local[k]
            local_omega[env,k]=angular[k]
            gravity[env,k]=down[k]


class StateRead:
    def __init__(self,env):
        self.env=env;self.inputs={};n=env.num_envs;device=env.device
        d=env.data
        for name,shape in dict(joint_pos=(n,30),joint_vel=(n,30),
                body_pos_w=(n,31,3),body_quat_w=(n,31,4),body_lin_vel_w=(n,31,3),
                root_lin_vel_w=(n,3),root_lin_vel_b=(n,3),root_ang_vel_b=(n,3),
                projected_gravity_b=(n,3)).items():
            setattr(d,name,torch.empty(shape,device=device))
        d.root_pos_w=d.body_pos_w[:,0];d.root_quat_w=d.body_quat_w[:,0]
        self.outputs=[wp.from_torch(getattr(d,key))for key in (
            'joint_pos','joint_vel','body_pos_w','body_quat_w','body_lin_vel_w',
            'root_lin_vel_w','root_lin_vel_b','root_ang_vel_b','projected_gravity_b')]
        self.com=env.plant.model.body_com
        self.qadr=wp.from_torch(env.qadr);self.vadr=wp.from_torch(env.vadr)

    def update(self):
        e=self.env;p=e.plant;s=p.state;key=s.joint_q.ptr
        if key not in self.inputs:
            self.inputs[key]=[wp.from_torch(wp.to_torch(s.joint_q).reshape(e.num_envs,-1)),
                wp.from_torch(wp.to_torch(s.joint_qd).reshape(e.num_envs,-1)),s.body_q,s.body_qd]
        wp.launch(read_state,dim=(e.num_envs,31),inputs=[*self.inputs[key],self.com,
            self.qadr,self.vadr,*self.outputs],device=e.device)


def install_state_read(env):
    reader=StateRead(env)
    env.update_data=reader.update
    env.fused_state_read=reader
    reader.update()
    return dict(implementation='NEWTON_FUSED_STATE_READ_V1',physics_changed=False,
                preallocated_outputs=True,body_quaternion_order='wxyz')


@wp.kernel(enable_backward=False)
def closure_read(position: wp.array3d[float],quaternion: wp.array3d[float],
                 joints: wp.array2d[float],bodies: wp.array2d[int],
                 anchors: wp.array3d[float],mimics: wp.array2d[int],
                 closure: wp.array[float],mimic: wp.array[float]):
    i=wp.tid()
    maximum=float(0.0)
    for c in range(bodies.shape[0]):
        a,b=bodies[c,0],bodies[c,1]
        qa=wp.vec4(quaternion[i,a,0],quaternion[i,a,1],quaternion[i,a,2],quaternion[i,a,3])
        qb=wp.vec4(quaternion[i,b,0],quaternion[i,b,1],quaternion[i,b,2],quaternion[i,b,3])
        pa=wp.vec3(position[i,a,0],position[i,a,1],position[i,a,2])+rotate(qa,wp.vec3(anchors[c,0,0],anchors[c,0,1],anchors[c,0,2]))
        pb=wp.vec3(position[i,b,0],position[i,b,1],position[i,b,2])+rotate(qb,wp.vec3(anchors[c,1,0],anchors[c,1,1],anchors[c,1,2]))
        maximum=wp.max(maximum,wp.length(pa-pb))
    closure[i]=maximum
    maximum=float(0.0)
    for c in range(mimics.shape[0]):
        maximum=wp.max(maximum,wp.abs(joints[i,mimics[c,0]]-joints[i,mimics[c,1]]))
    mimic[i]=maximum


class ClosureRead:
    def __init__(self,env):
        self.env=env
        self.bodies=wp.from_torch(torch.tensor([[env.body_names.index(row[k])for k in ('body0','body1')]
            for row in env.contract['closures'].values()],device=env.device,dtype=torch.int32))
        self.anchors=wp.from_torch(torch.tensor([[row[k]for k in ('anchor0_m','anchor1_m')]
            for row in env.contract['closures'].values()],device=env.device))
        pairs=[(side+'_'+driven,side+'_'+source)for side in ('left','right')
            for driven,source in (('drive_hip_spin','hip'),('drive_input_spin','crank'))]
        self.mimics=wp.from_torch(torch.tensor([[env.joint_names.index(x)for x in p]for p in pairs],
            device=env.device,dtype=torch.int32))
        self.closure=torch.empty(env.num_envs,device=env.device)
        self.mimic=torch.empty_like(self.closure)
        self.outputs=[wp.from_torch(self.closure),wp.from_torch(self.mimic)]

    def update(self):
        e=self.env;d=e.data
        wp.launch(closure_read,dim=e.num_envs,inputs=[wp.from_torch(d.body_pos_w),
            wp.from_torch(d.body_quat_w),wp.from_torch(d.joint_pos),self.bodies,
            self.anchors,self.mimics,*self.outputs],device=e.device)
        # Endpoint reports own their values; subsequent safety checks reuse the
        # scratch buffers. Preserve the previous return-value lifetime.
        return self.closure.clone(),self.mimic.clone()


def install_closure_read(env):
    reader=ClosureRead(env)
    env.closure_errors=reader.update
    env.fused_closure_read=reader
    return dict(implementation='NEWTON_FUSED_CLOSURE_V1',physics_changed=False,
        closure_m=.01,mimic_rad=.01,check_frequency_hz=400)


class AcceptanceRead:
    def __init__(self,env):
        self.env=env;device=env.device
        r=env.reward
        self.wheels=torch.tensor(env.wheel_bodies,dtype=torch.int32,device=device)
        self.nonwheels=torch.tensor(r._nonwheel_contact_link_idx,dtype=torch.int32,device=device)
        from .math_ops import quat_apply
        shapes=[env.contract['geometry'][s+'_tire']for s in ('left','right')]
        if any(g['type']!=5 for g in shapes):raise ValueError('Expected authored tire cylinders')
        q=torch.tensor([g['quat_wxyz']for g in shapes],device=device)
        self.axes=quat_apply(q,q.new_tensor([[0.,0.,1.],[0.,0.,1.]]))
        self.offsets=q.new_tensor([g['position_m']for g in shapes])
        self.radii=q.new_tensor([g['size'][0]for g in shapes])
        self.widths=q.new_tensor([g['size'][1]for g in shapes])

    def update(self,positions,quaternions,contract,origins,top,ground,wheel_net,
               nonwheel_force,velocity,root_quat,active):
        e=self.env;a=e.acceptance;d=e.data
        values=[d.body_pos_w,d.body_quat_w,root_quat,velocity,origins,e.net_force,
            self.wheels,self.nonwheels,self.axes,self.offsets,self.radii,self.widths,
            top,ground,a.success,a.wholeclear,a.leading,a.ground_seen,a.previous_air,
            a.up,a.current_clear,a.failed_return,a.landed_top,a.flight_id,a.stable_ticks,
            a.stable_peak,a.support_ticks,a.support_peak,a.initial_yaw,active]
        wp.launch(acceptance,dim=e.num_envs,inputs=[wp.from_torch(x)for x in values],device=e.device)
        return a.stable_ticks>0


def install_sampling(env):
    closure=install_closure_read(env)
    reader=AcceptanceRead(env)
    env.acceptance.update_world=reader.update
    env.fused_acceptance_read=reader
    from .warp_sampling import FudanReward,Dispatch
    reward=FudanReward(env.reward,Dispatch(env.device,graphs=False))
    env.reward.compute=reward.compute
    env.fused_fudan_reward=reward
    return dict(implementation='NEWTON_FUSED_TASK_SAMPLING_V1',closure=closure,
        fused=['closure400Hz','jump200acceptance400Hz','Fudan16reward50Hz'],
        state_read_fusion_enabled=False,physics_changed=False)
