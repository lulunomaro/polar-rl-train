E0V2 full1000 early-command review — saved text only

20k ×1000controls /20s /100warm900steady completed;17Adam641200/LR unchanged. Native24=24/192/48+legs/wheels192, full8000physics. Originalwait0/allownout/private released/errors[]/integrity[] verified. This is execution and exposure evidence; skill graduation remains pending.

Actual early original postrestore resample adopted20000 IDs at physics0/phase0; timer 12.000231743..15.999968529s. No extra reset/RNG was needed. New per-profile initial-leftcensored counters all0. The saved profile's two old generic booleans still say initialunknown/leftcensored; both are retained and labelled alongside the realV2 admission, not silently overwritten. OldV1 is unchanged.

Closed records 60,000: acted 40,000,0-control 20,000. Fully observed resample-to-resample events 20,000; reset-ended acted 20,000; acted-window-end0. All20k window-end rows have0controls. Events are not uniqueenv and0-control records are not successes.

| Original profile | Acted events | Complete command events /perprofile uniqueenv | Complete controls | Complete bodyVx MAE | Complete yaw MAE | Complete height MAE |
|---|---:|---:|---:|---:|---:|---:|
| standing | 3948 | 2000 / 2000 | 1401383 | 0.018380 | 0.033788 | 0.003753 |
| straight_negative | 7976 | 3970 / 3970 | 2781362 | 0.029619 | 0.046657 | 0.005363 |
| straight_zero | 0 | 0 / 0 | 0 | unknown | unknown | unknown |
| straight_positive | 8162 | 4097 / 4097 | 2870364 | 0.039424 | 0.058307 | 0.003895 |
| pure_negative | 3997 | 2005 / 2005 | 1405126 | 0.034503 | 0.178390 | 0.004777 |
| pure_positive | 3960 | 1961 / 1961 | 1371025 | 0.035324 | 0.183988 | 0.005418 |
| transition_initial_negative | 1998 | 987 / 987 | 685419 | 0.029780 | 0.125504 | 0.004964 |
| transition_initial_positive | 1959 | 992 / 992 | 692410 | 0.029137 | 0.124999 | 0.004927 |
| moving_yaw_negative_abs1_to2 | 4029 | 2023 / 2023 | 1418324 | 0.048252 | 0.074259 | 0.007792 |
| moving_yaw_positive_abs1_to2 | 3971 | 1965 / 1965 | 1372595 | 0.046902 | 0.078889 | 0.008288 |

Moving signed yaw profiles8/9: 12,918 accepted signed2pi sampled-window events, 54529.578125 population-seconds (68.333% of moving exposure). Time-weighted worldprojected progress 0.501780355m/s vs integrated commandreference 0.498146326; nominal.5 cycle absolute error 0.015849513m/s; integrated-reference error 0.016576535. These are sampled-cycle metrics, not bodyvelocity MAE, instantaneousworldvelocity or fullcommand success rates.

Both original transition signs have complete instances covering every pre12s bin:987negative+992positive=1979 events. Later incomplete commands still contribute exposure, so whole phase metrics cannot be relabelled complete-command metrics. Original non-timeout events0; timeout20000. All thresholds retained; maxclosure 0.000932704308m is an observed maximum, not an added skill line.

Pending original acceptance:
- No original numerical skill pass tolerances/per-command success thresholds saved; do not invent a graduation rule.
- straight_zero has0 exposure; original continuous straight command has a zero label but no discrete zero atom guaranteed. No exposure is pending, not failed/success.
- Only one20s window/seed and sampled original commands; no full stochastic range or long-term reliability claim.
- Moving worldprogress metrics cover only accepted sampled same-command2pi windows (~68%movingtime), not every command/all elapsed movingtime.
- Complete command summaries provide body/yaw/height errors but not per-command worldprogress success counts or distributions; JSONL content intentionally NOT transferred/read.
- Global unique env unions across changing signed profiles are not saved. Retain perprofile exactunique and conservative union bounds, never sum overlaps as exact globalunique.
- Per-transition error tensor axis names are not explicit in saved schema; report axis0/1/2 only, no guessed physical labels.
- 20k reset-ended acted commands are incomplete despite no non-timeout failure;20k0-control window-end rows cannot be positive skill evidence.
- No complete127-state/executedaction/queue/DR/reset WM transition dataset; command JSONL and weights are not that dataset.

Producer indexes only: instances60000rows/31308073B/SHA8313411b…a1f63; initial20000rows/4534848B/SHA0ac3f985…8dc25. Contents not opened or fetched. 251 bounded saved-text integrity/accounting checks passed. Full numeric and exact path/bytes/SHA evidence are in adjacent JSON. No remote/SDK/GPU/model/NPZ/raw/JSONL access. Root ordinaryGit pending; no new trial/tag.
