import numpy as np,json,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('trace');args=p.parse_args();path=Path(args.trace);a=np.load(path);m=json.loads(Path(str(path)+'.json').read_text());dt=m['control_dt_s'];ids=list(a['env_ids']);motorids=[m['joint_names'].index(n) for n in m['motor_names']];rows=[]
def first_run(mask,count,start=0):
 mask=mask.copy();mask[:start]=False;r=0
 for i,v in enumerate(mask):
  r=r+1 if v else 0
  if r>=count:return round((i-count+2)*dt,4)
 return None
for j,eid in enumerate(ids):
 done=np.flatnonzero(a['done'][:,j]>0);end=int(done[0]) if len(done) else len(a['done']);q=a['q'][:end,j][:,motorids];qd=a['qd'][:end,j][:,motorids];target=a['wheel_target'][:end,j];leg=a['leg_target'][:end,j];comp=a['computed_torque'][:end,j];applied=a['applied_torque'][:end,j];fz=a['mean_fz'][:end,j].sum(1);tilt=np.rad2deg(np.arccos(np.clip(-a['gravity_b'][:end,j,2],-1,1)));v=a['root_vel_b'][:end,j,0];gap=a['support_gap'][:end,j].max(1);clip=(np.abs(comp[:,4:]-applied[:,4:])>.1).any(1);hiplim=(q[:,[1,3]]>.495)&(leg[:,[1,3]]>.55)
 onset={'sustained_hip_upper_stop_and_target_overrun':first_run(hiplim.any(1),10,50),'wheel_target_above_no_load':first_run((np.abs(target)>m['wheel_no_load']).any(1),5,50),'wheel_speed_near_no_load':first_run((np.abs(qd[:,4:])>.95*m['wheel_no_load']).any(1),5,50),'voltage_falloff_and_clipping':first_run(clip&(np.abs(qd[:,4:]).max(1)>44.0118718),10,50),'speed_error_above_0_375':first_run(np.abs(v+1.5)>.375,10,50),'tilt_above8deg':first_run(tilt>8,10,50),'gap_above5mm':first_run(gap>.005,3,50),'mean_vertical_load_below_half_weight':first_run(fz<14.22*9.81*.5,5,50),'guide_force_above10N':first_run(a['guide_force'][:end,j]>10,2,50)}
 segments=[]
 for lo,hi in [(0,.5),(.5,2),(2,5),(5,10),(10,15)]:
  x=int(lo/dt);y=min(end,int(hi/dt))
  if y<=x:continue
  segments.append({'time_s':[lo,min(hi,end*dt)],'v_mean':float(v[x:y].mean()),'v_error_mean':float(np.abs(v[x:y]+1.5).mean()),'tilt_mean_deg':float(tilt[x:y].mean()),'tilt_max_deg':float(tilt[x:y].max()),'wheel_target_range':list(map(float,[target[x:y].min(),target[x:y].max()])),'wheel_speed_abs_max':float(np.abs(qd[x:y,4:]).max()),'wheel_clip_any_fraction':float(clip[x:y].mean()),'hip_stop_fraction':hiplim[x:y].mean(0).tolist(),'gap_max_mm':float(gap[x:y].max()*1000),'mean_total_wheel_fz_N':float(fz[x:y].mean())})
 rows.append({'env_id':int(eid),'first_done_s':None if not len(done) else round((int(done[0])+1)*dt,4),'steps_before_first_done':end,'onsets_s':onset,'segments':segments})
result={'checkpoint':m['checkpoint'],'seed':m['seed'],'simulated_seconds_recorded':len(a['done'])*dt,'control_resolution_s':dt,'contact_resolution_s':m['raw_contact_dt_s'],'physical_trajectory_causality_not_proven_by_temporal_order':True,'rows':rows};path.with_suffix('.timeline.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
