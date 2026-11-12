"""Diagnostic property parity variants in memory; authored XML/PT unchanged."""
from pathlib import Path
import sys,json,numpy as np,time
T=Path(__file__).resolve().parent;R=T.parents[2];sys.path.insert(0,str(R/'sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112'));import kinematics_audit as audit
E=T/'evidence/mj_property_ablation';E.mkdir(exist_ok=True);audit.E=E
factory=audit.replay.Simulation;variant='original'
def modified(args):
 s=factory(args);m=s.env.m
 if variant in ('zero_active_damping','match_native_dynamics'):
  for n in s.active_names:m.dof_damping[s.env.dadr_all[s.env.spec.joint_names.index(n)]]=0.
 if variant in ('zero_passive_armature','match_native_dynamics'):
  for n in s.env.spec.joint_names:
   if n not in s.active_names and not n.endswith('_spring2_joint'):m.dof_armature[s.env.dadr_all[s.env.spec.joint_names.index(n)]]=0.
 if variant=='match_native_dynamics':
  for n in s.env.spec.joint_names:
   if n.endswith('_guide_joint'):m.dof_damping[s.env.dadr_all[s.env.spec.joint_names.index(n)]]=0.
 return s
audit.replay.Simulation=modified
for variant in ('original','zero_active_damping','zero_passive_armature','match_native_dynamics'):
 for name in ('parent','010m'):
  for h in (.28,.38):
   label=name+'__'+variant;audit.run(label,audit.actors[name],0,(2.2,),height=h)
np.savez_compressed(E/'TRAJECTORIES.npz',**audit.arrays)
(E/'COMPLETE.json').write_text(json.dumps(dict(epoch=time.time(),cases=len(audit.results),no_optimizer=True,all_property_changes_in_memory_only=True)),encoding='utf8')
