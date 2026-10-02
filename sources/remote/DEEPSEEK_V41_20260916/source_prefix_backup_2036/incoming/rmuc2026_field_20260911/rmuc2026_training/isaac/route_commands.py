"""Vectorized route commands and terrain-event gates, independent of Isaac imports.

Use with an existing robot locomotion environment. This is not a complete PPO
task: retain its balance/effort/limit/contact rewards and failure termination.
"""
from pathlib import Path
import json,math
import torch
ROOT=Path(__file__).resolve().parents[1]

class RouteCommands:
    def __init__(self,env_origins,base_height_m,seed=20260911):
        self.origins=env_origins
        self.device=env_origins.device;self.num_envs=len(env_origins);self.base_height=float(base_height_m)
        self.routes=json.loads((ROOT/'data/routes.json').read_text(encoding='utf8'))
        table=lambda data:torch.tensor(data,device=self.device,dtype=torch.float32)
        self.starts=table([r['spawn_ground_m'] for r in self.routes])
        self.goals=table([r['waypoints_m'][-1] for r in self.routes])
        self.yaws=table([r['spawn_yaw_rad'] for r in self.routes])
        self.speeds=table([r['speed_range_m_s'] for r in self.routes])
        kinds=list(dict.fromkeys(r['kind'] for r in self.routes))
        self.kind_ids={k:i for i,k in enumerate(kinds)}
        self.route_kinds=torch.tensor([self.kind_ids[r['kind']] for r in self.routes],device=self.device)
        self.generator=torch.Generator(device=self.device).manual_seed(seed)
        self.ids=torch.arange(self.num_envs,device=self.device)%len(self.routes)
        for name in ['speed','spin_speed','jump_target','elapsed','last_dist','spin_angle','air_time','max_air_time','peak_z']:
            setattr(self,name,torch.zeros(self.num_envs,device=self.device))
        self.launched=torch.zeros(self.num_envs,device=self.device,dtype=torch.bool)
        self.air_after_launch=self.launched.clone()
        self.underpass_visited=self.launched.clone()
        self.finished=self.launched.clone()

    def reset(self,env_ids,route_ids=None):
        e=torch.as_tensor(env_ids,device=self.device,dtype=torch.long)
        if route_ids is not None:self.ids[e]=torch.as_tensor(route_ids,device=self.device,dtype=torch.long)
        ids=self.ids[e]
        if bool(((ids<0)|(ids>=len(self.routes))).any()):raise ValueError('Invalid route index')
        rand=lambda:torch.rand(len(e),device=self.device,generator=self.generator)
        self.speed[e]=self.speeds[ids,0]+rand()*(self.speeds[ids,1]-self.speeds[ids,0])
        self.spin_speed[e]=(2.+2.*rand())*torch.where(rand()>.5,1.,-1.)
        self.jump_target[e]=.08+.27*rand()
        for name in ['elapsed','spin_angle','air_time','max_air_time']:getattr(self,name)[e]=0
        self.launched[e]=False;self.air_after_launch[e]=False;self.underpass_visited[e]=False;self.finished[e]=False
        self.last_dist[e]=torch.linalg.vector_norm(self.goals[ids,:2]-self.starts[ids,:2],dim=-1)
        self.peak_z[e]=self.starts[ids,2]+self.base_height
        state=torch.zeros((len(e),13),device=self.device)
        state[:,:3]=self.origins[e]+self.starts[ids];state[:,2]+=self.base_height
        state[:,3]=torch.cos(self.yaws[ids]/2);state[:,6]=torch.sin(self.yaws[ids]/2)
        return state

    def update(self,root_pos_w,yaw_w,yaw_rate,wheel_grounded,stable,dt):
        """wheel_grounded: bool [N] (any wheel contact); stable: caller's safety mask.

        Returns motion commands and event-gated progress/success. Root states are
        simulator training data here; transfer commands/observations consistently
        when deploying your policy, as with any other navigation training task.
        """
        if dt<=0:raise ValueError('dt must be positive')
        p=root_pos_w-self.origins;ids=self.ids;k=self.route_kinds[ids]
        delta=self.goals[ids,:2]-p[:,:2];distance=torch.linalg.vector_norm(delta,dim=-1)
        heading=torch.atan2(delta[:,1],delta[:,0]);error=torch.atan2(torch.sin(heading-yaw_w),torch.cos(heading-yaw_w))
        command=torch.zeros((self.num_envs,3),device=self.device)
        command[:,0]=self.speed*torch.clamp(torch.cos(error),0.,1.)
        command[:,2]=torch.clamp(2.*error,-2.,2.)
        is_kind=lambda name:k==self.kind_ids[name]
        spin=is_kind('slope_spin');jump=is_kind('jump_in_place');fly=is_kind('fly_jump');tunnel=is_kind('tunnel_cross')
        command[spin,0]=0.;command[spin,2]=self.spin_speed[spin];command[jump]=0.
        self.elapsed+=dt
        directed_spin=yaw_rate*torch.sign(self.spin_speed)
        self.spin_angle+=torch.where(spin&stable,directed_spin*dt,0.)
        self.air_time=torch.where(wheel_grounded,0.,self.air_time+dt)
        self.max_air_time=torch.maximum(self.max_air_time,self.air_time)
        self.peak_z=torch.maximum(self.peak_z,p[:,2])
        # A fly-ramp route must visit the elevated launch region. Reaching the
        # far goal by driving on the low trench floor is explicitly rejected.
        sign=torch.sign(self.goals[ids,0]-self.starts[ids,0])
        u=p[:,0]*sign
        self.launched |= fly&(u>-.8)&(u<.10)&((p[:,2]-self.base_height)>.10)&wheel_grounded&(torch.abs(p[:,1]-self.goals[ids,1])<.40)
        self.air_after_launch |= fly&self.launched&~wheel_grounded&(self.air_time>.04)
        # The CAD roof spans |x|=0.751..1.101 m at these two routes.
        # A root below the ceiling while inside the opening distinguishes an
        # underpass from crossing the highway above it. Robot collision shapes
        # and the caller's safety/contact mask must still enforce body clearance.
        self.underpass_visited |= tunnel&(u>.78)&(u<1.07)&(p[:,2]<.080)&(torch.abs(p[:,1]-self.goals[ids,1])<.35)
        height_gate=p[:,2]>(self.goals[ids,2]+.45*self.base_height)
        reached=(distance<.35)&stable&height_gate
        reached=torch.where(fly,reached&self.air_after_launch&wheel_grounded,reached)
        reached=torch.where(tunnel,reached&self.underpass_visited&wheel_grounded,reached)
        reached=torch.where(spin,(self.spin_angle>=2.*math.pi)&(distance<.35)&stable,reached)
        jumped=(self.peak_z-self.starts[ids,2]-self.base_height)>=self.jump_target
        reached=torch.where(jump,jumped&(self.max_air_time>.04)&wheel_grounded&stable&(distance<.35)&(self.elapsed>1.),reached)
        success=reached&~self.finished
        progress=self.last_dist-distance
        progress=torch.where(spin,torch.clamp(directed_spin,-6.,6.)*dt/(2.*math.pi),progress)
        progress=torch.where(jump,torch.zeros_like(progress),progress)
        progress=torch.where(self.finished,torch.zeros_like(progress),progress)
        self.finished|=reached;self.last_dist=distance
        command[self.finished]=0.
        return dict(command=command,progress_reward=progress,success=success,
                    jump_height_command=torch.where(jump,self.jump_target,0.),distance_to_goal=distance,
                    completed=self.finished.clone())
