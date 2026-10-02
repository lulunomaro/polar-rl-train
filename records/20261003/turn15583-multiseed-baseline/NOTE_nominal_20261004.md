# Frozen ordinary turn baseline

Source: mature four-rad/s model15583, not the current six-rad/s production weights.
Protocol: nominal, seed 20261004, 96 environments, 1500 control steps / 15 seconds, deterministic actions. Twelve groups cover standing, straight motion, pure spin and forward/reverse arcs with vx +/-0.3 m/s and yaw +/-0.5 rad/s.

Result: 96/96 survived; all original turn skill groups and physical checks passed. No new PPO, budget extension, production source change or hardware change. This is ordinary body-frame turning, not world-directed FPS movement or the 0.5m/s spinning-translation goal.

Complete original metrics and all samples are preserved in turn15583_nominal_seed20261004_15s.json. The latest production model must be checked separately before deploying controls.
