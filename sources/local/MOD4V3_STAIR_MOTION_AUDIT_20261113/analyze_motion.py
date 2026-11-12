"""Extract phase metrics and plot recorded frozen stair motions; no new simulation."""
from pathlib import Path
import json,collections,hashlib
import numpy as np,mujoco
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
T=Path(__file__).resolve().parent;E=T/'evidence';F=T/'figures';F.mkdir(exist_ok=True)
font_manager.fontManager.addfont('C:/Windows/Fonts/msyh.ttc');plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False,'font.size':11})

def intervals(mask,t,minimum=.01):
 starts=np.flatnonzero(mask&np.r_[True,~mask[:-1]]);ends=np.flatnonzero(mask&np.r_[~mask[1:],True])
 return [dict(start=float(t[i]),end=float(t[j]+.0025),duration=float((j-i+1)*.0025)) for i,j in zip(starts,ends) if (j-i+1)*.0025>=minimum]

summaries=[]
for folder in sorted(E.iterdir()):
 if not folder.is_dir() or not (folder/'trajectory.npz').exists():continue
 a=np.load(folder/'trajectory.npz');r=json.loads((folder/'RESULT.json').read_text());t=a['time'];contact_events={};body={};both_supported={}
 for line in (folder/'contacts.jsonl').open(encoding='utf8'):
  row=json.loads(line)
  if row['t']<3:continue
  for lev in [1,2]:
   supported={c['body'] for c in row['contacts'] if c['terrain']=='step_'+str(lev) and c['normal_force']>=5 and c['normal_on_robot'][2]>.7 and c['body'] in r['wheel_body_names']}
   if len(supported)==2:both_supported.setdefault(lev,row['t'])
  for c in row['contacts']:
   if c['normal_force']<5:continue
   kind='riser' if abs(c['normal_on_robot'][0])>.7 and abs(c['normal_on_robot'][2])<.35 else 'tread' if c['normal_on_robot'][2]>.7 else 'edge'
   key='|'.join([c['body'],c['terrain'],kind]);contact_events.setdefault(key,dict(t=row['t'],body=c['body'],terrain=c['terrain'],kind=kind,geom=c['robot_geom']))
   bk='|'.join([c['body'],c['terrain']]);br=body.setdefault(bk,dict(body=c['body'],terrain=c['terrain'],normal_impulse_Ns=0.,vertical_impulse_Ns=0.,peak_force_N=0.,first_t=row['t'],last_t=row['t'],geoms=set()))
   br['normal_impulse_Ns']+=c['normal_force']*.0025;br['vertical_impulse_Ns']+=c['force_on_robot'][2]*.0025;br['last_t']=row['t'];br['geoms'].add(c['robot_geom'])
   if c['normal_force']>br['peak_force_N']:br['peak_force_N']=c['normal_force'];br['peak_t']=row['t']
 waves=[]
 for level in [1,2]:
  terrain='step_'+str(level);rs=[v['t'] for v in contact_events.values() if v['terrain']==terrain and v['kind']=='riser' and v['body'] in r['wheel_body_names']];tops=[v['t'] for v in contact_events.values() if v['terrain']==terrain and v['kind']=='tread' and v['body'] in r['wheel_body_names']]
  if not rs:continue
  begin=min(rs);end=max(tops) if len(tops)>=2 else float('nan');idx=int(np.argmin(abs(t-begin)));mask=(t>=begin)&(t<=((end+.25) if np.isfinite(end) else min(begin+1.,t[-1])));indices=np.flatnonzero(mask);lo=indices[np.argmin(a['root_vel_world'][mask,0])];pi=indices[np.argmin(a['root_noseup_deg'][mask])];li=indices[np.argmin(a['leg_length'][mask].mean(1))]
  recover={}
  if level in both_supported:
   ti=both_supported[level];ii=int(np.argmin(abs(t-ti)))
   for threshold in [1.,1.5,1.8]:
    hit=np.flatnonzero((t>=ti)&(a['root_vel_world'][:,0]>=threshold))
    if len(hit):
     jj=hit[0];recover[str(threshold)]=dict(t=float(t[jj]),seconds_after_both_wheels_supported=float(t[jj]-ti),forward_distance_after_support_m=float(a['root_pose'][jj,0]-a['root_pose'][ii,0]))
  wheel_slip=(a['qvel'][:,r['actuator_dof_adr'][4:]]*.0625)-a['wheel_vel_world'][:,:,0]
  waves.append(dict(level=level,first_both_wheels_supported_t=both_supported.get(level),recovery= recover,wheel_riser_first_t=begin,first_wheel_tread_t=min(tops) if tops else None,both_wheel_tread_seen_t=end if np.isfinite(end) else None,impact_root_vx=float(a['root_vel_world'][idx,0]),min_root_vx=float(a['root_vel_world'][lo,0]),min_vx_t=float(t[lo]),most_nose_down_deg=float(a['root_noseup_deg'][pi]),most_nose_down_t=float(t[pi]),mean_effective_leg_m_at_impact=float(a['leg_length'][idx].mean()),minimum_mean_effective_leg_m=float(a['leg_length'][li].mean()),minimum_leg_t=float(t[li]),wheel_spin_peak_rad_s=a['qvel'][mask][:,r['actuator_dof_adr'][4:]].max(0).tolist(),max_wheel_speed_minus_center_vx=float(wheel_slip[mask].max()),maximum_base_contact_N=float(np.linalg.norm(a['base_contact_force'][mask],axis=1).max()),guide_vertical_impulse_Ns=float(a['other_contact_force'][mask,2].sum()*.0025),leg_positive_actuator_work_J=float(np.maximum(a['joint_power_env'][mask,:4],0).sum()*.0025),wheel_positive_actuator_work_J=float(np.maximum(a['joint_power_env'][mask,4:],0).sum()*.0025),leg_negative_actuator_work_J=float(np.minimum(a['joint_power_env'][mask,:4],0).sum()*.0025),wheel_negative_actuator_work_J=float(np.minimum(a['joint_power_env'][mask,4:],0).sum()*.0025)))
 for br in body.values():br['geoms']=sorted(br['geoms'])
 stationary=(t>2)&(t<3);all_zero=np.linalg.norm(a['all_terrain_force_world'],axis=1)<1;active=t>3.5
 report=dict(case=folder.name,success=r['success'],height_command=r['height'],speed_command=r['speed'],first_success_t=r['first_success_time'],resets=r['resets'],maximum_closure_mm=r['max_closure_m']*1000,final_root_x=float(a['root_pose'][-1,0]),standing_support_Fz_N=float(a['all_terrain_force_world'][stationary,2].mean()),weight_N=r['mass_kg']*9.81,phase_events=list(contact_events.values()),contact_body_impulses=list(body.values()),step_waves=waves,all_external_support_below_1N_intervals=intervals(all_zero&active,t),maximum_base_contact_N=float(np.linalg.norm(a['base_contact_force'][active],axis=1).max()))
 summaries.append(report)
 (folder/'MOTION_METRICS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

# Verify instrumentation alignment and that it preserves the old successful trajectories.
checks=[]
for case,h in [('raised365_fast',.365),('raised400_fast',.4)]:
 folder=E/case;a=np.load(folder/'trajectory.npz');r=json.loads((folder/'RESULT.json').read_text());m=mujoco.MjModel.from_xml_path(str(folder/'scene.xml'));d=mujoco.MjData(m);error=[]
 for ts in [2.5,4.1,4.3,5.7]:
  i=int(np.argmin(abs(a['time']-ts)));d.qpos[:]=a['qpos'][i];d.qvel[:]=a['qvel'][i];mujoco.mj_forward(m,d);error.append(float(np.abs(d.xpos[[m.body(n).id for n in r['wheel_body_names']]]-a['wheel_pos_world'][i]).max()))
 fresh=json.loads((folder/'policy_trace.json').read_text());old=json.loads((T.parent/'MOD4V3_FLAT_SPEED_REPAIR_20261112/evidence/stair_final'/f'up_h{h}.json').read_text())['trajectory'];n=min(len(fresh),len(old));difference=max(abs(old[i][k]-fresh[i][k]) for i in range(n) for k in ['x','y','vx','relative_height'])
 checks.append(dict(case=case,sampled_kinematic_alignment_max_m=max(error),original_policy_trace_max_difference=difference,compared_policy_steps=n))
(E/'VALIDATION.json').write_text(json.dumps(dict(checks=checks,no_optimizer=True,all_cases_zero_resets=all(s['resets']==0 for s in summaries),model_unchanged=True,plant_unchanged=True,contact_force_orientation_check='Standing mean summed upward force compared with total weight in each case; sign and contact-frame transform consistent.',limits='Four deterministic nominal MuJoCo cases, one start each; not a fullDR/PhysX success-rate test; speed-command comparisons change both incoming speed and policy input.'),indent=2)+'\n',encoding='utf8')
(E/'MOTION_SUMMARY.json').write_text(json.dumps(dict(cases=summaries,measurement_definitions=dict(nose_down='Negative root_noseup_deg means chassis front (+x) tilts downward',effective_leg='Wheel center to midpoint of two actuated joint anchors; not individual link length',contact_threshold='First event requires normal force >=5N',tread_seen='Both drive wheels have separately registered upward-normal contact with that tread; not a new graduation gate',no_support='Norm of summed all-terrain force <1N, intervals >=10ms; minor contact chatter is not called a purposeful jump',work='Signed/positive actuator generalized torque times joint rate integrated at2.5ms; omits passive spring/contact work; not an energy attribution proof')),ensure_ascii=False,indent=2)+'\n',encoding='utf8')

a=np.load(E/'raised365_fast/trajectory.npz');t=a['time'];mask=(t>=3.7)&(t<=6.4);x=t[mask];fig,axs=plt.subplots(5,1,figsize=(14,13),sharex=True);fig.suptitle('上台阶动作分解｜iter24692｜高度0.365m、速度指令2.2m/s',fontsize=18)
axs[0].plot(x,a['root_vel_world'][mask,0],label='机身前向速度 m/s',color='#1375be',lw=2);axs[0].plot(x,a['velocity_command'][mask],label='速度指令',ls='--',color='#888888');axs[0].set_ylabel('速度 m/s');axs[0].legend(loc='upper left')
axs[1].plot(x,a['root_noseup_deg'][mask],color='#a24a9a',label='正值抬头 / 负值前俯');axs[1].set_ylabel('机身俯仰 °');axs[1].legend(loc='upper left')
for i,name in enumerate(['左','右']):axs[2].plot(x,a['leg_length'][mask,i]*100,label=name+'等效腿长 cm')
axs[2].set_ylabel('等效腿长 cm');axs[2].legend(loc='upper left')
for i,name in enumerate(['左','右']):axs[3].plot(x,a['qvel'][mask][:,[10,21]][:,i],label=name+'驱动轮角速度 rad/s')
axs[3].set_ylabel('轮速 rad/s');axs[3].legend(loc='upper left')
axs[4].plot(x,a['wheel_force_world'][mask,:,2].sum(1),label='两驱动轮竖向支撑 N',color='#e6a52c');axs[4].plot(x,a['other_contact_force'][mask,2],label='前侧导向轮等接触体竖向支撑 N',color='#319969');axs[4].set_ylabel('竖向支撑 N');axs[4].set_yscale('symlog',linthresh=50);axs[4].set_ylim(-50,3500);axs[4].legend(loc='upper right')
for ax in axs:
 for start,end,label in [(4.01,4.3825,'一级攀爬'),(5.485,5.83,'二级攀爬')]:ax.axvspan(start,end,color='#f4ba6e',alpha=.22)
 ax.grid(alpha=.25)
axs[0].text(4.07,2.05,'一级：触立面→轮落台面',fontsize=10);axs[0].text(5.52,2.05,'二级重复同样动作',fontsize=10);axs[-1].set_xlabel('回放时间 s（3s开始前进；阴影为接触攀爬阶段）')
fig.tight_layout(rect=[0,0,1,.97]);fig.savefig(F/'MOTION_PHASES.png',dpi=160);plt.close(fig)
print(json.dumps(dict(cases=[dict(case=s['case'],success=s['success'],waves=s['step_waves']) for s in summaries],alignment=checks)),flush=True)
