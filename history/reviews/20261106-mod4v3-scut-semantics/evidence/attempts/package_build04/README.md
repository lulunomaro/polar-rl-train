# MOD4v3 source

Build a separate HW300N60 package from the immutable MOD4v2 delivery and the
SCUT V14_2 USD at the recorded repository commit. `build.py` derives semantic
zeros from homologous mechanical rays, changes body coordinate frames without
changing physical shapes/inertia, and records every reference body and pivot.

The same physical six-bar mechanism uses a different spanning-tree cut at
front3. The faithful files retain that cut and their original constraint
physics. `semantics.Semantics` exposes the SCUT front2-to-front3 coordinate,
with its exact invertible position/velocity and power-conjugate force mapping.
The USD front3 pivot is consequently a spherical loop closure, and f3r1 is a
tree hinge. Calling an articulation's raw front3 selector is not equivalent to
reading the semantic coordinate; use the supplied `ScutRobotView` interface.
It supports `find_joints`, `find_bodies`, joint position/velocity/acceleration,
power-conjugate actuator force and explicit quaternion ordering. Missing
requested reference joints raise errors. Resolve contacts in sensor name space.

`runtime_config.json` supplies the real anatomical default positions. All-zero
anatomical coordinates are **not** the MOD4 assembly pose. Policy actions use
`default_position + leg_scale * raw_action`; wheel mode and scale are explicit.
`kinematics.py` solves the original MOD4 mechanism in the v3 coordinates, rather
than using SCUT's different link lengths. Its initial controller/force envelopes
retain MOD4 motor specifications and the asset-owned gas spring.

A trial with the SCUT tree cut was rejected: the installed MuJoCo 3.15 compiler
did not preserve cross-branch fixed-tendon armature cross terms. The failed
candidate and reports remain in the experiment archive and are not release
assets. The default model retains the verified original cut.

SCUT's public reference revision contains USD assets and **no MJCF**. The package
records that absence rather than using a Fudan/old-infantry MJCF as SCUT V14.
The native reference is the actual USD plus inherited task code and configured
joint ordering. There are no gimbal bodies and fewer guide rollers on MOD4;
their absent reference names are explicit errors when requested.

Example (all paths are supplied rather than embedded in the portable runtime):

```powershell
python build.py --source-package PATH_TO_HW300N60_PACKAGE --reference-repo PATH_TO_SCUT_REPO --output NEW_DIRECTORY
python validate.py NEW_DIRECTORY
```

No training, physics randomization, reward reweighting, or active-task asset
replacement occurs as part of this delivery. The package reports physical
representation and the actual verification scope separately.
