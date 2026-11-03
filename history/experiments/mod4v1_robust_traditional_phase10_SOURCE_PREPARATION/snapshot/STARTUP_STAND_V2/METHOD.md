# Startup V2 — coupled leg recovery + wheel-rate damping (UNQUALIFIED)

## Why a new controller, not a replay
V1's one physical front-rest case reached SHAPE .31, VERIFY2.31, timed out6.00, never BLEND/BALANCE. Wheel requests railed positive, large forward travel, joint reference error~.1rad and pitch~.67rad persisted. Its later report API error is independent. Keep V1, 601/12020 prefix, ERROR, original gates. No replay to repair bookkeeping.

## Parent-locked new hypothesis
- New subclass of STARTUP_STAND_V1.StartupStand. Extra exact-bool `recovery_actuation_enable=False` by default, stripped before base config. Disabled calls literal base with no extra packet reads or mutations.
- Enabled, operator armed only: validate same packet wheel_vel2 finite shape2 before base command. Still call base command exactly once for phase/reference/normal-GC state progression; do not call another GroundController/DARE inside command. INHIBIT/DISARMED remain base output.
- Replace output only while final current phase is SHAPE_TO_STAND or VERIFY, not OBSERVE/BLEND/BALANCE. Use the existing nominal GroundController.K already synthesized by the base constructor, but do NOT use fixed-leg PD replacement output for recovery.
- Let err=estimated.state14 - current ctrl.ref, copied locally. Set err[0,1,7,8]=0: no recovery leg action from drifting IMU-only distance/longitudinal velocity or yaw. Do not overwrite any estimator state. Multiply err[2,9] by the already published `nominal_ff_scale` (same quintic scale), avoiding immediate large pitch feedback at first lock. Keep other leg-angle/rate errors intact.
- Recovery leg torque = scale*ff[LEG] - K[LEG,:]@err. Add the exact existing bounded roll correction: r=clip(-20*roll-2*omega_x,-8,+8); Lhip-=r,Lcrank+=r,Rhip+=r,Rcrank-=r. No additional60/3 or120/4 leg PD in parallel. This is a local linear-feedback hypothesis outside the original upright domain, NOT a nonlinear stability proof.
- Recovery wheel torque = clip(-0.30*packet.wheel_vel2,-2.0,+2.0) Nm per axis. It is encoder-rate damping, not chassis velocity observation or a physical speed/stop guarantee. No normal pitch/distance wheel command until the original readiness and BLEND transition.
- Final original six-axis bounds remain40/5.775909774436091. Store actual replacement as last_tau and actual log output; optional clearly labelled discarded base candidate. Base captures this last_tau as blend_from, preserving original .5s bridge and normal fixed-leg GC after handoff.
- No observer, attitude/velocity/covariance reset, timing, shape trajectory, ready thresholds, support confidence, driver/PD/DC/contact/model/gain-file changes. Existing6s timeout remains. No true states or contact identities enter control.

## Bounded zero-step work first
New explicit feature fixtures only: <=420 enabled100Hz synthetic commands through OBSERVE/SHAPE/VERIFY/BLEND/BALANCE (analytic tracking, not a robot), <=40 disabled commands compared with base, <=12 typed cases. New math checks should cover exact formula, wheel sign/cap, ignored copied error coordinates, finite rejection before scheduler mutation, no post-capture wheel invariance claim, blend continuity, actual output logging, default-off delegation. Never rerun prior499 QA, passive-settle physics, model/FK or source packages. Record actual new counts; no inflated robot-trial claim.

Produce only prototype/core/test/evidence and a fresh entry derived from report-fixed startup runnerV3 (config allows only two exact bools; use new controller import); zero physics/real model. Parent will review entry and approve at most one NEW nominal case later, not old case replay. No DR/back/side rollout or hardware/send permission is granted here.
