"""Private cached-stage audit only. No writes to model/data/control/DR/sensors.

Full finite world↔robot normal force is aggregated before any air threshold.
No forward/step occurs here. Contact/mesh/root-cache values after mj_step are
explicitly its last pre-integration dynamics stage; root qpos is separate post.
"""
import copy
import numpy as np
import mujoco
from .schema_v2 import (InstrumentationError,finite,vector,integer,finite_sum,require,
                        validate_grade_row,SCHEMA,PHYSICS_DT_S,AIR_NORMAL_LIMIT_N,
                        AIR_MINIMUM_S,CLOCK_EPS_S)

class ReadOnlyGrade:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.audit=[];self.air_run=0.;self.max_air=0.;self.first_air=None;self.first_air_confirmed_s=None;self.first_landing=None
        self.peak_air_main_clearance_m=None;self._drivepoint=None;self._private_pre=None
        self.instrumentation_error=None;self._last_stage=None;self._last_tick=None;self._air_ticks=0;self._air_start=None
        try:
            require(finite(self.dt,'physics_dt')==PHYSICS_DT_S,'physics_dt',self.dt)
            self._names=[self.m.geom(i).name for i in range(self.m.ngeom)]
            self._body_ids=[integer(self.m.geom_bodyid[i],'geom_bodyid')for i in range(self.m.ngeom)]
            self._body_names=[self.m.body(i).name for i in self._body_ids]
            # A contype=0 geom may still contact through its conaffinity. Never
            # use contact masks as a force-observation filter.
            self._world={i for i,b in enumerate(self._body_ids)if b==0}
            require(len(self.tires)==2 and len(set(self.tires))==2,'two_main_tires',self.tires)
            for i in self.tires:require(integer(i,'tire_id')<self.m.ngeom and i not in self._world,'tire_id',i)
        except Exception as e:self._raise_fault(e,'initialize')

    def _raise_fault(self,error,where):
        if self.instrumentation_error is None:
            fault=error if isinstance(error,InstrumentationError)else InstrumentationError('INSTRUMENTATION_EXCEPTION',where,repr(error))
            self.instrumentation_error={**fault.receipt(),'hook':where,'good_rows':len(self.audit),'last_good_stage_s':self._last_stage}
        r=self.instrumentation_error
        raise InstrumentationError(r['code'],r['field'],r['observed_repr']) from error

    def _check_latch(self):
        if self.instrumentation_error is not None:
            raise InstrumentationError('INSTRUMENTATION_LATCHED','first_error',self.instrumentation_error)

    def _capture_drivepoint(self,actual_dq,bounded):
        self._check_latch()
        try:
            require(self._drivepoint is None,'capture_without_previous_grade')
            t=finite(self.d.time,'drive.time');require(t>=0,'drive.time_nonnegative',t)
            tick=integer(self.tick_phys,'drive.physics_tick')
            if self._last_stage is not None:
                require(abs(t-self._last_stage-PHYSICS_DT_S)<=CLOCK_EPS_S and tick==self._last_tick+1,'capture_contiguous',(t,tick))
            dq=vector(actual_dq,(6,),'drive.velocity6');tau=vector(bounded,(6,),'drive.bounded_tau6');root=vector(self.d.qpos[:3],(3,),'drive.root_pre')
            mass=np.asarray(self.m.body_mass,dtype=float)
            require(mass.ndim==1 and mass.size>0 and np.isfinite(mass).all()and np.all(mass>=0),'model.body_mass')
            with np.errstate(over='raise',invalid='raise'):total_mass=finite(float(mass.sum()),'model.body_mass.sum')
            require(total_mass>0,'model.mass_positive',total_mass)
            # xmat/subtree_com here still belong to the PREVIOUS dynamics
            # evaluation. Read them only in the post-step grade hook, when
            # they have been refreshed for this captured pre-integration time.
            rotation=com=None
            dp=dict(time_s=t,physics_tick=tick,velocity6_rad_s=dq.tolist(),actual_tau6_Nm=tau.tolist(),root_xyz_pre_m=root.tolist())
            private=dict(visibility='private_physics_only',meaning='contact_only_not_complete_trueCOMproper',stage_time_s=t,
                         contact_external_force_world_N3=None,actual_model_body_mass_sum_kg=total_mass,
                         root_rotation_world_from_body33_pre=rotation,chassis_subtree_com_world_m3_pre=com)
            self._drivepoint=dp;self._private_pre=private
        except Exception as e:self._raise_fault(e,'capture_drivepoint')

    def _grade_minihop_sample(self):
        self._check_latch()
        try:self._grade_checked()
        except Exception as e:self._raise_fault(e,'grade_sample')

    def _grade_checked(self):
        dp=self._drivepoint;require(dp is not None,'grade_requires_capture')
        stage=dp['time_s'];post=finite(self.d.time,'root_post.time');tick=integer(self.tick_phys,'root_post.tick')
        require(abs(post-stage-PHYSICS_DT_S)<=CLOCK_EPS_S and tick==dp['physics_tick']+1,'grade_stage_interval',(stage,post,tick))
        root=vector(self.d.qpos[:3],(3,),'root_post.xyz')
        env_contacts=[];self_count=0;world_count=0;parts=[[],[],[],[]];force_world=[]
        for ci,ct in enumerate(self.d.contact):
            a=integer(ct.geom1,'contact.geom1');b=integer(ct.geom2,'contact.geom2')
            require(a<self.m.ngeom and b<self.m.ngeom and a!=b,'contact.geom_ids',(a,b))
            pos=vector(ct.pos,(3,),'contact.position')
            frame=vector(ct.frame,(9,),'contact.frame').reshape(3,3)
            force=np.zeros(6)
            mujoco.mj_contactForce(self.m,self.d,ci,force)
            force=vector(force,(6,),'contact.force6')
            aw=a in self._world;bw=b in self._world
            if aw==bw:
                if aw:world_count+=1
                else:self_count+=1
                continue
            robot=b if aw else a;env=a if aw else b;sign=1. if aw else -1.
            with np.errstate(over='raise',invalid='raise'):
                world=vector(sign*(frame.T@force[:3]),(3,),'contact.force_on_robot_world')
            fn=max(0.,float(force[0]));name=self._names[robot]
            if robot in self.tires:kind='main_wheel';main_index=self.tires.index(robot);part=main_index
            elif isinstance(name,str)and name.startswith('guide_wheel_'):kind='guide_roller';main_index=None;part=2
            else:kind='hard_other';main_index=None;part=3
            parts[part].append(fn);force_world.append(world)
            env_contacts.append(dict(contact_index=ci,robot_geom_id=robot,robot_geom=name,robot_body_id=self._body_ids[robot],robot_body=self._body_names[robot],
                environment_geom_id=env,environment_geom=self._names[env],robot_is_geom2=bool(aw),kind=kind,main_index=main_index,
                normal_signed_N=float(force[0]),normal_N=fn,position_world_m=pos.tolist(),normal_geom1_to_geom2_world=frame[0].tolist(),
                local_force6=force.tolist(),force_on_robot_world_N3=world.tolist()))
        main=[finite_sum(parts[i],'main_normal')for i in (0,1)];guide=finite_sum(parts[2],'guide_normal');hard=finite_sum(parts[3],'hard_normal')
        total=finite_sum((c['normal_N']for c in env_contacts),'all_world_normal')
        positive=[c for c in env_contacts if c['normal_N']>0.]
        private=copy.deepcopy(self._private_pre)
        if hasattr(self,'chassis'):
            chassis=integer(self.chassis,'chassis')
            if hasattr(self.d,'xmat'):private['root_rotation_world_from_body33_pre']=vector(self.d.xmat[chassis].reshape(3,3),(3,3),'cached.root_rotation_pre').tolist()
            if hasattr(self.d,'subtree_com'):private['chassis_subtree_com_world_m3_pre']=vector(self.d.subtree_com[chassis],(3,),'cached.subtree_com_pre').tolist()
        private['contact_external_force_world_N3']=[finite_sum((f[i]for f in force_world),'external_force_world')for i in range(3)]
        env=self.exact_support.envelopes(self.d)
        require(isinstance(env,dict)and len(env)==2,'mesh.two_main_envelopes')
        by_id={integer(item['geom_id'],'mesh.geom_id'):item for item in env.values()}
        require(set(by_id)==set(self.tires),'mesh.main_ids',list(by_id))
        min_z=[]
        for gid in self.tires:
            v=np.asarray(by_id[gid]['world_vertices'],dtype=float)
            require(v.ndim==2 and v.shape[0]>0 and v.shape[1]==3,'mesh.vertices_shape',v.shape)
            if not np.isfinite(v).all():raise InstrumentationError('NONFINITE','mesh.world_vertices',v.tolist())
            min_z.append(float(v[:,2].min()))
        air_ticks=self._air_ticks+1 if total<=AIR_NORMAL_LIMIT_N else 0
        air_start=(stage if self._air_ticks==0 else self._air_start)if air_ticks else None
        duration=finite(air_ticks*PHYSICS_DT_S,'air_run_s');qualified=duration>=AIR_MINIMUM_S
        first=self.first_air;confirmed=self.first_air_confirmed_s;landing=self.first_landing;peak=self.peak_air_main_clearance_m
        if first is None and qualified:first=air_start;confirmed=post
        if first is not None and landing is None and total>AIR_NORMAL_LIMIT_N:
            landing=dict(stage_time_s=stage,root_post_time_s=post,all_world_normal_N=total,main_normal_N2=main,guide_normal_N=guide,hard_normal_N=hard,contacts=copy.deepcopy(positive),environment_contacts=copy.deepcopy(env_contacts))
        if qualified:peak=min(min_z)if peak is None else max(peak,min(min_z))
        row=dict(schema=SCHEMA,sample_index=len(self.audit),stage_time_s=stage,root_post_time_s=post,root_xyz_post_m=root.tolist(),drivepoint=copy.deepcopy(dp),
            cache_stages=dict(force_s=stage,contact_geometry_s=stage,mesh_s=stage,drive_s=stage,root_post_s=post),
            main_normal_N2=main,guide_normal_N=guide,hard_normal_N=hard,all_world_normal_N=total,air_run_s=duration,air_qualified=qualified,
            main_mesh_min_z_world2_m=min_z,contacts=positive,environment_contacts=env_contacts,environment_contact_count=len(env_contacts),
            environment_nonpositive_contact_count=len(env_contacts)-len(positive),self_contact_count=self_count,world_world_contact_count=world_count,private_contact_diagnostic=private)
        validate_grade_row(row)
        # Commit audit state only after successful finite schema + stream append.
        self.audit.append(row)
        self._air_ticks=air_ticks;self._air_start=air_start;self.air_run=duration;self.max_air=max(self.max_air,duration)
        self.first_air=first;self.first_air_confirmed_s=confirmed;self.first_landing=landing;self.peak_air_main_clearance_m=peak
        self._last_stage=stage;self._last_tick=dp['physics_tick'];self._drivepoint=None;self._private_pre=None
