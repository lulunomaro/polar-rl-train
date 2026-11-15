"""Paired identical-length pitch/rate/speed comparison with the frozen db6 parent."""
from pathlib import Path
import numpy as np

def compare(parent_path,candidate_path):
 a=np.load(parent_path);b=np.load(candidate_path);rows=[]
 for k in a.files:
  if k not in b.files:raise ValueError('Missing pitch case '+k)
  n=min(len(a[k]),len(b[k]));x=a[k][:n];y=b[k][:n]
  if not np.allclose(x[:,0],y[:,0]):raise ValueError('Mismatched simulated timestamps')
  valid=x[:,0]>=2.;moving=valid&(x[:,9]>.5);startup=moving&(x[:,10]<.8);brake=valid&(x[:,9]<.5)&(x[:,10]>=1)&(x[:,10]<1.8)
  def peak(z,mask,col,deg=False):
   v=float(np.abs(z[mask,col]).max()) if mask.any() else None
   return float(np.rad2deg(v)) if v is not None and deg else v
  def metrics(z):return dict(pitch_RMS_deg=float(np.rad2deg(np.sqrt(np.mean(z[valid,1]**2)))),startup_pitch_peak_deg=peak(z,startup,1,True),braking_pitch_peak_deg=peak(z,brake,1,True),rate_RMS_rad_s=float(np.sqrt(np.mean(z[valid,2]**2))),startup_rate_peak_rad_s=peak(z,startup,2),braking_rate_peak_rad_s=peak(z,brake,2),moving_vx_MAE=float(np.mean(abs(z[moving,4]-z[moving,3]))))
  rows.append(dict(case=k,common_horizon_s=float(x[-1,0]),samples=n,parent=metrics(x),candidate=metrics(y)))
 summary={}
 for fam in ['random_uniform_for_rm','plane_for_rm']:
  selected=[r for r in rows if r['case'].startswith(fam)];group={}
  for side in ['parent','candidate']:
   keys=selected[0][side].keys();group[side]={k:float(max(r[side][k] for r in selected) if 'peak' in k else np.mean([r[side][k] for r in selected])) for k in keys}
  summary[fam]=group
 return dict(rows=rows,summary=summary,protocol='Compare common timestamps from2s to minimum first-episode duration for each of8 fixed cases; same nominal0ms scene and commands. Map exit is not a fall. No graduation assertion.')
