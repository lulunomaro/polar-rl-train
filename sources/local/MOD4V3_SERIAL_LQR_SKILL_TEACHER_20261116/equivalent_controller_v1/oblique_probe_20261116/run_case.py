from pathlib import Path
import sys,json,hashlib,shutil,numpy as np
P=Path(__file__).resolve().parent;E=P.parent
sys.path.insert(0,str(E))
import run_teacher as rt
BaseTeacher=rt.NativeTeacher
class ObliqueTeacher(BaseTeacher):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs)
  angle=float(kwargs.get('yaw',0.));c=self.controller
  c.initial_target_yaw=c.target_yaw=angle
  if c.reference_governor is not None:
   c.reference_governor.initial_yaw=c.reference_governor.yaw=angle
  (self.output/'HEADING_COMMAND.json').write_text(json.dumps(dict(initial_yaw_rad=angle,target_yaw_rad=c.target_yaw,governor_yaw_rad=c.reference_governor.yaw,controller_gains_unchanged=True),indent=2)+chr(10),encoding='utf8')
rt.NativeTeacher=ObliqueTeacher
case=json.loads(sys.argv[1]);out=P/case['name'];out.mkdir(exist_ok=False)
files=['native_contact_latch.py','sim/controller.py','sim/step_climb.py','native_runtime.py','native_contacts.py','native_actuation.py','run_teacher.py','data/lqr_gain_fit.py','native_geometry.py']
for rel in files:
 dst=out/'code'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(E/rel,dst)
(out/'SOURCE.json').write_text(json.dumps({rel:hashlib.sha256((E/rel).read_bytes()).hexdigest()for rel in files},indent=2)+chr(10),encoding='utf8')
r=rt.run(case,out)
a=np.load(out/'trace.npz');f=a['trace'];v=a['qvel'][:,:2];t=f[:,0];angle=np.deg2rad(case['yaw_deg']);axis=np.array([np.cos(angle),np.sin(angle)]);forward=v@axis;position=f[:,1:3]@axis;error=np.rad2deg(np.arctan2(np.sin(f[:,6]-angle),np.cos(f[:,6]-angle)));post=t>=2.;entry=r.get('entry');mask=np.zeros(len(t),bool)
if entry is not None:mask=(t>=entry['time']-.100001)&(t<entry['time']-1e-6)
entry_heading=None if not mask.any()else float(np.rad2deg(np.arctan2(np.mean(np.sin(f[mask,6])),np.mean(np.cos(f[mask,6])))))
travel_heading=None if not mask.any()else float(np.rad2deg(np.arctan2(v[mask,1].mean(),v[mask,0].mean())))
heading_ok=bool(post.any()and abs(error[post]).max()<=5.)
entry_angle_ok=bool(entry_heading is not None and abs(entry_heading-case['yaw_deg'])<=5. and abs(entry_heading)>=.7*abs(case['yaw_deg']))
final_top=bool(np.all(f[-1,16:18]>.5))
since=np.ones(len(t),bool)if entry is None else t>=entry['time'];p=position[since]
z=dict(case=case,pass_oblique=bool(r['pass_stair']and r['entry_speed_qualified']and heading_ok and entry_angle_ok and final_top),stable_top_s=r['max_continuous_top_hold_s'],final_top=final_top,entry_angle_valid=entry_angle_ok,entry_body_yaw_deg=entry_heading,entry_travel_heading_deg=travel_heading,entry_speed_mps=None if entry is None else entry['pre_100ms_speed'],entry_forward_speed_mps=None if not mask.any()else float(forward[mask].mean()),heading_error_peak_deg=float(abs(error[post]).max())if post.any()else None,pitch_peak_deg=float(np.rad2deg(abs(f[since,5])).max()),roll_peak_deg=float(np.rad2deg(abs(f[since,4])).max()),min_forward_speed_mps=float(forward[since].min()),max_backward_mm=float(np.max(np.maximum.accumulate(p)-p)*1000),final_position=r['final_position'],phase_transitions=r['phase_transitions'],raw_straight_heading_pass=r['pass_teacher_stair'],raw_straight_heading_pass_is_applicable=False,actor_calls=r['actor_calls'],optimizer_steps=r['optimizer_steps'],error=r['error'])
(out/'OBLIQUE_EVAL.json').write_text(json.dumps(z,ensure_ascii=False,indent=2)+chr(10),encoding='utf8')
print('OBLIQUE',json.dumps(z,ensure_ascii=False),flush=True)
