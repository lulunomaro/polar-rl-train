"""Independent complete model CPU review; scalar Adam state is flattened before byte view."""
from pathlib import Path
import json,time,torch,numpy as np,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
def exact(a,b):
 if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and a.contiguous().reshape(-1).view(torch.uint8).equal(b.contiguous().reshape(-1).view(torch.uint8))
 if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and a.tobytes()==b.tobytes()
 if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
 if isinstance(a,(list,tuple)):return isinstance(b,type(a)) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
 return a==b
def finite(x):
 if torch.is_tensor(x):return not (x.is_floating_point() or x.is_complex()) or bool(torch.isfinite(x).all())
 if isinstance(x,np.ndarray):return x.dtype.kind not in 'fc' or bool(np.isfinite(x).all())
 if isinstance(x,dict):return all(finite(v) for v in x.values())
 if isinstance(x,(tuple,list)):return all(finite(v) for v in x)
 return True
def main():
 r=json.loads((R/'H1_CLOSED_CALIBRATION_MODEL_USD_POSE_SOURCE_ACTUAL_COLLECTION.json').read_bytes());source=torch.load(D/'payload/job1/source/E0_full_source.pt',map_location='cpu',weights_only=False);rows=[]
 for row in r['local_models']:
  p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA'];m=torch.load(p,map_location='cpu',weights_only=False);assert finite(m)
  for k in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(m[k],source[k]),k
  steps=[int(v['step']) for v in m['optimizer_state_dict']['state'].values()];assert len(steps)==17 and set(steps)=={639560};rows.append(dict(**row,all_model_runtime_tensorfinite=True,actor9_critic8_STD17Adam_source_literal_byteexact=True,all17Adam_steps=639560))
 report=dict(epoch=time.time(),models=rows,calibration_optimizer_updates=0,no_PPO_charge=True,actual_USD_collision_API_shapes=len(r['source_USD_enabled_collision_shapes']),actual_USD_enabled_shape_count=sum(x['collision_enabled'] is True for x in r['source_USD_enabled_collision_shapes']),geometry_disclosure='Old observer WXYZ interpretation invalid on current XYZW SDK; finite stored clearances are not independently correct airborne geometry. Old raw and CPU reports retained with this explicit rejection.',prior_empty_pose_alias_lookup='ArticulationData is a backend factory; empty direct method list does not verify pose semantics. Actual math.py and physical root quaternion separately identify XYZW.',new_corrected_geometry_requires_actual_bodyposes_and_independent_CPU_reconstruction=True)
 with (R/'H1_CALIBRATION_COMPLETE_MODELS_LITERAL_SOURCE_CPU_AND_GEOMETRY_REJECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
 print(json.dumps(dict(bothmodels_source_literalexact=True,all17Adam639560=True,geometry_old_observer_rejected=True)),flush=True)
if __name__=='__main__':main()
