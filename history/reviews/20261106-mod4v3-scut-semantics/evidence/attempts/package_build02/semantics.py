"""MOD4v3 physical-coordinate and SCUT semantic-coordinate boundary.

The two front3 hinges lie on loop cuts in the MOD4 spanning tree. Their scalar
angles are measured from front2 to front3, rather than fabricated from a roller.
Arrays may be NumPy arrays or PyTorch tensors; no simulator is imported here.
"""
from __future__ import annotations

import json
from pathlib import Path


class Semantics:
    def __init__(self, package):
        self.package = Path(package)
        self.spec = json.loads((self.package / "semantics.json").read_text(encoding="utf8"))
        self.native_names = tuple(self.spec["coordinates"]["native_order"])
        self.names = tuple(self.spec["coordinates"]["semantic_order"])
        self._expressions = self.spec["coordinates"]["semantic_from_native"]

    @staticmethod
    def _stack(values, like):
        if type(like).__module__.startswith("torch"):
            import torch
            return torch.stack(values, dim=-1)
        import numpy as np
        return np.stack(values, axis=-1)

    @staticmethod
    def _ordered(actual, expected):
        actual = tuple(actual)
        if len(actual) != len(set(actual)):
            raise ValueError("Duplicate runtime joint names")
        missing = set(expected).difference(actual)
        if missing:
            raise ValueError(f"Missing physical coordinates: {sorted(missing)}")
        return [actual.index(name) for name in expected]

    def positions(self, native, names=None):
        """Native v3 radians/metres -> SCUT relative joint radians/metres.

        Native files already include the authored reference offsets. Do not
        apply the legacy-v2 offsets a second time. Continuous angles stay lifted.
        """
        names = tuple(names or self.native_names)
        self._ordered(names, self.native_names)
        index = {name: i for i, name in enumerate(names)}
        return self._stack([
            sum(native[..., index[k]] * coefficient for k, coefficient in expression.items())
            for expression in self._expressions.values()
        ], native)

    velocities = positions
    accelerations = positions

    def native_positions(self, semantic, names=None):
        names = tuple(names or self.names)
        self._ordered(names, self.names)
        values = {n: semantic[..., names.index(n)] for n in self.names}
        for side in ("left", "right"):
            values[side + "_f3r1_joint"] = (
                values[side + "_front3_joint"] - values[side + "_rear1_joint"]
                + values[side + "_front1_joint"] + values[side + "_front2_joint"]
            )
        return self._stack([values[n] for n in self.native_names], semantic)

    def native_forces(self, semantic_tau):
        """Inverse power-conjugate force map: tau_native=A^T tau_sem."""
        values = {n: semantic_tau[..., i] for i, n in enumerate(self.names)}
        for side in ("left", "right"):
            loop = values[side + "_front3_joint"]
            values[side + "_f3r1_joint"] = loop
            values[side + "_rear1_joint"] = values[side + "_rear1_joint"] + loop
            values[side + "_front1_joint"] = values[side + "_front1_joint"] - loop
            values[side + "_front2_joint"] = values[side + "_front2_joint"] - loop
        return self._stack([values[n] for n in self.native_names], semantic_tau)

    def from_legacy_v2(self, q, names):
        """V2 joint coordinates -> v3 native coordinates, including reference offsets."""
        index = {n: i for i, n in enumerate(names)}
        rows = self.spec["coordinates"]["native_from_v2"]
        missing = {v["source"] for v in rows.values()} - index.keys()
        if missing:
            raise ValueError(f"Missing v2 coordinates: {sorted(missing)}")
        return self._stack([q[..., index[row["source"]]] + row["offset_si"]
                            for row in rows.values()], q)

    def generalized_forces(self, native_tau):
        """Power-conjugate force transform: tau_sem = A^(-T) tau_native.

        Merely applying the position map to torque would violate virtual work.
        These are generalized forces, not an invented motor on a passive hinge.
        """
        index = {n: i for i, n in enumerate(self.native_names)}
        values = {n: native_tau[..., i] for n, i in index.items()}
        for side in ("left", "right"):
            loop = values[side + "_f3r1_joint"]
            values[side + "_front3_joint"] = loop
            values[side + "_rear1_joint"] = values[side + "_rear1_joint"] - loop
            values[side + "_front1_joint"] = values[side + "_front1_joint"] + loop
            values[side + "_front2_joint"] = values[side + "_front2_joint"] + loop
        return self._stack([values[n] for n in self.names], native_tau)

    def action_to_native(self, actions, native_names=None):
        """SCUT's four ordered leg targets and two wheel velocities -> name bindings.

        This returns targets; the package's MOD4 motor limits and PD/envelope
        remain the controller's responsibility. No SCUT hardware limits are copied.
        """
        expected = self.spec["control"]["policy_action_order"]
        if actions.shape[-1] != len(expected):
            raise ValueError("Expected four SCUT leg targets followed by two wheel velocities")
        requested = tuple(native_names or self.native_names)
        self._ordered(requested, expected)
        return {n: actions[..., i] for i, n in enumerate(expected)}

    def decode_actions(self, raw_actions, default_leg_positions, *, leg_scale,
                       wheel_scale, wheel_mode):
        """Decode the SCUT raw-action formula with explicit controller settings.

        Upstream uses default_joint_pos+leg_action_scale*raw_leg_action; wheel
        control can be velocity or torque. No mode or action scale is guessed.
        """
        if wheel_mode not in ("velocity", "torque"):
            raise ValueError("Explicit wheel mode: velocity or torque")
        if raw_actions.shape[-1] != 6 or default_leg_positions.shape[-1] != 4:
            raise ValueError("Expected six raw actions and four default leg angles")
        targets = {n: default_leg_positions[..., i] + leg_scale * raw_actions[..., i]
                   for i,n in enumerate(self.spec["control"]["policy_action_order"][:4])}
        wheels = {n: wheel_scale * raw_actions[..., 4+i]
                  for i,n in enumerate(self.spec["control"]["policy_action_order"][4:])}
        return dict(leg_position_targets=targets, wheel_targets=wheels, wheel_mode=wheel_mode)

    def mujoco_joint_state(self, model, data):
        """Actual compiled-state reader returning anatomical SCUT coordinates."""
        import numpy as np
        q=np.array([data.qpos[model.joint(n).qposadr[0]] for n in self.native_names])
        v=np.array([data.qvel[model.joint(n).dofadr[0]] for n in self.native_names])
        a=np.array([data.qacc[model.joint(n).dofadr[0]] for n in self.native_names])
        tau=np.array([data.qfrc_actuator[model.joint(n).dofadr[0]] for n in self.native_names])
        return dict(names=self.names,joint_pos=self.positions(q),joint_vel=self.velocities(v),
                    joint_acc=self.accelerations(a),applied_torque=self.generalized_forces(tau))

    def require_reference(self, names, kind="joint"):
        rows = self.spec["reference_coverage"]["joints" if kind == "joint" else "bodies"]
        lookup = {row["scut"]: row for row in rows}
        for name in names:
            if name not in lookup or lookup[name]["status"] == "absent_on_MOD4":
                raise ValueError(f"SCUT {kind} has no MOD4 counterpart: {name}")
        return [lookup[n] for n in names]


