"""One new C2 root-cause probe: read-only cached contact geometry, no new control.
Reuses the frozen formal runner, gates and original audited actuation loop.
Aggregates online; never opens an old raw log or modifies dynamics caches.
"""
from pathlib import Path
import copy
import json
import math
import sys
import numpy as np
import mujoco

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from RM_FPS_PLAYER_V1 import runtime
from RM_ROBUSTNESS_V1 import run_t01_formal as formal
from RM_ROBUSTNESS_V1 import t01_contact_audit as audit
from RM_ROBUSTNESS_V1.controller_heading_follow_v2 import GroundController

DIRECTORY=ROOT/'RM_ROBUSTNESS_V1/contact_geometry_probe_v1'
CASE='t01_c2_contact_geometry_420151_probe001'


def bucket():
    return dict(ticks=0,no_contact_points=0,penetrating_points_present=0,
                nonpenetrating_only=0,active_constraint_present=0,
                exactly_zero_normal=0,geometry_set_changes=0,
                min_contact_distance_m=None,max_contact_distance_m=None,
                max_abs_applied_torque_Nm=0.,post_speed_abs_peak_rad_s=0.,
                normal_sum_N=0.,normal_peak_N=0.,root_qacc_z_min=None,
                root_qacc_z_max=None)


class ProbePlant(audit.AuditedPlant):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.probe_buckets={name:bucket()for name in('left_supported','left_low_force','right_supported','right_low_force','whole_low_force')}
        self.probe_examples=[];self.probe_ticks=0;self.previous_env=[None,None]

    def _grade_contact_sample(self):
        super()._grade_contact_sample()
        stage=float(self.d.time)-self.dt
        if int(round(stage/self.dt))<4000:return
        row=self.audit_samples[-1]
        sides=[[],[]];f=np.empty(6)
        for ci,ct in enumerate(self.d.contact):
            a,b=int(ct.geom1),int(ct.geom2)
            if bool(self._env[a])==bool(self._env[b]):continue
            robot,env=(b,a)if self._env[a]else(a,b)
            if robot not in self._main:continue
            side=self._main.index(robot)
            mujoco.mj_contactForce(self.m,self.d,ci,f)
            fn=max(0.,float(f[0]))
            sides[side].append(dict(environment_geom_id=env,normal_N=fn,
                distance_m=float(ct.dist),active_constraint=int(ct.efc_address)>=0,
                normal_world_into_robot=(np.asarray(ct.frame[:3])*(1 if robot==b else -1)).tolist(),
                point_world=ct.pos.copy().tolist()))
        sums=[math.fsum(p['normal_N']for p in points)for points in sides]
        if not np.allclose(sums,row['main_normal_N2'],rtol=0.,atol=1e-9):
            raise RuntimeError('Probe and original audited normal sums differ')
        qaccz=float(self.d.qacc[2]);snapshots=[]
        self.probe_ticks+=1
        for side in(0,1):
            points=sides[side];envs=frozenset(p['environment_geom_id']for p in points)
            change=self.previous_env[side]is not None and envs!=self.previous_env[side]
            self.previous_env[side]=envs
            axis=(2,5)[side]
            snap=dict(side=('left','right')[side],normal_N=sums[side],contacts=points,
                geometry_set_changed=change,applied_tau_Nm=float(self.d.ctrl[axis]),
                wheel_q_post_rad=float(self.d.qpos[self.qids[axis]]),
                wheel_qd_post_rad_s=float(self.d.qvel[self.vids[axis]]))
            snapshots.append(snap)
            key=snap['side']+('_supported'if sums[side]>1. else'_low_force')
            self._accumulate(self.probe_buckets[key],points,sums[side],change,axis,qaccz)
        if row['all_environment_positive_normal_N']<=1.:
            self._accumulate(self.probe_buckets['whole_low_force'],sides[0]+sides[1],
                row['all_environment_positive_normal_N'],any(s['geometry_set_changed']for s in snapshots),None,qaccz)
        if (min(sums)<=1.)and len(self.probe_examples)<32:
            self.probe_examples.append(dict(cache_time_s=stage,root_post_time_s=float(self.d.time),
                main_wheels=snapshots,whole_normal_N=row['all_environment_positive_normal_N'],
                ctrl6_Nm=self.d.ctrl.copy().tolist(),root_qacc_z_cached=qaccz))

    def _accumulate(self,b,points,normal,change,axis,qaccz):
        b['ticks']+=1;b['no_contact_points']+=not bool(points)
        b['penetrating_points_present']+=any(p['distance_m']<0. for p in points)
        b['nonpenetrating_only']+=bool(points)and all(p['distance_m']>=0. for p in points)
        b['active_constraint_present']+=any(p['active_constraint']for p in points)
        b['exactly_zero_normal']+=normal==0.;b['geometry_set_changes']+=bool(change)
        b['normal_sum_N']+=normal;b['normal_peak_N']=max(b['normal_peak_N'],normal)
        for p in points:
            dist=p['distance_m']
            b['min_contact_distance_m']=dist if b['min_contact_distance_m']is None else min(b['min_contact_distance_m'],dist)
            b['max_contact_distance_m']=dist if b['max_contact_distance_m']is None else max(b['max_contact_distance_m'],dist)
        b['root_qacc_z_min']=qaccz if b['root_qacc_z_min']is None else min(b['root_qacc_z_min'],qaccz)
        b['root_qacc_z_max']=qaccz if b['root_qacc_z_max']is None else max(b['root_qacc_z_max'],qaccz)
        if axis is not None:
            b['max_abs_applied_torque_Nm']=max(b['max_abs_applied_torque_Nm'],abs(float(self.d.ctrl[axis])))
            b['post_speed_abs_peak_rad_s']=max(b['post_speed_abs_peak_rad_s'],abs(float(self.d.qvel[self.vids[axis]])))

    def probe_summary(self):
        return dict(status='READ_ONLY_CONTACT_GEOMETRY_PROBE_NOT_NEW_CONTROLLER_OR_PASS',
            physics_ticks=self.probe_ticks,buckets=self.probe_buckets,first_low_force_examples=self.probe_examples,
            epoch='contact distances/normal forces/constraint IDs and qacc: existing dynamics PRE cache; wheel q/qd explicitly POST time, separated by0.5ms',
            interpretation='Low force remains a failure of the original gate. Negative distance means cached collision overlap, not proof of load support; no contact points alone is not a measured finite separation distance. Root qacc is not whole-COM acceleration.',
            control_changes=False,extra_forward_or_step_calls=0,old_raw_files_opened=0,
            original_contact_sums_cross_checked=True,actual_DC_clip_duty='not inferred from torque peaks')


