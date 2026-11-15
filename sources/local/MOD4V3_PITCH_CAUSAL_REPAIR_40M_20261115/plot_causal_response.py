"""Scientific figures from recorded counterfactual replay; no rerun of physics."""
from pathlib import Path
import numpy as np,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
T=Path(__file__).resolve().parent;E=T/'evidence';A=np.load(E/'causal_full/trajectories.npz')
variants=[('baseline','Hard-stop policy','#d24c46'),('hold_wheels_100ms','Hold wheels 100 ms','#2e8879'),('brake_ramp_4mps2','4 m/s2 command ramp','#426ab3')]
fig,axes=plt.subplots(3,2,figsize=(12,9),sharex=True);fig.patch.set_facecolor('white')
for col,(family,title) in enumerate([('random_uniform_for_rm','Level 9 random rough'),('plane_for_rm','Flat ground')]):
 for variant,label,color in variants:
  z=A[family+'_h0.4_v2.2_'+variant];q=(z[:,0]>=2.7)&(z[:,0]<=4.5)&(z[:,9]==0);t=z[q,0]-3.
  axes[0,col].plot(t,np.degrees(z[q,1]),color=color,label=label,lw=1.8)
  axes[1,col].plot(t,z[q,2],color=color,lw=1.8)
  axes[2,col].plot(t,z[q,5],color=color,lw=1.8)
 axes[0,col].set_title(title+' | height 0.40 m, command 2.2 -> 0 m/s',fontsize=11)
 for ax in axes[:,col]:
  ax.axvline(0,color='#777777',linestyle=':',lw=1);ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False)
 axes[2,col].axhline(0,color='#777777',linestyle=':',lw=1);axes[2,col].set_xlabel('Time from hard stop (s)')
axes[0,0].set_ylabel('Body pitch (degrees)');axes[1,0].set_ylabel('Pitch rate (rad/s)');axes[2,0].set_ylabel('Actual forward speed (m/s)')
axes[0,0].legend(fontsize=9,frameon=False);fig.suptitle('Frozen MOD4v3: the braking impulse precedes the pitch peak',fontsize=15,fontweight='bold')
fig.text(.075,.013,'Diagnostic interventions only. Identical states through -0.02 s; nominal MuJoCo, 2.5 ms, legs 100 Hz / wheels 400 Hz, 2 mm guard.',fontsize=8,color='#555555');fig.tight_layout(rect=[0,.03,1,.96]);fig.savefig(E/'causal_pitch_response.png',dpi=160);fig.savefig(E/'causal_pitch_response.pdf');plt.close(fig)
print(E/'causal_pitch_response.png')
