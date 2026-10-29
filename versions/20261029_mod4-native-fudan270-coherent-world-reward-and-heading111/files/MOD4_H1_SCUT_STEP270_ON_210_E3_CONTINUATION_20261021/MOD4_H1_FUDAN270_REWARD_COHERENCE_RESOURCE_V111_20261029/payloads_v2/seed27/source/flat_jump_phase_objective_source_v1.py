"""Own low-jump curriculum math only; not installed or a physical success gate.

The real video informs extension/tuck/landing phases, not measured MOD4 joints.
Inputs must come from the actual own wheel FK/forces. A future imagined adapter
must advance its phase and update dynamic contact context on every rollout step.
"""
from dataclasses import dataclass
import math
import torch

@dataclass(frozen=True)
class FlatJumpPhase:
    height_m: float = .05
    control_dt_s: float = .01
    initial_standing_s: float = 2.
    repeat_s: float = 2.5
    stable_recovery_s: float = .5
    gravity_m_s2: float = 9.81

    def __post_init__(self):
        assert self.height_m in (.05, .10, .20, .27)
        assert self.control_dt_s in (.01, .02)
        assert self.initial_standing_s >= self.stable_recovery_s

    def targets(self, ages, env_ids):
        """Stagger first requests, never start an environment in a fake air pose.

        Uses deterministic IDs, no RNG draws or physical reset modifications.
        Actual integration must bind IDs/age after each genuine reset.
        """
        age = ages.to(dtype=torch.float32) * self.control_dt_s
        period_ticks = round(self.repeat_s / self.control_dt_s)
        delay = torch.remainder(env_ids, period_ticks).to(age.dtype) * self.control_dt_s
        elapsed = age - self.initial_standing_s - delay
        active = elapsed >= 0
        phase = torch.remainder(elapsed.clamp_min(0), self.repeat_s)
        v0 = math.sqrt(2 * self.gravity_m_s2 * self.height_m)
        flight_s = 2 * v0 / self.gravity_m_s2
        flight = active & (phase <= flight_s)
        height = torch.where(flight, (v0*phase - .5*self.gravity_m_s2*phase.square()).clamp_min(0), torch.zeros_like(phase))
        vertical_v = torch.where(flight, v0-self.gravity_m_s2*phase, torch.zeros_like(phase))
        return dict(height=height, vertical_v=vertical_v, flight=flight,
                    ground=~flight, phase_s=phase, active=active,
                    nominal_flight_s=flight_s)


def huber(x):
    a=x.abs()
    return torch.where(a <= 1, .5*x.square(), a-.5)


def flat_jump_terms(wheel_bottom_m, wheel_vertical_v, Rzz, root_vxy,
                    ground_support_probability, target, action, previous_action):
    """Task reward on real or predicted OWN measurements, not a forced path.

    ground_support_probability must be a live current-step wheel support signal
    from the admitted real/imagined adapter. No constant contact assumption.
    Reward positivity avoids rewarding early termination through negative tails.
    """
    assert wheel_bottom_m.shape[-1] == wheel_vertical_v.shape[-1] == 2
    assert ground_support_probability.shape == wheel_bottom_m.shape
    assert torch.isfinite(ground_support_probability).all()
    assert ((ground_support_probability >= 0) & (ground_support_probability <= 1)).all()
    h=target['height'][...,None];vz=target['vertical_v'][...,None]
    height_cost=huber((wheel_bottom_m-h)/.02).mean(-1)
    velocity_cost=huber((wheel_vertical_v-vz)/.5).mean(-1)
    # The original actual hard orientation limit is.75rad, not acos(.3).
    tilt_cost=huber((1-Rzz)/(1-math.cos(.75)))
    ground=target['ground'].to(wheel_bottom_m.dtype)
    support_target=ground[...,None].expand_as(ground_support_probability)
    support_cost=(ground_support_probability-support_target).square().mean(-1)
    ground_drift_cost=huber(root_vxy/.15).mean(-1)*ground
    action_rate=(action-previous_action).square().mean(-1)
    cost=4*height_cost+velocity_cost+4*tilt_cost+2*support_cost+ground_drift_cost+action_rate/6
    return dict(height_cost=height_cost,tilt_cost=tilt_cost,support_cost=support_cost,
                total=.06/(1+cost),nonnegative_cost=cost,
                tilt_failure_probability=torch.sigmoid((math.cos(.75)-Rzz)/.04))


def physical_skill_scope():
    return dict(first_training_target_wheel_bottom_m=.05,
        later_height_targets_m=[.10,.20,.27],
        flat_acceptance='actual both-wheel clearance, actual landing support and >=200 stable2.5ms callbacks',
        step_final_acceptance='unchanged270mm cross/fullfootprint/topcontact12+stable200callbacks',
        not_COM_height_or_imagined_reward_success=True,
        source_math_only_not_installed=True,
        actual_FK_force_basis_phase_advance_context_refresh_SDK_and_runtime_pending=True,
        no_new_Fudan_joint_mocap_or_dynamic_feasibility_claim=True)
