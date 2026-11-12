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
Joint limit arrays are reordered and transformed too. Derived front3 interval
and speed limits are conservative bounds; they are not new physical stops.
Physical per-joint stiffness, armature and friction do not remain diagonal
across the changed cut: access those through `view.raw.data` and the raw names.
The view raises an error for unsupported joint properties instead of returning
an incorrectly indexed array. It is a read interface; writes use the backend.
Pass `position_basis='mjcf_absolute'`, `'usd_absolute'`, or
`'newton_displacement'` explicitly. Newton `joint_q` is relative to the authored
pose; the view adds the corresponding ref once before exposing reward angles.

`runtime_config.json` supplies the real anatomical default positions. All-zero
anatomical coordinates are **not** the MOD4 assembly pose. Policy actions use
`default_position + leg_scale * raw_action`; wheel mode and scale are explicit.
`decode_actions` requires `position_basis` for output targets as well: choose
`newton_displacement` for Newton controls, or `mjcf_absolute`/`usd_absolute` for
absolute-angle controllers. Supply anatomical absolute default leg positions;
the helper subtracts the authored ref once for Newton leg targets. Wheel
velocity and torque never receive an angular reference offset.
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

From the delivery folder, run `python tools/validate.py . --report NEW_REPORT.json`.
This full equivalence validator also needs the immutable MOD4v2 source files at
the paths recorded in `PROVENANCE.json`; the portable runtime helpers do not.
`tools/probe_newton.py` additionally checks the installed Newton/SolverMuJoCo on
CPU. Native USD inspection and MuJoCo checks do not claim PhysX GPU approval.
With PyTorch installed, `python tools/probe_torch.py . --report TORCH_CHECK.json`
checks reordered runtime tables, target reference conversion and autograd on CPU.
`assets/robot_physx.usda` is the optional OmniPhysics finite-angle wrapper. It
encodes only infinite limit ends as 1e20 degrees; finite CAD stops and the
physical asset remain inherited from `robot.usd`. Native PhysX dynamics of this
new v3 wrapper have not been run.

No training, physics randomization, reward reweighting, or active-task asset
replacement occurs as part of this delivery. The package reports physical
representation and the actual verification scope separately.
