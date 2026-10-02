# Two-seed nominal/light-DR paired turning review

All four real 96env x 1500step deterministic reports completed. All 384 environments survived and every tested group passed its original skill and physical checks. Nominal and white_v1 initial root/q arrays are exactly equal for each seed. The source is model15583 (mature 4rad/s policy), not the current 6rad/s policy.

Tested ordinary forward/reverse left/right arcs: body vx +/-0.3m/s and yaw +/-0.5rad/s. Worst peak tilt across the four reports is approximately 1.383 degrees. This does not validate world-directed FPS control, moving spin at 0.5m/s, or 120rpm. No new PPO or production/budget change was made.

Decision: first recheck latest production weights and integrate controls if the existing skill suffices; do not add unnecessary training. Transfer receipt records exact remote paths and raw-file SHA256 values.
