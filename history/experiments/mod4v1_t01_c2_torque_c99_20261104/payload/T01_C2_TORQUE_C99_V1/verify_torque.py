"""New C2 requested-torque component; fresh synthetic math, zero physics."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,math,subprocess,sys,time
from types import SimpleNamespace
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;OUT=HERE/'validation001'
sys.path.insert(0,str(ROOT))
import physics_bridge as bridge
from RM_ROBUSTNESS_V1.controller_heading_follow_v2 import GroundController as C2
from RM_ROBUSTNESS_V1.controller_roll_follow_v1 import GroundController as C1
TOL=dict(torque_Nm=.002,wheel_first_Nm=.002,reference_state14=5e-5,projected_shaped=5e-5,yaw_integral=2e-4,park_m=3e-6)
SEQUENCES=[['slow_commands',1,200],['park_hold',1,500],['drive_brake_reverse',1,900],['rate_only_math_stress',0,700]]
def main():
 OUT.mkdir(exist_ok=False)
 protocol=dict(id='C2_TORQUE_NATIVE_MATH_001',scope='Selected nominal C2 requested torque only, not estimator/driver/robot qualification',
  physics_steps=0,old_cases_read=0,sequences=SEQUENCES,thresholds=TOL,native_fault_assertions=33,
  required_status_valid=True,require_torque_bounds=True,require_stress_exercises_saturation_and_envelope=True,
  projected_shaped='ref7/ref8 and raw shaper acceleration; not unprojected internal v/w',
  stress_note='Mode0 high command/rate/encoder-speed synthetic stress is NOT actual FPS motion or a dynamics trajectory',
  unchanged='Original K/geometry/C1/reference/base equations, twice clipping order, actuator limits and original inner actuation path')
 (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
 result=dict(protocol_id=protocol['id'],passed=False,physics_steps=0,old_cases_read=0,full_T01_acceptance=False)
 try:
  gain=bridge.load_gain(ROOT/'nominal_gain_v1.json');pack=json.loads((ROOT/'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json').read_bytes())
  geometry=bridge.geometry();rows=[];expected=[]
  q0=np.array([gain['q'][3],gain['q'][3]+gain['q'][4]])
  for name,mode,count in SEQUENCES:
   py=(C2 if mode else C1)(gain,pack['controller'],geometry=geometry);py.K=np.asarray(pack['K_6x14'])
   for i in range(count):
    t=i*.01;x=np.zeros(14);x[0]=.1*t;x[1]=3.+.03*t;x[8]=.2*math.sin(t);x[9]=.05*math.cos(.7*t)
    forward=.3 if .5<=t<1.5 else 0.;yaw=.2*math.sin(t)
    roll=.02*math.sin(t);pitch=.02*math.sin(.7*t);hip=.02*math.sin(2*t);crank=.015*math.cos(2*t);speed=.02*math.sin(t)
    qdot=.04*math.cos(2*t);cdot=-.03*math.sin(2*t)
    if name=='park_hold':forward=yaw=0.;x[8]=0.;x[9]=.02;speed=.02*math.sin(t)
    if name=='drive_brake_reverse':
     forward=2. if t<3. else (0. if t<5. else (-2. if t<7. else 0.))
     yaw=.6 if 1.<t<4. else (-.6 if 5.<t<8. else 0.)
     pitch=.12*math.sin(.7*t);roll=.2*math.cos(t);hip=.08*math.sin(2*t);crank=.06*math.cos(2*t);speed=.4*math.sin(.8*t)
    if name=='rate_only_math_stress':
     forward=10. if t<5. else -4.;yaw=10. if t<5. else -7.
     pitch=.3*math.sin(.7*t);roll=.3*math.sin(t);hip=.08*math.sin(2*t);crank=.06*math.cos(2*t)
     speed=.2*math.sin(t);qdot=12.*math.cos(2*t);cdot=-12.*math.sin(2*t)
    qL=q0+np.array([hip,crank]);qR=q0-np.array([hip,crank])
    x[2]=pitch;x[3],x[4],x[5],x[6]=qL[0],qL[1]-qL[0],qR[0],qR[1]-qR[0];x[7]=speed
    x[10],x[11],x[12],x[13]=qdot,cdot-qdot,-qdot,qdot-cdot
    omega=[.1*math.cos(t),.1*math.sin(t),x[8]]
    values=np.asarray([forward,yaw,*x,roll,*omega],dtype=np.float32).astype(float)
    e=SimpleNamespace(state14=values[2:16].copy(),roll=values[16],omega_body=values[17:20].copy(),sensor_age_s=0.)
    tau=py.command(e,values[0],values[1])
    expected.append(dict(tau=tau.copy(),wheel_first=tau[[2,5,0,1,3,4]].copy(),ref=py.ref.copy(),
      shaped=np.array([py.ref[7],py.ref[8],py.shaper.a]),I=py.yaw_integral,park=py.park_error))
    rows.append(f'{int(i==0)} {mode} '+' '.join(format(v,'.9g') for v in values)+'\n')
  data=OUT/'new_synthetic_input.txt';data.write_text(''.join(rows),encoding='ascii')
  exe=OUT/'pc2_torque_host.exe';base=ROOT/'SPR_AUDIT/portable_control_v3_current'
  command=['C:/MinGW/bin/gcc.exe','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math',
   str(HERE/'pc2_balance.c'),str(HERE/'host_check.c'),str(ROOT/'T01_C2_REFERENCE_C99_V1/pc2_reference.c'),
   str(ROOT/'SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.c'),str(base/'pc3_controller.c'),'-lm','-o',str(exe)]
  result['compile_command']=command;built=subprocess.run(command,capture_output=True,text=True)
  (OUT/'compile.stdout.log').write_text(built.stdout,encoding='utf8');(OUT/'compile.stderr.log').write_text(built.stderr,encoding='utf8')
  result['compile_exit']=built.returncode
  if built.returncode:raise RuntimeError('Native compile failed; attempt preserved')
  output=OUT/'native_output.jsonl';start=time.perf_counter();native=subprocess.run([str(exe),str(data),str(output)],capture_output=True,text=True)
  result.update(native_exit=native.returncode,native_wall_seconds=time.perf_counter()-start)
  (OUT/'native.stdout.log').write_text(native.stdout,encoding='utf8');(OUT/'native.stderr.log').write_text(native.stderr,encoding='utf8')
  if native.returncode:raise RuntimeError('Native fault/run failed; attempt preserved')
  got=[json.loads(s) for s in output.read_text(encoding='utf8').splitlines()]
  if len(got)!=len(expected):raise AssertionError('Native row count')
  maxima={k:0. for k in TOL};invalid=[];saturated=scaled=0;bound_failures=[]
  mapping={'torque_Nm':('tau','tau'),'wheel_first_Nm':('wheel_first','wheel_first'),'reference_state14':('ref','ref'),
           'projected_shaped':('shaped','shaped'),'yaw_integral':('I','I'),'park_m':('park','park')}
  for a,b in zip(got,expected):
   if a['status']!=0 or a['valid']!=1:invalid.append(a['i'])
   for key,(ka,kb) in mapping.items():maxima[key]=max(maxima[key],float(np.max(np.abs(np.asarray(a[ka])-b[kb]))))
   if np.any(np.abs(a['tau'])>np.array([40,40,5.775909774436091]*2)+2e-6):bound_failures.append(a['i'])
   saturated+=bool(a['saturation']);scaled+=bool(a['envelope_scaled'])
  result.update(rows=len(got),max_errors=maxima,thresholds=TOL,invalid_rows=invalid,torque_bound_failures=bound_failures,
   saturated_rows=saturated,envelope_projected_rows=scaled,native_summary=native.stdout.strip(),component_only=True)
  result['passed']=not invalid and not bound_failures and saturated>0 and scaled>0 and all(maxima[k]<=TOL[k] for k in TOL)
  if not result['passed']:raise AssertionError('Predeclared new-component contract/tolerance failed')
 except BaseException as error:
  result['error']=repr(error);(OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');raise
 (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
