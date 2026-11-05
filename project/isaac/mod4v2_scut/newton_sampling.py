"""Optional Newton state-read fusion; install only at a saved boundary.

This only translates the existing solver buffers to the task's wxyz tensors.
It neither steps physics nor changes coordinates, actions, DR, or rewards.
"""
import torch
import warp as wp


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
