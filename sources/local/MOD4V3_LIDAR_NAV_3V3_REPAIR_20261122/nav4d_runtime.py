"""Shared raw-command 50 Hz policy path, Livox Mid-360 live 3D point-cloud fusion, and unchanged 400 Hz MuJoCo plant."""
from nav_common import HERE,DONOR,LOCAL,donor_imports,sha256,put
from pathlib import Path
import json
import math
import shutil
import numpy as np
import torch
import mujoco as mj
donor_imports()
from fsm_paths import E0_PATH,E0_BASE_PATH,JUMP_PATH
from manual_fsm_model import SymmetricE0
from jump_warp_model import JumpWarpPerceptionActor
from stair_warp_model import StairWarpExpert
from unified_policies import StairNav4DExpert,UnifiedJumpActor
from fsm_maps import reference
from jump360_scene import JumpPlant,geom_extent,geom_groups
from lidar_nav_planner import ElevationMap,WaypointFollower
from terrain_sensor_4d import TerrainSensor4D,EMPTY_NP,EMPTY_JUMP_NP
from mid360_sensor import LivoxMid360Sensor,Mid360Config
from mid360_stair_nav_detector import Mid360PointCloudNavDetector
from nav_maps import stage_scene

PPO_TO_NATIVE=np.array([0,2,1,3,4,5]);DT=.0025;SUBSTEPS=8

def prepare_weights():
    folder=HERE/'weights';folder.mkdir(exist_ok=True)
    for src,name in [(E0_PATH,'e0.pt'),(E0_BASE_PATH,'e0_base.pt'),(JUMP_PATH,'jump_r10_donor.pt'),
        (DONOR/'weights/E_stair_stage2_gate_final_fsm_r10c_model_015m.pt','stair_donor.pt')]:
        if not (folder/name).exists():shutil.copy2(src,folder/name)
    if not (HERE/'E0_CALIBRATION.json').exists():shutil.copy2(DONOR/'E0_CALIBRATION.json',HERE/'E0_CALIBRATION.json')

