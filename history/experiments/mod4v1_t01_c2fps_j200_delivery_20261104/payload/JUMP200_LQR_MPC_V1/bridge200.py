"""Extra vertical 200mm fixture + private audit; robot/PD/D4/DC/IMU loop reused unchanged."""
from pathlib import Path
import math,xml.etree.ElementTree as ET
import numpy as np
import mujoco
import physics_bridge as base
from physics_bridge_contact_audit_v2 import ContactAuditPlant as OriginalAudit

HEIGHT=.200

def model_factory200(step=False,imu_offset=(.03,0.,.04),physics_dt=.0005):
    # Same authoritative robot XML. Only external test fixture differs from old270.
    p=base.ROOT/'MODEL_AUDIT'/base.MODEL_FILE
    root=ET.fromstring(p.read_bytes());root.find('compiler').set('meshdir',str(p.parent))
    root.find('option').set('timestep',str(physics_dt));root.find(".//site[@name='imu']").set('pos',' '.join(map(str,imu_offset)))
    if step:
        # Retain legacy audit geom-name only; actual geometry is explicitly200mm.
        ET.SubElement(root.find('worldbody'),'geom',name='step270',type='box',pos='1.5 0 .100',size='1.5 1 .100',contype='1',conaffinity='2',friction='.9 .003 .0001',rgba='.3 .5 .7 1')
    return mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'))

class ContactAuditPlant(OriginalAudit):
    def __init__(self,*a,**kw):
        prior=base.model_factory;base.model_factory=model_factory200
        try:super().__init__(*a,**kw)
        finally:base.model_factory=prior
        assert self.m.nbody==32 and abs(self.dt-.0005)<1e-12
        self.env={int(i)for i in np.flatnonzero((self.m.geom_bodyid==0)&((self.m.geom_contype|self.m.geom_conaffinity)!=0))}
        self.j200_first_contact=None
    def _grade_contact_sample(self):
        if not self.audit_armed:return
        from mesh_support import StepPatch
        main=np.zeros(2);top=np.zeros(2);guide=hard=0.;positive=[];contacts=[];stepid=self.m.geom('step270').id
        for i,c in enumerate(self.d.contact):
            a,b=int(c.geom1),int(c.geom2)
            if (a in self.env)==(b in self.env):continue
            robot=b if a in self.env else a;environment=a if a in self.env else b
            force=np.empty(6);mujoco.mj_contactForce(self.m,self.d,i,force)
            if not np.isfinite(force).all():raise ValueError('nonfinite J200 contact instrumentation')
            fn=max(0.,float(force[0]));positive.append(fn)
            if fn<=0.:continue
            name=self.m.geom(robot).name or'';kind='main_wheel'if robot in self.tires else'guide_roller'if name.startswith('guide_wheel_')else'hard_other'
            if kind=='main_wheel':main[self.tires.index(robot)]+=fn
            elif kind=='guide_roller':guide+=fn
            else:hard+=fn
            pos=np.asarray(c.pos);normal=np.asarray(c.frame).reshape(3,3)[0]
            surface='step_top'if environment==stepid and abs(pos[2]-HEIGHT)<.003 and abs(normal[2])>.7 else'vertical_riser'if environment==stepid and abs(pos[0])<.003 and abs(normal[0])>.7 else'ground'if self.m.geom(environment).name=='ground'else'edge_or_side'
            if kind=='main_wheel'and surface=='step_top':top[self.tires.index(robot)]+=fn
            contacts.append(dict(robot_geom=name,robot_body=self.m.body(int(self.m.geom_bodyid[robot])).name,environment_geom=self.m.geom(environment).name,normal_N=fn,kind=kind,contact_position_world_m=pos.tolist(),normal_geom1_to_geom2_world=normal.tolist(),surface_diagnostic=surface))
        total=math.fsum(positive);stage=max(0.,float(self.d.time)-self.dt)
        self.air_run=self.air_run+self.dt if total<=1. else 0.;self.max_full_air=max(self.max_full_air,self.air_run)
        if self.air_run>=.020-1e-12 and not self.full_air_confirmed:self.full_air_confirmed=True;self.first_full_air=stage-self.air_run+self.dt
        if self.full_air_confirmed and total>1. and self.first_landing is None:self.first_landing=dict(time_s=stage,contacts=contacts)
        self.guide_contact_ticks+=int(guide>1.);self.hard_contact_ticks+=int(hard>1.)
        significant=[c for c in contacts if c['normal_N']>1.]
        if self.j200_first_contact is None and any(c['environment_geom']=='step270'for c in significant):self.j200_first_contact=dict(time_s=stage,contacts=significant)
        env=self.exact_support.step_envelope(self.d,StepPatch(top_z_m=HEIGHT))
        clear=env['both_rear_crossing_margin_m']>0 and env['both_entire_bottom_above_top_m']>0
        if clear and self.first_physics_mesh_clear is None:self.first_physics_mesh_clear=stage
        if clear and self.full_air_confirmed and self.first_air_mesh_clear is None:self.first_air_mesh_clear=stage
        self.audit_samples.append(dict(time_s=stage,root_post_time_s=float(self.d.time),main_normal_N2=main.tolist(),top_main_normal_N2=top.tolist(),guide_normal_N=guide,hard_other_normal_N=hard,all_world_normal_N=total,full_air_run_s=self.air_run,contacts=contacts))
