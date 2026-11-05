"""New question on compact M2 reference records: common wheel-position drift.
Exactly nominal+2 recorded references, 2 sides each = 6 pure pose calls. No raw.
"""
from pathlib import Path
import json,sys
import numpy as np
R=Path(__file__).resolve().parents[1];V1=R.parent/'mod4v1_lqr_mpc_robust_20261102'
sys.path.insert(0,str(V1));from sensor_core import LinkageGeometry

def main():
 out=R/'T01_REFERENCE_STATIC_FF_V1/COMMON_REFERENCE_GEOMETRY001';out.mkdir(exist_ok=False)
 p=R.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package/reports/model_manifest.json'
 pre=dict(question='fixed mean absolute joint reference vs mean wheel-center xz at NEW recorded M2 references',
  source='bridge_v2.geometry lines19-21 same class,public manifest,trackdefault,radius.0625; no copied FK',
  pose_calls_planned=6,SDK_imports=False,simulation_model_builds=0,forward=0,physics_steps=0,raw_reads=0,
  reference_records=[765,1199],not_causal_proof=True)
 (out/'PREEXEC.json').write_text(json.dumps(pre,indent=2),encoding='utf-8')
 g=LinkageGeometry(json.loads(p.read_text(encoding='utf-8'))['neutral_skeleton_xz_m'],radius=.0625)
 reduction=json.loads((R/'T01_REFERENCE_STATIC_FF_V1/REDUCTION001/RESULT.json').read_text(encoding='utf-8'))
 q0=np.array(reduction['q0_abs']);calls=0
 def pose(q):
  nonlocal calls
  left=g.pose(*q[:2],'left')[0];right=g.pose(*q[2:],'right')[0];calls+=2
  return np.array([left,right])
 base=pose(q0);rows=[]
 for k in (765,1199):
  r=next(v for v in reduction['selected_boundary_and_peak_rows']if v['k']==k);q=np.array(r['qr']);w=pose(q)
  rows.append(dict(k=k,reference_q4=q.tolist(),mean_joint_minus_nominal2_rad=(.5*(q[:2]+q[2:])-.5*(q0[:2]+q0[2:])).tolist(),
   reference_wheel_B_m2=w.tolist(),mean_wheel_shift_B_m=(w.mean(axis=0)-base.mean(axis=0)).tolist(),
   left_minus_right_wheel_B_m=(w[0]-w[1]).tolist(),source='recorded references only,not actual contact/root path'))
 result=dict(protocol=pre,nominal_wheel_B_m2=base.tolist(),records=rows,actual_pose_calls=calls,
  limits=['mean joint preservation is not mean wheel-position preservation',
   'reference positions are NOT measured terrain/contact gaps/COM or proof of support-loss cause',
   'this geometric calculation creates no controller or physical candidate'])
 assert calls==6
 (out/'RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
