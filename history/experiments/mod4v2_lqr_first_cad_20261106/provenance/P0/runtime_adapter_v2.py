"""Explicit MOD4v2 HW300N60 pre-build adapter. Importing this file has no environment effects.

No Isaac, torch, asset, training job or source task is imported automatically.
Call prepare_environment(opt_in=True) BEFORE importing the selected task module.
Then apply_runtime_cfg(new_cfg, task_module, prebuild=True), before constructing
an environment. This is not a live-environment/articulation patch interface.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
LEG_ORDER = ("left_crank", "left_hip", "right_crank", "right_hip")
_PREPARED = None
_GEOMETRY = None


def _geometry():
    global _GEOMETRY
    if _GEOMETRY is None:
        name = "_mod4v2_HW300N60_source_geometry"
        path = HERE / "kinematics_v2.py"
        previous = sys.modules.get(name)
        if previous is not None:
            if Path(previous.__file__).resolve() != path:
                raise RuntimeError("A different MOD4v2 geometry package is already loaded")
            _GEOMETRY = previous
        else:
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            try:
                spec.loader.exec_module(module)
            except Exception:
                if sys.modules.get(name) is module:
                    del sys.modules[name]
                raise
            _GEOMETRY = module
    return _GEOMETRY


def _requirements():
    return json.loads((HERE / "runtime_requirements.json").read_text(encoding="utf-8"))


def _contract():
    path = HERE / "assets/import_contract.json"
    raw = path.read_bytes()
    contract = json.loads(raw)
    bounds = _geometry().JOINT_BOUNDS
    for side in ("left", "right"):
        for name, expected in bounds.items():
            actual = contract["joints"][side + "_" + name]["limits_si"]
            if expected == [None, None]:
                if actual is not None and actual != expected:
                    raise ValueError(f"v2 active axis remains bounded: {side}_{name}")
            else:
                if actual is None or len(actual) != 2:
                    raise ValueError(f"Missing v2 mechanical stop for {side}_{name}")
                for want, got in zip(expected, actual):
                    if want is None:
                        if got is not None:
                            raise ValueError(f"v2 one-sided stop gained a second bound: {side}_{name}")
                    elif got is None or abs(float(got) - float(want)) > 5.0e-10:
                        raise ValueError(f"v2 stop mismatch: {side}_{name}")
        gas = contract["gas_springs"][side + "_gas_slide"]
        law = _geometry().PARAMS["gas_spring"]
        for key, expected in (("stiffness_n_m", law["stiffness_n_m"]),
                              ("damping_n_s_m", law["damping_n_s_m"]),
                              ("target_position_m", law["target_position_m"][side])):
            if abs(float(gas[key]) - expected) > 1.0e-10:
                raise ValueError(f"HW300N60 configured gas-law mismatch: {side} {key}")
    return contract, hashlib.sha256(raw).hexdigest()


def prepare_environment(*, opt_in: bool = False) -> dict:
    """Explicitly select this portable asset before any source MOD4 task import.

    Stale RM_DIFF_MIN/MAX are REPLACED by geometric mechanical endpoints. They
    never silently restore the old .85 cap or the legacy training soft inset.
    The new action subclass also ignores these old environment keys entirely.
    """
    global _PREPARED
    if not opt_in:
        raise ValueError("MOD4v2 selection requires explicit opt_in=True")
    req = _requirements()
    if (req.get("hardware_spec_status") != "CONFIRMED" or
            req.get("runtime_selection_enabled") is not True):
        raise RuntimeError("Hardware specification unresolved or superseded; runtime selection stays disabled")
    for module in tuple(sys.modules.values()):
        namespace = getattr(module, "__dict__", {})
        if (namespace.get("DelayedJointPositionAction") is not None and
                namespace.get("USD_PATH") is not None and namespace.get("CONTRACT") is not None):
            raise RuntimeError("MOD4 task already imported; start a fresh pre-build process")
    usd = (HERE / "assets/robot.usd").resolve()
    if not usd.is_file():
        raise FileNotFoundError(usd)
    _, contract_sha = _contract()
    geometry = _geometry()
    mechanical = {side: geometry.mechanical_delta_bounds(side) for side in ("left", "right")}
    env = dict(req["environment_before_import"])
    env.update(RM_MOD4_USD=str(usd),
               RM_DIFF_MIN=str(max(pair[0] for pair in mechanical.values())),
               RM_DIFF_MAX=str(min(pair[1] for pair in mechanical.values())))
    stale = {key: os.environ[key] for key in ("RM_DIFF_MIN", "RM_DIFF_MAX") if key in os.environ}
    os.environ.update(env)
    _PREPARED = {"asset": str(usd), "contract_sha256": contract_sha,
                 "environment": env.copy(), "discarded_legacy_diff_environment": stale,
                 "mechanical_delta_by_side_rad": mechanical,
                 "target_physx_verified": False}
    return copy.deepcopy(_PREPARED)


def _target_bounds(soft_delta_window=None) -> dict:
    bounds = {side: _geometry().mechanical_delta_bounds(side) for side in ("left", "right")}
    if soft_delta_window is None:
        return bounds
    if len(soft_delta_window) != 2:
        raise ValueError("Optional soft window must have two explicit endpoints")
    for side, (low, high) in bounds.items():
        soft_low, soft_high = soft_delta_window
        if soft_low is not None:
            if not math.isfinite(soft_low):
                raise ValueError("Soft lower endpoint must be finite or None")
            low = max(low, soft_low)
        if soft_high is not None:
            if not math.isfinite(soft_high):
                raise ValueError("Soft upper endpoint must be finite or None")
            high = min(high, soft_high)
        if low >= high:
            raise ValueError("Optional soft window has no interior in the mechanical branch")
        bounds[side] = (low, high)
    return bounds


def make_mechanical_action_class(task_module, soft_delta_window=None):
    """Subclass the selected source action; replace ONLY its legacy delta guard.

    Original _DelayMixin owns initialization, queue/resampling/hold/reset and its
    super() call into the original JointPositionAction scaling/offset path.
    apply_actions and motor feedback are inherited unchanged. The generated class
    is installed on the new config only, never on task_module or a live manager.
    """
    legacy = task_module.DelayedJointPositionAction
    delay_mixin = task_module._DelayMixin
    base_action = task_module.mdp_actions.JointPositionAction
    if legacy.__bases__ != (delay_mixin, base_action):
        raise TypeError("Unexpected source DelayedJointPositionAction MRO; explicit ABI review required")
    if tuple(task_module.LEG_ORDER) != LEG_ORDER:
        raise ValueError("Source policy leg order changed")
    torch = task_module.torch
    target_bounds = _target_bounds(soft_delta_window)

    class MechanicalDelayedJointPositionActionV2(legacy):
        def __init__(self, cfg, env):
            if tuple(cfg.joint_names) != LEG_ORDER or not cfg.preserve_order:
                raise ValueError("v2 projection requires the original ordered four-leg action ABI")
            super().__init__(cfg, env)  # source _init_delay and source base action are retained
            if self.action_dim != 4:
                raise ValueError("Expected the unchanged four-dimensional leg action term")
            self.v2_delta_bounds = target_bounds.copy()
            self.diff_min = max(pair[0] for pair in target_bounds.values())
            self.diff_max = min(pair[1] for pair in target_bounds.values())

        def process_actions(self, actions):
            # Explicitly skip legacy.process_actions, but NOT the original delay
            # mixin or its super() call into JointPositionAction.process_actions.
            delay_mixin.process_actions(self, actions)
            pa = self.processed_actions
            current = self._asset.data.joint_pos[:, self._joint_ids]
            for side, crank_slot, hip_slot in (("left", 0, 1), ("right", 2, 3)):
                low, high = self.v2_delta_bounds[side]
                # Parent source inspection identified a missing relative-phase lift;
                # this correction is not a claim of a failed or passed SDK run.
                # Lift the periodic target difference near the CURRENT continuous
                # mechanical branch before clamping; never wrap the two axes alone.
                raw_delta = pa[:, crank_slot] - pa[:, hip_slot]
                current_delta = current[:, crank_slot] - current[:, hip_slot]
                relative_turns = torch.round((current_delta - raw_delta) / (2.0 * math.pi))
                delta = (raw_delta + relative_turns * (2.0 * math.pi)).clamp(min=low, max=high)
                target_hip = pa[:, hip_slot]
                turns = torch.round((current[:, hip_slot] - target_hip) / (2.0 * math.pi))
                target_hip = target_hip + turns * (2.0 * math.pi)
                pa[:, hip_slot] = target_hip
                pa[:, crank_slot] = target_hip + delta

    # Stable diagnostic name; this class is a source-bound pre-build factory result.
    MechanicalDelayedJointPositionActionV2.__name__ = "MechanicalDelayedJointPositionActionV2"
    return MechanicalDelayedJointPositionActionV2


def apply_runtime_cfg(cfg, task_module, *, prebuild: bool = False,
                      soft_delta_window=None) -> dict:
    """Configure a NEW source task cfg before env creation; no live env accepted.

    prebuild=True is the caller's explicit construction-stage attestation. Objects
    with live managers/physics handles and already-adapted configs are rejected.
    This function does not replace a running action manager or USD stage.
    """
    if not prebuild or _PREPARED is None:
        raise RuntimeError("Prepare an explicitly opted-in fresh process and pass prebuild=True")
    req = _requirements()
    if (req.get("hardware_spec_status") != "CONFIRMED" or
            req.get("runtime_selection_enabled") is not True):
        raise RuntimeError("Hardware specification changed or remains unresolved")
    if any(hasattr(cfg, name) for name in ("action_manager", "observation_manager", "physics_sim_view")):
        raise TypeError("Expected a new configuration, not a live environment/articulation")
    if getattr(cfg, "_mod4v2_adapter_applied", False):
        raise RuntimeError("This configuration was already adapted; build a fresh config")
    contract, contract_sha = _contract()
    asset = str((HERE / "assets/robot.usd").resolve())
    if contract_sha != _PREPARED["contract_sha256"]:
        raise RuntimeError("v2 contract changed after pre-import preparation")
    if Path(task_module.USD_PATH).resolve() != Path(asset):
        raise RuntimeError("Selected task imported a different USD; restart before task import")
    if task_module.CONTRACT != contract:
        raise RuntimeError("Selected task imported a stale or different contract")
    for name in ("closure", "mimic"):
        term = getattr(cfg.terminations, name, None)
        if term is None or "threshold" not in term.params:
            raise ValueError("Expected original source-compatible termination " + name)
    spawn = cfg.scene.robot.spawn
    if spawn.articulation_props is None or spawn.rigid_props is None:
        raise ValueError("Expected source-compatible spawn property configs")
    action_type = make_mechanical_action_class(task_module, soft_delta_window)
    # Avoid accidentally changing another config through shared class defaults.
    cfg.scene = copy.deepcopy(cfg.scene)
    cfg.sim = copy.deepcopy(cfg.sim)
    cfg.actions = copy.deepcopy(cfg.actions)
    cfg.terminations = copy.deepcopy(cfg.terminations)
    spawn = cfg.scene.robot.spawn
    spawn.usd_path = asset
    spawn.copy_from_source = False
    cfg.sim.dt = 0.0025
    cfg.decimation = 8  # actual policy clock; old task may ignore RM_POLICY_HZ
    cfg.sim.physx.solver_type = 1
    spawn.articulation_props.solver_position_iteration_count = 32
    spawn.articulation_props.solver_velocity_iteration_count = 4
    spawn.rigid_props.enable_gyroscopic_forces = True
    spawn.rigid_props.max_depenetration_velocity = 1.0
    spawn.rigid_props.linear_damping = 0.0
    spawn.rigid_props.angular_damping = 0.0
    cfg.terminations.closure.params["threshold"] = 0.01
    cfg.terminations.mimic.params["threshold"] = 0.01
    cfg.actions.legs.class_type = action_type
    cfg._mod4v2_adapter_applied = True
    return {
        "asset": asset, "contract_sha256": contract_sha,
        "physics_dt_s": 0.0025, "policy_dt_s": 0.02, "policy_hz": 50,
        "feedback_hz_required": 100, "feedback_binding": "inherited external binding; not changed or verified",
        "solver": "TGS32/4", "closure_episode_reset_m": 0.01, "mimic_tolerance_rad": 0.01,
        "action_class": action_type.__name__, "delta_by_side_rad": _target_bounds(soft_delta_window),
        "optional_soft_delta_window": soft_delta_window,
        "source_delay_mixin_retained": True, "source_apply_actions_retained": True,
        "rewards_observations_action_dimensions_and_DR_changed": False,
        "target_physx_verified": False, "live_patch_supported": False,
    }
