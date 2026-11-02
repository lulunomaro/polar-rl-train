E2 V5 full900 early-command saved-text acceptance review

Original20k/900controls18s/100warm800steady complete; actualnative24=24/192/48+legs/wheels192,full7200physics. Core/STD/norm17Adam859300/LR.00022500000000000002 literalunchanged, actualwait0/allownout/privateEXreleased/errors[]/integrity[]. No timeout or originalnon-timeout events. Skill graduation remains pending.

Actual original postrestore resample adopted20000IDs at physics0/phase0, timer12.000049591..15.999617577s. TrueE2 movingyaw±4, timer12..16s and12s transition kept; this is notE0±1..2. Initialwrittenphasevalid true/leftcensorfalse. Warmup transitionphase exposure192000 now accounts for every observed transitioncontrol.

40000 closed events=40000 ACTED +0 zero-control.20000 are complete observed resample→resample commands;20000 are window-ended/rightcensored partialcommands;0 reset-ended/initialleftcensored. Aggregate event counts are not automatically uniqueenv. Complete-command exposure 14,007,141 population-controls (77.817% of all18M); mean observed complete lifetime 14.007141s. Both transition signs have complete pre12s-phase coverage:962negative+958positive=1920 events.

| Original E2 profile | Acted /window-ended instances | Complete events /perprofile uniqueenv | Complete controls | Complete body-v MAE m/s | Yaw MAE rad/s | Height MAE m |
|---|---:|---:|---:|---:|---:|---:|
| standing | 3952 /1911 | 2041 /2041 | 1433788 | 0.020505 | 0.029420 | 0.004879 |
| straight_negative | 8087 /4028 | 4059 /4059 | 2838091 | 0.034089 | 0.048187 | 0.007191 |
| straight_zero | 0 /0 | 0 /0 | 0 | unknown | unknown | unknown |
| straight_positive | 8086 /4079 | 4007 /4007 | 2810234 | 0.039917 | 0.058372 | 0.004775 |
| pure_negative | 4069 /2007 | 2062 /2062 | 1446176 | 0.034013 | 0.182124 | 0.005896 |
| pure_positive | 3987 /2014 | 1973 /1973 | 1378988 | 0.035681 | 0.188533 | 0.005624 |
| transition_initial_negative | 1953 /991 | 962 /962 | 672040 | 0.030848 | 0.131690 | 0.005579 |
| transition_initial_positive | 1937 /979 | 958 /958 | 670061 | 0.029742 | 0.131258 | 0.005521 |
| moving_yaw_minus4 | 4031 /1990 | 2041 /2041 | 1427730 | 0.061699 | 0.130302 | 0.017514 |
| moving_yaw_plus4 | 3898 /2001 | 1897 /1897 | 1330033 | 0.064595 | 0.124458 | 0.018736 |

Moving±4 accepted sampled2pi windows: 39,594 events across 63582.345703 population-seconds (89.408% of movingexposure). Time-weighted worldprojected cycleprogress 0.592000451m/s vs integratedcommandreference 0.501076759; nominal.5 cycleabsoluteerror 0.106909574m/s, integrated-reference error 0.105483486. Progress exceeds the reference on average; it is not a proven trackingpass. Body-v MAE and this worldcycle quantity use different denominators/semantics. Per-signed rows and warmup/steady/whole controlweights retained in JSON.

Remaining acceptance gaps:
- No original numeric skill pass tolerances or per-command success rule is present in the saved texts; do not invent a globalMAE pass threshold.
- straight_zero has no exposure/complete instances and allerrorsnull: pending, not a pass or a failed attempted profile. Original standing profile is separate.
- 20k window-end acted commands are incomplete despite absence of resets; fullrun900 is not40000 fullcommands.
- Perprofile uniqueenv is exact, but crossprofile/signed-direction union is not directly saved. Show bounds, not sum overlapping uniqueenv counts as a total.
- Complete command summaries provide body-v/yaw/height means; per-command worldprogress success rates, extremes and raw timer/first-action distributions were not extracted because JSONL content remains metadata-only.
- Moving worldprogress is measured on accepted signed2pi sampled windows (~89%movingtime). Unsampled elapsedtime/commands are not assumed successful; cycleabsolute error is not instantaneous world-v error/body-v MAE.
- All18s runs here use the saved model and one declared case design; no broad stochastic coverage, long-term reliability or preserved frozen graduation label is established.
- No complete127-state/executedaction/DR/queue/reset WM transition dataset is produced by a command-instance JSONL/weight checkpoint.

InstanceJSONL index only:40000rows/29613072B/SHA0f061551d29c49088a6165f0376c59c64ba86185f4d2f192ac57e3c8056e1a1c; initialJSONL20000rows/4417964B/SHA053926c8bed1fb31e1ac2af2ffcb658e26bbb5802d78bbc4845444a0d9fd741d. Contents never opened/decoded. 151 saved-text/exposure/clock/producer checks. No remote/SDK/GPU/model/PT/NPZ/raw/gz/JSONL artifact access. Root ordinaryGitpending; no newtrial/tag.