class ScutRobotView:
    """Name/query/data view that SCUT rewards can consume with raw joint queries.

    Physical scalar coordinates retain the original loop cut. The reward-facing
    joint table exposes front3 as a genuine *derived relative angle*, while the
    supplied USD still identifies its actual physical hinge/closure topology.
    Runtime articulation and contact-sensor indices must each be resolved from
    their own name tables. No missing gimbal/roller is replaced by a dummy zero.
    """
    def __init__(self, robot, package, *, quaternion_order):
        if quaternion_order not in ("xyzw", "wxyz"):
            raise ValueError("Explicit native quaternion order required")
        self.raw=robot
        self.semantics=Semantics(package)
        self.joint_names=list(self.semantics.names)
        self.body_names=list(robot.body_names)
        self._native_ids=self.semantics._ordered(robot.joint_names,self.semantics.native_names)
        required=self.semantics.spec['source_to_v3']['bodies'].values()
        if set(required).difference(self.body_names):
            raise ValueError("Robot body table does not belong to the v3 package")
        self.quaternion_order=quaternion_order
        self.data=_ScutDataView(self)

    def _find(self, patterns, names, preserve_order=False):
        import re
        patterns=[patterns] if isinstance(patterns,str) else list(patterns)
        matches=[]
        if preserve_order:
            for pattern in patterns:
                ids=[i for i,n in enumerate(names) if re.fullmatch(pattern,n)]
                if not ids:
                    raise ValueError(f"Unmatched semantic selector: {pattern}")
                matches.extend(i for i in ids if i not in matches)
        else:
            for pattern in patterns:
                if not any(re.fullmatch(pattern,n) for n in names):
                    raise ValueError(f"Unmatched semantic selector: {pattern}")
            matches=[i for i,n in enumerate(names) if any(re.fullmatch(p,n) for p in patterns)]
        return matches,[names[i] for i in matches]

    def find_joints(self, patterns, preserve_order=False):
        return self._find(patterns,self.joint_names,preserve_order)

    def find_bodies(self, patterns, preserve_order=False):
        return self._find(patterns,self.body_names,preserve_order)