def main():
    DIRECTORY.mkdir(parents=True,exist_ok=False)
    protocol=copy.deepcopy(json.loads((ROOT/'RM_ROBUSTNESS_V1/heading_follow_v2/T01_PROTOCOL_V1.json').read_text(encoding='utf8')))
    protocol.update(id='T01_C2_READ_ONLY_CONTACT_GEOMETRY_PROBE_V1',candidate_number=2,
        status='frozen_before_diagnostic_physics_not_fourth_candidate',
        formal_cases=[dict(id='nominal_slow',seed=420151,nominal=True,profile='slow')],
        diagnostic_purpose='One new case with previously unavailable zero-force contact distances/active constraints/2k applied torques; C2 unmodified; preserve all original gates.')
    formal.dump(DIRECTORY/'T01_PROTOCOL_V1.json',protocol)
    instances=[]
    class BoundController(GroundController):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs,geometry=runtime.bridge.geometry())
    class BoundPlant(ProbePlant):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs);instances.append(self)
    old_controller,old_plant,old_directory=runtime.GroundController,audit.AuditedPlant,formal.D
    try:
        runtime.GroundController=BoundController;audit.AuditedPlant=BoundPlant;formal.D=DIRECTORY
        sys.argv=[__file__,'--case',CASE,'--formal-id','nominal_slow']
        formal.main()
    finally:
        runtime.GroundController,audit.AuditedPlant,formal.D=old_controller,old_plant,old_directory
        if instances:
            formal.dump(DIRECTORY/'runs'/CASE/'contact_geometry_summary.json',instances[-1].probe_summary())


if __name__=='__main__':main()
