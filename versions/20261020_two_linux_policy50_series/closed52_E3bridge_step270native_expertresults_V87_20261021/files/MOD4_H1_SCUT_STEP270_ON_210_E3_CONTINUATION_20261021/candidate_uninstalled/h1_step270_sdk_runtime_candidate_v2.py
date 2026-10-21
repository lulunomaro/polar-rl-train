"""New-task SDK candidate; original H1 runtime/physics files remain unchanged.

Static 270mm vertical step, standing preparation, public4 forward request only.
All original closures, mimic, hardware, action/feedback clocks and costs remain.
This file is not a qualification receipt and performs no learning by itself.
"""
from pathlib import Path
import hashlib,json,os
import numpy as np
import torch
from step270_triangle_geometry_cpu import generate
from step270_goal_and_scut_rates_candidate import Step270Events
from scut_ballistic_reference_uninstalled import reference
from h1_takeoff_progress_environment_v2 import H1FullstateEnv as OriginalH1Env,tensor
from e1_rough_ground import AuthoredTerrainRaycast
import mod4_task as task

GEOMETRY=dict(height=.270,edge_x=.35,depth=.8,width=1.2)
SETTINGS={};SPAWN={}

def spawn_step270(prim_path,cfg,translation=None,orientation=None,**kwargs):
    from pxr import UsdGeom,UsdPhysics
    from isaaclab import cloner
    from isaaclab.sim import get_current_stage,define_collision_properties,bind_physics_material
    stage=get_current_stage();origins,_=cloner.grid_transforms(SETTINGS['num_envs'],SETTINGS['spacing'],device='cpu')
    vertices,faces,groups=generate(origins[:,:2].numpy(),**GEOMETRY)
    root=UsdGeom.Xform.Define(stage,prim_path).GetPrim();material=prim_path+'/physicsMaterial'
    if cfg.physics_material is not None:cfg.physics_material.func(material,cfg.physics_material)
    # Preserve every authored triangle, with the already used 25k-face cooking bound.
    for first in range(0,len(faces),25000):
        block=faces[first:first+25000];ids,inverse=np.unique(block,return_inverse=True)
        path=prim_path+'/part'+str(first//25000).zfill(4);mesh=UsdGeom.Mesh.Define(stage,path)
        mesh.CreatePointsAttr().Set(vertices[ids].tolist());mesh.CreateFaceVertexCountsAttr().Set([3]*len(block));mesh.CreateFaceVertexIndicesAttr().Set(inverse.tolist());mesh.CreateSubdivisionSchemeAttr().Set('none');mesh.CreateOrientationAttr().Set('rightHanded')
        UsdPhysics.CollisionAPI.Apply(mesh.GetPrim());UsdPhysics.MeshCollisionAPI.Apply(mesh.GetPrim()).CreateApproximationAttr().Set('none')
        if cfg.collision_props is not None:define_collision_properties(path,cfg.collision_props,stage=stage)
        if cfg.physics_material is not None:bind_physics_material(path,material,stage=stage)
    SPAWN.update(origins=origins.numpy(),groups=groups,ordered_triangle_f32_SHA=hashlib.sha256(vertices[faces].astype('<f4').tobytes()).hexdigest(),triangles=len(faces),material_path=material)
    return root

def configure_scene(cfg):
    cfg.scene.env_spacing=max(2.5,float(cfg.scene.env_spacing));SETTINGS.update(num_envs=cfg.scene.num_envs,spacing=cfg.scene.env_spacing)
    cfg.scene.ground.spawn.func=spawn_step270;cfg.scene.ground.init_state.pos=(0.,0.,0.)
    cfg.scene.wheel_contact_scut.filter_prim_paths_expr=[]
    cfg.sim.enable_scene_query_support=True;cfg.sim.physics.enable_scene_query_support=True
    return cfg

def mesh_query(env):
    if not hasattr(env,'_step270_ray'):env._step270_ray=AuthoredTerrainRaycast(env.sim.stage,env.device)
    return env._step270_ray

def ground_height(env):
    r=env.scene['robot'];points=tensor(r.data.root_pos_w)[:,None,:].clone();points[:,:,2]+=1.
    q=mesh_query(env).cast(points.contiguous(),4.)
    if not q['hit'].all() or not torch.isfinite(q['height']).all() or not (q['normal'][...,2]>0).all():raise RuntimeError('Step270 actual terrain query missing/invalid; no flat fallback')
    env._mod4_ground_z=q['height'][:,0];return env._mod4_ground_z

def wheel_bounds(env):
    robot=env.scene['robot'];pos=tensor(robot.data.body_pos_w);quat=tensor(robot.data.body_quat_w);lows=[];highs=[]
    for indices in env.h1_wheel_shapes:
        low=[];high=[]
        for si in indices:
            s=env.h1_shapes[si];q=quat[:,s['body_index']];x,y,z,w=q.unbind(-1)
            R=torch.stack((torch.stack((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)),-1),torch.stack((2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)),-1),torch.stack((2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)),-1)),-2)
            L=torch.tensor(s['linear_body_from_shape'],device=env.device,dtype=pos.dtype);t=torch.tensor(s['origin_body_m'],device=env.device,dtype=pos.dtype);row=R@L;center=pos[:,s['body_index']]+(R@t[:,None]).squeeze(-1)
            if s['type'] in ('Cylinder','Capsule'):
                axis=row[:,:,s['axis']].abs();norm2=row.square().sum(-1);radial=(norm2-axis.square()).clamp_min(0).sqrt();extent=axis*s['height']*.5+(norm2.sqrt() if s['type']=='Capsule' else radial)*s['radius'];a=center-extent;b=center+extent
            elif s['type']=='Cube':extent=row.abs().sum(-1)*s['size']*.5;a=center-extent;b=center+extent
            elif s['type']=='Mesh':
                points=torch.tensor(s['points'],device=env.device,dtype=pos.dtype);v=row@points.T;a=center+v.amin(-1);b=center+v.amax(-1)
            else:raise ValueError('Unqualified wheel collider '+s['type'])
            low.append(a);high.append(b)
        lows.append(torch.stack(low).amin(0));highs.append(torch.stack(high).amax(0))
    return torch.stack(lows,1),torch.stack(highs,1)

