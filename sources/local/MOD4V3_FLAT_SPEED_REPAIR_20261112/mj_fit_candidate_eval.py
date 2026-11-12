"""Closed-loop evaluation of the offline wheel-head repair experiment."""
from pathlib import Path
import sys,json,numpy as np,torch,hashlib,time
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R/'sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112'));import kinematics_audit as audit
p=T/'weights/parent_wheel_head_jointfit_r1.pt';d=torch.load(p,map_location='cpu',weights_only=False);actor=type(audit.actors['parent'])(*[]) if False else __import__('copy').deepcopy(audit.actors['parent']);actor.load_state_dict({k.removeprefix('mlp.'):v for k,v in d['actor_state_dict'].items() if k.startswith('mlp.')});actor.eval()
E=T/'evidence/mj_wheel_head_fit_r1';E.mkdir(exist_ok=False);audit.E=E;audit.identities['wheel_head_fit_r1']=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),derived_from='parent',PPO_updates=0)
for h in (.22,.28,.38,.4):audit.run('wheel_head_fit_r1',actor,0,(-1.5,0.,1.5,2.2),height=h)
np.savez_compressed(E/'TRAJECTORIES.npz',**audit.arrays);(E/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(audit.results),no_optimizer=True)))
