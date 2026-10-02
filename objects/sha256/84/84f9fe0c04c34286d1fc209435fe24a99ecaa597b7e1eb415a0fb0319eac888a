from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parent
old=np.load(r.parent/'MOD4_CONTACT_SAMPLING_FIX_20260930/legacy10ms.npz')
new=np.load(r/'integrated_probe.npz');v=new['values'];columns=list(new['columns'])
t=(np.arange(v.shape[0])+1)*.0005;tc=(np.arange(500)+1)*.01;e=3
fig,axes=plt.subplots(2,2,figsize=(12,7),layout='constrained')
m=(t>=2)&(t<=2.08);ax=axes[0,0]
ax.plot(t[m],v[m,e,columns.index('left_fz')],label='0.5ms physical force',lw=1)
bins=new['bin_history'][:,e,0,0,2]
mc=(tc>=2)&(tc<=2.08);ax.scatter(tc[mc],bins[mc],label='5ms mean at sampled endpoints',color='tab:orange',marker='s',s=28)
ax.set(title='Raw force and impulse-derived mean, +1.5m/s',ylabel='Left vertical force (N)',xlabel='Time (s)');ax.legend(fontsize=8)
ax=axes[0,1]
ax.plot(tc,old['height_credit'][:,e],label='Old endpoint-gated height credit',alpha=.8)
ax.plot(tc,new['height_credit'][:,e],label='Integrated-gated height credit',lw=1.8)
ax.set(title='Reward signal changed; frozen policy did not learn',ylabel='Unweighted credit',xlabel='Time (s)');ax.legend(fontsize=8)
ax=axes[1,0];ax.plot(t,v[:,e,columns.index('root_z')]*1000,label='Integrated candidate')
ax.plot(t,old['values'][:,e,columns.index('root_z')]*1000,ls='--',label='Old capture (identical)')
ax.set(title='Physical trajectory unchanged (all47 columns max diff=0)',ylabel='Root height (mm)',xlabel='Time (s)');ax.legend(fontsize=8)
ax=axes[1,1]
ax.plot(t[m],v[m,e,columns.index('left_gap')]*1000,label='Input-hull support gap')
low=(v[m,e,columns.index('left_force_norm')]<=1)&(v[m,e,columns.index('right_force_norm')]<=1)
ax.fill_between(t[m],0,1,where=low,alpha=.2,transform=ax.get_xaxis_transform(),label='Both forces <=1N')
ax.set(title='Unload and geometry evidence retained',ylabel='Left support gap (mm)',xlabel='Time (s)');ax.legend(fontsize=8)
fig.suptitle('MOD4 contact sampling repair | model7450 seed20260927 | diagnostic5s, not graduation')
fig.savefig(r/'sampling_evidence.png',dpi=150)
print(r/'sampling_evidence.png')
