"""Read-only package integrity and hardware calibration preflight. Never actuates."""
from pathlib import Path
import argparse,json,hashlib,sys
import numpy as np
B=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--real-enable',action='store_true');p.add_argument('--hardware-calibration');a=p.parse_args();c=json.loads((B/'config/deployment_contract.json').read_text(encoding='utf-8'))
manifest=B/'SHA256SUMS.txt'
if manifest.exists():
 for line in manifest.read_text(encoding='utf-8').splitlines():
  digest,name=line.split('  ',1);f=(B/name).resolve()
  if not f.is_relative_to(B) or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:raise SystemExit('INTEGRITY_FAIL '+name)
for name,expected in [('model/training_checkpoint.pt',c['checkpoint_sha256']),(c['plant']['mjcf'],c['plant']['mjcf_sha256']),(c['plant']['physx'],c['plant']['physx_sha256']),(c['plant']['root_usd'],c['plant']['root_usd_sha256'])]:
 if hashlib.sha256((B/name).read_bytes()).hexdigest()!=expected:raise SystemExit('IDENTITY_FAIL '+name)
import onnxruntime as ort
s=ort.InferenceSession(str(B/'model/policy.onnx'),providers=['CPUExecutionProvider']);x=s.get_inputs()[0];y=s.get_outputs()[0];assert x.name=='observation' and x.shape[-1]==35 and y.shape[-1]==6
v=json.loads((B/'examples/golden_vectors.json').read_text(encoding='utf-8'))['vectors'];o=np.asarray([r['observation'] for r in v],np.float32);expected=np.asarray([r['action'] for r in v],np.float32);actual=s.run(['action'],{'observation':o})[0];err=float(np.abs(actual-expected).max());assert err<2e-4
print(json.dumps({'offline_package':'PASS','model':c['selected_model'],'actor_golden_max_abs':err,'actual_hardware_tested':False},ensure_ascii=False))
f=Path(a.hardware_calibration) if a.hardware_calibration else B/'config/hardware_calibration.json'
if not f.is_file():
 print('HARDWARE_CALIBRATION_REQUIRED: copy the template and fill measured values; offline package is ready.');raise SystemExit(2 if a.real_enable else 0)
h=json.loads(f.read_text(encoding='utf-8'));problems=[]
if h.get('verified') is not True:problems.append('verified must reflect actual physical calibration')
if h.get('plant_version')!=c['plant']['version']:problems.append('wrong plant version')
try:
 R=np.asarray(h['imu_rotation_sensor_to_body'],float);assert R.shape==(3,3) and np.isfinite(R).all() and np.max(abs(R@R.T-np.eye(3)))<1e-4 and abs(np.linalg.det(R)-1)<1e-4
except (AssertionError,KeyError,TypeError,ValueError):problems.append('measured IMU rotation missing or invalid')
rows=h.get('joints',[])
if [r.get('name') for r in rows]!=c['output']['order']:problems.append('joint order mismatch')
for row in rows:
 name=row.get('name','?')
 if row.get('sign') not in (-1,1):problems.append(name+':sign')
 for key in ['raw_zero','raw_position_units_per_model_rad','raw_effort_units_per_model_Nm']:
  val=row.get(key)
  if not isinstance(val,(int,float)) or not np.isfinite(val) or (key!='raw_zero' and val<=0):problems.append(name+':'+key)
 if row.get('can_id') is None:problems.append(name+':CAN mapping')
if problems:
 print(json.dumps({'hardware_calibration':'BLOCKED','reasons':problems},ensure_ascii=False));raise SystemExit(2 if a.real_enable else 0)
print('HARDWARE_CONFIGURATION_COMPLETE: proceed with the documented controlled bring-up; this check is not physical robot acceptance.')
