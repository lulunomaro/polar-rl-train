"""MOD4 D0--D7 engineering DR for the independent 400 N MuJoCo plant.

Only ``sample`` writes model parameters; this module never advances physics.
Action arrays use MuJoCo actuator order (Lhip, Lcrank, Lwheel, Rhip,
Rcrank, Rwheel).  Feedback leg arrays retain the historical policy order
(Lcrank, Lhip, Rcrank, Rhip).  Call ``observe`` exactly once per 100 Hz
feedback sample, even when high-level control runs at 50 Hz.  Call
``process_targets`` on EVERY physical application tick with the current
processed position/velocity targets, not already computed motor torques.

The caller keeps the original low-level sequence::

    raw clip +/-6 -> leg .5 rad / wheel 10 rad/s scale + offset
    -> crank-minus-hip CAD projection [-1.0843, .85]
    -> process_targets -> current-state explicit PD -> signed DC clip
    -> motor_gain6 -> the SAME signed DC clip again

Nominal explicit PD is leg60/2, wheel0/.6.  D7 changes those coefficients;
nominal inverse PD must not use randomized coefficients/gains to cancel DR.
Gas force is k*(qpos_spring-q)-c*qd, with the original spring reference kept.
D6 varies only the two gas damping coefficients, not joint friction.

All distributions are engineering pressure ranges, not measured calibration.
RNG families are independent and reproducible under this NumPy implementation;
Torch/CUDA historical random streams are not claimed byte-identical.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
from numbers import Integral
from types import SimpleNamespace
import json

import numpy as np

ACTUATOR_ORDER = (
    "left_hip", "left_crank", "left_wheel_spin",
    "right_hip", "right_crank", "right_wheel_spin",
)
LEG_FEEDBACK_ORDER = ("left_crank", "left_hip", "right_crank", "right_hip")
LEG_ACTUATOR_INDICES = np.array([0, 1, 3, 4], dtype=int)
WHEEL_ACTUATOR_INDICES = np.array([2, 5], dtype=int)
GAS_NAMES = ("left_gas_slide", "right_gas_slide")
CHANNELS = {
    "omega3": (3, .125, 101),
    "gravity3": (3, .025, 203),
    "legq4": (4, .005, 307),
    "legqd4": (4, .25, 409),
    "wheelqd2": (2, .5, 503),
}
NOMINAL_KP6 = np.array([60., 60., 0., 60., 60., 0.])
NOMINAL_KD6 = np.array([2., 2., .6, 2., 2., .6])


def _vector(value, width, name):
    a = np.asarray(value, dtype=np.float64)
    if a.shape != (width,) or not np.isfinite(a).all():
        raise ValueError(f"{name} must be a finite ({width},) vector")
    return a.copy()


def _id(model, kind, name):
    value = int(getattr(model, kind)(name).id)
    if value < 0:
        raise ValueError(f"missing MOD4 {kind}: {name}")
    return value


class FullDR:
    """Sample one fresh model/episode; reuse its coefficients until discarded.

    ``sample`` accepts either ``control_core.Plant`` or its ``.m`` MjModel.
    It is deliberately one-shot so accidental repeated calls cannot compound
    masses/inertias or COM shifts.  ``reset(initial_target6)`` clears feedback
    and target queues without drawing a second physical episode.  Create a new
    FullDR and a fresh nominal model for an independently randomized episode.
    ``sampled`` and the return value of ``sample`` are JSON-serializable.
    """

    def __init__(self, seed, nominal=False):
        if isinstance(seed, bool) or not isinstance(seed, Integral) or seed < 0:
            raise ValueError("seed must be a nonnegative integer")
        self.seed = int(seed)
        self.nominal = bool(nominal)
        self._sampled = False
        self.sampled = None
        self.physics_dt = .0005
        self.motor_gain6 = np.ones(6)
        self.KP6 = NOMINAL_KP6.copy()
        self.KD6 = NOMINAL_KD6.copy()
        self.bias4 = np.zeros(4)
        self.obs_delay_ticks = 0
        self.action_delay_ticks6 = np.zeros(6, dtype=int)
        self._noise_rng = {k: self._rng(913007 + row[2]) for k, row in CHANNELS.items()}
        self.reset(np.zeros(6))

    def _rng(self, namespace):
        return np.random.default_rng(np.random.SeedSequence([self.seed, int(namespace)]))

    def sample(self, model):
        """Apply exact D0/D5/D6/D7 ranges to a fresh 400 N model once.

        D0's 20% nominal selection is shared ONLY by D0 mass/inertia, all six
        motor gains and wheel friction.  D1--D7 remain independently active.
        Tire priority is raised above other geoms so MuJoCo's max-friction
        mixing cannot mask sampled tire mu below a .9 floor.  Existing explicit
        tire pairs receive matching sliding coefficients as well.
        Real MjModel constants are refreshed via mj_setConst, without mj_step.
        """
        if self._sampled:
            raise RuntimeError("FullDR.sample is one-shot; use a fresh model and FullDR")
        plant = model if hasattr(model, "m") else None
        m = plant.m if plant is not None else model
        if int(m.nu) != 6:
            raise ValueError("the MOD4 contract requires six actuators")
        dt = float(m.opt.timestep)
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("positive finite physics timestep required")
        delay_tick = int(round(.0025 / dt))
        if delay_tick < 1 or not np.isclose(delay_tick * dt, .0025, atol=1e-12, rtol=0):
            raise ValueError("physics timestep must exactly divide the 2.5 ms D4 quantum")

        chassis = _id(m, "body", "chassis")
        tires = np.array([_id(m, "geom", side + "_tire") for side in ("left", "right")])
        gas_ids = np.array([_id(m, "joint", name) for name in GAS_NAMES])
        gas_dofs = np.asarray(m.jnt_dofadr)[gas_ids].astype(int)
        gas_qpos = np.asarray(m.jnt_qposadr)[gas_ids].astype(int)
        nominal_k = np.asarray(m.jnt_stiffness)[gas_ids].copy()
        nominal_d = np.asarray(m.dof_damping)[gas_dofs].copy()
        springref = np.asarray(m.qpos_spring)[gas_qpos].copy()
        if not np.allclose(nominal_k, 2000., atol=1e-8, rtol=0):
            raise ValueError("fresh nominal400 gas stiffness must be 2000 N/m")
        if not np.allclose(nominal_d, 3., atol=1e-8, rtol=0):
            raise ValueError("fresh nominal400 gas damping must be 3 Ns/m")
        if not np.allclose(springref, .2206394410901294, atol=1e-8, rtol=0):
            raise ValueError("the original MOD4 gas preload reference must be retained")

        d0 = self._rng(1717)
        d0_nominal = self.nominal or bool(d0.random() < .20)
        mass_factor = 1. if d0_nominal else float(d0.uniform(.9, 1.1))
        gains = np.ones(6) if d0_nominal else d0.uniform(.9, 1.1, 6)
        buckets = np.r_[.9, np.linspace(.7, 1., 32)]
        # Historical randomized D0 episodes choose from the 32 nonnominal buckets.
        bucket_index = 0 if d0_nominal else int(self._rng(1818).integers(1, 33))
        mu = float(buckets[bucket_index])
        spring_factors = np.ones(2) if self.nominal else np.array([
            self._rng(offset).uniform(.9, 1.1) for offset in (790103, 790123)
        ])
        damping_factors = np.ones(2) if self.nominal else np.array([
            self._rng(offset + 170003).uniform(.9, 1.1) for offset in (790103, 790123)
        ])
        com_delta = np.zeros(3) if self.nominal else np.array([
            self._rng(190009 + axis * 100003).uniform(-.005, .005) for axis in range(3)
        ])
        kp_f = np.ones(4) if self.nominal else self._rng(230003).uniform(.95, 1.05, 4)
        kd_f = np.ones(4) if self.nominal else self._rng(330006).uniform(.95, 1.05, 4)
        wkd_f = np.ones(2) if self.nominal else self._rng(430009).uniform(.95, 1.05, 2)
        bias = np.zeros(4) if self.nominal else self._rng(913007).uniform(-.0075, .0075, 4)
        obs_delay = 0 if self.nominal else int(self._rng(1400039).integers(0, 2))
        leg_delay = 0 if self.nominal else int(self._rng(2100037).integers(0, 3)) * delay_tick
        wheel_delay = 0 if self.nominal else int(self._rng(3100097).integers(0, 3)) * delay_tick

        # MuJoCo physical indexing excludes world body0; body inertia is expressed
        # about its local COM, and D7 translates that COM without changing inertia.
        m.body_mass[1:] *= mass_factor
        m.body_inertia[1:] *= mass_factor
        m.body_ipos[chassis] += com_delta
        m.jnt_stiffness[gas_ids] = nominal_k * spring_factors
        m.dof_damping[gas_dofs] = nominal_d * damping_factors
        m.geom_friction[tires, 0] = mu
        old_priorities = np.asarray(m.geom_priority)[tires].copy()
        others = np.ones(len(m.geom_priority), dtype=bool)
        others[tires] = False
        other_max = int(np.max(np.asarray(m.geom_priority)[others])) if others.any() else 0
        new_priorities = np.maximum(old_priorities, other_max + 1)
        m.geom_priority[tires] = new_priorities
        explicit_pairs = []
        for pair in range(int(getattr(m, "npair", 0))):
            if int(m.pair_geom1[pair]) in tires or int(m.pair_geom2[pair]) in tires:
                m.pair_friction[pair, :2] = mu
                explicit_pairs.append(pair)

        constants_refreshed = False
        if type(m).__module__.startswith("mujoco"):
            import mujoco
            mujoco.mj_setConst(m, mujoco.MjData(m))
            constants_refreshed = True
        if plant is not None and hasattr(plant, "mass"):
            plant.mass = float(np.sum(m.body_mass))

        self.physics_dt = dt
        self.motor_gain6 = gains.copy()
        self.KP6 = NOMINAL_KP6.copy()
        self.KD6 = NOMINAL_KD6.copy()
        self.KP6[LEG_ACTUATOR_INDICES] *= kp_f
        self.KD6[LEG_ACTUATOR_INDICES] *= kd_f
        self.KD6[WHEEL_ACTUATOR_INDICES] *= wkd_f
        self.bias4 = bias
        self.obs_delay_ticks = obs_delay
        self.action_delay_ticks6 = np.array([leg_delay, leg_delay, wheel_delay] * 2, dtype=int)
        self._sampled = True
        self.sampled = {
            "schema": "mod4.mujoco400N.full_D0_D7.v1",
            "seed": self.seed, "nominal": self.nominal,
            "actuator_order": list(ACTUATOR_ORDER),
            "leg_feedback_order": list(LEG_FEEDBACK_ORDER),
            "physics_dt_s": dt, "feedback_period_s": .01,
            "D0": {
                "profile": "white_v3", "D0_only_nominal_episode": d0_nominal,
                "nominal_probability": .20,
                "all_moving_bodies_shared_mass_inertia_factor": mass_factor,
                "motor_gain6": self.motor_gain6.tolist(),
                "wheel_sliding_mu": mu, "wheel_friction_bucket_index": bucket_index,
                "wheel_friction_buckets": buckets.tolist(),
                "tire_geom_ids": tires.tolist(), "tire_priority_before": old_priorities.tolist(),
                "tire_priority_after": new_priorities.tolist(),
                "explicit_tire_pairs_updated": explicit_pairs,
                "nonwheel_friction_unchanged": True,
                "gain_application": "signed DC clip -> motor_gain6 -> signed DC clip",
            },
            "D1": {"raw_uniform_half_widths": {k: row[1] for k, row in CHANNELS.items()},
                   "enabled": not self.nominal, "sample_hz": 100,
                   "units": {"omega3": "rad/s", "gravity3": "dimensionless", "legq4": "rad", "legqd4": "rad/s", "wheelqd2": "rad/s"}},
            "D2": {"episode_leg_bias4_rad": self.bias4.tolist(), "true_joint_state_unchanged": True},
            "D3": {"shared_feedback_delay_ticks100Hz": obs_delay,
                   "requested_delay_us": obs_delay * 10000,
                   "noise_bias_before_queue": True, "first_sample_age_us": 0,
                   "only_five_feedback_channels_delayed": True,
                   "BODY_components_kept_in_sample_frame": True},
            "D4": {"action_delay_ticks6": self.action_delay_ticks6.tolist(),
                   "action_delay_us6": (self.action_delay_ticks6 * dt * 1e6).round().astype(int).tolist(),
                   "independent_leg_and_wheel_episode_lags": True,
                   "queued_values": "processed leg position rad / wheel velocity rad_s; current-state PD after queue",
                   "reset_initial": "caller actual/default leg q and zero wheel velocity; all stale samples cleared"},
            "D5": {"gas_joint_names": list(GAS_NAMES), "stiffness_factor2": spring_factors.tolist(),
                   "stiffness_N_m2": np.asarray(m.jnt_stiffness)[gas_ids].tolist(),
                   "springref_m2": springref.tolist(), "preload_reference_unchanged": True},
            "D6": {"gas_damping_factor2": damping_factors.tolist(),
                   "gas_damping_Ns_m2": np.asarray(m.dof_damping)[gas_dofs].tolist(),
                   "joint_friction_randomization": False},
            "D7": {"chassis_local_COM_delta_m3": com_delta.tolist(),
                   "leg_kp_factor4_actuator_leg_order": kp_f.tolist(),
                   "leg_kd_factor4_actuator_leg_order": kd_f.tolist(),
                   "wheel_kd_factor2": wkd_f.tolist(),
                   "KP6": self.KP6.tolist(), "KD6": self.KD6.tolist(),
                   "inertia_tensor_about_COM_unchanged_by_D7": True},
            "model_constants_refreshed": constants_refreshed,
            "engineering_pressure_not_hardware_calibration": True,
            "legacy_push_armature_joint_friction_DR_enabled": False,
            "historical_CUDA_RNG_bit_identity_claimed": False,
        }
        self.reset(np.zeros(6))
        # Prove the public receipt contains no ndarray/scalar objects or NaNs.
        json.dumps(self.sampled, allow_nan=False)
        return deepcopy(self.sampled)

    def reset(self, initial_target6):
        """Clear D1/D3 caches and D4 pending values; retain episode parameters.

        The caller supplies real/default leg joint positions and zero wheel
        velocity in actuator order.  Reset does not draw another bias or lag.
        """
        initial = _vector(initial_target6, 6, "initial_target6")
        self._feedback_previous = None
        self.feedback_samples = 0
        self.last_feedback_age_us = 0
        self._target_applied = initial.copy()
        self._target_previous_input = initial.copy()
        self._target_pending = {"legs": deque(), "wheels": deque()}
        self._target_last_tick = None
        self._target_last_call_input = None
        self._target_issue_tick6 = np.full(6, -1, dtype=int)
        self._target_first_apply_latency6 = np.full(6, -1, dtype=int)

    def observe(self, clean):
        """Return one noisy/delayed 100 Hz feedback sample; never mutate input.

        Required keys: omega3, gravity3, legq4, legqd4, wheelqd2.  Additional
        fields pass through without delay.  The first sample after reset uses
        this episode's current noisy sample even when the selected lag is one.
        """
        if not isinstance(clean, dict):
            raise ValueError("clean must be a dict of feedback arrays")
        noisy = {}
        for key, (width, half_width, _) in CHANNELS.items():
            if key not in clean:
                raise ValueError("missing feedback channel " + key)
            value = _vector(clean[key], width, key)
            if not self.nominal:
                value += self._noise_rng[key].uniform(-half_width, half_width, width)
                if key == "legq4":
                    value += self.bias4
            noisy[key] = value
        delayed = self.obs_delay_ticks == 1 and self._feedback_previous is not None
        selected = self._feedback_previous if delayed else noisy
        out = deepcopy(clean)
        out.update({key: value.copy() for key, value in selected.items()})
        self._feedback_previous = {key: value.copy() for key, value in noisy.items()}
        self.feedback_samples += 1
        self.last_feedback_age_us = 10000 if delayed else 0
        return out

    def process_targets(self, target6, tick_phys):
        """Delay coherent processed leg/wheel targets at real physics ticks.

        Each changed target group is issued once; unchanged held targets do not
        create duplicate queue entries.  Both groups use independent episode
        lags.  Consecutive physics calls make the first-transition latency
        exact.  A repeated call at one tick must contain the same input.
        """
        value = _vector(target6, 6, "target6")
        if isinstance(tick_phys, bool) or not isinstance(tick_phys, Integral) or tick_phys < 0:
            raise ValueError("tick_phys must be a nonnegative integer")
        tick = int(tick_phys)
        if self._target_last_tick is not None:
            if tick == self._target_last_tick:
                if not np.array_equal(value, self._target_last_call_input):
                    raise ValueError("different target submitted twice at one physics tick")
                return self._target_applied.copy()
            if tick != self._target_last_tick + 1:
                raise ValueError("process_targets must run on every consecutive physics tick")
        groups = (("legs", LEG_ACTUATOR_INDICES), ("wheels", WHEEL_ACTUATOR_INDICES))
        for name, ids in groups:
            lags = self.action_delay_ticks6[ids]
            if np.any(lags != lags[0]) or int(lags[0]) < 0:
                raise ValueError("all targets in a motor group must share a nonnegative episode lag")
            pending = self._target_pending[name]
            if not np.array_equal(value[ids], self._target_previous_input[ids]):
                pending.append((tick + int(lags[0]), tick, value[ids].copy()))
            while pending and pending[0][0] <= tick:
                due, issued, applied = pending.popleft()
                if due != tick:
                    raise ValueError("a delayed target missed its exact physical application tick")
                self._target_applied[ids] = applied
                self._target_issue_tick6[ids] = issued
                self._target_first_apply_latency6[ids] = tick - issued
        self._target_previous_input = value.copy()
        self._target_last_tick = tick
        self._target_last_call_input = value.copy()
        return self._target_applied.copy()

    def queue_receipt(self):
        """JSON-ready actual queue timing; holding age differs from latency."""
        tick = -1 if self._target_last_tick is None else self._target_last_tick
        age = np.where(self._target_issue_tick6 >= 0, tick - self._target_issue_tick6, -1)
        return {
            "physics_tick": tick,
            "actual_first_transition_delay_ticks6": self._target_first_apply_latency6.tolist(),
            "applied_command_sample_age_ticks6": age.tolist(),
            "pending_groups": {key: len(value) for key, value in self._target_pending.items()},
            "feedback_samples100Hz": self.feedback_samples,
            "last_feedback_actual_age_us": self.last_feedback_age_us,
        }


def _self_test():
    """Pure array/model-double checks; no MuJoCo import, scene or physics step."""
    class FakeModel:
        nu = 6
        npair = 1
        def __init__(self):
            self.opt = SimpleNamespace(timestep=.0005)
            self.body_mass = np.array([0., 10., .3, .3])
            self.body_inertia = np.array([[0., 0., 0.], [1., 2., 3.], [.01, .02, .03], [.01, .02, .03]])
            self.body_ipos = np.zeros((4, 3))
            self.jnt_dofadr = np.array([0, 1])
            self.jnt_qposadr = np.array([0, 1])
            self.jnt_stiffness = np.array([2000., 2000.])
            self.dof_damping = np.array([3., 3.])
            self.qpos_spring = np.array([.22063944109012937, .2206394410901294])
            self.geom_friction = np.tile([.9, .003, .0001], (4, 1))
            self.geom_priority = np.zeros(4, dtype=int)
            self.pair_geom1 = np.array([0])
            self.pair_geom2 = np.array([1])
            self.pair_friction = np.array([[.9, .9, .003, .0001, .0001]])
        def body(self, name):
            return SimpleNamespace(id={"chassis": 1}[name])
        def geom(self, name):
            return SimpleNamespace(id={"left_tire": 1, "right_tire": 2}[name])
        def joint(self, name):
            return SimpleNamespace(id={"left_gas_slide": 0, "right_gas_slide": 1}[name])

    model, same = FakeModel(), FakeModel()
    dr, again = FullDR(27), FullDR(27)
    receipt = dr.sample(model)
    assert receipt == again.sample(same), "same-seed receipt and parameter determinism"
    for name in ("body_mass", "body_inertia", "body_ipos", "jnt_stiffness", "dof_damping", "geom_friction"):
        assert np.array_equal(getattr(model, name), getattr(same, name)), name
    assert model.body_mass[0] == 0 and np.array_equal(model.body_ipos[[0, 2, 3]], np.zeros((3, 3)))
    assert np.all(model.jnt_stiffness >= 1800) and np.all(model.jnt_stiffness <= 2200)
    assert np.all(model.dof_damping >= 2.7) and np.all(model.dof_damping <= 3.3)
    assert np.all(model.geom_priority[[1, 2]] > model.geom_priority[0])
    assert model.pair_friction[0, 0] == receipt["D0"]["wheel_sliding_mu"]
    try:
        dr.sample(model)
    except RuntimeError:
        pass
    else:
        raise AssertionError("repeated sample must not compound physical parameters")
    json.dumps(receipt, allow_nan=False)

    nominal = FullDR(9, nominal=True)
    original = FakeModel()
    nominal.sample(original)
    assert np.array_equal(original.body_mass, [0., 10., .3, .3])
    assert np.array_equal(nominal.KP6, NOMINAL_KP6) and np.array_equal(nominal.KD6, NOMINAL_KD6)
    clean = {key: np.linspace(-.2, .2, row[0]) for key, row in CHANNELS.items()}
    saved_clean = deepcopy(clean)
    assert all(np.array_equal(nominal.observe(clean)[key], clean[key]) for key in CHANNELS)
    # Two controls with deliberately contrasting clean feedback establish that
    # the queued sample contains its own noise+bias, not newly added noise.
    dr.obs_delay_ticks = 1
    dr.reset(np.zeros(6))
    first = dr.observe(clean)
    second_clean = {key: value + 100. for key, value in clean.items()}
    second = dr.observe(second_clean)
    assert all(np.array_equal(first[key], second[key]) for key in CHANNELS)
    assert dr.last_feedback_age_us == 10000
    assert all(np.array_equal(clean[key], saved_clean[key]) for key in CHANNELS)
    for key, (width, bound, _) in CHANNELS.items():
        error = first[key] - clean[key] - (dr.bias4 if key == "legq4" else 0.)
        assert error.shape == (width,) and np.max(np.abs(error)) <= bound + 1e-14

    initial = np.array([.1, -.2, 0., .1, -.2, 0.])
    target = initial + np.arange(1., 7.)
    dr.action_delay_ticks6 = np.array([5, 5, 10, 5, 5, 10])
    dr.reset(initial)
    for tick in range(11):
        actual = dr.process_targets(target, tick)
        assert np.array_equal(actual[LEG_ACTUATOR_INDICES], (initial if tick < 5 else target)[LEG_ACTUATOR_INDICES])
        assert np.array_equal(actual[WHEEL_ACTUATOR_INDICES], (initial if tick < 10 else target)[WHEEL_ACTUATOR_INDICES])
    assert dr.queue_receipt()["actual_first_transition_delay_ticks6"] == [5, 5, 10, 5, 5, 10]
    assert np.array_equal(dr.process_targets(target, 10), target)
    dr.reset(initial)
    assert np.array_equal(dr.process_targets(initial, 400), initial), "reset must clear stale commands"
    dr.action_delay_ticks6[:] = 0
    dr.reset(initial)
    assert np.array_equal(dr.process_targets(target, 0), target), "zero-lag applies on issue tick"
    return {"passed": True, "checks": ["D0-D7 same-seed/model mapping", "one-shot sampling", "nominal identity", "100Hz noise+bias-before-delay", "coherent exact physics target delays", "reset clears stale queues", "zero-lag same-tick", "JSON receipt"], "physics_steps": 0}


if __name__ == "__main__":
    print(json.dumps(_self_test(), ensure_ascii=False))
