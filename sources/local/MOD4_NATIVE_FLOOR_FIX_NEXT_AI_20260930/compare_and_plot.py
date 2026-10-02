from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

r=Path(__file__).parent
a=np.load(r/'trace8350.npz');b=np.load(r/'cap8350.npz')
m=json.loads((r/'trace8350.npz.json').read_text())
j=list(a['env_ids']).index(14);dt=m['control_dt_s']
out={'checkpoint':m['checkpoint'],'seed':m['seed'],'intervention':'Only env14 wheel targets capped at +/-35 rad/s from decision t=5.07s; no physics/PPO change.',
     'pre_intervention_end_state_time_s':5.07,'pre_intervention_max_abs_difference':{}}
for k in a.files:
 if k!='env_ids' and k in b and a[k].ndim>1:
  out['pre_intervention_max_abs_difference'][k]=float(np.max(np.abs(a[k][:507].astype(float)-b[k][:507].astype(float))))
out['all_pre_intervention_arrays_exactly_equal']=all(x==0 for x in out['pre_intervention_max_abs_difference'].values())
def metrics(x,lo,hi):
 done=np.flatnonzero(x['done'][:,j]>0);end=min(len(x['done']),int(done[0]) if len(done) else len(x['done']))
 sl=slice(int(lo/dt),min(end,int(hi/dt)))
 v=x['root_vel_b'][sl,j,0];tilt=np.rad2deg(np.arccos(np.clip(-x['gravity_b'][sl,j,2],-1,1)))
 clip=np.any(abs(x['computed_torque'][sl,j,4:]-x['applied_torque'][sl,j,4:])>.1,axis=1)
 return {'first_done_s':None if not len(done) else float((done[0]+1)*dt),'interval_s':[lo,min(hi,end*dt)],
     'speed_mean_m_s':float(v.mean()),'speed_error_mean_m_s':float(abs(v+1.5).mean()),
     'tilt_mean_deg':float(tilt.mean()),'tilt_max_deg':float(tilt.max()),'wheel_clip_any_fraction':float(clip.mean()),
     'gap_max_control_mm':float(x['support_gap'][sl,j].max()*1000),'wheel_fz_sum_mean_N':float(x['mean_fz'][sl,j].sum(1).mean()),
     'longest_both_low_force_ms':float(x['off_max_s'][sl,j].max()*1000),
     'wheel_target_abs_max_rad_s':float(abs(x['wheel_target'][sl,j]).max()),
     'max_closure_m':float(x['closure'][sl,j].max()),'max_mimic_rad':float(x['mimic'][sl,j].max())}
out['baseline_5_to10']=metrics(a,5,10);out['counterfactual_5_to10']=metrics(b,5,10)
out['baseline_10_to15']=metrics(a,10,15);out['counterfactual_10_to15']=metrics(b,10,15)
out['conclusion']='The cap suppresses wheel saturation and overspeed but does not restore upright posture. It is not an acceptable production repair; contact-origin diagnosis is required.'
(r/'cap_comparison.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.grid':True,'grid.alpha':.25,'figure.facecolor':'white'})
fig,axes=plt.subplots(5,2,figsize=(14,13),sharex='col',layout='constrained')
wheelidx=[m['joint_names'].index(n) for n in m['motor_names'][4:]]
for col,(x,label) in enumerate([(a,'Original model8350'),(b,'Isolated wheel target cap 35 rad/s')]):
 done=np.flatnonzero(x['done'][:,j]>0);end=int(done[0]) if len(done) else len(x['done']);t=np.arange(1,end+1)*dt
 axes[0,col].plot(t,x['root_vel_b'][:end,j,0],label='Body forward velocity');axes[0,col].axhline(-1.5,c='k',ls='--',label='Command -1.5');axes[0,col].set(title=label,ylabel='Velocity (m/s)')
 for w,c in enumerate(['#1264a3','#da7b00']):
  axes[1,col].plot(t,x['qd'][:end,j,wheelidx[w]],c=c,label=['Left actual','Right actual'][w]);axes[1,col].plot(t,x['wheel_target'][:end,j,w],c=c,ls='--',alpha=.65,label=['Left target','Right target'][w])
 axes[1,col].axhline(-m['wheel_no_load'],c='gray',ls=':',label='Motor no-load speed');axes[1,col].set_ylabel('Wheel speed (rad/s)')
 tilt=np.rad2deg(np.arccos(np.clip(-x['gravity_b'][:end,j,2],-1,1)));axes[2,col].plot(t,tilt,c='#b4312d',label='Body tilt');axes[2,col].axhline(8,c='gray',ls='--',label='8 degree target');axes[2,col].set_ylabel('Tilt (degree)')
 for w,c in enumerate(['#1264a3','#da7b00']):axes[3,col].plot(t,x['mean_fz'][:end,j,w],c=c,label=['Left mean Fz','Right mean Fz'][w])
 axes[3,col].set_ylabel('Wheel load (N / 10ms mean)')
 for w,c in enumerate(['#1264a3','#da7b00']):axes[4,col].plot(t,x['support_gap'][:end,j,w]*1000,c=c,label=['Left support gap','Right support gap'][w])
 axes[4,col].set(ylabel='Input-hull gap (mm)',xlabel='Simulation time (s)')
 for ax in axes[:,col]:ax.axvline(5.07,c='#6b2c91',ls=':',lw=1.5);ax.legend(loc='upper left',fontsize=8,ncol=2)
fig.suptitle('MOD4 backwards instability: same checkpoint / seed / initial state\nPurple line: shock at 5.07s; clipping intervention begins at next control decision',fontsize=14)
fig.savefig(r/'backward_failure_comparison.png',dpi=150)
