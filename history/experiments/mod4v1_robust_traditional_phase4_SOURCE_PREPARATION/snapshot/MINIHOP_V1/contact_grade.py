"""Read-only simulation grading. NEVER imported by the sensor controller.
All world contacts, including guides/hard parts, are included in air definition.
Contact geometry/force caches are PRE-step dynamics; root_post is separately timed.
"""
import numpy as np
import mujoco

class ReadOnlyGrade:
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.audit=[];self.air_run=0.;self.max_air=0.;self.first_air=None;self.first_landing=None
        self.peak_air_main_clearance_m=None;self._drivepoint=None
        self._world={i for i in range(self.m.ngeom)if int(self.m.geom_bodyid[i])==0 and int(self.m.geom_contype[i])!=0}
        self._names=[self.m.geom(i).name for i in range(self.m.ngeom)]
        self._body_names=[self.m.body(int(self.m.geom_bodyid[i])).name for i in range(self.m.ngeom)]

    def _capture_drivepoint(self,actual_dq,bounded):
        self._drivepoint=dict(time_s=float(self.d.time),velocity6_rad_s=np.asarray(actual_dq,float).copy().tolist(),
                              actual_tau6_Nm=np.asarray(bounded,float).copy().tolist(),root_xyz_pre_m=self.d.qpos[:3].copy().tolist())

    def _grade_minihop_sample(self):
        stage=float(self.d.time)-self.dt
        assert self._drivepoint is not None and abs(self._drivepoint['time_s']-stage)<1e-8
        main=np.zeros(2);guide=0.;hard=0.;contacts=[]
        for ci,ct in enumerate(self.d.contact):
            a,b=int(ct.geom1),int(ct.geom2)
            if a not in self._world and b not in self._world:continue
            robot=b if a in self._world else a;env=a if a in self._world else b
            force=np.zeros(6);mujoco.mj_contactForce(self.m,self.d,ci,force);fn=max(0.,float(force[0]))
            if fn<=1.:continue
            name=self._names[robot]
            kind='main_wheel'if robot in self.tires else'guide_roller'if name.startswith('guide_wheel_')else'hard_other'
            if kind=='main_wheel':main[self.tires.index(robot)]+=fn
            elif kind=='guide_roller':guide+=fn
            else:hard+=fn
            contacts.append(dict(robot_geom=name,robot_body=self._body_names[robot],environment_geom=self._names[env],
                                 kind=kind,normal_N=fn,position_world_m=np.asarray(ct.pos).tolist(),
                                 normal_geom1_to_geom2_world=np.asarray(ct.frame).reshape(3,3)[0].tolist()))
        total=float(main.sum())+guide+hard
        self.air_run=self.air_run+self.dt if total<=1. else 0.
        self.max_air=max(self.max_air,self.air_run)
        if self.first_air is None and self.air_run>=.02:self.first_air=stage-self.air_run+self.dt
        if self.first_air is not None and self.first_landing is None and total>1.:
            self.first_landing=dict(stage_time_s=stage,contacts=contacts)
        env=self.exact_support.envelopes(self.d)
        main_min_z2=[float(np.min(item['world_vertices'][:,2]))for item in env.values()]
        if self.air_run>=.02:
            clearance=min(main_min_z2)
            self.peak_air_main_clearance_m=clearance if self.peak_air_main_clearance_m is None else max(self.peak_air_main_clearance_m,clearance)
        row=dict(stage_time_s=stage,root_post_time_s=float(self.d.time),root_xyz_post_m=self.d.qpos[:3].copy().tolist(),
                 drivepoint=self._drivepoint,main_normal_N2=main.tolist(),guide_normal_N=guide,hard_normal_N=hard,
                 all_world_normal_N=total,air_run_s=self.air_run,main_mesh_min_z_world2_m=main_min_z2,contacts=contacts)
        self.audit.append(row)
