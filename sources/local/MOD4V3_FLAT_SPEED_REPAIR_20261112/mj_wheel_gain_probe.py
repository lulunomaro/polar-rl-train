"""Frozen MuJoCo controller-gain parity test, no file/plant edits."""
from pathlib import Path
import sys,json,numpy as np,torch,time
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R/'sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112'));import kinematics_audit as audit
E=T/'evidence/mj_wheel_kd02_r1';E.mkdir(exist_ok=False);audit.E=E;factory=audit.replay.Simulation

def setup(args):
 s=factory(args);e=s.env;original=e._torque
 def torque(a):
  result=original(a);v=torch.as_tensor(e.d.qvel[e.dadr_all],dtype=torch.float32)[e.wheel_ids].unsqueeze(0)
  raw=.2*(10.*a[:,4:6]-v);stall=v.new_tensor([28.18525375641699]*2);no=v.new_tensor([55.35573187814664]*2);peak=v.new_tensor([5.775909774436091]*2)
  hi=(stall*(1-v/no)).clamp_min(0).minimum(peak);lo=(-stall*(1+v/no)).clamp_max(0).maximum(-peak);result[:,4:]=raw.minimum(hi).maximum(lo);return result
 e._torque=torque;return s
audit.replay.Simulation=setup
for name in ('parent','010m'):
 for h in (.28,.38):audit.run(name+'__kd02',audit.actors[name],0,(-1.5,0.,2.2),height=h)
np.savez_compressed(E/'TRAJECTORIES.npz',**audit.arrays);(E/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(audit.results),no_optimizer=True,in_memory_wheel_feedback=.2,canonical_plant_unchanged=True)))