class Nav4DPolicy:
    def __init__(self,stair_checkpoint=None,jump_checkpoint=None):
        torch.set_num_threads(1);prepare_weights()
        self.e0=SymmetricE0().load_e0(torch.load(HERE/'weights/e0.pt',map_location='cpu',weights_only=False),
            torch.load(HERE/'weights/e0_base.pt',map_location='cpu',weights_only=False)).eval()
        self.e0.load_calibration(json.loads((HERE/'E0_CALIBRATION.json').read_text(encoding='utf-8')))
        self.stair_donor=torch.load(HERE/'weights/stair_donor.pt',map_location='cpu',weights_only=False)
        self.jump=UnifiedJumpActor(HERE/'weights/jump_r10_donor.pt').eval()
        candidate=HERE/'CANDIDATE_NAV4D.json'
        manifest=json.loads(candidate.read_text(encoding='utf-8')) if candidate.exists() else {}
        self.stair_checkpoint=Path(stair_checkpoint) if stair_checkpoint else (HERE/manifest['stair']['checkpoint'] if 'stair' in manifest else None)
        self.jump_checkpoint=Path(jump_checkpoint) if jump_checkpoint else (HERE/manifest['jump']['checkpoint'] if 'jump' in manifest else None)
        stair_sd=torch.load(self.stair_checkpoint,map_location='cpu',weights_only=False)['actor'] if self.stair_checkpoint is not None else None
        if stair_sd is not None and any(k.startswith('cond_mlp.') for k in stair_sd):
            has_hs=any(k.startswith('hs_delta.') for k in stair_sd)
            self.stair=StairWarpExpert(self.stair_donor,enable_hs_residual=has_hs).eval()
        else:
            self.stair=StairNav4DExpert(self.stair_donor).eval()
        if stair_sd is not None:self.stair.load_state_dict(stair_sd,strict=True)
        jump_sd=torch.load(self.jump_checkpoint,map_location='cpu',weights_only=False)['actor'] if self.jump_checkpoint is not None else None
        if jump_sd is not None and any(k.startswith('jump_delta.') for k in jump_sd):
            self.jump=JumpWarpPerceptionActor(HERE/'weights/jump_r10_donor.pt').eval()
            self.jump_is_perception=True
        else:
            self.jump=UnifiedJumpActor(HERE/'weights/jump_r10_donor.pt').eval()
            self.jump_is_perception=False
        if jump_sd is not None:self.jump.load_state_dict(jump_sd,strict=True)
        self.sha=sha256(self.stair_checkpoint or HERE/'weights/stair_donor.pt')
        self.assist=True;self.reset_history()

    def reset_history(self):
        self.history=None;self.stair_hold_ticks=0;self.jump_active=False;self.jump_fired=False
        self.jump_ticks=0;self.jump_pulse=0;self.jump_seen_air=False;self.landing_ticks=0
        self.jump_latched_g=None;self.jump_fire_dist=None
        self.last_mode=-100.;self.last_g=EMPTY_NP.copy();self.last_g_jump=EMPTY_JUMP_NP.copy();self.last_model_obs=None
        self.route={'e0':1.,'e1':0.,'e2':0.};self.jump_exit_timeout=False
    def request_jump(self):
        if self.jump_active:return False
        self.jump_active=True;self.jump_fired=False;self.jump_ticks=0;self.jump_pulse=0
        self.jump_seen_air=False;self.landing_ticks=0;self.jump_latched_g=None;self.jump_fire_dist=None;self.jump_exit_timeout=False
        return True

    @torch.inference_mode()
    def act(self,obs,g_step,ceiling,physical,key_held=False,g_jump=None):
        gj_raw=EMPTY_JUMP_NP.copy() if g_jump is None else np.asarray(g_jump,dtype=np.float32).copy()
        if not self.jump_active:self.jump_latched_g=None;self.jump_fire_dist=None
        raw_has_obs=bool(self.jump_is_perception and gj_raw[0]<=2.25 and (gj_raw[2]>.05 or (gj_raw[1]-gj_raw[0])>.20))
        if self.jump_active and raw_has_obs:
            self.jump_latched_g=gj_raw.copy()
        elif self.jump_active and self.jump_latched_g is not None and not raw_has_obs:
            # Keep obstacle context continuous once robot flies past the front/back edge until touchdown completes!
            span_l=max(.08,float(self.jump_latched_g[1]-self.jump_latched_g[0]))
            self.jump_latched_g=np.array([-.40,-.40+span_l,self.jump_latched_g[2],self.jump_latched_g[3]],dtype=np.float32)
        gj=self.jump_latched_g.copy() if (self.jump_active and self.jump_latched_g is not None) else gj_raw
        has_jump_obs=bool(self.jump_is_perception and (raw_has_obs or (self.jump_active and self.jump_latched_g is not None)))

        x=torch.as_tensor(np.asarray(obs,dtype=np.float32)).reshape(1,35).clone()
        v_runup_override=None
        if self.jump_active and not self.jump_fired:
            if has_jump_obs:
                # Pre-coil tall stance into 0.255m athletic crouch during armed runup so fire_ready uses coiled timing!
                x_coil_chk=x.clone();x_coil_chk[:,3]=min(float(x[0,3]),5.*.255)
                gj_t0=torch.as_tensor(gj,dtype=torch.float32).reshape(1,4)
                ready_t,v_run_t=self.jump.fire_ready(x_coil_chk,gj_t0)
                # Wait briefly if body is still tall (>0.315m) and obstacle is safely >0.74m ahead so legs pre-coil cleanly!
                body_still_tall=float(physical.get('body_height',.26))>.315 and float(gj[0])>.74
                if (bool(ready_t[0]) and not body_still_tall) or float(gj[0])<=.56 or self.jump_ticks>=85:
                    self.jump_fired=True;self.jump_pulse=26;self.jump_fire_dist=float(gj[0])
                else:
                    v_runup_override=float(v_run_t[0])
            else:
                self.jump_fired=True;self.jump_pulse=12;self.jump_fire_dist=None

        # On open flat ground, x[:,30] fires on tick 0; before an obstacle, x[:,30] stays 0 during runup and fires a clean 0->1 rising edge at d_sweet!
        x[:,30]=float((key_held and self.jump_fired) or self.jump_pulse>0)
        self.jump_pulse=max(0,self.jump_pulse-1)
        # Velocity-proportional Time-To-Contact (TTC) lookahead: 1.00 m at <=1.15 m/s, up to 2.00 m at 3.0 m/s!
        v_wheel_est=0.5*(float(x[0,20])+float(x[0,21]))*10.0*0.0625
        d_trig=min(2.00,1.00+0.55*max(0.0,v_wheel_est-1.15))
        step_ahead=bool(g_step[1]>.06 and g_step[0]<=d_trig)
        fwd_intent=float(x[0,0])>.12
        hold_len=32 if v_wheel_est<=1.50 else 38
        self.stair_hold_ticks=hold_len if (not self.jump_active and self.assist and step_ahead and fwd_intent) else max(0,self.stair_hold_ticks-1)
        if float(x[0,0])<-.05 or not self.assist or self.jump_active:self.stair_hold_ticks=0
        if not self.jump_active and not self.stair_hold_ticks and ceiling<.36:
            x[:,3]=min(float(x[0,3]),5.*.22)
        if self.history is None:self.history=x[:,None].repeat(1,12,1)
        else:self.history=torch.cat((self.history[:,1:],x[:,None]),1)
        signature=torch.cat((x,self.history.flatten(1)),1)
        if self.jump_active:
            self.jump_ticks+=1
            if not self.jump_fired:
                x_run=x.clone()
                if v_runup_override is not None:x_run[:,0]=v_runup_override
                x_run[:,3]=min(float(x_run[0,3]),5.*.255)
                action=self.e0(x_run);self.last_mode=-50.;self.route={'e0':0.,'e1':0.,'e2':1.}
            else:
                if self.jump_is_perception:
                    gj_t=torch.as_tensor(gj,dtype=torch.float32).reshape(1,4)
                    fd_t=None if self.jump_fire_dist is None else torch.tensor([self.jump_fire_dist],dtype=torch.float32)
                    action,mode=self.jump.action_and_phase(x,self.history.flatten(1),gj_t,fire_dist=fd_t)
                else:
                    action,mode=self.jump.core.action_and_phase(x,self.history.flatten(1))
                self.last_mode=float(mode[0])
                self.jump_seen_air |= bool(physical['airborne'])
                stable=bool(physical['stable']) and self.jump_seen_air
                self.landing_ticks=self.landing_ticks+1 if stable else 0
                self.route={'e0':0.,'e1':0.,'e2':1.}
                recent_key=bool(x[0,30]>.5 or self.history[:,:,30].amax()>.5)
                max_jticks=185 if has_jump_obs else 120
                if (self.landing_ticks>=10 and not recent_key) or self.jump_ticks>=max_jticks:
                    self.jump_exit_timeout=self.jump_ticks>=max_jticks and self.landing_ticks<10
                    self.jump_active=False;self.jump_fired=False;self.jump_latched_g=None;self.jump_fire_dist=None
        elif self.stair_hold_ticks>0:
            action=self.stair(torch.cat((signature,torch.as_tensor(g_step,dtype=torch.float32).reshape(1,4)),1))
            self.route={'e0':0.,'e1':1.,'e2':0.}
        else:
            action=self.e0(x);self.route={'e0':1.,'e1':0.,'e2':0.}
        self.last_g=np.array(g_step,copy=True);self.last_g_jump=np.array(gj,copy=True);self.last_model_obs=x[0].numpy().copy()
        return action.clamp(-6.,6.)[0].numpy().copy(),self.route.copy()

