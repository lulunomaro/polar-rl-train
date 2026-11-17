"""Decouple tuck_mean_bias (-0.10 for flat flight) from land_mean_bias (+0.12..+0.20 for world-vertical COM landing & 0.0N guide contact)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from test_zero_pitch_flight_and_land import eval_zero_pitch, ProbeSim  # noqa: E402


def main():
    sim = ProbeSim()
    base = dict(
        cruise_h=0.365,
        crouch_delta=0.22,
        crouch_speed_k=0.03,
        crouch_rate_rad_s=1.80,
        compress_s=0.48,
        push_mean_bias=-0.17,
        push_speed_mean_k=-0.01,
        tuck_delta=0.173,
        tuck_ramp_s=0.025,
        tuck_s=0.14,
        tuck_mean_bias=-0.10,
        land_delta=1.54,
        skyhook_s=0.34,
        skyhook_kd=0.45,
        z_guard_kp=13.0,
        z_guard_ref=0.290,
        absorb_pitch_mean_k=+0.65,
        absorb_wy_mean_k=+0.07,
        leg_pitch_kp=2.5,
        leg_pitch_kd=0.20,
        pitch_kp=9.0,
        pitch_kd=1.05,
    )
    variants = [
        dict(name="d1_lm_p10", **base, land_mean_bias=+0.10),
        dict(name="d2_lm_p15", **base, land_mean_bias=+0.15),
        dict(name="d3_lm_p20", **base, land_mean_bias=+0.20),
        dict(name="d4_lm_p25", **base, land_mean_bias=+0.25),
    ]
    for v in [0.0, 0.4, 0.8, 1.2, -0.5]:
        print(f"\n=== SPEED v_cmd = {v:+.1f} m/s ===")
        for c in variants:
            r = eval_zero_pitch(sim, c, v_cmd=v)
            if not r.get("survived") or not r.get("jumps"):
                print(f"{c['name']:12s} -> FAILED: {r}")
                continue
            print(f"{c['name']:12s} -> rim={r['rim_cm']:5.2f} dz={r['com_rise_cm']:5.2f} zMin={r['z_min']:.3f} zL={r['z_min_land']:.3f} "
                  f"airP=[{r['air_p_min']:+5.1f},{r['air_p_max']:+5.1f}]({r['air_p']:4.1f}) airR={r['air_r']:4.2f} postP={r['post1s_p']:5.2f} gN={r['guide_N']}")

    print("\n=== MULTI-JUMP 3x AT v_cmd = +0.8 m/s ===")
    for c in variants:
        r = eval_zero_pitch(sim, c, v_cmd=0.8, jump_times=(1.8, 3.8, 5.8), total_s=8.0)
        if not r.get("survived") or not r.get("jumps"):
            print(f"{c['name']:12s} -> FAILED: {r}")
            continue
        print(f"{c['name']:12s} -> jumps={r['jumps']} rims={r['all_rims']} airP={r['all_air_p']} postP={r['all_post_p']} gN={r['guide_N']} cl={r['closure_mm']}mm")


if __name__ == "__main__":
    main()
