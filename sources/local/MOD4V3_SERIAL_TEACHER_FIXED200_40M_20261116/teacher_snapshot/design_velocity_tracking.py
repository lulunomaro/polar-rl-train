"""Native LQR velocity weight from the requested 20 mm/s tracking tolerance.
All MJCF A/B, equilibrium, state/control dimensions and source R stay unchanged.
"""
import json,time,numpy as np
from scipy.linalg import solve_discrete_are
from native_geometry import ROOT
start=time.perf_counter();data=np.load(ROOT/'native_full_mjcf_gains.npz');physical=json.loads((ROOT/'PHYSICAL_PARAMETERS.json').read_text());q=np.asarray(physical['source_Q']);q[5]=1./.02**2;Q=np.diag(q);R=np.asarray(physical['source_R']);Ks=[];poles=[]
for Ad,Bd in zip(data['Ad'],data['Bd']):
 P=solve_discrete_are(Ad,Bd,Q,R);K=np.linalg.solve(R+Bd.T@P@Bd,Bd.T@P@Ad);Ks.append(K);poles.append(abs(np.linalg.eigvals(Ad-Bd@K)))
arrays={k:data[k]for k in data.files};arrays['K']=np.asarray(Ks);arrays['poles']=np.asarray(poles);np.savez_compressed(ROOT/'native_velocity_tracking_gains.npz',**arrays)
(ROOT/'VELOCITY_TRACKING_DESIGN.json').write_text(json.dumps(dict(method='Same native full-MJCF LQR; velocity Bryson weight from 0.02 m/s tolerance',Q_old=physical['source_Q'],Q_new=q.tolist(),R=R.tolist(),max_pole=float(np.max(poles)),points=len(Ks),wall_seconds=time.perf_counter()-start,model_and_motor_limits_unchanged=True),indent=2)+chr(10));print('Velocity design max pole',float(np.max(poles)))
