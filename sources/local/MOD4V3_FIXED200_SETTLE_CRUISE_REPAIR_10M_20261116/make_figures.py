"""Plot stored closed-loop measurements only; no simulation or optimization."""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze_student import analyze
T=Path(__file__).resolve().parent;R=T.parents[2];S=R/'sources/local/MOD4V3_FIXED200_DAGGER_SEMANTIC_10M_20261116';O=T/'evidence/figures';O.mkdir(exist_ok=True)
curves=[]
for name,path,c in [('010m parent',S/'evidence/checkpoint_evals/model_010m','#777777'),('Repair 5 min',T/'evidence/checkpoint_evals/model_005m','#e68724'),('Repair 10 min',T/'evidence/checkpoint_evals/model_010m','#286ec8')]:
 diag=analyze(path);rows=sorted(diag['rows'],key=lambda x:x['start_offset_mm']);z=np.load(path/'single_step/start_+000mm/rollout.npz')['trace'];curves.append((name,c,rows,z))
fig,axes=plt.subplots(2,2,figsize=(12,7));offsets=np.array([-60,-30,0,30,60]);width=8
for j,(name,c,rows,z)in enumerate(curves):
 axes[0,0].bar(offsets+(j-1)*width,[r['zero_command_first_second_displacement_x_m']for r in rows],width,label=name,color=c)
 axes[0,1].bar(offsets+(j-1)*width,[r['entry_speed_m_s']if r['entry_speed_m_s']is not None else np.nan for r in rows],width,label='_nolegend_',color=c)
 missing=[k for k,r in enumerate(rows)if r['entry_speed_m_s']is None]
 if missing:axes[0,1].scatter((offsets+(j-1)*width)[missing],np.zeros(len(missing)),marker='x',s=35,color=c,zorder=5)
 axes[1,0].plot(z[:,0],z[:,1],color=c,label=name,lw=1.5);axes[1,1].plot(z[:,0],np.rad2deg(z[:,6]),color=c,label=name,lw=1.5)
axes[0,0].set_ylabel('Zero-command first-second\nX displacement (m)');axes[0,0].axhline(0,color='black',lw=.7);axes[0,1].set_ylabel('Actual stair entry speed (m/s)');axes[0,1].set_ylim(-.045,1.55);axes[0,1].axhline(.6,color='#b83434',ls='--',label='Acceptance cap 0.6 m/s');axes[0,1].axhline(.47,color='#168557',ls=':',label='Requested 0.47 m/s')
for ax in axes[0]:ax.set_xticks(offsets);ax.set_xlabel('Start offset (mm)')
axes[1,0].set_ylabel('Center case base X (m)');axes[1,0].axhline(1.2,color='black',ls=':',lw=.8);axes[1,1].set_ylabel('Center case pitch (deg)')
for ax in axes[1]:ax.set_xlabel('Actual simulation time (s), no time warping');ax.set_xlim(0,10)
for ax in axes.ravel():ax.grid(alpha=.2)
axes[0,0].legend(fontsize=8);axes[0,1].legend(fontsize=8);fig.suptitle('Same 200 mm stair, independent 35-to-6 students; settle/cruise sampling repair');fig.text(.5,.005,'Entry-speed cross markers: no recorded main-wheel stair contact, not zero-speed entry.',ha='center',fontsize=8);fig.tight_layout(rect=[0,.025,1,.96]);fig.savefig(O/'SETTLE_ENTRY_AND_MOTION_COMPARE.png',dpi=160);plt.close(fig);print('FIGURE_READY',O/'SETTLE_ENTRY_AND_MOTION_COMPARE.png')
