# Startup V3 — deploy legs with tracking PD, then bounded pitch alignment (hypothesis only)

## Evidence motivating a new variant
V2 had one real nominal601/12020 case, no software error, but startup_timeout6s/noBALANCE. Actual root travel max .01194m (runaway prevented), height fell7.50mm. Saved one-pass controls show hip near+.500 upper and crank~.891 at3–5.99s versus reference all+.123; q error~.77rad and guide support persist. Its nominal K-only leg output17/-20Nm did not deploy the legs. Preserve V1/V2 failures, never rerun old case IDs or claim no-motion is standing.

## Two fixed new nominal TRAIN profiles, predeclared before any new physics
- New independent subclass of StartupStandV1. Defaults featureFalse -> literal base. Exactbool config operator_enable, recovery_tracking_enable=False, alignment_wheel_enable=False. alignment requires tracking=True.
- Profile A: strong tracking legs + quiet wheels (alignmentFalse). Profile B: same legs + eligible bounded pitch alignment (alignmentTrue). This is a mechanism ablation, not independent reliability/holdout.
- Parent later may admit A first; B is deferred unless saved A controls show its sensor-only alignment eligibility at least once before fault. Otherwise B would repeat identical actuation and is not consumed. No physics permission from this METHOD.

## Shared recovery behavior
Only final current SHAPE_TO_STAND/VERIFY overrides actuation; OBSERVE/BLEND/BALANCE remain base. Base command exactly once; original observer, trajectory,6s timeout and original private grade unchanged. Validate samepacket wheel/q4/qd4 finite shapes before scheduler mutation.
- Leg torque = original scale*ff +120*(qref-q_packet)+4*(vref-qd_packet), plus original roll r=clip(-20roll-2omega_x,±8): LH-=r,LC+=r,RH+=r,RC-=r. No K-leg feedback in parallel.120/4 are the existing normal-ground tracking constants, not new model fits. Joint references remain original projected legal quintic; actual measured joints are never clamped/reset. Bounds40/5.7759 unchanged.
- Before pitch alignment wheels =clip(-.30*packet.wheel_vel2,±2Nm). Encoder angular damping is not chassis-velocity measurement or a stop guarantee.
- Compute eligibility in VERIFY from samepacket max|q-target|<=.08rad and max|qd|<=.40rad/s. Report candidate eligibility even when profileA disables alignment. ProfileB latches alignment only on this event. This is an untrusted sensor phase proxy, not true contact permission. Do not manufacture an ALIGN state in base FSM; log recovery_subphase only.

## Profile B aligned-wheel policy
- Pose-only existing nominal wheel K columns2/9: common=mean(-K[WHEEL,2]*estimatedPitch -K[WHEEL,9]*estimatedPitchRate). No distance/vx/yaw errors and no changes to estimator state. Wheel request=common-.30*samepacket wheel rate, peraxis clipped±3Nm.
- Soft overspeed rule: if |wheel rate|>12rad/s and candidate torque accelerates in that sign, substitute opposing -.30*sign(w)*(|w|-12), clipped±3Nm. Already braking torque is preserved. This is feedback limitation, not a proved physical speed bound with delayed measurements/driver.
- Track recovery wheel-rotation travel estimate from SHAPE onward: integral dt*.0625*mean(abs(wheelRate)); actual validated control-time dt, no estimator-state reset. If>.50m latch INHIBIT. This is wheel rotation proxy not true chassis path; private true maxXY<=.5 remains unchanged. Count the last VERIFY interval even if base enters BLEND in the current call. Numeric invalid input must not advance this proxy; path fault after valid base scheduling may latch, not a rollback guarantee.
- V3 narrows base ready by also requiring max|current packet wheel rates|<=2rad/s before BLEND, so a moving wheel does not immediately hand off to ground control. All original ready conditions remain, none are relaxed. Default featureFalse does not add this condition. OriginalBLEND must capture previous actual replacement through last_tau; actual logs reflect returned torque.

## Bounded implementation proof first
New synthetic only: <=420 enabled external commands total (one main trajectory plus bounded profileB math/typed contexts),<=40 total disabled/base comparison calls,<=12typed. Cover formulas, normal threshold unchanged vs extra wheel-quiet condition, eligibility/latch, caps/overspeed sign, travel threshold and last VERIFY-toBLEND interval, actual log/last_tau, disabled equivalence, no true-state input, numeric fail-before-base, sticky faults. No rerun prior499/V2proof, no raw/model/FK/DR/PHY/Git/newagent.
New entry derived from report-fixedV4 may only change controller import, exact3bool config and new source/kind records, keeping loop/driver/private gates AST unchanged; reject both old case IDs. Parent must read real code/evidence and separately freeze/approve fresh nominal cases before physics. No DR/back/side/hardware grant.
