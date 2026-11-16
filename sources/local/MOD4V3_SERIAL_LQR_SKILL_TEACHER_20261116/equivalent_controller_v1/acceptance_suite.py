"""Predeclared teacher-only matrix; speed calibrated independently of control law."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,sys,json,os,hashlib,time
import numpy as np
P=Path(__file__).resolve().parent
BASE=P/'acceptance_v1'
BASE.mkdir(exist_ok=True)
ENV={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
def execute(case):
 out=BASE/case['name'];out.mkdir(exist_ok=False)
 with (out/'process.log').open('w',encoding='utf8')as log:
  code=subprocess.call([sys.executable,'-X','utf8','-u','-B',str(P/'run_teacher.py'),'--case',json.dumps(case),'--out',str(out)],cwd=P,env=ENV,stdout=log,stderr=subprocess.STDOUT)
 d=json.loads((out/'RESULT.json').read_text())if (out/'RESULT.json').exists()else dict(error='subprocess failed',returncode=code,case=case)
 print(case['name'],code,d.get('pass_teacher_stair'),d.get('pass_teacher_jump'),flush=True)
 return d
if __name__=='__main__':
 start=time.perf_counter();inputs=[x for x in P.rglob('*.py')if 'tests'not in x.parts and 'acceptance_v1'not in x.parts and 'snapshot_v1'not in x.parts]+[P/'native_full_mjcf_gains.npz',P/'config/robot_params.yaml']
 manifest={str(x.relative_to(P)):hashlib.sha256(x.read_bytes()).hexdigest()for x in inputs}
 (BASE/'CONTROLLER_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+chr(10))
 protocol=dict(name='NATIVE_EQUIVALENT_TEACHER_V1_20261116',heights_m=[.07,.10,.15,.20],offsets_m=[-.06,-.03,0.,.03,.06],target_entry_speeds_mps=[.3,.4,.5],yaw_deg=[-10,0,10],duration_s=12.,actor_calls=0,optimizer_steps=0,top_hold_s=.4,body_edge_clearance_m=.03,pitch_roll_bound_rad=.35,stable_speed_max_mps=.60,heading_after_2s_max_deg=5.,entry_pre100ms_tolerance_mps=.02,jump_double_air_min_s=.04,jump_landed_min_s=.4,jump_target_COM_error_max_m=.02,default_pointer_modified=False)
 (BASE/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+chr(10))
 with ThreadPoolExecutor(max_workers=4)as pool:
  cal=[dict(name=f'cal_h{h:03d}_v{round(v*100):02d}',kind='stair',height=h/1000.,length=.3375,speed=v,duration=9.)for h in [70,100,150,200]for v in [.3,.4,.5]]
  data=list(pool.map(execute,cal))
  calibration={}
  for h in [70,100,150,200]:
   group=[x for x in data if x['case']['height']==h/1000.]
   measured=np.array([x['entry']['pre_100ms_speed']for x in group]);commands=np.array([x['case']['speed']for x in group]);fit=np.polyfit(measured,commands,1)
   calibration[str(h)]=dict(observed=list(zip(commands.tolist(),measured.tolist())),linear_inverse=fit.tolist(),commands={str(v):float(np.polyval(fit,v))for v in [.3,.4,.5]})
  (BASE/'ENTRY_SPEED_CALIBRATION.json').write_text(json.dumps(calibration,indent=2)+chr(10))
  cases=[dict(name=f'stair_h{h:03d}_x{round(x*1000):+04d}_v{round(v*100):02d}_yaw{yaw:+03d}',kind='stair',height=h/1000.,start_x=x,length=.3375,speed=calibration[str(h)]['commands'][str(v)],target_entry_speed=v,yaw_deg=yaw,duration=12.)for h in [70,100,150,200]for x in [-.06,-.03,0.,.03,.06]for v in [.3,.4,.5]for yaw in [-10,0,10]]
  cases +=[dict(name=f'jump_h{round(h*100):02d}_yaw{yaw:+03d}',kind='jump',target_height=h,length=.25,yaw_deg=yaw,duration=8.)for h in [.06,.10,.14]for yaw in [-10,0,10]]
  cases +=[dict(name=f'normal_l{round(l*1000):03d}_v{round(v*100):02d}_yaw{yaw:+03d}',kind='normal',length=l,speed=v,yaw_deg=yaw,duration=8.)for l in [.18,.25,.3375]for v in [0.,.4]for yaw in [-10,0,10]]
  (BASE/'CASES.json').write_text(json.dumps(cases,indent=2)+chr(10));results=list(pool.map(execute,cases))
 (BASE/'RESULTS.json').write_text(json.dumps(dict(actual_seconds=time.perf_counter()-start,count=len(results),results=results),ensure_ascii=False,indent=2)+chr(10))
 print('MATRIX_COMPLETE',len(results),time.perf_counter()-start,flush=True)
