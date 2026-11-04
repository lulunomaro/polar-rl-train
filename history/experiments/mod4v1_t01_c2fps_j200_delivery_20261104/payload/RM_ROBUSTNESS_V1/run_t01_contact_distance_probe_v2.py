"""One new C2 diagnostic: native signed distance at absent-force ticks.
No new dynamics, controller, contact threshold or old-raw replay.
World AABBs conservatively select pairs; capped searches are explicitly incomplete.
"""
from pathlib import Path
import copy
import json
import sys
from collections import Counter
import numpy as np
import mujoco

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from RM_ROBUSTNESS_V1.run_t01_contact_geometry_probe_v1 import ProbePlant
from RM_ROBUSTNESS_V1 import run_t01_formal as formal, t01_contact_audit as audit
from RM_ROBUSTNESS_V1.controller_heading_follow_v2 import GroundController
from RM_FPS_PLAYER_V1 import runtime

DIRECTORY=ROOT/'RM_ROBUSTNESS_V1/contact_distance_probe_v2'
CASE='t01_c2_contact_distance_420152_probe002'
LIMIT=.002
MAX_PAIRS=64

def bounds(m,d,ids):
    """Conservative world AABB from compiled local center/half-size and PRE cache."""
    ids=np.asarray(ids,dtype=int)
    rot=np.asarray(d.geom_xmat[ids]).reshape(-1,3,3)
    local=np.asarray(m.geom_aabb[ids])
    center=np.asarray(d.geom_xpos[ids])+np.einsum('nij,nj->ni',rot,local[:,:3])
    half=np.einsum('nij,nj->ni',np.abs(rot),local[:,3:])
    if not np.all(np.isfinite(center)) or not np.all(np.isfinite(half)) or np.any(half<0):
        raise ValueError('Nonfinite or invalid compiled AABB; no fabricated distance')
    return center-half,center+half

