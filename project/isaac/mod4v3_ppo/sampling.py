"""Warp fusion/preallocation/CUDA Graph dispatch on the existing PhysX state."""
import torch
import warp as wp


@wp.func
def rotate(q:wp.vec4,v:wp.vec3):
    xyz=wp.vec3(q[1],q[2],q[3]);t=2.*wp.cross(xyz,v)
    return v+q[0]*t+wp.cross(xyz,t)


@wp.kernel
def endpoint(pos:wp.array3d(dtype=float),quat:wp.array3d(dtype=float),
             joint:wp.array2d(dtype=float),pair:wp.array2d(dtype=int),
             a0:wp.array2d(dtype=float),a1:wp.array2d(dtype=float),
             mimic:wp.array2d(dtype=int),errors:wp.array2d(dtype=float)):
    i=wp.tid();worst=float(0.);angle=float(0.)
    for k in range(pair.shape[0]):
        b0=pair[k,0];b1=pair[k,1]
        p0=wp.vec3(pos[i,b0,0],pos[i,b0,1],pos[i,b0,2])
        p1=wp.vec3(pos[i,b1,0],pos[i,b1,1],pos[i,b1,2])
        q0=wp.vec4(quat[i,b0,0],quat[i,b0,1],quat[i,b0,2],quat[i,b0,3])
        q1=wp.vec4(quat[i,b1,0],quat[i,b1,1],quat[i,b1,2],quat[i,b1,3])
        x0=wp.vec3(a0[k,0],a0[k,1],a0[k,2]);x1=wp.vec3(a1[k,0],a1[k,1],a1[k,2])
        worst=wp.max(worst,wp.length(p0+rotate(q0,x0)-p1-rotate(q1,x1)))
    for k in range(mimic.shape[0]):
        angle=wp.max(angle,wp.abs(joint[i,mimic[k,0]]-joint[i,mimic[k,1]]))
    errors[i,0]=worst;errors[i,1]=angle


class Sampling:
    def __init__(self,env):
        self.env=env;self.device=str(env.device);wp.init()
        wp.load_module(module=__name__,device=self.device)
        self.p=torch.empty(env.num_envs,len(env.robot.body_names),3,device=env.device)
        self.q=torch.empty(env.num_envs,len(env.robot.body_names),4,device=env.device)
        self.j=torch.empty(env.num_envs,len(env.robot.joint_names),device=env.device)
        self.errors=torch.zeros(env.num_envs,2,device=env.device)
        rows=list(env.meta['closures'].values());body=env.robot.body_names
        self.pair=torch.tensor([[body.index(r['parent']),body.index(r['child'])] for r in rows],
                              device=env.device,dtype=torch.int32)
        self.a0=torch.tensor([r['local_pos0'] for r in rows],device=env.device)
        self.a1=torch.tensor([r['local_pos1'] for r in rows],device=env.device)
        names=env.robot.joint_names
        self.mimic=torch.tensor([[names.index(s+'_'+j+'_drive_joint'),names.index(s+'_'+j+'_joint')]
            for s in ('left','right') for j in ('rear1','front1')],device=env.device,dtype=torch.int32)
        self.args=[wp.from_torch(x) for x in (self.p,self.q,self.j,self.pair,self.a0,self.a1,self.mimic,self.errors)]
        self.stream=wp.Stream(self.device)
        with wp.ScopedCapture(stream=self.stream,force_module_load=True) as capture:
            wp.launch(endpoint,dim=env.num_envs,inputs=self.args,device=self.device,stream=self.stream)
        self.graph=capture.graph

    def run(self):
        d=self.env.view.data
        self.p.copy_(d.body_pos_w);self.q.copy_(d.body_quat_w)
        from .env import tensor
        self.j.copy_(tensor(self.env.robot.data.joint_pos))
        ts=wp.stream_from_torch(torch.cuda.current_stream(self.device))
        self.stream.wait_stream(ts);wp.capture_launch(self.graph,stream=self.stream);ts.wait_stream(self.stream)
        self.env.closure_error.copy_(self.errors[:,0]);self.env.mimic_error.copy_(self.errors[:,1])

    def parity(self):
        self.run()
        from mod4v1_scut.math_ops import quat_apply
        d=self.env.view.data;values=[]
        for row in self.env.meta['closures'].values():
            a=self.env.robot.body_names.index(row['parent']);b=self.env.robot.body_names.index(row['child'])
            p0=d.body_pos_w[:,a]+quat_apply(d.body_quat_w[:,a],self.p.new_tensor(row['local_pos0']).expand(self.env.num_envs,-1))
            p1=d.body_pos_w[:,b]+quat_apply(d.body_quat_w[:,b],self.p.new_tensor(row['local_pos1']).expand(self.env.num_envs,-1))
            values.append((p0-p1).norm(dim=-1))
        expected=torch.stack(values,-1).amax(-1)
        error=float((expected-self.errors[:,0]).abs().max())
        if error>2e-5:raise ValueError('Warp/Torch endpoint mismatch')
        return dict(closure_max_absolute_difference_m=error,preallocated=True,CUDA_graph=True,
                    physics='PhysX TGS32/4',supermimic=False,newton=False)
