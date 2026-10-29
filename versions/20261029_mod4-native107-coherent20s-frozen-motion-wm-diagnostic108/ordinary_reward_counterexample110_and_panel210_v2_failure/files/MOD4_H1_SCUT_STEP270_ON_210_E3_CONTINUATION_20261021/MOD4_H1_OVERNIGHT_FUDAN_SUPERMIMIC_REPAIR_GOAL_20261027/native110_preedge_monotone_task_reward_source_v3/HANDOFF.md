# FROZEN source110 V3 — reward counterexample checked, NOT runtime admitted
User required computing reward and eliminating concrete counterexamples before use. No H1 training is started by this source package.

Original same supported floor stance/zero velocity moved from rootx0.056m to0.20m: reward0.022030741 to0.015871387, delta-0.006159354. Proposed109 still decreases0.023205139 to0.020557195, so109 is NOT_SELECTED and not trained.

SelectedV3:
- Original recovery common baseline plus nonnegative stage advantage A=J-E. J is six nonnegative jump bonuses; E is nonpositive recovery height/vertical residual after removing its dt baseline. total=R_recovery+w*A+top_quiet_bonus. Original nonrequest recovery is preserved exactly.
- Near gate is monotone before actual leading-edge crossing, continuously decays after it. Keep original top-support recovery.
- Support-height cue depends on top support rather than horizontal footprint alone. For a fixed supported floor pose P=0, command and height cue are constant, and A>=0 means approach cannot lose reward solely through the mode gate.
- Planar tracking uses fixed-platform worldXY versus(+0.5,0), and on-top zero. Body-frame diagnostics and actual raw command/observation domain are retained. Heading-away and lateral-drift algebraic counterexamples are now distinguished.
- Top quiet uses vertical velocity as well as planar/angular motion. Coefficient12 is an engineering choice derived above jumpbonus bound0.0985/dt; not an optimal measured value.
- total <= Cmax0.02+dt0.01+0.0985*(1-P)+0.12P <=0.15. Idealquiettop approximately0.15 exceeds any P=0 upper0.1285. max_step_reward0.15 is a logging normalization bound; learner source uses it only in logged actual/imagined reward metrics, not loss/TDlambda/optimizer.

Specific counterexample now0.024134053 to0.024264112. 600 structured measurement combinations*257 positions evaluated;153600 actual computed preedge points had finite nonnegative position derivative and nondecreasing reward.600 endpoint values were correctly classified postedge by original float32 geometry. OriginalCPUv1 false and diagnostic guard/parser errors retained; the fixture domain was corrected without runtime geometry tolerance/FP64/physical gate changes.
V2grid passed after that scope correction, but explanatory text assumed footprint-only support height was position-independent. V3 fixes the height cue and tests five observed bodyheight values; originalV2 text/report retained. All nonfinite rejection/RNG identity/nonrequest equality/worldheading/lateral/verticalquiet/top-bound checks passed.

Scope: algebra and deterministic sourceCPU only, not measured reachable trajectories, complete reward correctness, successful learned policy or27cm mechanics. Monotonicity condition is fixed supported floor pose before leading edge and P=0 with unchanged command/contact. No claim across actual contact/landing/reset or postedge fade. Soft support/model exploitation/collision errors still require actual runtime/domain checks. Real270dualwheelcross/fullfootprint/topcontact12+stable200callbacks=.5s acceptance stays external and exact.

Unchanged:20s/request200..1999/age_seconds/private4096/horizon32/goal10/focus sampling/native100Hz/400N/TGS32/4/2.5ms/FP32/clip6/PD/queue/DR/reset/networks/norms/threeopts/source107 fullstate. Originalextension0.31/tuck0.16/positive-vz extension gate remain in this priority blend repair;109geometry proposal is not silently bundled. No action/force script or fakeairreset.

NEXT BEFORE USE: new payload+typedinput107/output110/producer/sourceSHA/reference1a038.../Task+GO seals, actualtargetSDK/fullstate/400reset+preload and task-frame reward readback, freshlightresources/sole72authority. No oldonce/hotpatch, no additional savedweight/raw read just for statistics/Git. Source107 metadata SHA36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef/global17272-172720WM-16632Pi. Preserve inputnative107 validation separately from newobjective outputcontract; no stale producer/reference/frame label.