class DistancePlant(ProbePlant):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.world_ids=np.flatnonzero(self._env)
        self.world_bounds=None
        self.distance_stats={s:dict(ticks=0,classes=Counter(),min_signed_m=None,
            max_signed_m=None,min_aabb_lower_m=None,max_aabb_lower_m=None,
            max_candidate_count=0,incomplete_ticks=0)for s in('left','right')}
        self.distance_examples=[];self.distance_sanity=[];self.query_calls=0
        self.query_eps=max(1e-9,float(getattr(self.m.opt,'ccd_tolerance',1e-6)))

    def _query(self,wheel,env):
        segment=np.empty(6,dtype=np.float64)
        dist=float(mujoco.mj_geomDistance(self.m,self.d,int(wheel),int(env),LIMIT,segment))
        self.query_calls+=1
        if not np.isfinite(dist):raise ValueError('Native distance query returned nonfinite')
        return dist,segment.tolist()if dist<LIMIT and np.all(np.isfinite(segment))else None

    def _measure(self,side):
        wheel=self._main[side]
        lo,hi=bounds(self.m,self.d,[wheel]);wlo,whi=lo[0],hi[0]
        elo,ehi=self.world_bounds
        axis_gap=np.maximum(np.maximum(elo-whi,wlo-ehi),0.)
        lower=np.sqrt(np.einsum('ij,ij->i',axis_gap,axis_gap))
        chosen=np.flatnonzero(lower<=LIMIT)
        complete=len(chosen)<=MAX_PAIRS
        if not complete:chosen=chosen[np.argsort(lower[chosen],kind='stable')[:MAX_PAIRS]]
        best=None;best_env=None;segment=None
        for index in chosen:
            env=int(self.world_ids[index]);dist,seg=self._query(wheel,env)
            if best is None or dist<best:best,best_env,segment=dist,env,seg
        if best is not None and best < -self.query_eps:kind='negative_overlap_pair'
        elif not complete:kind='incomplete_candidate_search'
        elif best is None:kind='aabb_lower_bound_beyond_2mm'
        elif abs(best)<=self.query_eps:kind='within_query_tolerance_of_zero'
        elif best>=LIMIT-self.query_eps:kind='at_or_beyond_query_limit'
        else:kind='positive_gap_above_query_tolerance'
        return dict(classification=kind,signed_distance_m=best,environment_geom_id=best_env,
            closest_segment_world=segment,global_aabb_lower_bound_m=float(lower.min()),
            candidate_count=int(np.count_nonzero(lower<=LIMIT)),queried_pairs=len(chosen),
            complete_within_2mm=complete,query_tolerance_m=self.query_eps)

    def _grade_contact_sample(self):
        super()._grade_contact_sample()
        stage=float(self.d.time)-self.dt
        if int(round(stage/self.dt))<4000:return
        if self.world_bounds is None:self.world_bounds=bounds(self.m,self.d,self.world_ids)
        # Read-only native-query comparison against an actually generated contact.
        if len(self.distance_sanity)<2:
            for ct in self.d.contact:
                a,b=int(ct.geom1),int(ct.geom2)
                if bool(self._env[a])==bool(self._env[b]):continue
                robot,env=(b,a)if self._env[a]else(a,b)
                if robot not in self._main:continue
                side=self._main.index(robot)
                if any(x['side']==side for x in self.distance_sanity):continue
                dist,_=self._query(robot,env)
                self.distance_sanity.append(dict(side=side,cache_time_s=stage,
                    wheel_geom=robot,environment_geom=env,contact_distance_m=float(ct.dist),
                    native_signed_distance_m=dist,delta_m=dist-float(ct.dist)))
        row=self.audit_samples[-1];measured={}
        for side,name in enumerate(('left','right')):
            if row['main_normal_N2'][side]>1.:continue
            item=self._measure(side);measured[name]=item;s=self.distance_stats[name]
            s['ticks']+=1;s['classes'][item['classification']]+=1
            s['incomplete_ticks']+=not item['complete_within_2mm']
            s['max_candidate_count']=max(s['max_candidate_count'],item['candidate_count'])
            for value,prefix in((item['signed_distance_m'],'signed_m'),(item['global_aabb_lower_bound_m'],'aabb_lower_m')):
                if value is None:continue
                for op,fn in(('min',min),('max',max)):
                    key=op+'_'+prefix;s[key]=value if s[key]is None else fn(s[key],value)
        if measured and len(self.distance_examples)<24:
            self.distance_examples.append(dict(cache_time_s=stage,root_post_time_s=float(self.d.time),
                main_normal_N2=list(row['main_normal_N2']),whole_normal_N=row['all_environment_positive_normal_N'],
                measured=measured))

    def probe_summary(self):
        out=super().probe_summary()
        out['buckets']['whole_low_force']['max_abs_applied_torque_Nm']=None
        out['buckets']['whole_low_force']['post_speed_abs_peak_rad_s']=None
        out.update(status='READ_ONLY_NATIVE_DISTANCE_PROBE_NOT_NEW_CONTROL_OR_PASS',
            native_api='mj_geomDistance existing cached geom_xpos/geom_xmat; const dynamics data',
            distance_scope='All static world collision AABBs; up to64 pairs per low-force wheel. Outside2mm is a lower-bound observation, not exact distance. Incomplete search never establishes global positive separation.',
            world_collision_geoms=len(self.world_ids),distance_query_limit_m=LIMIT,
            distance_query_tolerance_m=self.query_eps,native_distance_query_calls=self.query_calls,
            distance_at_low_force=self.distance_stats,generated_contact_sanity=self.distance_sanity,
            first_distance_examples=self.distance_examples,
            compiled_collision_settings=dict(disableflags=int(self.m.opt.disableflags),
                tire_margin_m=self.m.geom_margin[list(self._main)].tolist(),
                tire_gap_m=self.m.geom_gap[list(self._main)].tolist(),
                tire_solref=self.m.geom_solref[list(self._main)].tolist()),
            whole_motor_fields='unavailable/null: prior axis=None accumulator did not measure whole-bucket torque/speed',
            interpretation_distance='Native signed-distance results remain subject to query tolerance and reported search coverage. No contact alone is not finite separation proof. No distances feed control; all original gates unchanged.')
        return out

def main():
    DIRECTORY.mkdir(parents=True,exist_ok=False)
    protocol=copy.deepcopy(json.loads((ROOT/'RM_ROBUSTNESS_V1/heading_follow_v2/T01_PROTOCOL_V1.json').read_text(encoding='utf8')))
    protocol.update(id='T01_C2_READ_ONLY_NATIVE_DISTANCE_PROBE_V2',
        status='frozen_before_new_diagnostic_not_fourth_controller',
        formal_cases=[dict(id='nominal_slow',seed=420152,nominal=True,profile='slow')],
        diagnostic_purpose='Resolve missing finite geometry distance at zero-contact ticks using native API only. C2, robot, physics and gates unchanged; no old raw replay.',
        distance_probe=dict(limit_m=LIMIT,max_pairs=MAX_PAIRS,coverage='all world AABBs; capped queries explicitly incomplete'))
    formal.dump(DIRECTORY/'T01_PROTOCOL_V1.json',protocol)
    instances=[]
    class BoundController(GroundController):
        def __init__(self,*a,**kw):super().__init__(*a,**kw,geometry=runtime.bridge.geometry())
    class BoundPlant(DistancePlant):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);instances.append(self)
    old_controller,old_plant,old_directory=runtime.GroundController,audit.AuditedPlant,formal.D
    try:
        runtime.GroundController=BoundController;audit.AuditedPlant=BoundPlant;formal.D=DIRECTORY
        sys.argv=[__file__,'--case',CASE,'--formal-id','nominal_slow'];formal.main()
    finally:
        runtime.GroundController,audit.AuditedPlant,formal.D=old_controller,old_plant,old_directory
        if instances:formal.dump(DIRECTORY/'runs'/CASE/'contact_distance_summary.json',instances[-1].probe_summary())

if __name__=='__main__':main()