class _ScutDataView:
    def __init__(self, view):
        self.view=view

    def __getattr__(self, name):
        view=self.view
        value=getattr(view.raw.data,name)
        if name in ("joint_pos","default_joint_pos","joint_vel","joint_acc","default_joint_vel","applied_torque"):
            value=value[...,view._native_ids]
            return (view.semantics.generalized_forces(value) if name=='applied_torque'
                    else view.semantics.positions(value))
        if name.endswith('quat_w') and view.quaternion_order=='xyzw':
            return value[...,[3,0,1,2]]
        return value


def weighted_rewards(terms, weights, control_dt):
    """Explicit reward registration. Missing nonzero terms are errors, not zero."""
    if not control_dt > 0:
        raise ValueError("Positive control timestep required")
    missing = [k for k, w in weights.items() if w != 0 and k not in terms]
    if missing:
        raise KeyError(f"Enabled rewards were not computed: {missing}")
    active = {k: terms[k] * w * control_dt for k, w in weights.items() if w != 0}
    if not active:
        raise ValueError("No enabled reward terms")
    return sum(active.values()), active


def termination_reward_term(terminated, truncated):
    """Use final flags from the pre-reset endpoint; a timeout alone is not a fall.

    A true failure on the horizon is still a failure. Learners must separately
    bootstrap truncation from the terminal observation, never the reset observation.
    """
    if terminated.shape != truncated.shape:
        raise ValueError("Termination and truncation shapes differ")
    return terminated


def kinematic_measures(root_pos, root_quat_wxyz, wheel_pos, hip_anchor_b):
    """Separate SCUT projected-leg features from MOD4's old 3-D L0 and theta.

    Reference SCUT uses a base-origin, heading-frame vector with its y set to 0.
    Its signed leg angle is atan2(-x,-z). A real hip-to-wheel 3-D norm is also
    returned with a different name so that callers cannot silently conflate them.
    NumPy implementation is for probes/offline readers; training can use the
    same explicit formulas with its device tensor operations.
    """
    import numpy as np
    from scipy.spatial.transform import Rotation
    q = np.asarray(root_quat_wxyz)
    rotation = Rotation.from_quat(q[..., [1, 2, 3, 0]])
    rel = np.asarray(wheel_pos) - np.asarray(root_pos)[..., None, :]
    matrix = rotation.as_matrix()
    body = np.einsum("...ji,...kj->...ki", matrix, rel)
    yaw = np.arctan2(matrix[..., 1, 0], matrix[..., 0, 0])
    c, s = np.cos(yaw)[..., None], np.sin(yaw)[..., None]
    heading = np.stack((c*rel[..., 0] + s*rel[..., 1],
                        -s*rel[..., 0] + c*rel[..., 1], rel[..., 2]), axis=-1)
    scut_projected = heading.copy()
    scut_projected[..., 1] = 0
    hip_vector = body - np.asarray(hip_anchor_b)
    return dict(scut_wheel_position_heading_xz=scut_projected,
                scut_leg_length_xz=np.linalg.norm(scut_projected, axis=-1),
                scut_leg_angle=np.arctan2(-scut_projected[..., 0], -scut_projected[..., 2]),
                hip_to_wheel_vector_b=hip_vector,
                hip_to_wheel_length_3d=np.linalg.norm(hip_vector, axis=-1),
                mod4_theta=np.arctan2(hip_vector[..., 0], -hip_vector[..., 2]))
