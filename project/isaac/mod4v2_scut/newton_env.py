"""MOD4v2 task bridge to Newton/SolverMuJoCo, independent of Kit/PhysX.

The old checkpoint-visible sensor, delay, gas and PD components are reused by
reference. This module owns only simulator data access and physical writes.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import json
import math
import sys

import mujoco
import newton
import numpy as np
import torch
import warp as wp
from newton.sensors import SensorContact
from newton._src.geometry.raycast import ray_intersect_box, map_ray_to_local

from .config import observation_component, ground_scan_config
from .jump200 import Jump200Acceptance
from .math_ops import quat_apply, quat_apply_inverse, quat_from_euler_xyz, euler_xyz_from_quat
from .newton_model import NewtonPlant
from .rewards import ScutRewards


def referenced_components(folder):
    """Import existing simulator-independent components without copying them."""
    folder = Path(folder)
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
    names = dict(sensor=('sensor_mild_math', 'SensorCorruption'),
                 feedback=('feedback_delay_mild', 'FeedbackDelay'),
                 action=('action_delay_physics_queue', 'PhysicsActionQueue'),
                 spring=('spring_pressure_component', 'SpringPressure'),
                 gas=('gas_damping_factor', 'GasDamping'),
                 com=('chassis_com_component', 'ChassisCOM'),
                 pd=('explicit_pd_component', 'ExplicitPD'))
    return {key: getattr(__import__(module), cls) for key, (module, cls) in names.items()}


class Component:
    def __init__(self, component):
        self.component = component

    def state_dict(self):
        return self.component.state_dict()

    def load_state_dict(self, state):
        self.component.load_state_dict(state)


class Commands:
    """The jump200 profile's fixed .6/0/0 command and source time counters."""
    def __init__(self, n, device, seed):
        self.vel_command_b = torch.zeros(n, 3, device=device)
        self.vel_command_b[:, 0] = .6
        self.command_counter = torch.zeros(n, dtype=torch.long, device=device)
        self.time_left = torch.zeros(n, device=device)
        self.heading_target = torch.zeros(n,device=device)
        self.is_heading_env = torch.zeros(n,dtype=torch.bool,device=device)
        self.is_standing_env = torch.zeros_like(self.is_heading_env)
        self.special_mode_id = torch.full((n,),-1,dtype=torch.long,device=device)
        self._mode_enabled = torch.zeros(1,dtype=torch.bool)
        for name in ('_error_xy_sum','_error_yaw_sum','_step_count'):
            setattr(self,name,torch.zeros(n,device=device))

    @property
    def command(self):
        return self.vel_command_b

    def compute(self, dt):
        self.time_left -= dt
        ids = (self.time_left <= 0).nonzero().flatten()
        if len(ids):
            self.resample(ids)

    def reset(self, ids):
        self.command_counter[ids] = 0
        self.resample(ids)

    def resample(self,ids):
        self.command[ids] = self.command.new_tensor([.6, 0., 0.])
        self.command_counter[ids] += 1
        self.time_left[ids] = torch.empty(len(ids), device=self.command.device).uniform_(5., 15.)

    def set_training_iteration(self, value):
        self.iteration = value


@wp.kernel(enable_backward=False)
def ground_rays(points: wp.array2d[wp.vec3], shape_ids: wp.array2d[int],
                transforms: wp.array[wp.transform], scales: wp.array[wp.vec3],
                result: wp.array2d[wp.vec3]):
    env, k = wp.tid()
    start = points[env,k]+wp.vec3(0.,0.,5.)
    direction = wp.vec3(0.,0.,-1.)
    best = float(1.e6)
    for s in range(2):
        shape = shape_ids[env,s]
        origin, ray = map_ray_to_local(transforms[shape],start,direction)
        distance, normal = ray_intersect_box(origin,ray,scales[shape])
        if distance >= 0. and distance < best:
            best = distance
    hit = wp.vec3(points[env,k][0],points[env,k][1],0.)
    if best < 1.e6:
        hit = start+best*direction
    result[env,k] = hit


