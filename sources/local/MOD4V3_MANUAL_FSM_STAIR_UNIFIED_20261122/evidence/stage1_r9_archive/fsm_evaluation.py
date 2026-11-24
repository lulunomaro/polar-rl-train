"""Independent 400 Hz measurements. Privileged geometry is confined to this file."""
import math
from pathlib import Path
import numpy as np
import mujoco as mj
import torch
from fsm_paths import HERE
from fsm_io import put
from fsm_maps import reference, metadata
from manual_fsm_runtime import ManualPolicy, ManualSimulation, DT, SUBSTEPS
from manual_fsm_core import Phase

class ContactJudge(reference.StrictJudge):
    def __init__(self, sim, case, yaw, direction, ground):
        course = case['course']
        if course == 'oblique_20_negative':
            reference.LEVELS[course] = (.20,)
        if course.startswith('platform_'):
            reference.LEVELS[course] = (int(course.split('_')[1])*.001,)
        super().__init__(sim, case, yaw, direction, ground)
        self.physics_tracks = np.zeros_like(self.track)
        self.epoch=float(sim.d.time)
        self.physics_best = np.zeros_like(self.track)
        self.e0_tracks=np.zeros_like(self.track)
        self.e0_best=np.zeros_like(self.track)
        self.crossed = np.zeros(len(self.levels), dtype=bool)
        self.first_face_time = None
        self.first_face_geom = None
        self.first_climb_time = None
        self.physics_records = []
        self.control_records = []
        self.final_deck_streak=0
        self.final_deck_best=0
        self.final_deck_crossed=False
        self._robot_gids = []
        for gid in range(sim.m.ngeom):
            body = sim.m.geom_bodyid[gid]
            while body and body != sim.env.base_id:
                body = sim.m.body_parentid[body]
            if body == sim.env.base_id and sim.m.geom_contype[gid]:
                self._robot_gids.append(gid)

    def edge(self, xy):
        if self.course in reference.AA:
            from fsm_geometry import rm27_profile
            floor,offset,lip=rm27_profile('west' in self.course,aa=True)
            return np.clip(offset+.70*xy[:,1],floor,lip-.31),np.full(len(xy),lip)
        if self.course == 'oblique_20_negative':
            return 1.+reference.oblique_edge(xy[:, 1], -1), np.full(len(xy), 99.)
        if self.course.startswith('platform_'):
            return np.full(len(xy), 3.3), np.full(len(xy), 99.)
        return super().edge(xy)

    def front_gap(self):
        """Exact primitive supports (mesh bound is conservative), evaluation only."""
        m, d = self.sim.m, self.sim.d
        positions = d.geom_xpos[self._robot_gids]
        first, _ = self.edge(positions[:, :2])
        radii = []
        for gid in self._robot_gids:
            axes = d.geom_xmat[gid].reshape(3, 3)[0]
            size = m.geom_size[gid]
            kind = m.geom_type[gid]
            if kind == mj.mjtGeom.mjGEOM_CYLINDER:
                extent = size[0]*np.sqrt(max(0., 1.-axes[2]**2))+size[1]*abs(axes[2])
            elif kind == mj.mjtGeom.mjGEOM_CAPSULE:
                extent = size[0]+size[1]*abs(axes[2])
            elif kind == mj.mjtGeom.mjGEOM_BOX:
                extent = np.abs(axes)@size
            elif kind == mj.mjtGeom.mjGEOM_SPHERE:
                extent = size[0]
            else:
                extent = m.geom_rbound[gid]
            radii.append(extent)
        return float(np.min(first-self.progress(positions[:, :2])-radii))

    def observe_fsm(self, sim):
        p = sim.unified
        self.weights = np.array([sim.route['e0'], 0., sim.route['e1'], sim.route['e2']])
        super().observe(sim.cmd_vx, 0.)
        row = self.trace[-1]
        forces = np.array(row[21:25])[:2*len(self.physics_tracks)].reshape(-1, 2)
        phase=int(p.fsm.phase[0])
        recovered=phase in (Phase.CRUISE_E0,Phase.STAIR_ARMED_APPROACH,Phase.DECK_SETTLE)
        good = (forces > 5.).all(1)
        self.physics_tracks = np.where(good, self.physics_tracks+1, 0)
        self.physics_best = np.maximum(self.physics_best, self.physics_tracks)
        self.e0_tracks=np.where(good & recovered,self.e0_tracks+1,0)
        self.e0_best=np.maximum(self.e0_best,self.e0_tracks)
        if self.levels:
            wheels = sim.d.geom_xpos[sim.tire_gids]
            edge, lip = self.edge(wheels[:, :2])
            progress = self.progress(wheels[:, :2])
            for k in range(len(self.levels)):
                self.crossed[k] |= bool((progress > (edge if k == 0 else lip)).all())
            if len(self.levels)>1:
                # Crest support alone is insufficient: both main wheels must
                # reach the lower final deck after the 150 mm crest strip.
                on_final=(progress>lip+.175).all()
                deck_load=np.zeros(2)
                for index in range(sim.d.ncon):
                    ct=sim.d.contact[index];a,b=map(int,ct.geom)
                    if a in self.terrain and b in self.tires:robot,sign=b,1.
                    elif b in self.terrain and a in self.tires:robot,sign=a,-1.
                    else:continue
                    mj.mj_contactForce(sim.m,sim.d,index,self.force_buffer)
                    z=ct.pos[2]-self.ground
                    if abs(z-self.deck_top)<.02:
                        deck_load[self.robot_side[robot]]+=max(0.,sign*self.force_buffer[0]*ct.frame[2])
                loaded=bool(on_final and recovered and (deck_load>5.).all())
                self.final_deck_streak=self.final_deck_streak+1 if loaded else 0
                self.final_deck_best=max(self.final_deck_best,self.final_deck_streak)
                self.final_deck_crossed |= bool(on_final)
        contact=False
        if self.levels:
            for index in range(sim.d.ncon):
                ct=sim.d.contact[index];a,b=map(int,ct.geom)
                if a in self.terrain and b in self._robot_gids:robot,sign=b,1.
                elif b in self.terrain and a in self._robot_gids:robot,sign=a,-1.
                else:continue
                normal=sign*ct.frame[:3]
                if self.direction*normal[0]>=-.6:continue
                mj.mj_contactForce(sim.m,sim.d,index,self.force_buffer)
                if self.force_buffer[0]<=5.:continue
                progress=self.progress(ct.pos[:2]);edges=self.edge(ct.pos[None,:2])
                for level,top in enumerate(self.levels):
                    if abs(progress-float(edges[min(level,1)][0]))<.04 and ct.pos[2]-self.ground<top+.005:
                        contact=True
                        if self.first_face_time is None:self.first_face_geom=sim.m.geom(robot).name
        if contact and self.first_face_time is None:
            self.first_face_time = float(sim.d.time)
        if sim.route['e1'] == 1. and self.first_climb_time is None:
            self.first_climb_time = float(sim.d.time-DT)
        local_ground=sim.ground_z(*sim.d.qpos[:2]) if self.course=='rough_L9' else self.ground
        self.physics_records.append((float(sim.d.time), phase, sim.route['e1'], self.front_gap(),
                                     float(sim.d.qpos[2]-self.ground), float(contact),
                                     float(sim.d.qpos[2]-local_ground)))

    def summary(self, case, failure):
        trace = np.asarray(self.trace, dtype=np.float64)
        phys = np.asarray(self.physics_records)
        control = np.asarray(self.control_records, dtype=np.float64)
        pre = phys[:, 3] > .10
        if self.first_face_time is not None:
            pre &= phys[:, 0] < self.first_face_time
        pre_moving = pre & (phys[:, 0] >= self.epoch+case.get('settle_s', .8))
        support = self.physics_best.tolist()
        required = ([40]*(len(self.levels)-1)+[160]) if self.levels else [160]
        physical = bool(self.crossed.all()) if self.levels else not failure
        strict = bool(physical and not failure and np.all(self.physics_best >= required))
        if self.levels:
            strict &= int(self.sim.unified.fsm.phase[0]) in (Phase.STAIR_ARMED_APPROACH,Phase.DECK_SETTLE,Phase.CRUISE_E0)
            strict &= bool(np.all(self.e0_best>=required))
        if len(self.levels)>1:
            physical=bool(physical and self.final_deck_crossed)
            strict=bool(strict and physical and self.final_deck_best>=160 and
                        int(self.sim.unified.fsm.phase[0]) in (Phase.STAIR_ARMED_APPROACH,Phase.DECK_SETTLE,Phase.CRUISE_E0))
        support_strict=strict
        tail = trace[-min(400, len(trace)):]
        if case['course'] in ('flat', 'flat60', 'rough_L9'):
            if case['course']!='flat60':
                tracking=(float(np.abs(tail[:,2]-case['speed']).mean())<=.25 and
                          abs(float(tail[:,20].mean())-case.get('wz',0.))<=.60)
            elif case.get('task', '').startswith('height'):
                tracking = abs(float(tail[:, 19].mean())-case['height']) <= .02
            elif case.get('wz', 0.):
                tracking = abs(float(tail[:, 20].mean())-case['wz']) <= abs(case['wz'])*.02
            else:
                tracking = abs(float(tail[:, 2].mean())-case['speed']) <= (.20 if case['speed'] < 0 else .15)
            strict = bool(tracking and not failure)
        initial = phys[pre_moving, 6]
        activation = phys[pre, 2]
        return dict(**case, failure=failure, passed=strict, physical_crossed=physical,
            stage_crossed=self.crossed.tolist(), strict_support_400hz=support_strict,
            longest_bilateral_support_substeps=support, required_support_substeps=required,
            longest_e0_bilateral_support_substeps=self.e0_best.tolist(),
            final_deck_crossed=self.final_deck_crossed if len(self.levels)>1 else None,
            final_deck_best_substeps=self.final_deck_best if len(self.levels)>1 else None,
            longest_bilateral_support_s=(self.physics_best*DT).tolist(), physics_samples=len(phys),
            stair_active_fraction=float((phys[:, 2] > 0.).mean()),
            cruise_stair_active_fraction=float((phys[phys[:, 1] == Phase.CRUISE_E0, 2] > 0.).mean())
                if np.any(phys[:, 1] == Phase.CRUISE_E0) else 0.,
            precontact_samples=int(pre.sum()), precontact_active_samples=int((activation > 0.).sum()),
            precontact_stair_active_fraction=float((activation > 0.).mean()) if len(activation) else None,
            precontact_min_relative_height_m=float(initial.min()) if len(initial) else None,
            first_face_contact_s=self.first_face_time, first_climb_s=self.first_climb_time,
            first_face_robot_geom=self.first_face_geom,
            trigger_delay_ms=1000.*(self.first_climb_time-self.first_face_time)
                if self.first_climb_time is not None and self.first_face_time is not None else None,
            mean_tail_speed_m_s=float(tail[:, 2].mean()), mean_tail_height_m=float(tail[:, 19].mean()),
            peak_abs_pitch_deg=float(np.abs(trace[:, 4]).max()),
            peak_speed_m_s=float(np.abs(trace[:, 2]).max()),
            max_rollback_m=float((np.maximum.accumulate(trace[:, 3])-trace[:, 3]).max()),
            max_closure_mm=float(max(0., self.sim.closure_mm)),
            end_phase=Phase(int(self.sim.unified.fsm.phase[0])).name,
            e0_sha256=reference.sha256(reference.E0/'weights/e0_c874_004m.pt'),
            stair_sha256=self.sim.unified.sha,
            detector_config=self.sim.unified.config.to_dict())