class Step270Phase:
    def __init__(self,env):
        self.env=env;self.n=env.num_envs;self.device=env.device;self.goal=Step270Events(self.n,self.device);self.goal.was_ready=torch.zeros(self.n,device=self.device,dtype=torch.bool)
        for k in ('age_control','takeoff_count','landing_count','recovery_count'):setattr(self,k,torch.zeros(self.n,device=self.device,dtype=torch.long))
        for k in ('request_for_action','ready','previous_request'):setattr(self,k,torch.zeros(self.n,device=self.device,dtype=torch.bool))
        for k in ('event_control','progress_control','yaw_reference','peak','release_reference_vz'):setattr(self,k,torch.zeros(self.n,device=self.device))
        self.target_body_peak=torch.full((self.n,),.5,device=self.device);self.previous_front=torch.full((self.n,2),-1e6,device=self.device);self.crossed=torch.zeros((self.n,2),device=self.device,dtype=torch.bool);self.last_measured={}
    def __getattr__(self,k):
        if k=='recovered':return self.goal.success
        return getattr(self.goal,k)
    def public_request(self):return (self.age_control>=100)&(self.age_control<180)
    def public_mode(self):return torch.where(self.public_request(),4,0).long()
    def begin_control(self):self.request_for_action.copy_(self.public_request());self.event_control.zero_();self.progress_control.zero_()
    def finish_control_before_selected_reset(self):self.age_control+=1
    def reset(self,ids):
        for x in vars(self).values():
            if torch.is_tensor(x):x[ids]=0
        self.previous_front[ids]=-1e6;self.target_body_peak[ids]=.5
        for x in vars(self.goal).values():
            if torch.is_tensor(x):x[ids]=0
    def physical(self,**kw):
        env=self.env;r=env.scene['robot'];root=tensor(r.data.root_state_w);lo,hi=wheel_bounds(env);orig=env.scene.env_origins
        edge=orig[:,0,None]+GEOMETRY['edge_x'];inside=(lo[:,:,0]>=edge)&(hi[:,:,0]<=edge+GEOMETRY['depth'])&(lo[:,:,1]>=orig[:,1,None]-.6)&(hi[:,:,1]<=orig[:,1,None]+.6)
        starts=tensor(r.data.body_pos_w)[:,[env.h1_body_names.index(n) for n in ('left_wheel','right_wheel')]].clone();starts[:,:,2]+=1.;q=mesh_query(env).cast(starts.contiguous(),4.)
        if not q['hit'].all() or not torch.isfinite(q['height']).all():raise RuntimeError('Missing actual wheel terrain query')
        top=(q['face_id'][:,:,None]==env.step270_top_faces[:,None,:]).any(-1)
        fresh=self.request_for_action&~self.previous_request;self.yaw_reference=torch.where(fresh,kw['yaw'],self.yaw_reference);self.previous_request.copy_(self.request_for_action)
        airborne=(kw['wheel_N']<=1).all(-1)&(lo[:,:,2]>.005).all(-1)&(kw['all_min_clear_m']>0)&(kw['nonwheel_max_N']<=1)
        crossing=(self.previous_front<edge)&(hi[:,:,0]>=edge);self.crossed|=crossing&airborne[:,None]&(lo[:,:,2]>=.27)&self.goal.launched[:,None];self.previous_front=hi[:,:,0].clone()
        prepared=(kw['wheel_N']>1).all(-1)&(kw['nonwheel_max_N']<=1)&(kw['all_min_clear_m']>=-.001)&(kw['root_vz'].abs()<=.2)&(kw['root_planar_speed']<=.2)&(kw['roll'].abs()<.2617993877991494)&(kw['pitch'].abs()<.2617993877991494)
        out=self.goal.physical(request=self.request_for_action,ground_ready=prepared,nonwheel_clean=(kw['nonwheel_max_N']<=1)&torch.where((kw['wheel_N']<=1).all(-1),kw['all_min_clear_m']>0,kw['all_min_clear_m']>=-.001),known_integrity=torch.ones(self.n,device=self.device,dtype=torch.bool),wheel_N=kw['wheel_N'],wheel_bottom_world_z=lo[:,:,2],wheel_contact_platform=top,wheel_footprints_inside_top=inside,both_wheel_edge_crossed=self.crossed.all(-1),root_vz=kw['root_vz'],planar_speed=kw['root_planar_speed'],roll=kw['roll'],pitch=kw['pitch'],heading_error=kw['yaw']-self.yaw_reference)
        self.ready=self.goal.ready_ticks>=80;self.takeoff_count+=out['takeoff'];self.landing_count+=out['landing'];self.recovery_count+=out['recovery'];self.peak=torch.maximum(self.peak,torch.where(airborne,lo[:,:,2].amin(-1),0))
        delta=out['wheel_clearance_progress_delta']+out['takeoff'].float()+2*out['landing'].float()+3*out['recovery'].float();self.event_control+=delta
        measured_peak=.27+(root[:,2]-lo[:,:,2].amin(-1)).clamp_min(0)+.02
        if (fresh & (measured_peak<=.31)).any():raise RuntimeError('Measured wheel/body offset cannot qualify SCUT release reference')
        self.target_body_peak=torch.where(fresh,measured_peak,self.target_body_peak);peak_body=self.target_body_peak
        _,refvel,_=reference(elapsed=(self.age_control-100).clamp_min(0).float()*.01,peak_height=peak_body,push_start_height=.20,release_height=.31)
        self.release_reference_vz=refvel.clamp_min(0)
        self.last_measured=dict(step_wheel_min=lo.clone(),step_wheel_max=hi.clone(),step_query_height=q['height'].clone(),step_query_face=q['face_id'].clone(),step_platform_contact=top.clone(),step_footprint_inside=inside.clone(),step_first_cross_clear=self.crossed.clone(),step_stable_ticks=self.goal.stable_ticks.clone(),step_goal_success=self.goal.success.clone())
        return dict(takeoff=out['takeoff'],landing=out['landing'],recovery=out['recovery'],event_delta=delta,prepared=prepared,air=airborne,prelaunch_proxy_delta=torch.zeros_like(delta),prelaunch_proxy_gate=torch.zeros_like(airborne))
    def state_dict(self):
        return dict(version=270,num_envs=self.n,geometry=GEOMETRY,tensors={k:v.clone() for k,v in vars(self).items() if torch.is_tensor(v)},goal={k:v.clone() for k,v in vars(self.goal).items() if torch.is_tensor(v)})
    def load_state_dict(self,s):
        assert s['version']==270 and s['num_envs']==self.n and s['geometry']==GEOMETRY
        for name,values in (('tensors',self),('goal',self.goal)):
            for k,v in s[name].items():
                old=getattr(values,k);assert old.shape==v.shape and old.dtype==v.dtype;old.copy_(v.to(old.device))

