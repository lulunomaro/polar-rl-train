# RAW2K COM Window v1 — new correlated-noise sensor-only shadow

Starts only after ROUGH_POSTURE_CAUSAL_V1 final delivery. No old-source/PH3 edits, physics/once/realIO/GPU/Git/new agents. Only six sensor_shadow.jsonl paths in RAW2K_SHADOW_V1/SENSOR_ONLY_MANIFEST.json + public nominal31bodymodel and sealed mathematical helpers. Do not read neighboring original trace/result/DR/GT. Original raw only existing producerSHA; this new analysis may stream authorized projections.

## Precisely observable target

At2k pre-step timestamps, q/qd/gyro/proper align. Use same-time raw sample endpoints t0,t1 and intervening left-held noisyraw values, h=.5ms. Define a **discrete-sample functional**, not continuous true COM:

```text
R_(i+1)=R_i exp([gyro_i]h)
I_(i+1)=I_i + R_i integral_0^h exp([gyro_i]s)ds * fIMU_i
u_endpoint=omega×(rCOM(q)−sIMU)+J(q)*qd(+nominal wheel radial term)
F_window = (I_end−I_start transported to startframe)/T
          + (Rrel_end*u_end−u_start)/T
```

No alpha/qdd required. Same-time endpoint_data come from samples, NOT original endpoint_joint_pos4 at epoch combined with mean rates. Current raw lastsample=sourceEpoch−500us, so a window ending there has nominal average ageT/2+arrival−lastsample; boxcar firstmoment/controllerepoch is not falsely synchronized.

Deduplicate source sequence/epoch; discard separate instant boot. Join only contiguous .5ms samples; gaps break eligibility. Evaluate50/100/150ms overlapping windows at eachfresh frame's final sample. RelativeRstart=I gauge, unknown constantworld orientation only rotates whole result, norm invariant.

## Paired old-mean approximation comparison

At EXACT SAME t0/t1 and with SAME raw endpointu, integrate original authoritative100Hz mean gyro/proper as constant bins over their overlapping time support. Compare to2k discrete functional. This isolates observed noisy intrawindow path/transport differences. It is not byte-replay of old epoch-endpoint policy, and not error against independent continuous-world COM/contacttruth (not available/admitted).

## Correlation and uncertainty

The publisher uses same-window D1offset; authoritative means exactly oldpacket, raw mean matches to roundoff, not bitidentical. This is information-enhanced/correlated-noise branch, not IID2k/oldbenchmark. No sqrt20/windowN noise reduction. Preserve public nominal model/zero/lever/J error scales and wheel missing-phase radial bounds. Endpoint rate-time mismatch term can be removed ONLY because raw endpoints themselves align; unobserved model/hardware errors do not vanish.

Noise/model budget refers to discrete functional conditional assumptions, with same-window offsets retained as worst-case correlated terms. Unknown sub-.5ms motion/gyro-proper covariance/quadrature remains UNBOUND for continuous physical COM. Hardwarebindingfalse, confidence cap.50/frozen trusted threshold.60, cues UNKNOWN. No FSM/actuation integration. Future dynamic spin/jump and highrate calibratedhardware requirements may be proposed, not run.
