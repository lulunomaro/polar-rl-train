"""Retained method of the completed inline plot; source only, do not execute again."""
from pathlib import Path
import numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(r'C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOE_SMALL_CURB_CONTACT_REPLAY_20261024')
sets=[('Original collision path','actual_contact_V3_4090/out/E0_vx_0p65.npz','#bf4545'),('Native CCD off','actual_contact_V4_4090/out/E0_native_off_vx_0p65.npz','#8a7caf'),('MultiCCD off candidate','actual_contact_V5_4090/out/E0_multi_off_vx_0p65.npz','#007f83')]
fig,axes=plt.subplots(2,1,figsize=(10,6.4),sharex=True,layout='constrained')
for label,relative,color in sets:
    with np.load(D/relative) as z:p=z['physics'];t=p[:,0];vz=p[:,6];tilt=np.degrees(np.arccos(np.clip(p[:,10],-1,1)))
    axes[0].plot(t,vz,label=label,color=color,lw=1.1)
    axes[1].plot(t,tilt,label=label,color=color,lw=1.3)
axes[0].set_ylabel('Root vertical velocity (m/s)');axes[0].legend(loc='upper left',frameon=False,ncol=1)
axes[0].set_title('Fixed E0 at 0.65 m/s: recorded collision-triggered launch',loc='left',fontweight='bold')
axes[1].set_ylabel('Tilt from world upright (degrees)');axes[1].set_xlabel('Simulation time (s)')
axes[1].axhline(np.degrees(np.arccos(.6)),color='#808080',ls='--',lw=.9)
axes[1].text(4.95,54.1,'Original UI fall limit',ha='right',fontsize=8,color='#555555')
for ax in axes:ax.grid(alpha=.18);ax.spines[['top','right']].set_visible(False);ax.set_xlim(0,5)
fig.supxlabel('Same initial pose, terrain, actors, gains and commands. Finite comparison; not all-terrain qualification.',fontsize=9)
# Actual completed output path/SHA/size are in SAVED_CONTACT_COMPARISON_PLOT_PRODUCER_ACTUAL.json.
