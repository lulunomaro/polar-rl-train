# Current mature5 policy: paired5/6 contact diagnosis completed

The previous COM/link reference-point repair is complete and correct. That change repaired frozen evaluation arithmetic; it did not modify the trained policy or reduce6rad/s contact residuals. The mature5 curriculum subsequently passed two full-policy assessments and two-seed nominal/white_v2 paired15-second regressions. Four newly completed6rad/s frozen transfers still fail the original positive-spin right-wheel input-mesh proxy gate. This is a remaining behavior/adaptation issue, not evidence that the same reference-point bug was left unfixed.

This new diagnostic uses precisely the mature17039 source SHA253ed8effd5fe8580859bce1b7731006ae62a5e7bf1c63a9f8825de2c74bc73e, seed20261002, white_v2. Three88env3-second rollouts completed:6 control without the substep hook,6 with the read-only .5ms hook, and5 with the same hook. All264 rollout instances survived with physical_smoke=true/noNaN. Complete initialroot/q/parameters match; control6/substep6 behavior arrays are exact; unchanged-command groups match5/6 exactly. Both hooks recorded6000 callbacks and5000 post-warmup samples per wheel. Whole canonical ledger bytes stayed exact:252000 authorized,175387.31713533401 charged,76612.68286466599 effective seconds remaining. No PPO, production or gate change.

The table summarizes eight positive-spin environments, right wheel. Ranges are min/max of per-environment summaries, not instantaneous minima/maxima unless explicitly labeled.

| Metric | +5rad/s | +6rad/s |
|---|---:|---:|
| Original100Hz input-mesh mean proxy, m/s | .12585–.13857 | .20208–.21066 |
| .5ms force>=10N fraction |44.56–48.96%|24.78–27.12%|
| Report-point loaded time mean tangent speed, m/s |.10710–.11507|.11873–.13678|
| Report-point impulse-weighted tangent speed, m/s |.09707–.11020|.10993–.12624|
| Impulse-weighted absolute rolling component, m/s |.08848–.09675|.10572–.12422|
| Input-mesh mean during force<10N, m/s |.14316–.15791|.22942–.24405|
| Fraction of loaded frames with tangent speed>.15 |15.98–24.37%|25.91–39.38%|
| Normal-force RMS, N |168.22–190.42|201.64–223.54|
| Positive-force report-point peak speed, m/s |.34240–.48644|.44047–.53128|
| Body mean XY speed magnitude, m/s |.07008–.07258|.09306–.13036|

The strongest increase in the whole-time mesh proxy occurs during low-force intervals, while loaded rolling residual also increases. The positive right-wheel loaded fraction drops and force RMS/body XY speed rise. This supports investigating rolling consistency and load pulsation together; it does not establish a causal reward fix. Mean XY speed is not net displacement. Pure +/-5 and +/-6 recorded zero wheel/leg rating clips during this short control-sampled window, so a software motor-limit increase is unsupported.

Negative-spin rows and both wheels' per-environment min/mean/max are preserved in MATURE5_CONTACT_PAIRED_REVIEW.json. Negative6's left-wheel impulse-weighted tangent speed is .12783–.13786m/s; the asymmetry cannot be hidden by a positive-only aggregate. All original skill booleans remain in the raw reports. Three-second ramp statistics must not be substituted for the existing15-second enable/stop/reverse tests.

Limits: the loaded data use PhysX-reported solver points and post-step rigid-body velocities, not persistent material-patch tracking or real-robot measurements. Force>=10N is a diagnostic filter; low force alone does not establish airborne state. Filtered mean values do not replace the original unfiltered .15m/s15-second gate. Simulated force peaks are not spring/hardware certification. This is one-seed3-second physics evidence, not skill graduation or sim2real validation.

Next work: prepare one isolated behavior adaptation aimed at loaded rolling consistency/load smoothness, verify actual inputs and old5 capability at fixed white_v2/hardware/physics, and run complete physical/PPO preflight before any bounded formal trial. Keep6 rejection history, original admission thresholds and mature17039 rollback. Do not repeat the arithmetic repair, blindly add the unloaded mesh proxy to reward, indefinitely retrain mature5, or simultaneously change rate/DR/reward/physics. No new reward, formal6 PPO or adaptation acceptance exists yet. Pure-spin priority continues; movement/FPS/terrain postponed.

The first diagnostic attempt's auxiliary shadow assertion was incompatible with the already-corrected evaluation input. Its isolated v2 compatibility repair retained legacy statistics and passed3 CPU checks; original error/logs remain. The retry finished with unique output paths. Do not rerun original/retry workers, preparation or completed settlement/extension transactions.
