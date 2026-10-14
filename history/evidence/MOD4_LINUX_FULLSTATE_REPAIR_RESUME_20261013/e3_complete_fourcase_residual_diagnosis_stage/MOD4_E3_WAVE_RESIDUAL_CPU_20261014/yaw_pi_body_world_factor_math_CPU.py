"""Read-only one-frame-factor mathematics; no SDK binding or candidate weights.

Flip body heading by pi and body-vx request together to preserve world course.
The physical resetZ must be independently calculated by the original footprint
adapter at future dispatch. This component never claims its previousZ remains safe.
"""
import numpy as np
PROFILE='e3_yaw_pi_body_sign_world_course_preserved_CPU_v1'
def transform(root_xyzw,command_body,measured_q30,group_ids):
 r=np.asarray(root_xyzw);c=np.asarray(command_body);q=np.asarray(measured_q30);g=np.asarray(group_ids)
 assert r.shape==(80,13) and r.dtype==np.float32
 assert c.shape==(80,3) and c.dtype==np.float32 and q.shape==(80,30) and q.dtype==np.float32
 assert g.shape==(80,) and np.array_equal(g,np.arange(80)%3)
 assert all(np.isfinite(x).all() for x in [r,c,q])
 assert np.allclose(np.linalg.norm(r[:,3:7],axis=1),1,atol=1e-6,rtol=0)
 assert np.array_equal(c[:,0],np.array([.3,-.3,0],np.float32)[g]) and not c[:,1:].any()
 nr=r.copy();nc=c.copy();nq=q.copy()
 # Left Hamilton multiply qz(pi)=[0,0,1,0] to q=[x,y,z,w], xyzw.
 # This exact permutation preserves the float32 quaternion norm bitwise.
 x,y,z,w=r[:,3:7].T
 nr[:,3]=-y;nr[:,4]=x;nr[:,5]=w;nr[:,6]=-z
 nc[:,0]=-c[:,0];nc[g==2]=0
 assert np.array_equal(nr[:,:3],r[:,:3]) and np.array_equal(nr[:,7:],r[:,7:]) and np.array_equal(nq,q)
 assert np.array_equal(np.linalg.norm(nr[:,3:7],axis=1),np.linalg.norm(r[:,3:7],axis=1))
 return nr,nc,nq,dict(profile=PROFILE,root_XY_preserved=True,root_Z_provisional_only_needs_original_full_footprint_safe_reset=True,q30_exact=True,body_vx_sign_derived_from_same_world_course=True,group_world_course_labels_preserved=True,standing_commands_exact=True,root30_quaternion_factor_changed_NOT_byteexact=True,no_velocity_setter_or_PPO=True)

if __name__=='__main__':
 from pathlib import Path
 import json,time,hashlib
 D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';O=R/'E3_YAWPI_FRAME_FACTOR_MATH_ONLY_CPU_PASSED.json';assert not O.exists()
 rv=json.loads((W/'MOD4_3060_LEFT_SECOND_FULL80_20261014/reports/FULL80_ORIGINAL_1N_ROUTE_ALL_PREFIX_COMPLETE_ACTUAL_REVIEW.json').read_bytes());raw=Path(rv['raw']['local_path'])
 def sha(p):
  h=hashlib.sha256()
  with Path(p).open('rb') as f:
   for b in iter(lambda:f.read(2**20),b''):h.update(b)
  return h.hexdigest()
 assert sha(raw)==rv['raw']['sha256']
 with np.load(raw) as z:r=z['before_root'][0];c=z['command'][0];q=z['q'][0];g=z['group_ids']
 nr,nc,nq,receipt=transform(r,c,q,g)
 def heading(x):
  a,b,d,e=x[:,3:7].T
  return np.stack((1-2*(b*b+d*d),2*(a*b+e*d)),1)
 error=float(np.max(np.abs(heading(r)*c[:,0,None]-heading(nr)*nc[:,0,None])))
 assert error<=1e-7 and not np.shares_memory(nr,r) and not np.shares_memory(nc,c) and not np.shares_memory(nq,q)
 bad=[(r.astype(np.float64),c,q,g),(r,c*0,q,g),(r,c,q[:,:29],g),(r,c,q,g[::-1])]
 for args in bad:
  try:transform(*args)
  except AssertionError:pass
  else:raise AssertionError('Malformed factor fixture accepted')
 out=dict(epoch=time.time(),passed_CPU_math_only=True,source_SHA=rv['source_SHA'],source_module_SHA=sha(__file__),actual_raw=rv['raw'],actual_fixture_envs=80,actual_world_heading_command_product_max_error=error,independent_storage=True,strict_invalid_inputs_rejected=4,receipt=receipt,
  physical_admission_pending=True,full80_native_GPU_evaluation_NOT_dispatched=True,resetZ_fullfootprint_and_30q_actual_CPUCUDA_terrain_query_contact_COMhardware_pending=True,
  no_new_candidate_weights_PPO_SSH_GPU_RNG_or_budget=True,Git_archive_pending_root_owner=True)
 O.write_text(json.dumps(out,indent=2),encoding='utf8');print(json.dumps(dict(report=str(O),worldcourse_error=error,CPU_only=True)))
