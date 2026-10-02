# MOD4 gas-spring DR contract (2026-09-25)

Current Isaac asset: 14.22014 kg chassis. Both gas slides have authored limits q in [-0.0267046843609, +0.0352033350025] m. At q=0 the delivered MJCF/contract uses stiffness 3500 N/m and target 0.220639441 m, so F_ref=772.24 N; crouched working force is about 847 N/side. The current mild DR also scales gas stiffness by 0.8-1.2 at reset.

The actuator model elastic force is F_elastic(q)=F_ref-k*q. Damping and linkage/constraint reaction forces are separate. In legacy/default RM_GAS_FORCE_FRAME=reference mode, RM_GAS_FORCE_MIN_N=300 and MAX_N=700 mean bounds on F_ref at q=0, NOT bounds on F_elastic throughout motion. Measured under 256-env x1500-step mild DR, the actual elastic range was 297.4-791.2 N/side, 25.6% of valid samples outside 300-700 N.

For a full-stroke elastic 300-700 N contract, set:
    RM_GAS_FORCE_DR=1
    RM_GAS_FORCE_FRAME=full_stroke
    RM_GAS_FORCE_MIN_N=300
    RM_GAS_FORCE_MAX_N=700
    RM_GAS_FORCE_NOMINAL_N=500

At each reset after gas-stiffness DR, the sampler calculates per-env q=0 reference bounds F_ref_low=300+k*q_max and F_ref_high=700+k*q_min, then samples within them. At nominal k=3500 these are 423.21-606.53 N; at k=4200 they are 447.85-587.84 N. The 500 N nominal remains feasible. This bounds only the elastic component if authored joint limits are respected. Runtime audit source/mod4/eval_episodes_mod4_gas.py reports frame, min/max, mean and out-of-range fraction; treat nonzero out-of-range fraction as a failure. Source is isolated under grounded_run_20260925/source/mod4; original project code and DeepSeek directory are unchanged.

Evidence: train_gas500_mild_v1/mild_gas300_700.json (legacy reference frame), mild_gas_bounded300_700.json (fixed nominal-k bounds), mild_gas_bounded_with_kdr.json (conservative worst-k bounds), and mild_gas_fullstroke_dynamic.json (per-env dynamic mode). These are deterministic 256-env x1500-step, seed20260917, same model_10 checkpoint. Dynamic full-stroke mode had elastic 410.8-692.6 N/side, zero out-of-range samples, but policy route completion only 49/288 and tilt 15.2 deg: physics-contract fix is not a stable-run pass. A short smoke report with explicit mode metadata is fullstroke_smoke.json.

Before selecting a real gas spring, measure force against stroke at several points and damping under extension/compression. The current 3500 N/m slope and any commanded 300-700 N force curve are hypotheses, not a measured part specification.