class H1Step270Env(OriginalH1Env):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.h1_phase=Step270Phase(self)
        assert np.array_equal(SPAWN['origins'],self.scene.env_origins.detach().cpu().numpy())
        ray=mesh_query(self);sha=hashlib.sha256(ray.geometry.vertices.astype('<f4')[ray.geometry.faces].tobytes()).hexdigest();assert sha==SPAWN['ordered_triangle_f32_SHA']
        self.step270_top_faces=torch.tensor([g['top_faces'] for g in SPAWN['groups']],device=self.device)
        old=self.scene.update
        def update(dt):
            old(dt)
            if self.h1_stepping and self.h1_capture and self.h1_physical_rows:self.h1_physical_rows[-1].update(self.h1_phase.last_measured)
        self.scene.update=update;self._h1_publish_external_request()
        self.step270_geometry_receipt=dict(geometry=GEOMETRY,SDK_origins_literal_exact=True,actual_stage_ordered_triangle_SHA=sha,triangles=SPAWN['triangles'],material_inherited_from_original_ground=True,authored_geometry_not_cooked_manifold_certification=True)
    def _h1_publish_external_request(self):
        if self.h1_phase is not None:
            self._mod4_mode_bit=self.h1_phase.public_mode();cmd=self.command_manager.get_term('twist');cmd.set_manual_evaluation_mode();cmd.vel_command_b.zero_();cmd.vel_command_b[:,0]=self.h1_phase.public_request().float()*.8

