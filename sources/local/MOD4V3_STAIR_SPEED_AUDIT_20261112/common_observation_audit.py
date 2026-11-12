"""Common-input policy evaluation and local sensitivities; autograd only, no optimizer."""
from pathlib import Path
import json,numpy as np,torch,hashlib,time
import kinematics_audit as audit
T=Path(__file__).resolve().parent;E=T/'evidence';z=np.load(E/'SPEED_RESPONSE_TRAJECTORIES.npz');reference=z['parent_d5_v2.2_h0.28_observation'][-200:];x=torch.from_numpy(reference)
with torch.no_grad():base=audit.actors['parent'](x)
rows=[]
for name,actor in audit.actors.items():
 with torch.no_grad():y=actor(x)
 v=x.clone().requires_grad_(True);out=actor(v);g=torch.autograd.grad(out[:,4:6].mean(),v)[0]*len(v)
 rows.append(dict(model=name,source='identical parent2.2m/s h.28 observations',mean_action=y.mean(0).tolist(),mean_action_delta=(y-base).mean(0).tolist(),leg_target_delta_rad=((y-base)[:,:4]*.5).mean(0).tolist(),wheel_target_delta_rad_s=((y-base)[:,4:]*10).mean(0).tolist(),local_common_mode_wheel_speed_sensitivity=float(g[:,20:22].sum(-1).mean()),local_common_mode_previous_wheel_action_sensitivity=float(g[:,26:28].sum(-1).mean()),std_param=audit.identities[name]['std_param']))
(E/'COMMON_OBSERVATION_POLICY.json').write_text(json.dumps(dict(no_optimizer=True,identities=audit.identities,rows=rows,interpretation='Same observation prevents confusing changed state feedback with a changed wheel network mapping. These partial derivatives hold all other inputs fixed; they are not full physical closed-loop eigenvalues.'),indent=2),encoding='utf8')
print(json.dumps(rows,ensure_ascii=False))
