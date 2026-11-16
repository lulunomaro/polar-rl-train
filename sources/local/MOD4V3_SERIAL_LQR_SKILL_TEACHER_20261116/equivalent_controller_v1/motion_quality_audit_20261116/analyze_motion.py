"""Measured source/native motion comparison. No controller changes."""
from pathlib import Path
import numpy as np,json,mujoco as mj
P=Path(__file__).resolve().parent

def native(case_path=None,label='MOD4v3 current'):
 path=Path(case_path)if case_path is not None else P.parent/'tests/step200_capture_phaseplane_center';a=np.load(path/'trace.npz');x=a['trace'];m=mj.MjModel.from_xml_path(str(path/'scene.xml'));qa=np.array([m.jnt_qposadr[int(v[0])]for v in m.actuator_trnid]);va=np.array([m.jnt_dofadr[int(v[0])]for v in m.actuator_trnid]);length=[]
 for q,row in zip(a['qpos'],x):
  R=np.empty(9);mj.mju_quat2Mat(R,q[3:7]);v=(row[[[8,9,10],[11,12,13]]]-q[:3])@R.reshape(3,3);length.append(np.linalg.norm(v[:,[0,2]],axis=1))
 dc=json.loads((path/'STEP_DIAGNOSTICS.json').read_text());c=[r['contact']for r in dc]
 return dict(name=label,path=path,t=x[:,0],x=x[:,1],z=x[:,3],pitch=x[:,5],yaw=x[:,6],vx=a['qvel'][:,0],length=np.array(length),phases=a['phases'][:,0],qpos=a['qpos'],qvel=a['qvel'],requested=a['requested'],actual=a['actual'].reshape(-1,6),actual_t=(x[:,0,None]-.02+np.arange(1,9)[None,:]*.0025).reshape(-1),guide_v=np.array([v.get('guide_vertical_n',0.)for v in c]),guide_h=np.array([v.get('guide_horizontal_n',0.)for v in c]),mass=float(m.body_mass.sum()),control_dt=.02,physics_dt=.0025,model=m,qa=qa,va=va)

def source(name):
 path=P/name;a=np.load(path/'trace.npz');x=a['trace'];meta=json.loads((path/'MODEL.json').read_text());m=mj.MjModel.from_xml_path(meta['scene'])
 return dict(name=name,path=path,t=x[:,0],x=x[:,1],z=x[:,3],pitch=x[:,5],yaw=x[:,6],vx=x[:,7],length=x[:,9:11],phases=a['phases'],qpos=a['qpos'],qvel=a['qvel'],requested=a['requested'],actual=a['actual'],actual_t=x[:,0],guide_v=x[:,23],guide_h=x[:,24],mass=meta['mass_kg'],control_dt=meta['control_dt'],physics_dt=meta['physics_dt'],model=m,qa=np.array(meta['qa']),va=np.array(meta['va']))

def transitions(d):
 ph=d['phases'];return [dict(t=float(d['t'][i]),phase=str(ph[i]),x=float(d['x'][i]),z=float(d['z'][i]),pitch_deg=float(np.rad2deg(d['pitch'][i])),vx=float(d['vx'][i]),length_m=d['length'][i].tolist())for i in range(len(ph))if i==0 or ph[i]!=ph[i-1]]

def metrics(d):
 ts=transitions(d);lift=next(r['t']for r in ts if r['phase']=='lift');capture=next(r['t']for r in ts if r['phase']=='capture');swing=next(r['t']for r in ts if r['phase']=='swing');plant=next(r['t']for r in ts if r['phase']=='plant');window=(d['t']>=lift-.3)&(d['t']<=capture+.25);pre=(d['t']>=lift-.3)&(d['t']<lift);act=(d['actual_t']>=lift)&(d['actual_t']<=capture);torque=d['actual'][act,:4]
 # Compare the Cartesian trajectories and torque changes on the same 20 ms grid.
 grid=np.arange(lift,capture,.02);L=np.stack([np.interp(grid,d['t'],d['length'][:,i])for i in range(2)],axis=1);qmean=[]
 for time in grid:
  mask=(d['actual_t']>=time)&(d['actual_t']<time+.02);qmean.append(d['actual'][mask,:4].mean(axis=0))
 qmean=np.asarray(qmean);vel=np.diff(L,axis=0)/.02
 guide_grid=np.arange(lift-.3,capture+.25,.02);force=[]
 for time in guide_grid:
  mask=(d['t']>=time)&(d['t']<time+.02)
  if mask.any():force.append([d['guide_v'][mask].mean(),d['guide_h'][mask].mean()])
 force=np.array(force)
 row=dict(name=d['name'],mass_kg=d['mass'],physics_dt=d['physics_dt'],control_dt=d['control_dt'],lift_s=lift,swing_s=swing,plant_s=plant,capture_s=capture,lift_duration_s=swing-lift,swing_duration_s=plant-swing,lift_to_capture_s=capture-lift,pitch_at_lift_deg=next(x['pitch_deg']for x in ts if x['phase']=='lift'),pitch_peak_pre_lift_deg=float(np.rad2deg(abs(d['pitch'][pre])).max()),pitch_peak_climb_window_deg=float(np.rad2deg(abs(d['pitch'][window])).max()),vx_at_lift=next(x['vx']for x in ts if x['phase']=='lift'),root_x_change_lift_to_capture_m=float(np.interp(capture,d['t'],d['x'])-np.interp(lift,d['t'],d['x'])),base_min_z_m=float(d['z'][window].min()),leg_min_m=float(d['length'][window].min()),leg_retraction_peak_common20ms_mps=float(max(0.,-vel.min())),leg_extension_peak_common20ms_mps=float(max(0.,vel.max())),actual_leg_torque_peak_nm=float(abs(torque).max()),actual_leg_torque_near40_fraction=float(np.mean(abs(torque)>=39.6)),actual_leg_torque_rms_nm=float(np.sqrt(np.mean(torque**2))),leg_torque_mean20ms_step_rms_nm=float(np.sqrt(np.mean(np.diff(qmean,axis=0)**2))),guide_vertical_peak20ms_N=float(force[:,0].max()),guide_horizontal_peak20ms_N=float(force[:,1].max()),transitions=ts)
 if d['name'].startswith('MOD4'):
  a=np.load(d['path']/'trace.npz');mask=(d['t']>=lift)&(d['t']<=capture)
  row['native_projection_rms_nm']=np.sqrt(np.mean((a['feasible_requested'][mask,:4]-a['requested'][mask,:4])**2,axis=0)).tolist();row['native_interval_tracking_rms_nm']=np.sqrt(np.mean((a['actual'][mask,:,:4]-a['requested'][mask,None,:4])**2,axis=(0,1))).tolist()
 return row
if __name__=='__main__':
 datasets=[source('source_player_v030'),source('source_reference_v047'),native(),native(P/'native_yaw_only_cartesian_probe','MOD4 yaw-only Cartesian probe'),native(P/'native_direct_torque_counterfactual','MOD4 direct torque contract-invalid')];rows=[metrics(d)for d in datasets]
 (P/'MOTION_METRICS.json').write_text(json.dumps(dict(protocol='Motion audit; source independent reproductions, not user historical replay; common 20ms trajectory and force means; native torque uses 400Hz recorded samples; source torque uses 1kHz samples',rows=rows,strict_source_speed_match_failure=json.loads((P/'source_matched_entry/RESULT.json').read_text())),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 for r in rows:print(json.dumps(r,ensure_ascii=False))