def step_rate(env,name):
    p=getattr(env,'h1_phase',None)
    if not isinstance(p,Step270Phase):return torch.zeros(env.num_envs,device=env.device)
    root=tensor(env.scene['robot'].data.root_state_w)
    if name=='release_shortfall':return (p.request_for_action&p.attempt&~p.launched).float()*(p.release_reference_vz-root[:,9]).clamp_min(0)
    if name=='landing_yaw_rate':return p.landed.float()*tensor(env.scene['robot'].data.root_ang_vel_b)[:,2].square()
    if name=='landing_planar_stop':return p.landed.float()*root[:,7:9].square().sum(-1)
    raise ValueError(name)

def configure_rewards(cfg,original):
    original(cfg)
    from isaaclab.managers import RewardTermCfg
    cfg.rewards.h1_prelaunch_progress.weight=0.
    for name in ('flight_vz','flight','takeoff_extend'):getattr(cfg.rewards,'h1_scut_fudan_'+name).weight=0.
    for name,weight in [('release_shortfall',-2.),('landing_yaw_rate',-1.),('landing_planar_stop',-2.)]:setattr(cfg.rewards,'h1_step270_'+name,RewardTermCfg(func=step_rate,weight=weight,params={'name':name}))
    task.ground_height=ground_height
    return configure_scene(cfg)
