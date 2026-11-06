"""T01 private grading only. Existing V3 PD/targets/D4/DC/IMU order unchanged.
Inherit the existing contact-audit apply loop; only its post-step read-only hook
is replaced. Contacts/forces use last dynamics PRE cache; current pose is separate.
"""
import math
import numpy as np
import mujoco
from physics_bridge_contact_audit_v1 import ContactAuditPlant as BufferedImuPlant
from physics_bridge_v4_grade import BufferedImuPlant as CurrentGrade

FLAGS=('left_main','right_main','both_main','guide','hard','allair','wheelsoff')
def _bucket():
    return dict(ticks=0,count=dict.fromkeys(FLAGS,0),run=dict.fromkeys(FLAGS,0),longest=dict.fromkeys(FLAGS,0),max_normal=np.zeros(5),contacts={})

class AuditedPlant(BufferedImuPlant):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._env=(np.asarray(self.m.geom_bodyid)==0)&((np.asarray(self.m.geom_contype)|np.asarray(self.m.geom_conaffinity))!=0)
        self._main=tuple(int(x)for x in self.tires)
        self._guides={i for i in np.flatnonzero(np.asarray(self.m.geom_bodyid)>0)if(self.m.geom(int(i)).name or '').startswith('guide_wheel_')}
        if len(set(self._main))!=2 or len(self._guides)!=8:raise ValueError('T01 requires exact2 main tires and8 named guide_wheel geoms')
        self._reset_audit()

    def _reset_audit(self):
        self.audit_armed=True;self._total=_bucket();self._window=_bucket();self.audit_samples=[]

    def reset(self,*args,**kwargs):
        result=super().reset(*args,**kwargs)
        self._reset_audit();return result

    def support_identity(self):
        def named(ids):return[dict(geom_id=int(i),geom=self.m.geom(int(i)).name,body=self.m.body(int(self.m.geom_bodyid[i])).name)for i in ids]
        return dict(main_wheels=named(self._main),guide_rollers=named(sorted(self._guides)),environment_geom_count=int(self._env.sum()),model_ngeom=int(self.m.ngeom),environment_rule='bodyid0 AND (contype|conaffinity)!=0',normal_threshold_N=1.,truth_grading_only=True)

    def _grade_contact_sample(self):
        stage=max(0.,float(self.d.time)-self.dt)
        stage_index=int(round(stage/self.dt))
        if stage_index<4000:return  # T01 2kHz: index4000 is2s; retain actual cache time below.
        main=np.zeros(2);guide=hard=0.;positive=[];contacts=[];force=np.empty(6)
        for ci,ct in enumerate(self.d.contact):
            a,b=int(ct.geom1),int(ct.geom2)
            if a<0 or b<0 or a>=len(self._env)or b>=len(self._env):raise ValueError('invalid contact geom ID')
            if bool(self._env[a])==bool(self._env[b]):continue
            robot,env=(b,a)if self._env[a]else(a,b)
            if int(self.m.geom_bodyid[robot])==0:continue
            mujoco.mj_contactForce(self.m,self.d,ci,force)
            if not np.isfinite(force).all():raise ValueError('nonfinite contact audit force; preserve prefix')
            fn=max(0.,float(force[0]));positive.append(fn)
            if fn<=0.:continue  # Sum ALL positive points before category >1N test.
            kind='main_wheel'if robot in self._main else'guide_roller'if robot in self._guides else'hard_other'
            if kind=='main_wheel':main[self._main.index(robot)]+=fn
            elif kind=='guide_roller':guide+=fn
            else:hard+=fn
            contacts.append(dict(robot_geom_id=robot,robot_geom=self.m.geom(robot).name,environment_geom_id=env,environment_geom=self.m.geom(env).name,kind=kind,normal_N=fn))
        total=math.fsum(positive)
        if not math.isfinite(total):raise ValueError('nonfinite environment force sum')
        flags=(main[0]>1.,main[1]>1.,bool((main>1.).all()),guide>1.,hard>1.,total<=1.,bool((main<=1.).all()))
        normals=np.array([main[0],main[1],guide,hard,total]);stage=max(0.,float(self.d.time)-self.dt)
        for bucket in(self._total,self._window):
            bucket['ticks']+=1;bucket['max_normal']=np.maximum(bucket['max_normal'],normals)
            for key,yes in zip(FLAGS,flags):
                bucket['count'][key]+=int(yes);bucket['run'][key]=bucket['run'][key]+1 if yes else 0;bucket['longest'][key]=max(bucket['longest'][key],bucket['run'][key])
            for c in contacts:
                key=(c['robot_geom_id'],c['environment_geom_id']);old=bucket['contacts'].get(key)
                if old is None or c['normal_N']>old['normal_N']:bucket['contacts'][key]=c.copy()
        self.audit_samples.append(dict(time_s=stage,root_post_time_s=float(self.d.time),main_normal_N2=main.tolist(),guide_normal_N=guide,hard_other_normal_N=hard,all_environment_positive_normal_N=total,contacts=contacts))

    def apply_torque_request(self,tau,packet,dt=.01,mechanical_power_limit=None):
        self._window=_bucket();self.audit_samples=[]
        return super().apply_torque_request(tau,packet,dt,mechanical_power_limit)

    def _summary(self,bucket):
        n=bucket['ticks'];available=bool(n)
        return dict(collected=available,physics_ticks=n,duration_s=n*self.dt if available else None,mainwheel_support_ticks2=[bucket['count'][k]for k in('left_main','right_main')]if available else None,
            mainwheel_support_duty2=[bucket['count'][k]/n for k in('left_main','right_main')]if available else None,
            guide_support_ticks=bucket['count']['guide']if available else None,hard_contact_ticks=bucket['count']['hard']if available else None,
            whole_body_unsupported_ticks=bucket['count']['allair']if available else None,wheels_off_ticks=bucket['count']['wheelsoff']if available else None,
            ticks_by_kind=dict(bucket['count'])if available else None,duration_by_kind_s={k:v*self.dt for k,v in bucket['count'].items()}if available else None,
            longest_by_kind_s={k:v*self.dt for k,v in bucket['longest'].items()}if available else None,
            max_normal_N_main2_guide_hard_all=bucket['max_normal'].tolist()if available else None,actual_support_contacts=list(bucket['contacts'].values())if available else None,
            contact_epoch='last dynamics PRE cache after each original mj_step',allair_definition='all finite positive robot-environment normal forces summed <=1N; not merely wheels off')

    def audit_totals(self):
        return dict(total=self._summary(self._total),window=self._summary(self._window),support_identity=self.support_identity(),contact_window_start_cache_s=2.0)

    def grade_current(self):
        # Existing v4: current freejoint root pose/qvel, staged cached closure.
        # No new MjData/forward/kinematics pipeline and no live cache mutation.
        out=CurrentGrade.grade(self)
        out['closure_cache_time_s']=out['collision_site_cache_time_s']
        return out
