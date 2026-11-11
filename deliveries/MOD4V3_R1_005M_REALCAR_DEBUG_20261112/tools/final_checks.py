from pathlib import Path
import json,sys,ctypes as c,subprocess,time,hashlib
import numpy as np,onnxruntime,mujoco
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B/'runtime'));from control import limit_torque
D=c.CDLL(str(B/'bin/windows-x64/mod4_runtime.dll'));F=c.c_float;P=c.POINTER(F);D.mod4_limit_torque.argtypes=[P,P,P];rng=np.random.default_rng(1211);maxerr=0.
for _ in range(1024):
 tau=rng.uniform(-80,80,6).astype(np.float32);v=rng.uniform(-100,100,6).astype(np.float32);out=np.empty(6,np.float32);assert D.mod4_limit_torque(tau.ctypes.data_as(P),v.ctypes.data_as(P),out.ctypes.data_as(P));maxerr=max(maxerr,float(abs(out-limit_torque(tau,v)).max()))
assert maxerr<1e-5
results=dict(fast_envelope_vectors=1024,C_vs_Python_limit_max_abs=maxerr,status='PASS')
(B/'evidence/FAST_TORQUE_LIMIT.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
q=json.loads((B/'examples/bench_input.json').read_text(encoding='utf-8'));v=q['command']+q['gyro_b_rad_s']+q['gravity_b']+q['joint_position_rad']+q['joint_velocity_rad_s'];msg='RESET\nPOLICY '+' '.join(map(str,v))+'\nPD '+' '.join(map(str,q['joint_position_rad']+q['joint_velocity_rad_s']))+'\n';r=subprocess.run([str(B/'bin/windows-x64/mod4_stdio.exe')],input=msg,capture_output=True,encoding='utf-8',errors='replace',check=True);reply=[json.loads(x) for x in r.stdout.splitlines()];assert len(reply)==3 and reply[0]['reset'] and len(reply[1]['action'])==6 and len(reply[2]['torque_Nm'])==6
(B/'evidence/C_CLI_SMOKE.json').write_text(json.dumps(dict(status='PASS',input=msg,replies=reply),indent=2)+'\n',encoding='utf-8')
(B/'evidence/VERSIONS.json').write_text(json.dumps(dict(python=sys.version,numpy=np.__version__,onnxruntime=onnxruntime.__version__,mujoco=mujoco.__version__,platform=sys.platform),indent=2)+'\n',encoding='utf-8')
checks=[]
for args,expected in [([],0),(['--real-enable','--hardware-calibration',str(B/'config/hardware_calibration.template.json')],2)]:
 r=subprocess.run([sys.executable,'-B',str(B/'tools/preflight.py'),*args],cwd=B,capture_output=True,encoding='utf-8',errors='replace');assert r.returncode==expected,(r.stdout,r.stderr);checks.append(dict(args=args,expected_exit=expected,actual_exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
(B/'evidence/PREFLIGHT_TEST.json').write_text(json.dumps(dict(status='PASS',checks=checks),ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('BOUNDARIES_C_CLI_OFFLINE_AND_UNVERIFIED_HARDWARE_BLOCK_PASS')
