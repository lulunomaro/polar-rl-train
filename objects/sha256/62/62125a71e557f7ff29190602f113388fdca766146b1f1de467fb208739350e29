from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

r=Path(__file__).parent
files={'original_4km_box':'reproduction.json','wheel_cap_only':'cap_reproduction.json',
       'isolated_200m_box':'small_ground_reproduction.json','isolated_native_plane':'native_plane_reproduction.json'}
out={'checkpoint':'model8350','seed':20260927,'num_envs':80,'steps':1500,
     'changed_factor_for_floor_trials':'Floor only; unchanged robot USD, motors, spring, solver, policy, reward and reset configuration.',
     'case_env_id':14,'rows':[]}
for label,name in files.items():
 x=json.loads((r/name).read_text());p=x['per_environment']
 row={'variant':label,'alive_15s':p['alive'][14]}
 for k in ['vel_error','tilt','max_tilt','left_gap_max_control_m','right_gap_max_control_m','longest_both_low_force_s_substep','wheel_effort_clip_fraction','leg_effort_clip_fraction','left_support_slip_control','right_support_slip_control']:
  row[k]=p[k][14]
 row['all_environments_alive']=all(p['alive']);row['max_closure_m']=x['max_closure_after_grace_m'];row['max_mimic_rad']=x['max_mimic_after_grace_rad']
 out['rows'].append(row)
raw=json.loads((r/'raw_partners8350.npz.raw_contacts.json').read_text())
neg=[q for q in raw if q['normal'][2]<-.9 and q['force_N']>1]
out['raw_first_invalid_ground_contact']=neg[0]
out['downward_ground_contact_count_in_4_9_to5_3s']={}
for label,prefix in [('original_4km_box','raw_partners8350'),('isolated_200m_box','small_ground8350'),('isolated_native_plane','native_plane8350')]:
 x=json.loads((r/(prefix+'.npz.raw_contacts.json')).read_text());out['downward_ground_contact_count_in_4_9_to5_3s'][label]=sum(q['normal'][2]<-.9 and q['force_N']>1 for q in x)
out['causal_scope']='The huge thin floor causes this reproducible contact failure. The exact PhysX numerical mechanism and all other historical failures are not established by this experiment.'
out['limitations']=['No retraining or PPO in floor probes.','15 seconds, one failing seed for causal probe; not long-duration/multiseed robustness.','Input hull support/slip sampled at10ms is not a contact manifold measurement.','Native floor candidate does not graduate legacy endpoint contact thresholds or certify2m/s constant/DR/Rough.']
(r/'floor_ab_comparison.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.grid':True,'grid.alpha':.25})
fig,axs=plt.subplots(4,1,figsize=(11,10),sharex=True,layout='constrained')
for fn,label,c in [('trace8350.npz','Original 4km thin box','#c33737'),('native_plane8350.npz','Native flat plane, same frozen policy','#1672a4')]:
 a=np.load(r/fn);j=list(a['env_ids']).index(14);done=np.flatnonzero(a['done'][:,j]>0);end=int(done[0]) if len(done) else len(a['done']);t=np.arange(1,end+1)*.01
 axs[0].plot(t,a['root_vel_b'][:end,j,0],c=c,label=label)
 tilt=np.rad2deg(np.arccos(np.clip(-a['gravity_b'][:end,j,2],-1,1)));axs[1].plot(t,tilt,c=c,label=label)
 axs[2].plot(t,a['mean_fz'][:end,j].sum(1),c=c,alpha=.75,label=label)
 axs[3].plot(t,a['support_gap'][:end,j].max(1)*1000,c=c,label=label)
axs[0].axhline(-1.5,c='black',ls='--',label='Command -1.5m/s');axs[1].axhline(8,c='gray',ls='--',label='8 degree target')
for ax,y in zip(axs,['Body velocity (m/s)','Body tilt (degree)','Both wheel load (N, 10ms mean)','Input-hull max support gap (mm)']):
 ax.set_ylabel(y);ax.axvline(5.0685,c='#6b2c91',ls=':');ax.legend(loc='upper left',fontsize=9)
axs[-1].set_xlabel('Simulation time (s)');fig.suptitle('MOD4 env14: floor-only counterfactual removes the reproduced failure\nmodel8350 / seed20260927 / unchanged robot and controller',fontsize=14)
fig.savefig(r/'floor_fix_comparison.png',dpi=150)
fig2,axs2=plt.subplots(2,1,figsize=(11,6),sharex=True,layout='constrained')
for prefix,label,c in [('raw_partners8350','Original box','#c33737'),('native_plane8350','Native plane','#1672a4')]:
 a=np.load(r/(prefix+'.npz'));f=a['partner_net_substep'][:,0,0,2];t=np.arange(1,len(f)+1)*.0005;sel=(t>=5.04)&(t<=5.12);axs2[0].plot(t[sel],f[sel],c=c,label=label)
 x=json.loads((r/(prefix+'.npz.raw_contacts.json')).read_text());sel=[q for q in x if q['wheel']==0 and 5.04<=q['time_s']<=5.12 and q['force_N']>1]
 axs2[1].scatter([q['time_s'] for q in sel],[q['normal'][2] for q in sel],s=12,c=c,label=label,alpha=.7)
axs2[0].set_ylabel('Left wheel Fz (N, .5ms)');axs2[1].set(ylabel='Raw contact normal Z',xlabel='Simulation time (s)');axs2[1].set_ylim(-1.15,1.15)
for ax in axs2:ax.axvline(5.0685,c='#6b2c91',ls=':');ax.legend(loc='upper left')
fig2.suptitle('Ground-contact artifact: incorrect downward normal / force\nUnfiltered PhysX raw contact actor: /World/ground/geometry/mesh',fontsize=13)
fig2.savefig(r/'raw_ground_contact_comparison.png',dpi=150)
