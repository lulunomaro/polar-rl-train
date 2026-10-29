E2 V4 完整900control保存文本审查。执行通过；技能毕业仍pending。

20k×900=18,000,000人口controls；100warm/800steady，18s。实际CUDA/native24=24/192/48、legs/wheels各192、trace1..24通过；core/STD/norm/17Adam859300及LR.00022500000000000002保持不变。原非timeout/timeout事件均0，只描述此窗。

|phase/group|人口controls|body-vx MAE|yaw MAE|height MAE|
|---|---:|---:|---:|---:|
|whole/standing_source_flag|1818834|0.025422|0.039119|0.005106|
|whole/straight_signed|7262574|0.047005|0.065837|0.006325|
|whole/constant_pure_signed|3629847|0.041723|0.227656|0.005942|
|whole/transition_initial_signed|1732991|0.036524|0.147496|0.005836|
|whole/moving_yaw_pm4|3555754|0.075474|0.150124|0.018265|
|whole/whole_population|18000000|0.048374|0.120281|0.008436|
|steady/standing_source_flag|1614734|0.025515|0.039726|0.005113|
|steady/straight_signed|6455974|0.039278|0.065896|0.006071|
|steady/constant_pure_signed|3226347|0.041250|0.187868|0.005917|
|steady/transition_initial_signed|1540991|0.036455|0.146156|0.005818|
|steady/moving_yaw_pm4|3161954|0.065795|0.130392|0.018154|
|steady/whole_population|16000000|0.043255|0.108326|0.008307|

Moving两sign的completed-window统计（不是全movingcontrols或每command合格率）：
whole: 3555754人口controls/19.7542%，39594窗口事件，63582.346人口秒（moving暴露的89.41%）；投影进度0.592000m/s、积分原command reference 0.501077m/s，time-weighted nominal.5误差0.106910、reference误差0.105483。
steady: 3161954人口controls/19.7622%，35656窗口事件，56886.248人口秒（moving暴露的89.95%）；投影进度0.603019m/s、积分原command reference 0.500883m/s，time-weighted nominal.5误差0.115266、reference误差0.114248。

Whole逐profile uniqueID之和=37266，不能当作distinct环境数。每profile原始unique/事件/分母和三阶段完整30行在JSON，跨sign/profile union只给上下界。

transition初始sign不同于反转后的当前sign；steady9个phase均有暴露。初次written phase未知的未标phase人口controls：{'6': 962, '7': 958}。没有每phase tracking MAE或同一command完整12s验收，不能由aggregate误差补出。

Trace仅56个control点，末点876，正文未读；不能称全900 WM数据。

待原技能条件：
- No original formal success tolerance/pass rule is recorded here; do not invent a threshold from MAE or positive progress
- Progress values condition on completed windows, not every moving control or whole command; unfinished tails/resamples/phase boundaries not graded
- Per-command-instance counts/IDs/success distributions are not in the saved summary; raw commandUID traces were NOT decoded
- Per-env continuous-exposure maxima and full motion are not in this saved summary; NPZ/gz were NOT opened
- Transition phase exposure exists, but phase-specific start/brake/stop/reversal tracking errors and a single-command full12s pass are not saved
- Source standing flag differs from all actual zero command; an independently zero-command-filtered metric is unavailable
- Command amplitude/world-direction/DR/action/queue/reset domain histograms and per-env physical constraints are not certified by this summary
- Ordinary termination-based resets are excluded by source window logic; summary alone does not audit every possible within-control health reset
- No complete127state/31contact/actualforce/action/DR/reset/dt WM dataset is certified
