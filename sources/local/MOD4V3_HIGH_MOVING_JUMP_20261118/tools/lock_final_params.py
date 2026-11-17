"""Final precision sweep to lock parameters achieving >34-36cm clearance, <8-9deg air pitch, <20deg post-landing pitch, and 0.0N guide/chassis contact."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import mujoco
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_locked_design import eval_locked, ProbeSim  # noqa: E402


def main():
    sim = ProbeSim()
    base = dict(
        cruise_h=0.37,
        crouch_delta=0.22,
        crouch_speed_k=0.04,
        crouch_rate_rad_s=1.75,
        compress_s=0.46,
        tuck_delta=0.173,
        tuck_ramp_s=0.025,
        tuck_s=0.14,
        land_delta=1.54,
        skyhook_s=0.30,
        skyhook_kd=0.42,
        z_guard_kp=11.0,
        z_guard_ref=0.275,
        leg_pitch_kp=2.4,
        leg_pitch_kd=0.20,
        pitch_kp=9.0,
        pitch_kd=1.05,
    )
    variants = [
        dict(name="f1_pmb_m09", **base, push_mean_bias=-0.09, push_speed_mean_k=-0.04, absorb_pitch_mean_k=+0.5, absorb_wy_mean_k=+0.05),
        dict(name="f2_pmb_m12", **base, push_mean_bias=-0.12, push_speed_mean_k=-0.05, absorb_pitch_mean_k=+0.5, absorb_wy_mean_k=+0.05),
        dict(name="f3_pmb_m12_ppos", **base, push_mean_bias=-0.12, push_speed_mean_k=+0.05, absorb_pitch_mean_k=+0.5, absorb_wy_mean_k=+0.05),
        dict(name="f4_pmb_m10_cleanabs", **base, push_mean_bias=-0.10, push_speed_mean_k=+0.04, absorb_pitch_mean_k=0.0, absorb_wy_mean_k=0.0),
    ]
    for v in [0.0, 0.4, 0.8, 1.2, -0.5]:
        print(f"\n=== SPEED v_cmd = {v:+.1f} m/s ===")
        for c in variants:
            r = eval_locked(sim, c, v_cmd=v)
            if not r.get("survived") or not r.get("jumps"):
                print(f"{c['name']:20s} -> FAILED: {r}")
                continue
            print(f"{c['name']:20s} -> rim={r['rim_cm']:5.2f} dz={r['com_rise_cm']:5.2f} zMin={r['z_min']:.3f} zL={r['z_min_land']:.3f} "
                  f"airP=[{r['air_p_min']:+5.1f},{r['air_p_max']:+5.1f}]({r['air_p']:4.1f}) airR={r['air_r']:4.2f} postP={r['post1s_p']:5.2f} gN={r['guide_N']}")

    print("\n=== MULTI-JUMP 3x AT v_cmd = +0.8 m/s ===")
    for c in variants:
        r = eval_locked(sim, c, v_cmd=0.8, jump_times=(1.8, 3.6, 5.4), total_s=7.6)
        if not r.get("survived") or not r.get("jumps"):
            print(f"{c['name']:20s} -> FAILED: {r}")
            continue
        print(f"{c['name']:20s} -> jumps={r['jumps']} rims={r['all_rims']} airP={r['all_air_p']} postP={r['all_post_p']} gN={r['guide_N']} cl={r['closure_mm']}mm")


if __name__ == "__main__":
    main()
