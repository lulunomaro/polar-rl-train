from pathlib import Path
import sys,json,numpy as np
sys.stdout.reconfigure(encoding='utf8')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
ROOT=Path(__file__).parent
parts=json.loads((ROOT/'reports/cad_parts.json').read_text(encoding='utf8'))
ids=[111,119,120,124,129,134,144,145,146,147,148,149,183]
fig,ax=plt.subplots(figsize=(14,10),layout='constrained')
for k,i in enumerate(ids):
 p=parts[i];mesh=np.load(ROOT/f'reports/cad_cache/part_{i:03}.npz')
 v=mesh['vertices'][:,[2,1]]*[-1,1]
 ax.add_collection(PolyCollection(v[mesh['faces']],facecolors=plt.get_cmap('tab20')(k),edgecolors='none',alpha=.8))
 ax.text(-p['com_mm'][2],p['com_mm'][1],str(i),weight='bold')
 print(i,p['name'],'volume',round(p['volume_mm3']), 'bounds',np.round(p['bbox_mm'],3))
 for c in p['cylinders']:
  if abs(c['axis'][0])>.99999:
   print('   r',round(c['r'],4),'yz',np.round(c['p'][1:],5))
ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.3);ax.set_xlabel('-CAD Z (mm)');ax.set_ylabel('CAD Y (mm)')
fig.savefig(ROOT/'reports/leg_source.png',dpi=150)

# Other plan views to audit gearbox component ownership.
fig,axs=plt.subplots(1,2,figsize=(16,8),layout='constrained')
for ax,dims in zip(axs,[[0,1],[0,2]]):
 for k,i in enumerate(range(167,186)):
  mesh=np.load(ROOT/f'reports/cad_cache/part_{i:03}.npz');v=mesh['vertices'][:,dims]
  ax.add_collection(PolyCollection(v[mesh['faces']],facecolors=plt.get_cmap('tab20')(k),edgecolors='none',alpha=.7))
  ax.text(*np.array(parts[i]['com_mm'])[dims],str(i),fontsize=8)
 ax.autoscale();ax.set_aspect('equal');ax.grid(alpha=.3);ax.set_xlabel('CAD X mm');ax.set_ylabel(f'CAD {"XYZ"[dims[1]]} mm')
fig.savefig(ROOT/'reports/wheel_source.png',dpi=160)
