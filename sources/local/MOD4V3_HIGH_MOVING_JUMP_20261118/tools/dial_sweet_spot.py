"""Sweet-spot dial-in: center airborne & touchdown pitch at 0 deg across ALL speeds so gN=0.0N, postP~12-18deg, airP<8deg, rim~34-36.5cm."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_locked_design import eval_locked, ProbeSim  # noqa: E402


def main():
    sim = ProbeSim()
    base = dict(
        cruise_h=0.36,
        crouch_delta=0.20,
        crouch_speed_k=0.03,
        crouch_rate_rad_s=1.85,
        compress_s=0.50,
        tuck_delta=0.173,
        tuck_ramp_s=0.025,
        tuck_s=0.14,
        land_delta=1.52,
        skyhook_s=0.26,
        skyhook_kd=0.38,
        z_guard_kp=10.0,
        z_guard_ref=0.270,
        leg_pitch_kp=2.4,
        leg_pitch_kd=0.20,
        pitch_kp=9.0,
        pitch_kd=1.05,
        absorb_pitch_mean_k=0.0,
        absorb_wy_mean_k=0.0,
    )
    variants = [
        dict(name="s1_pm16_lm00", **base, push_mean_bias=-0.16, push_speed_mean_k=-0.02, land_mean_bias=0.00),
        dict(name="s2_pm16_lm_m06", **base, push_mean_bias=-0.16, push_speed_mean_k=-0.02, land_mean_bias=-0.06, land_speed_mean_k=-0.03),
        dict(name="s3_pm18_lm_m08", **base, push_mean_bias=-0.18, push_speed_mean_k=-0.01, land_mean_bias=-0.08, land_speed_mean_k=-0.02),
        dict(name="s4_pm18_lm_p06", **base, push_mean_bias=-0.18, push_speed_mean_k=-0.01, land_mean_bias=+0.06, land_speed_mean_k=+0.02),
    ]
    for v in [0.0, 0.4, 0.8, 1.2, -0.5]:
        print(f"\n=== SPEED v_cmd = {v:+.1f} m/s ===")
        for c in variants:
            r = eval_locked(sim, c, v_cmd=v)
            if not r.get("survived") or not r.get("jumps"):
                print(f"{c['name']:18s} -> FAILED: {r}")
                continue
            print(f"{c['name']:18s} -> rim={r['rim_cm']:5.2f} dz={r['com_rise_cm']:5.2f} zMin={r['z_min']:.3f} zL={r['z_min_land']:.3f} "
                  f"airP=[{r['air_p_min']:+5.1f},{r['air_p_max']:+5.1f}]({r['air_p']:4.1f}) airR={r['air_r']:4.2f} postP={r['post1s_p']:5.2f} gN={r['guide_N']}")

    print("\n=== MULTI-JUMP 3x AT v_cmd = +0.8 m/s ===")
    for c in variants:
        r = eval_locked(sim, c, v_cmd=0.8, jump_times=(1.8, 3.8, 5.8), total_s=8.0)
        if not r.get("survived") or not r.get("jumps"):
            print(f"{c['name']:18s} -> FAILED: {r}")
            continue
        print(f"{c['name']:18s} -> jumps={r['jumps']} rims={r['all_rims']} airP={r['all_air_p']} postP={r['all_post_p']} gN={r['guide_N']} cl={r['closure_mm']}mm")


if __name__ == "__main__":
    main()
