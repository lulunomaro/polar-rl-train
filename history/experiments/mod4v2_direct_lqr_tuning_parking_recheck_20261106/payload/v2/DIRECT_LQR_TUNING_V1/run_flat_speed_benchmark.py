"""Actual full-P0 2m/s/stop/reverse benchmark on EXTRA long flat fixture.
NOT latestCAD/T02 acceptance;same actuator/observer model,28s fixed before execution.
"""
from pathlib import Path
import argparse,csv,json,sys,time
import numpy as np
R=Path(__file__).resolve().parents[1];D=Path(__file__).resolve().parent
sys.path.insert(0,str(R));sys.path.insert(0,str(R.parent/'mod4v1_lqr_mpc_robust_20261102'))
import runtime_v2 as runtime
from observed_bridge_v1 import ObservedV2Plant

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--variant',choices=['baseline','effort4'],required=True);ap.add_argument('--case',required=True);a=ap.parse_args()
 if not a.case or any(c not in'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'for c in a.case):raise ValueError('Plain new case id required')
 out=D/'FLAT_SPEED_BENCH'/a.case;out.mkdir(parents=True,exist_ok=False)
 tune={}if a.variant=='baseline'else dict(effort_weight=4.)
 protocol=dict(variant=a.variant,tuning=tune,seed=530302,nominal=True,duration_s=28.,physics_dt=.0005,control_dt=.01,
  extra_long_flat_fixture=True,not_CAD_or_T02_acceptance=True,profile=[[0,2,0],[2,10,2],[10,15,0],[15,23,-2],[23,28,0]],
  steady_windows=dict(forward=[7,10],reverse=[20,23],stop1=[14,15],stop2=[27,28]),source_full_robot_unchanged=True,
  no_new_gain_tuning=True,old_strict_CAD_failures_retained=True,truth_grading_only=True)
 (out/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
 started=time.perf_counter();oldc,oldp=runtime.GroundController,runtime.BufferedImuPlant
 def factory(gain,config=None,**kw):c=dict(config or{});c.update(tune);return oldc(gain,c,**kw)
 runtime.GroundController=factory;runtime.BufferedImuPlant=ObservedV2Plant
 try:e=runtime.Engine('flat',seed=530302,full_dr=False)
 finally:runtime.GroundController=oldc;runtime.BufferedImuPlant=oldp
 e.meta.update(purpose='EXTRA fullrobot flat speed/stop engineering benchmark,not linearization or CAD grade',tuning=tune,actual_K=e.controller.K.tolist())
 (out/'meta.json').write_text(json.dumps(e.meta,indent=2),encoding='utf-8')
 p=e.plant;rows=[]
 with(out/'trace.csv').open('x',newline='',encoding='utf-8')as f:
  w=csv.writer(f);w.writerow(['time','target_v','true_vx','estimated_vx','pitch','roll','x','y']+[f'qpos{i}'for i in range(37)])
  for k in range(2800):
   t=k*.01;v=2. if 2<=t<10 else -2. if 15<=t<23 else 0.
   e.tick(v,0.);g=p.grade_current();r=dict(time=float(p.d.time),target=v,vx=float(g['body_velocity'][0]),pitch=float(g['pitch_true']),roll=float(g['roll_true']),x=float(g['xyz'][0]),y=float(g['xyz'][1]))
   rows.append(r);w.writerow([r['time'],v,r['vx'],float(e.estimate.state14[7])if e.estimate is not None else None,r['pitch'],r['roll'],r['x'],r['y'],*map(float,p.d.qpos)])
   if e.paused or e.fault or not g['finite']:break
 def stats(lo,hi,target):
  s=[r for k,r in enumerate(rows)if lo<=k*.01<hi];v=np.array([r['vx']for r in s])
  return dict(n=len(s),mean_vx=float(np.mean(v))if len(v)else None,vx_RMSE=float(np.sqrt(np.mean((v-target)**2)))if len(v)else None)
 result=dict(variant=a.variant,tuning=tune,complete=e.controls==2800 and not e.fault,controls=e.controls,physics_steps=p.tick_phys,sim_time=float(p.d.time),wall_s=time.perf_counter()-started,fault=e.fault,
  forward=stats(7,10,2),reverse=stats(20,23,-2),stop1=stats(14,15,0),stop2=stats(27,28,0),
  pitch_peak_rad=max(abs(r['pitch'])for r in rows),roll_peak_rad=max(abs(r['roll'])for r in rows),contacts=p.audit_totals()['total'],
  extra_flat_fixture=True,NOT_CAD_or_T02_grade=True,actual_K=e.controller.K.tolist(),truth_in_controller=False,
  note='Whole-force/guide/hard remain reported;no qualification inferred from nominal benchmark;2kDCduty not summarized by this lightweight csv benchmark')
 (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
