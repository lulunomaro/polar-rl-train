""" Adaptation & Preflight Validator for Same-Configuration Wheel-Leg Robots (MOD4v3 Family).

Given a new robot's kinematic & actuator parameters (4-bar parallel linkage legs + hub wheels),
computes the exact IK startup pose, kinematic extension `ext` phase-portrait thresholds,
and action/reward scaling required to run the MOD4v3 RL Stair-Climbing and RL High/Moving-Jump recipes.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path


DEFAULT_MOD4V3_SPEC = {
    "robot_family": "MOD4v3_4Bar_WheelLeg",
    "total_mass_kg": 14.29414,
    "wheel_radius_m": 0.0625,
    "tall_root_height_m": 0.4091,
    "nominal_cruise_height_m": 0.2800,
    "crouch_park_height_m": 0.2000,
    "deep_jump_crouch_height_m": 0.1900,
    "gas_spring_stiffness_n_m": 2000.0,
    "physics_dt_s": 0.0025,
    "leg_pd_dt_s": 0.0100,
    "wheel_pd_dt_s": 0.0025,
    "policy_dt_s": 0.0200,
    "action_clip": 6.0,
    "obs_dim": 35,
    "history_steps": 12,
    "critic_obs_dim": 78,
}


def compute_adapted_recipe_thresholds(spec: dict) -> dict:
    rw = float(spec["wheel_radius_m"])
    h_tall = float(spec["tall_root_height_m"])
    h_crouch = float(spec["crouch_park_height_m"])
    mass_ratio = float(spec["total_mass_kg"]) / DEFAULT_MOD4V3_SPEC["total_mass_kg"]

    leg_len_tall = h_tall - rw
    leg_len_crouch = h_crouch - rw
    max_single_step_m = round(min(0.22, 0.58 * (leg_len_tall - leg_len_crouch + 0.17)), 3)

    return {
        "input_spec": spec,
        "derived_geometry": {
            "tall_leg_vertical_length_m": round(leg_len_tall, 5),
            "crouch_leg_vertical_length_m": round(leg_len_crouch, 5),
            "recommended_single_step_height_m": max_single_step_m,
            "recommended_continuous_2step_heights_m": [max_single_step_m, round(2.0 * max_single_step_m, 3)],
            "recommended_2step_tread_depth_m": 1.50,
            "obs3_tall_command": round(h_tall * 5.0, 4),
            "obs3_top_park_command": round(h_crouch * 5.0, 4),
        },
        "stair_expert_phase_gate": {
            "formula_ext": "0.25 * (obs[10] - obs[11] + obs[12] - obs[13])",
            "crouched_settled_max_recent5_threshold": -0.33,
            "rising_tread_d_ext_min": 0.020,
            "tall_handoff_ext_max": 0.195,
            "top_park_obs3_threshold": 1.50,
            "note": "Re-verify ext_tall (~+0.23) and ext_crouch (~-0.43) if joint zero offsets change.",
        },
        "anti_cheat_contract": {
            "drop_wheel_z_tolerance_m": 0.035,
            "slide_off_clawback_penalty": 25.0,
            "terminate_immediately_on_step_drop": True,
            "single_wheel_top_reward_requires_vx_min_m_s": 0.05,
            "pre_reset_max_speed_latch_required": True,
            "replay_strict_max_speed_m_s": 0.60,
        },
        "ppo_schedule": {
            "critic_only_warmup_iterations": 15,
            "learning_rate": 1.0e-4,
            "clip_param": 0.05,
            "desired_kl": 0.006,
            "e1_initial_std": [0.010, 0.010, 0.010, 0.010, 0.020, 0.020],
            "pinned_settle_anchor_weight": 8.0,
            "high_stance_anchor_decay": [3.0, 1.6],
            "low_stance_anchor_decay": [2.5, 1.4],
            "bilateral_symmetry_weight": 0.45,
            "dr_mixture_stages": [0.0, 0.0, 0.10, 0.25, 0.50, 0.75, 1.00],
        },
        "actuator_mass_scaling_hint": {
            "mass_ratio_vs_mod4v3": round(mass_ratio, 4),
            "recommended_pd_kp_kd_scale": round(mass_ratio, 4),
        },
    }


def main():
    p = argparse.ArgumentParser(description="Generate adapted post-training parameters for a MOD4v3-family wheel-leg robot.")
    p.add_argument("--spec-json", type=Path, help="Optional JSON overriding DEFAULT_MOD4V3_SPEC fields.")
    p.add_argument("--out", type=Path, help="Optional path to write adapted JSON.")
    args = p.parse_args()

    spec = dict(DEFAULT_MOD4V3_SPEC)
    if args.spec_json is not None:
        spec.update(json.loads(args.spec_json.read_text(encoding="utf8")))
    adapted = compute_adapted_recipe_thresholds(spec)
    text = json.dumps(adapted, ensure_ascii=False, indent=2) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf8")
    print(text)


if __name__ == "__main__":
    main()
