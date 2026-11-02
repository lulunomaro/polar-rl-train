# portable_spin_h2_v1 — frozen positive4π H2 pure math port

New files only here; sealed C3/C2/host/P25/old manifests stay read-only. Recheck H2 protocol/source SHA and state14 erratum. No R27 candidate, heldout-case selection, new physics, BSP/CAN, ARM runtime/WCET, Git or new agent.

Use sealed C3 packet estimator with explicit supported-upright prior, gyro-only attitude gain0 (acceleration still enters velocity/bias KF) and wheel-midpoint reference. Reuse sealed C2 FK, radius/FD epsilon/offset external and declared. Nominal K, NOT P25; base position leash=.2, fixed legs120/4, yawPI .8/.5/I15/rateFF .052/accelerationFF .08 and original envelopes.

Port source H2 relative planar odom, no-side-slip vy proxy, lead .008390087918603841, common wheel torque kp20/cap1.8 and preserved yaw-differential headroom. torque_v2 sets velocity-center cap0: no joystick velocity correction is injected.

Temporal fidelity matters: frozen center computes FK from age-view hip/crank state14 and combines it with held sample gyro. This is not identical to the C3 raw-epoch proxy field. Preserve/expose that source approximation rather than silently substituting a different proxy. state14 delta=crank−hip; passive FK knee is separate.

Only pure estimator+H2 mathematical valid/torque output in this stage. No P25 controller/dispatcher/profile25 reuse and no actuator enqueue. Full failsafe dispatch/deployment is DEFERRED; mathematical valid is not actuation qualification. Original downstream signed-DC/driver limits remain required, not widened or replaced by this math output.

Reference fixed TRAIN R11_k20_201 raw/time/request/center_log plus independent synthetic start/stop/reverse numerical vectors. Those vectors do not qualify physical start/stop/reverse; frozen H2 scope remains supported-upright positive4π. Relative2D odom is not world-position truth; unknown common side-slip remains unobserved. PostR16/PH3 pending, no PH2 expansion.
