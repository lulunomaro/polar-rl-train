# Proposed acceptance and evidence separation — not yet human-ratified

## Identity and invariants

- Physical primary: MODEL_AUDIT/mod4v1_usd_source_aligned.xml SHA0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324, derived from actual USD2c421a8e/contractbae3203a with documented conflicts/engine choices. Neither 3-MCI diagnostic nor preliminary cylindrical-tire file qualifies as the current model.
- 31robotbodies/37qpos/36qvel/6actuators; closed-loop and motor/guide collisions retained. No root assistance or state overwrite after initialization. Truth is isolated to identification, explicit diagnostic cases and grading.
- Existing D0–D7 coefficients are not narrowed. R01 distinguishes high-rate IMU acquisition/boxcar before100Hz D1+sharedD3 from R00 instantaneous sampling. Both use genuine processed-target D4 queues, not torque-after-delay relabelling. These NumPy streams do not claim historical CUDA-bit identity.
- MuJoCo0.5ms physics/100Hz outercontrol is a declared traditional-control prototype clock, not a claim of PhysX TGS/RL50Hz equivalence.

## Provisional engineering screening gates

These select candidates for further testing. They do not by themselves mean user acceptance, fullhardware DR or physical deployment approval.

|Family|Minimum next evaluation scope|Provisional measurements|
|---|---|---|
|Stand|20s, drift and separately declared perturbations|Complete, finite, closure≤.01m/mimic≤.01rad; tailpose≤10deg; low velocity error; no sustained nonwheelgroundsupport|
|2m/s|Acceleration/cruise/braking with≥5s settled cruise|TailbodyforwardRMSE≤.15m/s; speedovershoot/settling/brakingdistance reported; yaw/roll/pitch and actuator saturation recorded|
|Fastturn|Positive/negative yawsteps and command reversals|10–90%rise/settle/overshoot, translation coupling, contact/tilt/power; no unbounded yawangle wrap|
|4πselfspin|Continuous4πrad/s request, ≥5s hold after settle, start/stop/reverse separate|Bodyyaw mean within5%, RMSEwithin10%; actualcontinuous turns, axis drift≤.3m, pose/contacts/torque limits; two completed turns alone are not a skill pass|
|RMrough|Actualsource geometry/layout and signedroutes|Routecompletion withoutreset stitching, velocity error, slips/contact losses/termination reasons and terrain evidence|
|270mmstep|Sameepisode approach→firstflight→full-wheel-footprintclearance→topbearing→sustainedrecovery|Exactmesh envelope, originalsupport/contactand0.5s historicalmetric retained; additionally≥2s endholding reported; no height-onlysuccess|

R00 result.proposed_gate omitted explicit loadbearing and had a pre/post10ms estimatorRMSE mismatch; originalresults remain. reports/r00_first_six_analysis.json appends time-alignedmetrics and an explicit95%-controlsampleboth-wheel screen. That95% instantaneous-contact condition is NOT a universal highspeed/roughterrain gate: polygonal rigidtire contact can be intermittent. R01 before its new trials defines physics-rate wheel normalimpulse and requires tail meanperwheel>.2mg and zero nonwheelgroundcontact ticks; subsequent readers must retain these original case definitions, and any further metric revision must be append-only rather than retroactively turn old failures into pass.

## Full-DR statistical qualification (proposed)

- Tune only declared trainingseeds/configs. Freeze source/config before independentholdout, initially≥64newseeds perfamily/variant.
- Report exactdenominators, completions, event/continuous-hold distinctions, Wilson95% intervals, D3=0/10ms strata, independentleg/wheellags, mass/friction/gain/spring extremes and failuretypes. Smallscreen counts are not a passrate estimate for hardware.
- Provisional targetpointestimates: ≥95% ordinaryflat balance/velocity/turning, ≥90% demandingcontinuousspin/rough/step; these are proposedgoals, not userratifiedthresholds. Worststratumresults stay visible and cannot be hidden by D0 nominal episodes.

## Operating envelope and physical uncertainties

2m/s forward and4πrad/s yaw are separate capabilities. With track.4376m, yawalone needswheel tangentialspeed≈2.75m/s. Combinedforward2+yaw4π needsouterwheel≈4.75m/s, exceeding declaredwheelno-loadspeed≈3.46m/s usingnominalr.0625 (≈3.53 atmeshcircumradius). Firmware must projectcombinedcommands into a real speed/torque/power envelope and report the limitation rather than claimbothsimultaneously.

RawmechanicalpositiveΣτw is only a lower-levelpowerindicator. Electrical copperloss/driveefficiency, busvoltage/current, regen and thermal duration are not yet calibrated; a mechanicalcap is not a full referee/buspowerqualification. IMU mountingextrinsic, motorIDs/units/signs and targetboard remain explicitbindings.

## Deployment evidence ladder

Source/math tests → hostC float32 tests → targetARMcompile/memory/timing → boundBSP/CAN/IMU/HIL → lowenergyfixture bench → fieldvalidation. Each has separate status. Preserve independentLQR fallback onMPCdeadline/estimator/linkfail. Unknownboardbindings inhibit real output. DJI Cboard orDamiaoboard choices do not change the fact that targetmotors areDamiao; never reuseSPR3508 current mapping forDM3519.
