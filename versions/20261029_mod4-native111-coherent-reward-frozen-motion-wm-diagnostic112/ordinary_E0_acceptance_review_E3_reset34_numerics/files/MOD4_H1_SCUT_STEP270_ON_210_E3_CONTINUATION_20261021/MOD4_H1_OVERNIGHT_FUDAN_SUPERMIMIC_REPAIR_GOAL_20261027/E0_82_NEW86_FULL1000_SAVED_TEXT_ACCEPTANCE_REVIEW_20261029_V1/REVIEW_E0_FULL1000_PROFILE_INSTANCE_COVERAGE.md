E0 adapted82 — complete20s execution; skill acceptance incomplete

ActualN20k1000controls/20s,100warm900steady,8000physicscallbacks. CUDAfullrestore/native24(24/192/48,bothqueue192)/core+norm+STD+17Adam641200/finalLR.00038443359375000017 unchanged. Originalwait0/out/private released; errors/integrity empty. No new actor/model/raw/NPZ/gzip/SDK/host calls in this review.

Conditional moving: 3990012 population-controls; actual signed2pi sampled windows 12918 events /54529.578125 env-seconds, covering68.3326% of moving exposure. Time-weighted actual projected progress 0.501780355m/s vs integrated command reference 0.498146326; time-weighted absolute reference error 0.016576535m/s. These are measured same-command/episode sampled cycle-window metrics, not population-wideMAE, instantaneous cos² comparison, full-command completion or uniqueenv count. E0 moving yaw abs1..2rad/s, not E2±4.

True source zero-command standing: 1987851 controls/3737 unique exposed env; body forwardMAE0.022801185, yawMAE0.040875631, heightMAE0.003890233m. No invented MAE threshold. Nonsource-standing straight_exact_zero profile had0exposure, so is pending.

|profile|population-controls|unique exposed env|body-v MAE|yaw MAE|timeouts|
|---|---:|---:|---:|---:|---:|
|standing|1987851|3737|0.02280118548875142|0.04087563105207583|1948|
|straight_negative|3983888|7183|0.03655551122421112|0.05651280937742226|4006|
|straight_zero|0|0|None|None|0|
|straight_positive|4092235|7342|0.04738833119310108|0.06467828704851994|4065|
|pure_negative|2005228|3804|0.03991253581886948|0.206389217335884|1992|
|pure_positive|1970188|3777|0.04125240839960451|0.21397117305556626|1999|
|transition_initial_negative|986524|1944|0.03565044096747773|0.13422101236259837|1011|
|transition_initial_positive|984074|1916|0.03488080863329384|0.14105113030117652|967|
|moving_yaw_negative_abs1_to2|2019728|3818|0.055631814191069294|0.08225431530879405|2006|
|moving_yaw_positive_abs1_to2|1970284|3767|0.05525536309105692|0.08809158349760746|2006|

All9 original transition bins (start/hold/brake/stop/reverse/hold/brake/stop/post12stop), signs, and warm/steady errors/denominators are retained in JSON. 1968619/1970598 transition controls have observed written-phase cache; 1979 initially unknown are NOT guessed. Phase coverage across manycommands is not complete12s same-instance acceptance. Stop-phase samples are not relabelled standing.

Command-instance result: 60000 closed-event records reported, including20000 initial-left-censored,20000 reset-ended,20000 window-end. Fully observed resample→resample instances ZERO; complete-instance population denominator ZERO across all10profiles; complete12s transitions ZERO. Initial phase/start unknown staysleft-censored. Source close can count0-control instances (newly resampled at end); unique_closed can exceed unique_exposed. Do not call60000 all acted attempts or add profileunique counts as a global union. Per-instance population/tails cannot be reconstructed from aggregate summaries.

Originalrecord_file /data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_LONG_COMMAND_20261029v1/e0/frozen_regression/E0_OBSERVED_COMMAND_INSTANCE_RECORDS_ACTUAL.jsonl is reported60000rows/80kcap-notlimited, but prior reader suffix sets omitted .jsonl from bothfulltexts andlarge metadata. Its actual bytes/SHA are UNKNOWN here; no content/raw/host read was made to patch the gap. Existingaggregate JSON and producer declaration are preserved; not a full dataset claim.

Non-timeout events0, natural timeout-events20000; clock explicitly excludes timeouts and thus reports non-timeout reset0, while instance reset-ended counts20000. No contradiction. Actual maximum closure0.000932704m/mimic0.001691456rad retained; no newwholebatchgate. Longer20s evidence improves the prior2.4s case but does not establish full original command-life/heldout/generalization/skill graduation. Selectedtrace is partial diagnostic data, not complete WM dataset. 226 saved-text/denominator checks passed. RootordinaryGit pending.
