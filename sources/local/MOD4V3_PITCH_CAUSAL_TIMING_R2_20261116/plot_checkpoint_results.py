"""Plot all stored checkpoint results after the combined report is available."""
from pathlib import Path
import json,re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
T=Path(__file__).resolve().parent;d=json.loads((T/'evidence/COMBINED_RESULT.json').read_text());rows=[];seen=set()
for r in d['checkpoints']:
 key=(r['stage'],r['sha256'])
 if key in seen:continue
 seen.add(key)
 if r['checkpoint']=='model_final':minute=d['phase1_seconds']/60 if r['stage'].endswith('REPAIR_40M_20261115')else d['total_PPO_seconds']/60
 else:minute=int(re.search(r'model_(\d+)m',r['checkpoint']).group(1))
 p=r['full_14s_protocol_summary'];rows.append((minute,p['random_uniform_for_rm']['braking_peak_deg_max'],p['plane_for_rm']['braking_peak_deg_max'],r['skills']['straight5']))
rows.sort();x=[r[0]for r in rows];fig,axes=plt.subplots(3,1,figsize=(10.5,8),sharex=True)
for ax in axes:
 ax.axvspan(d['phase1_seconds']/60,40.1,color='#eaf1fc',zorder=0);ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False)
axes[0].plot(x,[r[1]for r in rows],'-o',color='#c74f43',lw=2,markersize=5);axes[0].axhline(19.2122663117362,color='#777777',ls='--',lw=1,label='Starting checkpoint ~19.21 deg');axes[0].set_ylabel('Rough braking peak (deg)');axes[0].legend(loc='upper left',frameon=False,fontsize=9)
axes[1].plot(x,[r[2]for r in rows],'-o',color='#426fa8',lw=2,markersize=5);axes[1].axhline(17.99,color='#777777',ls='--',lw=1);axes[1].set_ylabel('Flat braking peak (deg)')
axes[2].plot(x,[r[3]for r in rows],'-o',color='#31846f',lw=2,markersize=5);axes[2].axhline(4,color='#777777',ls='--',lw=1);axes[2].set_ylim(0,5.5);axes[2].set_yticks([0,1,2,3,4,5]);axes[2].set_ylabel('Straight stairs passed / 5');axes[2].set_xlabel('Cumulative PPO training (minutes)')
axes[0].set_title('MOD4v3: pitch reductions did not remain stable across checkpoints',fontsize=14,fontweight='bold',pad=16)
axes[0].text(.99,.95,'Blue background: corrected reward timing',transform=axes[0].transAxes,ha='right',va='top',fontsize=9,color='#526c95')
fig.text(.08,.015,'Original fixed nominal replay maxima. All full trajectories retained; equal 2.00-7.98 s selection comparisons are in COMBINED_RESULT.json.',fontsize=8,color='#555555');fig.tight_layout(rect=[0,.035,1,1]);fig.savefig(T/'evidence/checkpoint_learning_curve.png',dpi=160);fig.savefig(T/'evidence/checkpoint_learning_curve.pdf');plt.close(fig);print(T/'evidence/checkpoint_learning_curve.png')
