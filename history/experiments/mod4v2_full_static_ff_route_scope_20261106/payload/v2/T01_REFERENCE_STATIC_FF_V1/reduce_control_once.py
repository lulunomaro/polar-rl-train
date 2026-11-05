"""ONE first pass of NEW M2 control trace only; no replay/model/FK/physics/hash.
Question: reference excursion, actual differential tracking and matched-boundary roll.
"""
from pathlib import Path
import json,math
import numpy as np
D=Path(__file__).resolve().parent;R=D.parent;OUT=D/'REDUCTION001'
CASE=D/'runs/v2_t01_reference_static_ff_nominal_slow_520141_001'

def main():
 OUT.mkdir(exist_ok=False)
 protocol=dict(question='M2 reference/staticFF amplitude, differential tracking and phase; not a causal or force estimate',
  source=str(CASE/'trace.jsonl'),allowed_passes=1,old_raw_reads=0,motor_contact_raw_reads=0,
  model_builds=0,forward=0,FK=0,controller_replay=0,physics_steps=0,payload_hash_reads=0,
  phases=dict(initial_stand=[0,2],acceleration=[2,3],steady=[3,7],late_drive=[7,8],brake=[8,9],final=[9,12]),
  matched_truth='estimate at sensor epoch vs previous row POST at same epoch; not current row post truth',
  PD='exact existing absolute-coordinate 120(qref-q)-4 qdot, differential-only before second clip')
 (OUT/'START.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
 q7=json.loads((R/'nominal_gain_v2.json').read_text(encoding='utf-8'))['gain']['q']
 q0=np.array([q7[3],q7[3]+q7[4],q7[5],q7[5]+q7[6]])
 phases={k:[] for k in protocol['phases']};allrows=[];scale_events=[];peaks=[];prev=None;max_transport=0.;q_packet_diff=0.
 with (CASE/'trace.jsonl').open(encoding='utf-8') as f:
  for i,line in enumerate(f):
   r=json.loads(line);assert r['control_index']==i
   x=np.asarray(r['estimated14'],float);d=r['reference_static_ff_diagnostic'];qr=np.asarray(d['reference_q4_abs'],float)
   q=np.array([x[3],x[3]+x[4],x[5],x[5]+x[6]]);qd=np.array([x[10],x[10]+x[11],x[12],x[12]+x[13]])
   raw=np.asarray(d['nominal_static_delta4_Nm']);extra=np.asarray(d['extra_joint_tau6_Nm'])
   expected=np.zeros(6);expected[[0,1]]=.5*(raw[:2]-raw[2:]);expected[[3,4]]=-expected[[0,1]]
   max_transport=max(max_transport,float(np.max(np.abs(extra-d['scale']*expected))))
   q_packet_diff=max(q_packet_diff,float(np.max(np.abs(q-np.asarray(r['public_packet']['joint_pos4'])))))
   pd=120*(qr-q)-4*qd;pd_diff=.5*(pd[:2]-pd[2:]);ediff=.5*((q-qr)[:2]-(q-qr)[2:])
   truth=r['post_truth'];cw=r.get('contact_window')or{};n=int(cw.get('physics_ticks')or 0);support=cw.get('mainwheel_support_ticks2')
   low=[n-int(v)for v in support]if support is not None else[0,0]
   dr=np.zeros(4)if prev is None else(qr-prev['qr'])/.01
   matched=prev is not None and abs(prev['post_time']-r['sensor_time_s'])<1e-7
   row=dict(k=i,t=float(r['command_time_s']),qr=qr,q=q,qr_dev=qr-q0,q_dev=q-q0,qerr=q-qr,
    ediff=ediff,qd_diff=.5*(qd[:2]-qd[2:]),ref_rate=dr,extra=extra[[0,1]],pd_diff=pd_diff,
    combined_diff=pd_diff+extra[[0,1]],roll_est=float(r['estimated_roll']),roll_post=float(truth['roll_true']),
    roll_matched_error=float(r['estimated_roll']-prev['roll_post'])if matched else None,
    post_time=float(r['time_s']),lowL=low[0],lowR=low[1],whole=int(cw.get('whole_body_unsupported_ticks')or 0),
    extra_power_proxy=float(extra[[0,1]]@(.5*(qd[:2]-qd[2:]))) *2,
    scale=float(d['scale']),tau=np.asarray(r['requested_tau6_Nm']))
   assert all(np.isfinite(row[k]).all()for k in ['qr','q','qr_dev','qerr','ediff','extra','pd_diff','tau'])
   allrows.append(row)
   for key,(a,b)in protocol['phases'].items():
    if a<=row['t']<b:phases[key].append(row)
   if row['scale']<1-1e-12:scale_events.append(i)
   prev=row
 def stats(rows):
  if not rows:return None
  out={'rows':len(rows),'lowL':sum(r['lowL']for r in rows),'lowR':sum(r['lowR']for r in rows),'whole':sum(r['whole']for r in rows)}
  for key in ['qr_dev','q_dev','qerr','ediff','qd_diff','ref_rate','extra','pd_diff','combined_diff','roll_est','roll_post','extra_power_proxy']:
   a=np.array([r[key]for r in rows]);out[key]=dict(mean=np.mean(a,axis=0).tolist(),rms=np.sqrt(np.mean(a*a,axis=0)).tolist(),abs_peak=np.max(abs(a),axis=0).tolist())
  a=np.array([r['roll_matched_error']for r in rows if r['roll_matched_error']is not None]);out['roll_matched_boundary_error']=dict(n=len(a),mean=float(a.mean())if len(a)else None,rms=float(np.sqrt(np.mean(a*a)))if len(a)else None,abs_peak=float(np.max(abs(a)))if len(a)else None)
  return out
 indices=sorted(set([0,1,2,199,299,699,799,899,1199]+scale_events+sorted(range(len(allrows)),key=lambda i:float(np.max(abs(allrows[i]['extra']))),reverse=True)[:3]))
 for i in indices:
  peaks.append({k:(v.tolist()if isinstance(v,np.ndarray)else v)for k,v in allrows[i].items()})
 result=dict(status='NEW_M2_ONE_PASS_REFERENCE_TRACKING_REDUCTION',protocol=protocol,rows_read=len(allrows),
  q0_abs=q0.tolist(),projection_transport_max_abs_Nm=max_transport,estimated_q_vs_public_packet_abs_max_rad=q_packet_diff,
  scale_event_indices=scale_events,all=stats(allrows),phases={k:stats(v)for k,v in phases.items()},selected_boundary_and_peak_rows=peaks,
  limits=['PD fields are pre-clip algebra from logged estimated q,not measured output torque',
   'extra_power_proxy is logged extra joint effort dot estimated differential rate,not physical ground power',
   'normal-force-window counts are grading only; no unique cause or geometric-air conclusion',
   'no raw reread/rehash; all old/control/motor/contact once budgets unchanged except this NEW M2 pass'])
 assert len(allrows)==1200 and max_transport<1e-10
 (OUT/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
 print(json.dumps(dict(rows_read=len(allrows),scale_events=scale_events,transport_max_Nm=max_transport,all=result['all'],phases={k:{z:v[z]for z in ['rows','lowL','lowR','whole','ediff','extra','roll_post','roll_matched_boundary_error']}for k,v in result['phases'].items()}),indent=2,allow_nan=False))
if __name__=='__main__':main()
