"""Supplement existing fixed-policy grid at previously untested standing heights."""
from pathlib import Path
import sys,json,numpy as np,time
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R/'sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112'));import kinematics_audit as audit
E=T/'evidence/mj_parent_height_grid';E.mkdir(exist_ok=False);audit.E=E
for h in (.22,.25,.32,.36,.40):audit.run('parent',audit.actors['parent'],0,(-2.2,-1.5,0.,1.5,2.2),height=h)
np.savez_compressed(E/'TRAJECTORIES.npz',**audit.arrays);(E/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(audit.results),no_optimizer=True)))