def reset_case(sim, case):
    """Independent physical reset; truth is never forwarded to policy/FSM."""
    course = case['course']
    ref_case = dict(case)
    if course == 'oblique_20_negative':
        reference.LEVELS[course] = (.20,)
    if course.startswith('platform_'):
        reference.LEVELS[course] = (int(course.split('_')[1])*.001,)
    yaw, sign, ground = reference.reset(sim, ref_case)
    sim.mode_latched = bool(case.get('armed', False))
    sim.raw_keys = set()
    sim.unified.intent = dict(mode=sim.mode_latched, forward=False, reverse=False, force=False, jump=False)
    sim.resets = 0
    return yaw, sign, ground

def run_case(case, checkpoint=None, detector=None, calibration=False, frames=None, load_jumps=False,
             physics_frames=None):
    policy = ManualPolicy(checkpoint, detector=detector, load_jumps=load_jumps)
    sim = ManualSimulation(policy)
    sim.load_map(metadata(case['course']))
    yaw, sign, ground = reset_case(sim, case)
    if case.get('dr',0.):
        from fsm_cpu_dr import CPUFullDR
        sim.dr=CPUFullDR(sim,case.get('seed',1729))
    restart_initial=None
    if case.get('restart'):
        sim.mode_latched=False
        # Reset-only setup: settle an upright pose, translate it to the riser,
        # then initialize exactly zero velocity. No truth enters deployed control.
        for _ in range(40):sim.step(set(),command=(0.,0.))
        reset_judge=ContactJudge(sim,case,yaw,sign,ground)
        top=ground+reset_judge.levels[0]
        gaps=[]
        for gid in reset_judge.robot_side:
            if sim.m.geom_type[gid]!=mj.mjtGeom.mjGEOM_CYLINDER:continue
            point=sim.d.geom_xpos[gid]
            radius=float(sim.m.geom_size[gid,0])
            dz=max(0.,float(point[2]-top))
            if dz>=radius:continue
            tip=math.sqrt(max(0.,radius*radius-dz*dz))
            edge=float(reset_judge.edge(point[None,:2])[0][0])
            gaps.append(edge-float(reset_judge.progress(point[:2]))-tip)
        if not gaps:raise ValueError('No main/guide cylinder intersects the riser height')
        sim.d.qpos[0]+=sign*(min(gaps)-.002)
        sim.d.qvel[:]=0.
        mj.mj_forward(sim.m,sim.d)
        sim.unified.reset_history()
        sim.cmd_vx=sim.cmd_wz=0.
        sim.mode_latched=bool(case.get('armed'))
        restart_initial=dict(time_s=float(sim.d.time),root_velocity=sim.d.qvel[:3].tolist(),
            measured_wheel_m_s=float(sim._observe(False)[20:22].mean()*.625),
            protocol='stationary settled-pose reset at riser',riser_clearance_m=.002)
    judge = ContactJudge(sim, case, yaw, sign, ground)
    if restart_initial is not None:restart_initial['front_gap_m']=judge.front_gap()
    def observe_physics(s):
        judge.observe_fsm(s)
        if physics_frames is not None:
            physics_frames(s, judge)
    sim.physics_observer = observe_physics
    failure = None
    steps = round(case['seconds']/.02)
    for k in range(steps):
        moving = k*.02 >= case.get('settle_s', .8)
        speed = case['speed'] if moving else 0.
        keys = {'w'} if moving and speed > 0. else {'s'} if moving and speed < 0. else set()
        if case.get('force_at_s') is not None and abs(k*.02-case['force_at_s']) < .009:
            keys.add('v')
        if calibration:
            # Frozen-E0 collision trajectories, independently labelled offline.
            # Armed high stance, no expert action contaminates detector fitting.
            policy.config.pitch_impulse = policy.config.pitch_rate_impulse = 1.e6
            policy.config.wheel_deceleration = policy.config.leg_impulse = 1.e6
            policy.config.blocked_ticks = 100000
        sim.step(keys, command=(speed, case.get('wz', 0.) if moving else 0.))
        judge.control_records.append(np.r_[sim.d.time, sim.last_obs, sim.prev_a,
                                         policy.fsm.features[0].numpy(), judge.front_gap(),
                                         judge.trace[-1][15:17], int(policy.fsm.phase[0]),
                                         sim.d.qpos[2]-ground])
        if frames is not None:
            frames(sim, judge, k)
        tilt = math.degrees(math.acos(float(np.clip(sim.d.xmat[sim.env.base_id].reshape(3,3)[2,2], -1., 1.))))
        if tilt > 65. or sim.closure_mm > 1000.:
            failure = 'fall' if tilt > 65. else 'catastrophic_closure'
            break
    result = judge.summary(case, failure)
    if restart_initial is not None:result['restart_initial_state']=restart_initial
    if getattr(sim,'dr',None) is not None:
        result['dr_samples']=sim.dr.summary
    sim.physics_observer = None
    trace = dict(physics=np.asarray(judge.physics_records),
                 reference_trace=np.asarray(judge.trace), control=np.asarray(judge.control_records))
    return result, trace