@wp.kernel(enable_backward=False)
def contact_reduction(count: wp.array[int], shape0: wp.array[int], shape1: wp.array[int],
                      point0: wp.array[wp.vec3], point1: wp.array[wp.vec3],
                      normal: wp.array[wp.vec3], force: wp.array[wp.spatial_vector],
                      shape_body: wp.array[int], body_q: wp.array[wp.transform],
                      wheel_slot: wp.array[int], body_world: wp.array[int],
                      top: wp.array2d[float], ground: wp.array2d[float]):
    i = wp.tid()
    if i < count[0]:
        b0 = shape_body[shape0[i]]
        b1 = shape_body[shape1[i]]
        bid = b0
        p = point0[i]
        if b0 < 0:
            bid = b1
            p = point1[i]
        if bid >= 0 and (b0 < 0 or b1 < 0):
            slot = wheel_slot[bid]
            if slot >= 0 and wp.abs(normal[i][2]) > .8:
                position = wp.transform_point(body_q[bid], p)
                f = wp.abs(wp.dot(wp.spatial_top(force[i]), normal[i]))
                world = body_world[bid]
                if wp.abs(position[2]) < .001:
                    wp.atomic_add(ground, world, slot, f)
                if wp.abs(position[2]-.2) < .001 and position[0] >= .799 and position[0] <= 3.501 and wp.abs(position[1]) <= 3.501:
                    wp.atomic_add(top, world, slot, f)


