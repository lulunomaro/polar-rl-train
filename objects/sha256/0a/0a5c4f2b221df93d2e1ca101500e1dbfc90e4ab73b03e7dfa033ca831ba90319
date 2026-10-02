# MOD4 walking/running instability audit (2026-09-26)

Final model_385.pt, 14.22 kg chassis, Fudan flat plane. Deterministic first-episode audit: same seed 202609268, 64 environments, 15 seconds. Nominal completed 21/64 and gas-only 300-700 N completed 19/64; **0/64 met all stability criteria in both cases**. Nominal tilt 17.47 deg, root height 0.224 m against 0.30 m command, speed error 0.653 m/s, both driven wheels contact 75.1%. Gas-only tilt 17.36 deg, both-wheel contact 77.1%.

Main mechanism: COM is 46.9 mm toward CAD front (-X) of wheel axle, corresponding to about 6.9 N m gravity moment if supported only by main wheels. Wheel actuator absolute torque sum averages 1.19 N m. Front guide rollers 05 and 07 at X=-0.259 m take 3.5 and 32.7 N mean force; roller 07 touches on only 8.6% of first-episode steps, indicating impacts. Mixed stage log reports 56.8% base-contact terminations. Leg motor torque saturation, closure error, and action jitter are negligible by comparison.

A 64-pose symmetric leg-command sweep found no sampled pose with both root height above 0.28 m and tilt below 15 deg. Near the 0.30 m root-height command, sampled tilt was about 35-52 deg. The unconditioned stage driver promoted speed phases while stability gate stayed zero: run tilt 33.4 -> 24.8 -> 17.6 deg, root height 0.264 -> 0.239 -> 0.226 m, ending with 0.05-1.50 m/s commands and recurring base collision. Root height alone is a poor stance target here.

The phase named gas DR was actually fixed at 500 N: RM_DR_OFF=1 overrode RM_GAS_FORCE_DR=1. An isolated post-training fix adds RM_GAS_FORCE_DR_ONLY=1; true gas-only evaluation ran after the fix, but checkpoint weights remain untrained on 300-700 N. Eleven RM_RUN_* manifest keys are absent from active Python; RM_W_RUN_POSE and RM_W_RUN_TILT were zero, while general flat orientation penalty remained active.

Next: confirm physical forward axis (CAD labels front at -X, while task commands +X); calibrate an upright COM-over-wheel pose/height; train nominal low-speed balance with wheel support and no guide impacts; promote only after first-episode 15-second stability passes; then enable true gas-only DR. Re-evaluate the full 22 kg vehicle separately. No PPO process is running.

Evidence: eval_nominal_first_episode_v2.json, eval_gasdr_first_episode_v2.json, diagnostics_leg_sweep_com.json, diagnostics_bestpose_15s.json, and phase train.log files. Previous FINAL_8H_AUDIT.md aggregate tilt/contact means are superseded because that evaluator counted post-reset samples.