class Nav4DSimulation(reference.legacy.AutonomousMapSimulation):
    def __init__(self,policy,sensor_mode='mid360_fusion',use_pcd_prior=False):
        self.elevation=None;self.terrain_sensor=None;self.physics_observer=None
        self.sensor_mode=sensor_mode  # 'mid360_fusion' | 'mid360_online' | 'prior_only'
        self.use_pcd_prior=bool(use_pcd_prior)
        self.mid360_cfg=Mid360Config.from_json()
        self.mid360_sensor=LivoxMid360Sensor(self.mid360_cfg)
        self.mid360_detector=None
        self.raw_keys=set();self.last_g=EMPTY_NP.copy();self.last_g_jump=EMPTY_JUMP_NP.copy();self.jump_z_ref=None;self.ceiling=float('inf')
        self.profile=None;self.mode_latched=False;self.dr=None;self.follower=None;self.planned_path=[]
        self.nav_goal=None;self.nav_speed=1.;self.replan_count=0
        super().__init__(policy,policy.sha,show_viewer=False)
        self.max_vx=1.;self.max_wz=1.2;self.target_h=.28

    def set_sensor_mode(self,mode:str):
        assert mode in ('mid360_fusion','mid360_online','prior_only')
        self.sensor_mode=mode
        if self.elevation is not None:
            self.mid360_detector=Mid360PointCloudNavDetector(
                prior_map=None if mode=='mid360_online' else self.elevation,
                config=self.mid360_cfg,
                mode='online_pc' if mode=='mid360_online' else 'fusion',
            )
            if self.m is not None and self.d is not None:
                x,y,_=self.pose();self.mid360_detector.reset(x,y)
                self._warmup_mid360()

    def _tag_dynamic_obstacle_geoms(self):
        if self.m is None:return
        # Collect all body IDs belonging to our own robot subtree (`env.base_id`)
        robot_bodies={int(self.env.base_id)}
        changed=True
        while changed:
            changed=False
            for b in range(1,self.m.nbody):
                if int(self.m.body_parentid[b]) in robot_bodies and b not in robot_bodies:
                    robot_bodies.add(b);changed=True
        for g in range(self.m.ngeom):
            bid=int(self.m.geom_bodyid[g])
            if bid in robot_bodies:
                if self.m.geom_contype[g] or self.m.geom_conaffinity[g]:self.m.geom_group[g]=2
            elif (int(self.m.body_weldid[bid])!=0 or int(self.m.body_mocapid[bid])>=0) and (self.m.geom_contype[g] or self.m.geom_conaffinity[g]):
                # External movable body / enemy robot -> group 1 so LivoxMid360Sensor hits it!
                self.m.geom_group[g]=1

    def _warmup_mid360(self):
        if self.sensor_mode=='prior_only' or self.mid360_detector is None or self.m is None:return
        z_foot=self.ground_z(float(self.d.qpos[0]),float(self.d.qpos[1]))
        R_wb=self.d.xmat[self.env.base_id].reshape(3,3)
        for _ in range(3):
            sc=self.mid360_sensor.scan(self.m,self.d,self.d.qpos[:3],R_wb,n_rays=4000)
            self.mid360_detector.ingest_lidar_scan(sc['points_lidar'],self.d.qpos[:3],R_wb,z_foot=z_foot)

    def load_scene(self,course,spawn_idx=0,height=.28,extra_xml_mutator=None):
        meta=stage_scene(course)
        pcd_npz=HERE/'maps/mid360_prior'/f'{course}_pcd_nav25d.npz'
        map_key=f'mid360:{course}' if (self.use_pcd_prior and pcd_npz.is_file()) else course
        self.elevation=ElevationMap(map_key);self.terrain_sensor=TerrainSensor4D(self.elevation)
        self.mid360_detector=Mid360PointCloudNavDetector(
            prior_map=None if self.sensor_mode=='mid360_online' else self.elevation,
            config=self.mid360_cfg,
            mode='online_pc' if self.sensor_mode=='mid360_online' else 'fusion',
        )
        self._ray_grp=np.array([0,0,0,1,0,0],np.uint8)
        if extra_xml_mutator is not None:
            meta=extra_xml_mutator(meta)
        self.load_map(meta,spawn_idx)
        self._tag_dynamic_obstacle_geoms()
        self.groups=geom_groups(self.m,self.env.base_id)
        self.measured_gids=np.array(sum((list(v) for v in self.groups),[]))
        self.sizes=self.m.geom_size[self.measured_gids].copy()
        self.env.default_leg_q=self.env.default_q[self.env.leg_ids].numpy().astype(np.float32)
        self.env.kp_scale=np.ones(4,np.float32);self.env.kd_scale=np.ones(4,np.float32)
        self.env.kv_scale=np.ones(2,np.float32);self.env.effort_scale=np.ones(6,np.float32)
        self.target_h=height;self.reset_at_spawn(spawn_idx)
        return meta

    def ground_z(self,x,y,z_top=None):
        if self.elevation is not None:
            height=float(self.elevation.sample(x,y))
            if np.isfinite(height):return height
        if self.m is None:return 0.
        group=self.m.geom_group.copy()
        self.m.geom_group[self.m.body_weldid[self.m.geom_bodyid]!=0]=2
        dist=mj.mj_ray(self.m,self.d,np.array([x,y,float(z_top or 4.)]),np.array([0.,0.,-1.]),
                       np.array([0,0,0,1,0,0],np.uint8),True,-1,self._ray_gid)
        self.m.geom_group[:]=group
        return float((z_top or 4.)-dist) if dist>=0 else 0.

    def reset_at_spawn(self,spawn_idx=None):
        height=self.target_h
        spawn=super().reset_at_spawn(spawn_idx)
        self.target_h=height
        length=float(np.clip(height-.0625,.14,.35))
        fit=self.ik.fit(np.sqrt(length*length+self.ik.lateral_offset**2),0.)['qpos']
        x,y,yaw=float(spawn['x']),float(spawn['y']),math.radians(float(spawn['yaw_deg']))
        self.d.qpos[:]=fit;self.d.qpos[:3]=x,y,self.ground_z(x,y)+height+.002
        self.d.qpos[3:7]=[math.cos(yaw/2),0.,0.,math.sin(yaw/2)];self.d.qvel[:]=0.
        mj.mj_forward(self.m,self.d)
        self.raw_keys=set();self.follower=None;self.planned_path=[];self.nav_goal=None;self.replan_count=0;self.jump_z_ref=None
        self.mid360_sensor.reset()
        if self.mid360_detector is not None:
            self.mid360_detector.reset(x,y)
            self._warmup_mid360()
        return spawn

    def pose(self):
        r=self.d.xmat[self.env.base_id].reshape(3,3)
        return float(self.d.qpos[0]),float(self.d.qpos[1]),math.atan2(float(r[1,0]),float(r[0,0]))

    def measure(self):
        r=self.d.xmat[self.env.base_id].reshape(3,3)
        pitch=math.asin(float(np.clip(-r[2,0],-1,1)));roll=math.atan2(float(r[2,1]),float(r[2,2]))
        points=self.d.geom_xpos[self.measured_gids]
        frames=self.d.geom_xmat[self.measured_gids].reshape(-1,3,3)
        lowest=points[:,2]-geom_extent(self.sizes,frames[:,2,:],10)
        loads=np.zeros(2);ground_contacts=0.;contact_force=np.zeros(6)
        tire_index={int(g):i for i,g in enumerate(self.tire_gids)}
        for i in range(self.d.ncon):
            c=self.d.contact[i];a,b=map(int,c.geom)
            if (self.m.body_weldid[self.m.geom_bodyid[a]]!=0)==(self.m.body_weldid[self.m.geom_bodyid[b]]!=0):continue
            mj.mj_contactForce(self.m,self.d,i,contact_force)
            world=c.frame.reshape(3,3).T@contact_force[:3]
            ground_contacts+=float(np.linalg.norm(world))
            if a in tire_index:loads[tire_index[a]]-=world[2]
            if b in tire_index:loads[tire_index[b]]+=world[2]
        ground=self.ground_z(float(self.d.qpos[0]),float(self.d.qpos[1]))
        vx=float(np.dot(self.d.qvel[:2],r[:2,0])/max(.01,np.linalg.norm(r[:2,0])))
        airborne=ground_contacts<1. and float(lowest.min())-ground>.006
        stable=loads.min()>5. and abs(pitch)<math.radians(10.) and abs(roll)<math.radians(8.) and abs(self.d.qvel[2])<.35 and np.linalg.norm(self.d.qvel[3:5])<.8
        return dict(pitch=pitch,roll=roll,vx=vx,lowest=float(lowest.min()),tire_low=float(lowest[:2].min()),
                    wheel_low=lowest[:2].copy(),wheel_pos=points[:2].copy(),
                    guide_low=float(lowest[2:10].min()),ground=ground,loads=loads,airborne=airborne,stable=stable,
                    closure_mm=self.closure_mm,body_height=float(self.d.qpos[2])-ground)

    def request_jump(self):return self.unified.request_jump()
    def navigate_to(self,x,y,speed=1.):
        px,py,_=self.pose();self.nav_goal=(float(x),float(y));self.nav_speed=float(speed)
        dyn_blk=self.mid360_detector.dyn_blocked if (self.mid360_detector is not None and self.mid360_detector.last_dyn_cells_count>0) else None
        self.planned_path=self.elevation.plan((px,py),(x,y),dynamic_blocked=dyn_blk)
        self.follower=WaypointFollower(self.planned_path,speed);return self.planned_path

    def step(self,pressed,command=None):
        if self.paused:return
        keys=set(pressed);rising=keys-self.raw_keys
        if ('space' in rising or 'j' in rising):self.request_jump()
        if 't' in rising:self.unified.assist=not self.unified.assist
        if 'c' in rising:self.mode_latched=not self.mode_latched
        self.raw_keys=keys
        x,y,yaw=self.pose()
        meas=self.measure()
        z_foot_est=float(meas['tire_low']) if not meas['airborne'] else self.ground_z(x,y)

        # Live Livox Mid-360 3D scan & point-cloud stair/hurdle/dynamic-obstacle update
        if self.sensor_mode in ('mid360_fusion','mid360_online') and self.mid360_detector is not None:
            if self.steps%2==0:
                R_wb=self.d.xmat[self.env.base_id].reshape(3,3)
                sc=self.mid360_sensor.scan(self.m,self.d,self.d.qpos[:3],R_wb,n_rays=3200)
                self.mid360_detector.ingest_lidar_scan(sc['points_lidar'],self.d.qpos[:3],R_wb,z_foot=z_foot_est)
            # Live dynamic-obstacle A* replanning during autonomous navigation!
            if self.follower is not None and not self.follower.done and self.nav_goal is not None and self.steps%8==0:
                if self.mid360_detector.is_path_blocked(self.planned_path,x,y):
                    try:
                        self.planned_path=self.elevation.plan((x,y),self.nav_goal,dynamic_blocked=self.mid360_detector.dyn_blocked)
                        self.follower=WaypointFollower(self.planned_path,self.nav_speed)
                        self.replan_count+=1
                    except ValueError:
                        pass

        if command is None:
            manual=bool(keys&{'w','a','s','d'})
            if manual:self.follower=None;self.nav_goal=None
            if self.follower is not None:goal_vx,goal_wz=self.follower.command(x,y,yaw)
            else:goal_vx,goal_wz=((int('w' in keys)-int('s' in keys))*self.max_vx,(int('a' in keys)-int('d' in keys))*self.max_wz)
            self.cmd_vx+=(float(goal_vx)-self.cmd_vx)/10.
            self.cmd_wz+=(float(goal_wz)-self.cmd_wz)/8.
            if abs(self.cmd_vx)<1e-3 and goal_vx==0.:self.cmd_vx=0.
            if abs(self.cmd_wz)<1e-3 and goal_wz==0.:self.cmd_wz=0.
        else:
            # Explicit evaluation commands pass straight through unsmoothed for worst-case stress testing.
            self.cmd_vx,self.cmd_wz=map(float,command)
        self.target_h=float(np.clip(self.target_h+.0024*(int('e' in keys)-int('q' in keys)),.20,.42))
        if not self.unified.jump_active:self.jump_z_ref=None
        elif self.jump_z_ref is None:self.jump_z_ref=z_foot_est

        if self.sensor_mode in ('mid360_fusion','mid360_online') and self.mid360_detector is not None:
            self.last_g,self.ceiling,self.profile=self.mid360_detector.sample(x,y,yaw,z_foot=z_foot_est)
            self.last_g_jump=self.mid360_detector.sample_jump(x,y,yaw,z_ref=self.jump_z_ref,z_foot=z_foot_est)
        elif self.terrain_sensor is not None:
            self.last_g,self.ceiling,self.profile=self.terrain_sensor.sample(x,y,yaw)
            self.last_g_jump=self.terrain_sensor.sample_jump(x,y,yaw,z_ref=self.jump_z_ref)
        else:
            self.last_g=EMPTY_NP.copy();self.last_g_jump=EMPTY_JUMP_NP.copy();self.ceiling=float('inf')
            if (self.mode_latched or 'v' in keys) and meas['loads'].sum()>8. and abs(meas['pitch'])>.06:
                self.last_g=np.array([.08,.20,1.6,0.],np.float32)

        obs=self._observe(False)
        if self.dr is not None:obs=self.dr.observe(obs)
        self.last_obs=obs.copy()
        action,self.route=self.unified.act(obs,self.last_g,self.ceiling,meas,bool(keys&{'space','j'}),g_jump=self.last_g_jump)
        if not np.isfinite(action).all():raise FloatingPointError('Nonfinite neural action')
        native=torch.as_tensor(action[PPO_TO_NATIVE]).reshape(1,6)
        for sub in range(SUBSTEPS):
            if self.route['e2']:
                tau=JumpPlant._compute_motor_torque(self.env,native.numpy()[0])
            else:tau=self.env._torque(native).numpy().reshape(-1)
            if sub%4==0:self.d.ctrl[self.env.act_ids[:4]]=tau[:4]
            self.d.ctrl[self.env.act_ids[4:]]=tau[4:]
            mj.mj_step(self.m,self.d)
            if self.physics_observer is not None:self.physics_observer(self)
        self.prev_a=action.copy();self.steps+=1
        self.closure_mm=1000.*max(float(np.linalg.norm(self.d.site_xpos[a]-self.d.site_xpos[b])) for a,b in self.pairs)
        if not np.isfinite(self.d.qpos).all():raise FloatingPointError('Nonfinite plant state')
