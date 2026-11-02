"""Copyunchangedactuationkernelwithread-onlyphysics-ratecontact audit hook.
AllnewauditfieldsaregradingONLY; nocontroller/sensorpacket reads them.
"""
from pathlib import Path
import ast
R=Path(__file__).resolve().parent;original=(R/'physics_bridge_v3.py').read_text(encoding='utf-8');method=original[original.index(' def apply_torque_request('):];needle='    hit=False\n';assert needle in method;method=method.replace(needle,'    self._grade_contact_sample()\n'+needle)
head='''"""Instrumentation-onlybridge. Cachesensors/actuationidenticaltoV3; read-onlycontactgrading."""
import numpy as np,mujoco
from physics_bridge_v4_grade import BufferedImuPlant
class ContactAuditPlant(BufferedImuPlant):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.audit_armed=False;self.audit_samples=[];self.air_run=0.;self.max_full_air=0.;self.full_air_confirmed=False;self.first_full_air=None;self.first_landing=None;self.guide_contact_ticks=0;self.hard_contact_ticks=0
 def _grade_contact_sample(self):
  if not self.audit_armed:return
  contacts=[];main=np.zeros(2);guide=0.;hard=0.;world={self.m.geom('ground').id,self.m.geom('step270').id}
  for ci,ct in enumerate(self.d.contact):
   a,b=int(ct.geom1),int(ct.geom2)
   if a not in world and b not in world:continue
   robot=b if a in world else a;env=a if a in world else b;force=np.zeros(6);mujoco.mj_contactForce(self.m,self.d,ci,force);fn=max(0.,float(force[0]))
   if fn<=1.:continue
   name=self.m.geom(robot).name;kind='main_wheel'if robot in self.tires else'guide_roller'if name.startswith('guide_wheel_')else'hard_other'
   if kind=='main_wheel':main[self.tires.index(robot)]+=fn
   elif kind=='guide_roller':guide+=fn
   else:hard+=fn
   contacts.append(dict(robot_geom=name,robot_body=self.m.body(int(self.m.geom_bodyid[robot])).name,environment_geom=self.m.geom(env).name,normal_N=fn,kind=kind))
  stage=max(0.,float(self.d.time)-self.dt);total=float(main.sum())+guide+hard
  self.air_run=self.air_run+self.dt if total<=1. else 0.;self.max_full_air=max(self.max_full_air,self.air_run)
  if not self.full_air_confirmed and self.air_run>=.02:self.full_air_confirmed=True;self.first_full_air=stage-self.air_run+self.dt
  if self.full_air_confirmed and self.first_landing is None and total>1.:self.first_landing=dict(time_s=stage,contacts=contacts)
  self.guide_contact_ticks+=guide>1.;self.hard_contact_ticks+=hard>1.;self.audit_samples.append(dict(time_s=stage,main_normal_N2=main.tolist(),guide_normal_N=guide,hard_other_normal_N=hard,all_ground_force_N=total,fullair_run_s=self.air_run,contacts=contacts))
'''
s=head+method;ast.parse(s);p=R/'physics_bridge_contact_audit_v1.py';assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
source=(R/'run_jump270_roll_v3.py').read_text(encoding='utf-8').replace('from physics_bridge_v4_grade import BufferedImuPlant','from physics_bridge_contact_audit_v1 import ContactAuditPlant as BufferedImuPlant').replace("ROOT/'sensor_core_jump_v1.py',", "ROOT/'sensor_core_jump_v1.py',ROOT/'physics_bridge_contact_audit_v1.py',ROOT/'physics_bridge_v3.py',");source=source.replace('p.apply_torque_request(tau,packet);','p.audit_armed=launch is not None;p.apply_torque_request(tau,packet);')
needle="result['raw_trace']=";assert needle in source;extra="""ah=hashlib.sha256();an=0
  with(out/'physics_contact_audit.jsonl').open('xb')as af:
   for ar in p.audit_samples:
    ab=(json.dumps(ar,separators=(',',':'))+'\\n').encode();af.write(ab);ah.update(ab);an+=len(ab)
  result['physics_contact_audit']=dict(path=str(out/'physics_contact_audit.jsonl'),bytes=an,SHA=ah.hexdigest(),rate_hz=1/p.dt,stage_time_explicit=True,first_full_air_s=p.first_full_air,max_full_air_s=p.max_full_air,first_landing=p.first_landing,guide_contact_ticks=p.guide_contact_ticks,hard_other_contact_ticks=p.hard_contact_ticks);"""
source=source.replace(needle,extra+needle);ast.parse(source);rp=R/'run_jump270_audit_v1.py';assert not rp.exists();rp.write_text(source,encoding='utf-8',newline='\n');print('CONTACT_AUDIT_NEW_SOURCE_0PHYSICS_STEPS')
