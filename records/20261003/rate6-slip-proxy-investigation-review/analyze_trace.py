"""Control-rate kinematic decomposition, never a contact-manifold claim."""
import json,sys
from pathlib import Path
import numpy as np
D=Path(__file__).parent
model=int(sys.argv[1]) if len(sys.argv)>1 else 16929
z=np.load(D/f'model{model}_shadow.trace.npz');a=z['trace'];ids=z['environment_ids']
link=a[...,3:6];mid=a[...,9:12];w=a[...,12:15];arm=a[...,15:18];axis=a[...,21:24]
up=np.zeros_like(axis);up[...,2]=1
roll=np.cross(axis,up);roll/=np.maximum(np.linalg.norm(roll,axis=-1,keepdims=True),1e-8)
side=axis.copy();side[...,2]=0;side/=np.maximum(np.linalg.norm(side,axis=-1,keepdims=True),1e-8)
origin=link-np.cross(w,arm)
spin=(w*axis).sum(-1)[...,None]*axis
own_spin=np.cross(spin,arm);other_rot=np.cross(w-spin,arm)
valid=a[...,29].astype(bool);loaded=valid & (a[...,27]>=10)
quantities=dict(link_rolling_signed=(link*roll).sum(-1),link_axial_signed=(link*side).sum(-1),midplane_rolling_signed=(mid*roll).sum(-1),midplane_axial_signed=(mid*side).sum(-1),wheel_origin_rolling_signed=(origin*roll).sum(-1),own_spin_rolling_signed=(own_spin*roll).sum(-1),other_rotation_rolling_signed=(other_rot*roll).sum(-1),wheel_axis_angular_speed=(w*axis).sum(-1),link_horizontal_speed=np.linalg.norm(link[...,:2],axis=-1))
rows=[]
for gid in (7,8):
 selected=np.flatnonzero(ids%11==gid);r=dict(group_id=gid,environment_ids=ids[selected].tolist(),quantities={})
 for name,q in quantities.items():
  records=[]
  for j in selected:
   vals=[]
   for wheel in (0,1):
    v=q[:,j,wheel][valid[:,j,wheel]];l=q[:,j,wheel][loaded[:,j,wheel]]
    vals.append(dict(signed_mean=float(v.mean()),mean_abs=float(np.abs(v).mean()),loaded_mean_abs=float(np.abs(l).mean()),quantiles=np.quantile(v,[.05,.5,.95]).tolist()))
   records.append(vals)
  r['quantities'][name]=records
 rows.append(r)
review=dict(model=model,trace_sampling_s=float(z['step_dt']),groups=rows,production_or_gate_changed=False,not_PhysX_contact_manifold=True,no_new_policy_acceptance=True)
(D/f'TRACE_REVIEW_{model}.json').write_text(json.dumps(review,indent=2),encoding='utf8')
for row in rows:
 print('group',row['group_id'])
 for k,v in row['quantities'].items():print(k,np.mean([[c['signed_mean'] for c in wheels] for wheels in v],axis=0).tolist())