class NewtonEnv:
    def __init__(self, package, components, reset_bank, n=80, device='cuda:0', seed=66):
        self.num_envs, self.device, self.seed = n, device, seed
        wp.init()
        self.warp_stream=wp.Stream(device=device)
        self.torch_stream=torch.cuda.ExternalStream(self.warp_stream.cuda_stream,device=device)
        self.torch_stream.wait_stream(torch.cuda.current_stream(device))
        torch.cuda.set_stream(self.torch_stream)
        wp.set_stream(self.warp_stream)
        self.physics_dt, self.step_dt = .0025, .02
        self.max_episode_length, self.max_episode_length_s = 400, 8.
        self.num_actions=6
        self.cfg=dict(physics_backend='Newton/SolverMuJoCo',episode_length_s=8.,num_envs=n)
        self.plant = plant = NewtonPlant(package, n, device)
        self.contract = json.loads((Path(package)/'assets/import_contract.json').read_bytes())
        self.model, self.solver = plant.model, plant.solver
        self.body_names = plant.body_names
        mm = self.solver.mj_model
        self.joint_names = [s.rsplit('/',1)[-1] for s in self.model.joint_label[1:31]]
        assert len(self.joint_names) == 30 and len(self.body_names) == 31
        self.qadr = torch.tensor(mm.jnt_qposadr[1:], device=device, dtype=torch.long)
        self.vadr = torch.tensor(mm.jnt_dofadr[1:], device=device, dtype=torch.long)
        self.legs = [self.joint_names.index(x) for x in ('left_crank','left_hip','right_crank','right_hip')]
        self.wheels = [self.joint_names.index(x+'_wheel_spin') for x in ('left','right')]
        self.gas = [self.joint_names.index(x+'_gas_slide') for x in ('left','right')]
        self.wheel_bodies = [self.body_names.index(x+'_wheel') for x in ('left','right')]
        self.default_joint_pos = torch.zeros(n, 30, device=device)
        self.data = SimpleNamespace(joint_pos=torch.zeros(n,30,device=device),
            joint_vel=torch.zeros(n,30,device=device), applied_torque=torch.zeros(n,30,device=device),
            joint_pos_target=torch.zeros(n,30,device=device), default_joint_pos=self.default_joint_pos,
            soft_joint_pos_limits=torch.tensor(mm.jnt_range[1:],device=device).float().expand(n,-1,-1))
        self.robot = SimpleNamespace(joint_names=self.joint_names, body_names=self.body_names, data=self.data)
        self.scene = SimpleNamespace(env_origins=torch.zeros(n,3,device=device))
        self.episode_length_buf = torch.zeros(n,dtype=torch.long,device=device)
        self.physics_ticks, self.common_step_counter = 0, 0
        self.command = Commands(n, device, seed)
        self.command_manager = SimpleNamespace(get_term=lambda name:self.command,
                                               get_command=lambda name:self.command.command)
        c = referenced_components(components)
        self._sensor_mild = c['sensor'](n, device, seed, 'noise_bias_mild_v1')
        self._feedback_delay_mild = c['feedback'](n, device, seed, True)
        self._physics_action_delay = c['action'](n, device, seed, True)
        self._spring_pressure = Component(c['spring'](n, device, seed, True))
        self._gas_damping = Component(c['gas'](n, device, seed, True))
        self._chassis_com = Component(c['com'](n, device, seed, True))
        self._explicit_pd = Component(c['pd'](n, device, seed, True))
        self.rng = torch.Generator(device=device).manual_seed(seed+1717)
        self.cpu_generator = torch.Generator(device='cpu').manual_seed(seed+1818)
        self.mass_factor = torch.ones(n,device=device)
        self.motor_gain = torch.ones(n,6,device=device)
        self.friction = torch.full((n,),.9,device=device)
        self.nominal = torch.ones(n,dtype=torch.bool,device=device)
        self.reset_count = torch.zeros(n,dtype=torch.long,device=device)
        self.nominal_mass = wp.to_torch(self.model.body_mass).clone().reshape(n,31)
        self.nominal_inertia = wp.to_torch(self.model.body_inertia).clone().reshape(n,31,3,3)
        self.nominal_com = wp.to_torch(self.model.body_com).clone().reshape(n,31,3)
        self.nominal_shape_mu = wp.to_torch(self.model.shape_material_mu).clone().reshape(n,-1)
        self.shape_wheels = [i for i,x in enumerate(self.model.shape_label[:len(self.nominal_shape_mu[0])])
                             if x.rsplit('/',1)[-1] in ('left_tire','right_tire')]
        shapes_per_world = self.model.shape_count//n
        terrain = [i for i,x in enumerate(self.model.shape_label[:shapes_per_world])
                   if x.rsplit('/',1)[-1] in ('ground','jump200_platform')]
        assert len(terrain)==2
        self.terrain_shapes = wp.from_torch(torch.tensor(terrain,device=device,dtype=torch.int32)[None]
                                      +torch.arange(n,device=device,dtype=torch.int32)[:,None]*shapes_per_world)
        self.reset_poses = [p for p in json.loads(Path(reset_bank).read_bytes())['poses'] if .24 <= p['root_height_m'] <= .272]
        assert len(self.reset_poses) == 74
        self.bank = torch.tensor([[p['joint_pos'].get(j,0.) for j in self.joint_names]
                                  for p in self.reset_poses],device=device)
        self.sensor = SensorContact(self.model, sensing_bodies=list(range(self.model.body_count)),
                                    request_contact_attributes=False)
        pipeline = newton.CollisionPipeline(self.model, rigid_contact_max=self.solver.get_max_contact_count(),soft_contact_max=0)
        self.contacts = pipeline.contacts()
        self.observables = self.solver.observables(kinds=self.sensor.solver_observable_kinds,contacts=self.contacts)
        self.top_force = torch.zeros(n,2,device=device)
        self.ground_force = torch.zeros_like(self.top_force)
        slots = torch.full((n,31),-1,dtype=torch.int32,device=device)
        slots[:,self.wheel_bodies[0]], slots[:,self.wheel_bodies[1]] = 0, 1
        self.wheel_slots = wp.from_torch(slots.flatten())
        self.net_force = torch.zeros(n,31,3,device=device)
        self.contact_history = torch.zeros(n,3,31,3,device=device)
        self.acceptance = Jump200Acceptance(n, device)
        self.update_data()
        self.reward = ScutRewards(self.robot,self.contract,n,device,profile='jump200',quaternion_order='wxyz')
        self.reward.command_generator = self.command
        self.reward.jump200_landed_top = self.acceptance.landed_top
        self.reward.jump200_requested = torch.zeros(n,dtype=torch.bool,device=device)
        self.reward.forward_scan_provider = self.forward_scan
        self.reward.leg_action_term = SimpleNamespace(processed_actions=torch.zeros(n,4,device=device),
                                                     _scale=.5,_offset=torch.zeros(n,4,device=device))
        self.pending_actions = torch.zeros(n,6,device=device)
        self.feedback = {}
        self.completed_episodes = self.completed_strict = 0
        self.terminal_snapshot = None
        self.physics_observer = None
        self.physics_graphs = {}
        self.physics_eager_warmed = False
        self._last_observations = None
        self.reset(torch.arange(n,device=device))

    def update_data(self):
        p, d, n = self.plant, self.data, self.num_envs
        q = wp.to_torch(p.state.joint_q).reshape(n,-1)
        v = wp.to_torch(p.state.joint_qd).reshape(n,-1)
        body = wp.to_torch(p.state.body_q).reshape(n,31,7)
        vel = wp.to_torch(p.state.body_qd).reshape(n,31,6)
        d.joint_pos, d.joint_vel = q[:,self.qadr], v[:,self.vadr]
        d.body_pos_w, d.body_quat_w = body[...,:3],body[..., [6,3,4,5]]
        d.root_pos_w, d.root_quat_w = d.body_pos_w[:,0],d.body_quat_w[:,0]
        omega = vel[...,3:]
        com_world = quat_apply(d.body_quat_w,wp.to_torch(p.model.body_com).reshape(n,31,3))
        d.body_lin_vel_w = vel[...,:3]-torch.cross(omega,com_world,dim=-1)
        d.root_lin_vel_w = d.body_lin_vel_w[:,0]
        d.root_lin_vel_b = quat_apply_inverse(d.root_quat_w,d.root_lin_vel_w)
        d.root_ang_vel_b = quat_apply_inverse(d.root_quat_w,omega[:,0])
        d.projected_gravity_b = quat_apply_inverse(d.root_quat_w,d.root_pos_w.new_tensor([0.,0.,-1.]).expand(n,-1))

    def sample_feedback(self):
        d, tick = self.data, self.physics_ticks//4
        raw = dict(base_ang_vel=d.root_ang_vel_b, projected_gravity=d.projected_gravity_b,
                   leg_pos=d.joint_pos[:,self.legs], leg_vel=d.joint_vel[:,self.legs],
                   wheel_vel=d.joint_vel[:,self.wheels])
        self.feedback = {k:self._feedback_delay_mild.apply(k,self._sensor_mild.apply(k,x,tick),tick)
                         for k,x in raw.items()}

    def reset(self, ids):
        ids = torch.as_tensor(ids,device=self.device,dtype=torch.long)
        if not len(ids):
            return
        n, p, d = self.num_envs,self.plant,self.data
        self._sensor_mild.reset(ids)
        self._feedback_delay_mild.reset(ids)
        for key in ('_spring_pressure','_gas_damping','_chassis_com','_explicit_pd'):
            getattr(self,key).component.reset(ids)
        nominal = torch.rand(len(ids),device=self.device,generator=self.rng)<.2
        factor = torch.empty(len(ids),device=self.device).uniform_(.9,1.1,generator=self.rng)
        factor[nominal] = 1.
        self.mass_factor[ids],self.nominal[ids] = factor,nominal
        gains = torch.cat([torch.empty(len(ids),k,device=self.device).uniform_(.9,1.1,generator=self.rng)
                           for k in (4,2)],-1)
        gains[nominal] = 1.
        self.motor_gain[ids] = gains
        bucket = torch.randint(1,33,(len(ids),),generator=self.cpu_generator)
        bucket[nominal.cpu()] = 0
        buckets = torch.cat((torch.tensor([.9]),torch.linspace(.7,1.,32)))
        self.friction[ids] = buckets[bucket].to(self.device)
        wp.to_torch(p.model.body_mass).reshape(n,31)[ids] = self.nominal_mass[ids]*factor[:,None]
        wp.to_torch(p.model.body_inertia).reshape(n,31,3,3)[ids] = self.nominal_inertia[ids]*factor[:,None,None,None]
        com = wp.to_torch(p.model.body_com).reshape(n,31,3)
        com[ids] = self.nominal_com[ids]
        com[ids,0] += self._chassis_com.component.delta_m[ids]
        mu = wp.to_torch(p.model.shape_material_mu).reshape(n,-1)
        mu[ids[:,None],torch.tensor(self.shape_wheels,device=self.device)] = self.friction[ids,None]
        # Native gas drive coefficients remain at the released target/preload.
        ke = wp.to_torch(p.model.mujoco.dof_passive_stiffness).reshape(n,-1)
        kd = wp.to_torch(p.model.joint_damping).reshape(n,-1)
        gas_v = self.vadr[self.gas]
        ke[ids[:,None],gas_v] = self._spring_pressure.component.actual_stiffness([2000.,2000.])[ids]
        kd[ids[:,None],gas_v] = self._gas_damping.component.actual_damping_Ns_per_m()[ids]
        p.solver.notify_model_changed(newton.ModelFlags.BODY_INERTIAL_PROPERTIES|
                                     newton.ModelFlags.SHAPE_PROPERTIES|
                                     newton.ModelFlags.JOINT_DOF_FORCE_PROPERTIES)
        pick = torch.randint(len(self.bank),(len(ids),),device=self.device)
        joints = self.bank[pick]
        root = torch.empty(len(ids),3,device=self.device).uniform_(-.05,.05)
        quat = quat_from_euler_xyz(*root.unbind(-1))[:,[1,2,3,0]]
        for state in (p.state,p.next_state):
            mask=torch.zeros(n+1,dtype=torch.bool,device=self.device);mask[ids]=True
            p.solver.reset(state,wp.from_torch(mask),flags=0)
            q = wp.to_torch(state.joint_q).reshape(n,-1)
            v = wp.to_torch(state.joint_qd).reshape(n,-1)
            q[ids] = torch.as_tensor(p.initial_q.reshape(n,-1),device=self.device)[ids]
            q[ids,:3] = q.new_tensor([0.,0.,.38])
            q[ids,3:7] = quat
            q[ids[:,None],self.qadr] = joints
            v[ids] = 0.
            newton.eval_fk(p.model,state.joint_q,state.joint_qd,state)
        self.command.reset(ids)
        self.reward.reset(ids)
        self.reward.resample_height(ids)
        self.reward.command[ids] = self.command.command[ids]
        self.acceptance.reset(ids)
        self.acceptance.set_spawn_orientation(ids,quat[:,[3,0,1,2]])
        self.top_force[ids],self.ground_force[ids] = 0.,0.
        self.net_force[ids],self.contact_history[ids] = 0.,0.
        self.episode_length_buf[ids] = 0
        self.reset_count[ids] += 1
        self._physics_action_delay.reset('legs',ids,torch.zeros(n,4,device=self.device))
        self._physics_action_delay.reset('wheels',ids,torch.zeros(n,2,device=self.device))
        self.update_data()
        self.sample_feedback()
        self.reward.refresh_reset_scans(ids, *[x[ids] for x in self.scans()])
        self._last_observations = None

    def forward_scan(self, stair=False):
        r,d=self.reward,self.data
        yaw=euler_xyz_from_quat(d.root_quat_w)[2]
        sign=torch.where(r.command[:,0]<0.,-1.,1.)
        heading=torch.stack((yaw.cos()*sign,yaw.sin()*sign,torch.zeros_like(yaw)),-1)
        cfg=r.cfg.stair_state_machine_cfg if stair else r.cfg.wheel_forward_scan_cfg
        offset=float(cfg.get('scan',{}).get('forward_offset',.2 if stair else .1))
        return self.raycast(d.body_pos_w[:,self.wheel_bodies]+heading[:,None]*offset)

    def raycast(self,points):
        hits=torch.empty_like(points)
        wp.launch(ground_rays,dim=points.shape[:2],inputs=[wp.from_torch(points.contiguous(),dtype=wp.vec3),
            self.terrain_shapes,self.model.shape_transform,self.model.shape_scale,wp.from_torch(hits,dtype=wp.vec3)],device=self.device)
        starts=points.clone();starts[...,2]+=5.
        return starts,hits

    def scans(self):
        d,r=self.data,self.reward
        scan=ground_scan_config()
        sx,sy=scan['size'];res=scan['resolution']
        x=torch.linspace(-sx/2,sx/2,int(sx/res)+1,device=self.device)
        y=torch.linspace(-sy/2,sy/2,int(sy/res)+1,device=self.device)
        xx,yy=torch.meshgrid(x,y,indexing='ij')
        offsets=torch.stack((xx.flatten(),yy.flatten(),torch.zeros(xx.numel(),device=self.device)),-1)
        yaw=euler_xyz_from_quat(d.root_quat_w)[2]
        q=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw)
        points=d.root_pos_w[:,None]+quat_apply(q[:,None].expand(-1,len(offsets),-1),offsets[None].expand(self.num_envs,-1,-1))
        _,hits=self.raycast(points)
        ground=hits[...,2].mean(-1)
        wheels=ground[:,None].expand(-1,2)
        far,far_hits=self.forward_scan(False)
        near,near_hits=self.forward_scan(True)
        return ground,wheels,far,far_hits,near,near_hits

    def closure_errors(self):
        d=self.data;values=[]
        for row in self.contract['closures'].values():
            i,j=[self.body_names.index(row[k]) for k in ('body0','body1')]
            a=d.body_pos_w[:,i]+quat_apply(d.body_quat_w[:,i],d.root_pos_w.new_tensor(row['anchor0_m']).expand(self.num_envs,-1))
            b=d.body_pos_w[:,j]+quat_apply(d.body_quat_w[:,j],d.root_pos_w.new_tensor(row['anchor1_m']).expand(self.num_envs,-1))
            values.append((a-b).norm(dim=-1))
        closure=torch.stack(values,-1).amax(-1)
        mimic=[]
        for side in ('left','right'):
            for driven,source in (('drive_hip_spin','hip'),('drive_input_spin','crank')):
                mimic.append((d.joint_pos[:,self.joint_names.index(side+'_'+driven)]-
                              d.joint_pos[:,self.joint_names.index(side+'_'+source)]).abs())
        return closure,torch.stack(mimic,-1).amax(-1)

    def step(self,actions):
        p,d,r=self.plant,self.data,self.reward
        applied=actions.clamp(-6.,6.)
        self.pending_actions.copy_(applied)
        targets=applied[:,:4]*.5
        geometry=__import__('mod4v2_scut.hardware',fromlist=['adapter']).adapter()._geometry()
        for side,c,h in (('left',0,1),('right',2,3)):
            current=d.joint_pos[:,self.legs]
            lo,hi=geometry.mechanical_delta_bounds(side)
            raw=targets[:,c]-targets[:,h]
            delta=(raw+torch.round((current[:,c]-current[:,h]-raw)/(2*math.pi))*2*math.pi).clamp(lo,hi)
            hip=targets[:,h]+torch.round((current[:,h]-targets[:,h])/(2*math.pi))*2*math.pi
            targets[:,h],targets[:,c]=hip,hip+delta
        r.leg_action_term.processed_actions.copy_(targets)
        self._physics_action_delay.submit('legs',targets,self.physics_ticks)
        self._physics_action_delay.submit('wheels',applied[:,4:]*10.,self.physics_ticks)
        for substep in range(8):
            leg=self._physics_action_delay.apply('legs',self.physics_ticks)
            wheel=self._physics_action_delay.apply('wheels',self.physics_ticks)
            coeff=self._explicit_pd.component.coefficients()
            torque_leg=coeff['leg_kp']*(leg-d.joint_pos[:,self.legs])-coeff['leg_kd']*d.joint_vel[:,self.legs]
            torque_wheel=coeff['wheel_kd']*(wheel-d.joint_vel[:,self.wheels])
            velocity=d.joint_vel[:,self.legs+self.wheels]
            effort=torch.cat((torque_leg,torque_wheel),-1)
            stall=effort.new_tensor([53.333333333333336]*4+[28.1853]*2)
            no_load=effort.new_tensor([16.755160819145562]*4+[55.3557]*2)
            continuous=effort.new_tensor([40.]*4+[5.77590977444]*2)
            corner=no_load*(continuous/stall+1.)
            voltage_velocity=torch.maximum(torch.minimum(velocity,corner),-corner)
            upper=torch.minimum(continuous,stall*(1.-voltage_velocity/no_load))
            lower=torch.maximum(-continuous,-stall*(1.+voltage_velocity/no_load))
            effort=torch.maximum(torch.minimum(effort,upper),lower)*self.motor_gain
            effort=torch.maximum(torch.minimum(effort,upper),lower)
            d.applied_torque.zero_();d.applied_torque[:,self.legs+self.wheels]=effort
            d.joint_pos_target[:,self.legs]=leg
            p.control.joint_f.zero_()
            wp.to_torch(p.control.joint_f).reshape(self.num_envs,-1)[:,self.vadr[self.legs+self.wheels]]=effort
            key=p.state.joint_q.ptr
            if self.physics_eager_warmed:
                if key not in self.physics_graphs:
                    with wp.ScopedCapture(device=self.device) as capture:
                        p.state.clear_forces()
                        p.solver.step(p.state,p.next_state,p.control,self.contacts,.0025,observables=self.observables)
                    self.physics_graphs[key]=capture.graph
                wp.capture_launch(self.physics_graphs[key])
            else:
                p.state.clear_forces()
                p.solver.step(p.state,p.next_state,p.control,self.contacts,.0025,observables=self.observables)
                self.physics_eager_warmed=True
            p.state,p.next_state=p.next_state,p.state
            self.physics_ticks+=1
            self.update_data()
            self.sensor.update(p.state,self.contacts,observables=self.observables)
            self.net_force.copy_(wp.to_torch(self.sensor.total_force).reshape(self.num_envs,31,3))
            self.top_force.zero_();self.ground_force.zero_()
            wp.launch(contact_reduction,dim=self.contacts.rigid_contact_max,inputs=[self.contacts.rigid_contact_count,
                self.contacts.rigid_contact_shape0,self.contacts.rigid_contact_shape1,
                self.contacts.rigid_contact_point0,self.contacts.rigid_contact_point1,
                self.contacts.rigid_contact_normal,self.observables.contact_f,self.model.shape_body,
                p.state.body_q,self.wheel_slots,self.model.body_world,
                wp.from_torch(self.top_force),wp.from_torch(self.ground_force)],device=self.device)
            if self.physics_ticks%2==0:
                self.contact_history[:,1:]=self.contact_history[:,:-1].clone()
                self.contact_history[:,0]=self.net_force
            if self.physics_ticks%4==0:
                self.sample_feedback()
            nonwheel=self.net_force[:,r._nonwheel_contact_link_idx].norm(dim=-1).amax(-1)
            self.acceptance.update_world(d.body_pos_w[:,self.wheel_bodies],d.body_quat_w[:,self.wheel_bodies],
                self.contract,self.scene.env_origins,self.top_force,self.ground_force,
                self.net_force[:,self.wheel_bodies],nonwheel,d.root_lin_vel_w,d.root_quat_w,
                torch.ones(self.num_envs,dtype=torch.bool,device=self.device))
            if self.physics_observer is not None:self.physics_observer(self)
        self.common_step_counter+=1;self.episode_length_buf+=1
        ground,wheels,far,far_hits,near,near_hits=self.scans()
        finite=torch.isfinite(d.joint_pos).all(-1)&torch.isfinite(d.joint_vel).all(-1)
        closure,mimic=self.closure_errors()
        hard=(closure>.01)|(mimic>.01)|~finite
        r.begin(applied,r.command,r.height_cmd,hard,~finite,self.episode_length_buf,
                self.contact_history,ground,wheels,far,far_hits,near,near_hits)
        terminated,timeout=r._get_dones()
        terminated|=hard;timeout&=~hard
        rewards=r.compute()
        self.terminal_snapshot=dict(root_pos=d.root_pos_w.clone(),root_quat=d.root_quat_w.clone(),
            wheels=d.body_pos_w[:,self.wheel_bodies].clone(),top_force=self.top_force.clone(),
            ground_force=self.ground_force.clone(),flight_id=self.acceptance.flight_id.clone(),
            upward_flight=self.acceptance.up.clone(),wholeclear=self.acceptance.wholeclear.clone(),
            landed_top=self.acceptance.landed_top.clone(),success=self.acceptance.success.clone(),
            closure_error=closure,mimic_error=mimic,terminated=terminated.clone(),time_out=timeout.clone(),
            leg_length=r.fudan_leg_length.clone(),leg_theta=r.fudan_leg_theta.clone(),
            motor_position=d.joint_pos[:,self.legs+self.wheels].clone(),
            motor_velocity=d.joint_vel[:,self.legs+self.wheels].clone(),
            motor_torque=d.applied_torque[:,self.legs+self.wheels].clone(),
            joint_target=d.joint_pos_target[:,self.legs].clone(),
            command=r.command.clone(),command_height=r.height_cmd.clone(),
            contact_force=self.net_force.clone())
        done=terminated|timeout;ids=done.nonzero().flatten()
        if len(ids):
            self.completed_episodes+=len(ids);self.completed_strict+=int(self.acceptance.success[ids].sum())
            self.reset(ids)
        self._last_observations=self.observations()
        return self._last_observations,rewards,done,dict(time_outs=timeout)

    def observations(self):
        r,d=self.reward,self.data
        r.finish_observation()
        r._cached_wheel_kinematics_valid=False
        r.command=self.command.command.clone()
        r.episode_length_buf.copy_(self.episode_length_buf)
        r._on_command_updated()
        height=r._get_effective_height_cmd().clone()[:,None]
        observed=r._get_observed_height()[:,None]
        r.wheel_relative_ground_heights=r._get_wheel_relative_ground_heights_raw()
        r.state_machine_manager.on_observation_step(r)
        mode=r._get_ctrl_mode_obs_raw()
        zero=torch.zeros(self.num_envs,2,device=self.device)
        def blocks(noisy):
            f=self.feedback
            return dict(command=r.command,height_cmd=height,
                root_ang_vel_b=f['base_ang_vel'] if noisy else d.root_ang_vel_b,
                projected_gravity_b=f['projected_gravity'] if noisy else d.projected_gravity_b,
                joint_pos=torch.cat((f['leg_pos'] if noisy else d.joint_pos[:,self.legs],zero),-1),
                joint_vel_leg=f['leg_vel'] if noisy else d.joint_vel[:,self.legs],
                joint_vel_wheel=f['wheel_vel'] if noisy else d.joint_vel[:,self.wheels],actions=r._actions)
        actor,critic=blocks(True),blocks(False)
        actor['ctrl_mode_obs']=mode
        critic.update(root_lin_vel_b=d.root_lin_vel_b,obs_height=observed,ctrl_mode_obs=mode)
        r.cache_raw_observations(actor,critic)
        def encode(values,stream):
            return torch.cat([observation_component(r.cfg,k,x,stream) for k,x in values.items()],-1)
        coeff=self._explicit_pd.component.coefficients()
        extra=dict(joint_stiffness=torch.cat((coeff['leg_kp'],zero),-1),
            joint_damping=torch.cat((coeff['leg_kd'],coeff['wheel_kd']),-1),
            joint_torque=d.applied_torque[:,self.legs+self.wheels],
            obs_delay_steps=self._feedback_delay_mild.delay[:,None].float().expand(-1,4),
            act_delay_steps=torch.stack([self._physics_action_delay.groups[k]['lag_steps'].float() for k in ('legs','wheels')],-1),
            wheel_body_lin_vel=quat_apply_inverse(d.root_quat_w[:,None].expand(-1,2,-1),d.body_lin_vel_w[:,self.wheel_bodies]).flatten(1),
            wheel_contact_state=(r._get_wheel_contact_force_peaks(self.contact_history)>r.cfg.desired_contact_force_threshold).float(),
            body_mass_scale=self.mass_factor[:,None],
            body_material=torch.stack((self.friction,self.friction,torch.zeros_like(self.friction)),-1).repeat(1,2))
        policy=encode(actor,'policy');critic=torch.cat((encode(critic,'critic'),encode(extra,'critic')),-1)
        assert policy.shape==(self.num_envs,35) and critic.shape==(self.num_envs,78)
        from tensordict import TensorDict
        return TensorDict(dict(policy=policy,critic=critic),batch_size=[self.num_envs])

    def get_observations(self):
        if self._last_observations is None:
            self._last_observations=self.observations()
        return self._last_observations

    def close(self):
        wp.synchronize()
