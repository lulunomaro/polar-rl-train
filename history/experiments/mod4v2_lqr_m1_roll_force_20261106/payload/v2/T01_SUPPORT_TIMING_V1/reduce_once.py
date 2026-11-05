"""One reduction of NEW v2 failure only. No model construction or physics replay.
Contact truth is joined for private analysis, never used as a controller input.
Unlogged gyro is zero only in the replay where configured roll gains are zero;
requested-torque agreement is measured, not assumed. Output is not a new case.
"""
from pathlib import Path
from types import SimpleNamespace
import sys,json,math
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
D=Path(__file__).resolve().parent;O=D/'reduction001';O.mkdir(exist_ok=False)
C=R/'T01_V2/runs/v2_t01_nominal_slow_520111_001'
(O/'START.json').write_text(json.dumps(dict(case=str(C),old_cases_read=0,physics_steps=0,input_passes_each=1)),encoding='utf-8')
from runtime_v2 import bridge,GroundController,geometry
V1=R.parent/'mod4v1_lqr_mpc_robust_20261102'
g=geometry();gain=bridge.load_gain(R/'nominal_gain_v2.json')
cfg=json.loads((V1/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json').read_text(encoding='utf-8'))['controller']
ctl=GroundController(gain,cfg,geometry=g)
assert ctl.roll_kp==0 and ctl.roll_kd==0

def kinematic(q,qd,side):
 _,r,J,_=g.wheel_kinematics(float(q[0]),float(q[1]),float(qd[0]),float(qd[1]),0.,np.zeros(3),side)
 r=np.asarray(r)[[0,2]];J=np.asarray(J)[[0,2],:];l=float(np.linalg.norm(r))
 T=np.vstack([(r/l)@J,np.array([-r[1],r[0]])@J/(l*l)])
 return l,T,float(T[0]@qd)
def stat(a):
 a=np.asarray(a,float)
 if a.size==0:return None
 return dict(n=int(a.size),mean=float(a.mean()),rms=float(np.sqrt(np.mean(a*a))),min=float(a.min()),p50=float(np.quantile(a,.5)),p95=float(np.quantile(a,.95)),max=float(a.max()))
rows=[];replay_error=0.;pdF=[];stiffness=[]
with (C/'trace.jsonl').open(encoding='utf-8')as f:
 for line in f:
  r=json.loads(line);x=np.asarray(r['estimated14'],float);age=max(0.,r['command_time_s']-r['sensor_time_s'])
  e=SimpleNamespace(state14=x,roll=float(r['estimated_roll']),omega_body=np.zeros(3),sensor_age_s=age)
  tau=ctl.command(e,*r['command']);replay_error=max(replay_error,float(np.max(np.abs(tau-np.asarray(r['requested_tau6_Nm'])))))
  qL=x[[3,4]].copy();qL[1]+=qL[0];qR=x[[5,6]].copy();qR[1]+=qR[0]
  vL=x[[10,11]].copy();vL[1]+=vL[0];vR=x[[12,13]].copy();vR[1]+=vR[0]
  qrL=np.array([ctl.ref[3],ctl.ref[3]+ctl.ref[4]]);qrR=np.array([ctl.ref[5],ctl.ref[5]+ctl.ref[6]])
  lL,TL,ldL=kinematic(qL,vL,'left');lR,TR,ldR=kinematic(qR,vR,'right')
  lrL=kinematic(qrL,np.zeros(2),'left')[0];lrR=kinematic(qrR,np.zeros(2),'right')[0]
  T=.5*(TL+TR);pd=.5*(ctl.leg_kp*((qrL-qL)-(qrR-qR))-ctl.leg_kd*(vL-vR))
  ft=np.linalg.solve(T.T,pd);inv=np.linalg.inv(T);K=inv.T@(ctl.leg_kp*np.eye(2))@inv
  raw_delta=[float(x[4]+(tau[1]-tau[0]+2*x[11])/60.),float(x[6]+(tau[4]-tau[3]+2*x[13])/60.)]
  rows.append(dict(k=r['control_index'],t=r['command_time_s'],roll_error=float(e.roll-r['post_truth']['roll_true']),
   estimated_roll=e.roll,truth_roll=float(r['post_truth']['roll_true']),req=tau.tolist(),applied_endpoint=r['last_substep_applied_tau6_Nm'],
   axial_diff_N=float(ft[0]),angle_diff_Nm=float(ft[1]),effective_axial_K_N_m=float(K[0,0]),
   axial_length_error_m=float(.5*((lrL-lL)-(lrR-lR))),axial_velocity_diff_m_s=float(.5*(ldL-ldR)),
   raw_inverse_PD_target_delta2=raw_delta,progress_m=r['progress_m']))
  pdF.append(float(ft[0]));stiffness.append(float(K[0,0]))
assert len(rows)==1200
samples=[]
with (C/'contact_trace.jsonl').open(encoding='utf-8')as f:
 for line in f:
  r=json.loads(line);tick=int(round(float(r['time_s'])/.0005));k=tick//20
  sets=[]
  for side in ('left_tire','right_tire'):
   sets.append(tuple(sorted({int(x['environment_geom_id'])for x in r['contacts']if x['robot_geom']==side})))
  samples.append(dict(t=float(r['time_s']),tick=tick,k=k,sub=tick%20,n=r['main_normal_N2'],all=float(r['all_environment_positive_normal_N']),sets=sets))
assert len(samples)==20000 and samples[0]['tick']==4000 and samples[-1]['tick']==23999
N=np.asarray([s['n']for s in samples]);alln=np.array([s['all']for s in samples]);low=N<=1.;air=alln<=1.
phases=[]
for name,a,b in [('accel',2,3),('steady',3,7),('late_drive',7,8),('brake',8,9),('stopped',9,12)]:
 ids=[i for i,s in enumerate(samples)if a<=s['tick']*.0005<b];ii=np.array(ids,int);ks=sorted({samples[i]['k']for i in ids})
 phases.append(dict(phase=name,bounds_s=[a,b],physics_samples=len(ids),left_low=int(low[ii,0].sum()),right_low=int(low[ii,1].sum()),allair=int(air[ii].sum()),
  mean_normal_N2=N[ii].mean(axis=0).tolist(),max_normal_N2=N[ii].max(axis=0).tolist(),
  replayed_axial_diff_N=stat([rows[k]['axial_diff_N']for k in ks]),roll_estimation_error_rad=stat([rows[k]['roll_error']for k in ks])))
seams=[]
for side in (0,1):
 prev=[-1]*len(samples);nxt=[-1]*len(samples);last=-1
 for i in range(len(samples)):
  prev[i]=last
  if not low[i,side]:last=i
 last=-1
 for i in range(len(samples)-1,-1,-1):
  nxt[i]=last
  if not low[i,side]:last=i
 total=near=changed=0
 for i in np.flatnonzero(low[:,side]):
  total+=1;a,b=prev[i],nxt[i]
  if a>=0 and b>=0 and i-a<=4 and b-i<=4:
   near+=1;changed+=int(samples[a]['sets'][side]!=samples[b]['sets'][side])
 seams.append(dict(low_ticks=total,bracketed_by_support_within_2ms_each_side=near,positive_force_environment_set_changed_between_brackets=changed,
  interpretation='Correlation of positive-force sets, not geometric gap/contact-existence or cause proof'))
peaks=[]
for i in np.argsort(N[:,0])[-6:][::-1]:
 s=samples[int(i)];rr=rows[s['k']]
 peaks.append(dict(time_s=s['t'],substep=s['sub'],main_normal_N2=s['n'],positive_force_sets=s['sets'],control=rr,
  adjacent_normals_N2=N[max(0,i-2):min(len(N),i+3)].tolist()))
req=np.array([r['req']for r in rows]);app=np.array([r['applied_endpoint']for r in rows]);eff=np.array([40,40,5.775909774436091]*2)
clip_projection=sum(any(v< -1.0863195404360622 or v>.49192233306644084 for v in r['raw_inverse_PD_target_delta2'])for r in rows)
out=dict(status='NEW_V2_TRACE_REDUCTION_NOT_NEW_PHYSICAL_CASE',case=str(C),input_passes_each=1,control_rows=len(rows),contact_samples=len(samples),
 physics_steps=0,new_models=0,old_cases_read=0,raw_hashes_computed=0,
 replay=dict(max_requested_torque_error_Nm=replay_error,match_gate_Nm=1e-7,matched=replay_error<=1e-7,
  gyro_unlogged_zero_only_because_both_roll_gains_zero=True,not_a_sensor_or_independent_dynamics_replay=True),
 contacts=dict(low_ticks2=low.sum(axis=0).tolist(),allair_ticks=int(air.sum()),mean_normals_N2=N.mean(axis=0).tolist(),
  left_normal_distribution_N=stat(N[:,0]),right_normal_distribution_N=stat(N[:,1]),
  left_low_substep_histogram=np.bincount([s['sub']for s,z in zip(samples,low[:,0])if z],minlength=20).tolist(),
  allair_substep_histogram=np.bincount([s['sub']for s,z in zip(samples,air)if z],minlength=20).tolist(),
  support_brackets=seams),phases=phases,
 controller=dict(axial_diff_force_from_old_differential_PD_N=stat(pdF),effective_axial_stiffness_N_m=stat(stiffness),
  max_abs_requested_tau6_Nm=np.max(np.abs(req),axis=0).tolist(),max_abs_applied_ENDPOINT_tau6_Nm=np.max(np.abs(app),axis=0).tolist(),
  requested_at_peak_limit_calls6=(np.abs(req)>=eff-1e-7).sum(axis=0).tolist(),
  nominal_inverse_PD_raw_delta_out_of_v2_domain_control_calls=clip_projection,
  raw_delta_reconstruction='From exact nominal state14 encoder q/qd and requested tau,original inversePD60/2;not actual2kHz motor saturation measurement',
  physical_2kHz_saturation_duty='unavailable_not_logged'),top_left_force_samples=peaks,
 caveats=['Positive-force contact sets omit zero-force contacts;no geometric-gap inference',
 'Contact dynamics PRE stage,controller metadata100Hz;joined same control bin,not synchronized channels',
 'Virtual F/Tp derived at mean current leg Jacobian,not a contact-force estimate or ground-truth controller input',
 'No smoothing or reinterpretation of frozen contact pass/fail gate'])
(O/'RESULT.json').write_text(json.dumps(out,indent=2,allow_nan=False),encoding='utf-8')
print(json.dumps({k:out[k]for k in ['replay','contacts','phases','controller']},indent=2),flush=True)
