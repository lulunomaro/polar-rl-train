# W35 v3：最终冻结评测文本审查

实际600 controls/12s（100 warmup/2s、500 steady/10s）完整收尾；mean模型、actor/critic/STD/norm及17Adam648360不变。原fullrestore、24/192/48和legs/wheels各192/trace1..24正证明、wait/out/private release与integrity[]全部成立。技能毕业与完整WM数据资格仍pending。

仅保存JSON和3份已冻结语义Python文本被读取；Python只AST解析，未import/执行。NPZ/gz/PT/raw、SDK/GPU/remote均未访问。

## 条件分组与实际分母

|phase / source condition|人口control|独立暴露env|forward MAE|yaw MAE|height MAE|瞬时world-progress MAE|turn事件 / 有turn的独立env|
|---|---:|---:|---:|---:|---:|---:|---:|
|whole / all|12000000|20000|0.032483|0.040754|0.005170|未定义|532 / 491|
|whole / gentle|8035223|14677|0.028642|0.036535|0.004776|未定义|0 / 0|
|whole / standing|2880734|6018|0.017661|0.032316|0.004150|未定义|0 / 0|
|whole / straight|256109|1848|0.212399|0.122871|0.015122|未定义|0 / 0|
|whole / moving_world_yaw|540769|1979|0.089313|0.114955|0.012316|0.305882|532 / 491|
|whole / eligible_other|287165|1109|0.021183|0.030495|0.004087|未定义|0 / 0|
|steady / all|10000000|20000|0.028138|0.038937|0.004932|未定义|532 / 491|
|steady / gentle|6709817|14521|0.026189|0.036091|0.004644|未定义|0 / 0|
|steady / standing|2475894|6018|0.017372|0.031942|0.004109|未定义|0 / 0|
|steady / straight|141747|1169|0.192404|0.120262|0.014822|未定义|0 / 0|
|steady / moving_world_yaw|410130|1808|0.073205|0.105131|0.011794|0.303850|532 / 491|
|steady / eligible_other|262412|1035|0.020389|0.030288|0.004011|未定义|0 / 0|

moving占全窗4.5064%，steady占4.1013%。全人口MAE不能代替moving/straight表现。每行unique env是该条件实际暴露过的ID集合，条件间有交叉，不能相加当20000个独立人。

standing标签在实际75d source明确是mode1（%7==1），分母2880734；moving补集是11459231，两者不同。gentle/straight/eligible_other也在补集中。源码意图standing时command置0；但本允许文本没有逐控制真实zero-command筛选指标，报告不把source-label自动升级成实测纯零命令验收。

## world-progress与turn计数的限制

source command：moving BODY vx=cos(theta-alpha)、vy=0，目标V=.5；yaw magnitude按1+u生成1–2 rad/s（profile literal yaw12不能擅读为固定1.2）。理想跟踪时world投影速度=cos²(theta-alpha)，瞬时|projection-.5|本来也非零；uniform-angle理想均值1/pi仅是解析参考。实测.305882/.303850不是完整周期进度误差，既不能据此判moving失败，也不能据此判理想跟踪。

532是源码记录的signed-turn事件，491是至少一次此计数的独立env，二者不是成功episode数量。counter在同profile/phase/episode且live时净角达到2pi计数；没有command-instance UID，因此同profile resampling可能跨不同world_direction/target。也未保存周期投影位移/实际时长汇总，不能声称完整原world-progress技能已验收。

whole: 负/正sign暴露env=1206/1238，两sign都暴露465；有负/正turn计数env=264/260，两sign都有计数33。以上用两个实际集合的inclusion/exclusion推导，仍不是per-command world-progress成功率。
steady: 负/正sign暴露env=1131/1142，两sign都暴露465；有负/正turn计数env=264/260，两sign都有计数33。以上用两个实际集合的inclusion/exclusion推导，仍不是per-command world-progress成功率。

## 每profile覆盖（0曝光不当通过）

|phase / index / family / mode|人口control|unique env|forward / yaw / height MAE|turn事件 / unique env|最长live秒|
|---|---:|---:|---|---:|---:|
|whole / 7 / plane_for_rm / gentle|1531135|3588|0.032202 / 0.033563 / 0.004608|0 / 0|10.000039|
|whole / 8 / plane_for_rm / standing|1047222|2273|0.017252 / 0.030528 / 0.003869|0 / 0|10.000039|
|whole / 9 / plane_for_rm / negative_straight|127380|1183|0.204337 / 0.145272 / 0.019509|0 / 0|2.239999|
|whole / 10 / plane_for_rm / positive_straight|128729|1159|0.220378 / 0.100704 / 0.010782|0 / 0|2.339998|
|whole / 11 / plane_for_rm / negative_world_yaw|265131|1206|0.086698 / 0.103532 / 0.011656|267 / 264|6.439995|
|whole / 12 / plane_for_rm / positive_world_yaw|275638|1238|0.091829 / 0.125943 / 0.012951|265 / 260|5.999995|
|whole / 13 / plane_for_rm / eligible_without_retained_mode|287165|1109|0.021183 / 0.030495 / 0.004087|0 / 0|10.000039|
|whole / 14 / tiny_step / gentle|1778803|3025|0.027822 / 0.035789 / 0.004737|0 / 0|10.000039|
|whole / 15 / tiny_step / standing|521597|1044|0.017636 / 0.032253 / 0.004251|0 / 0|10.000039|
|whole / 21 / slope_for_rm_high / gentle|1928456|3300|0.023212 / 0.035437 / 0.004345|0 / 0|10.000039|
|whole / 22 / slope_for_rm_high / standing|542344|1134|0.017473 / 0.034652 / 0.004015|0 / 0|10.000039|
|whole / 28 / inv_slope_for_rm_low / gentle|1475237|2517|0.023424 / 0.033370 / 0.004302|0 / 0|10.000039|
|whole / 29 / inv_slope_for_rm_low / standing|399163|817|0.017364 / 0.031762 / 0.004035|0 / 0|10.000039|
|whole / 35 / random_uniform_for_rm / gentle|1321592|2247|0.039366 / 0.046115 / 0.006179|0 / 0|10.000039|
|whole / 36 / random_uniform_for_rm / standing|370408|750|0.019444 / 0.034635 / 0.005121|0 / 0|10.000039|
|steady / 7 / plane_for_rm / gentle|1314629|3432|0.027241 / 0.032768 / 0.004387|0 / 0|10.000039|
|steady / 8 / plane_for_rm / standing|923082|2273|0.017165 / 0.030311 / 0.003841|0 / 0|10.000039|
|steady / 9 / plane_for_rm / negative_straight|72472|736|0.185345 / 0.139038 / 0.018882|0 / 0|2.239999|
|steady / 10 / plane_for_rm / positive_straight|69275|747|0.199788 / 0.100619 / 0.010575|0 / 0|2.339998|
|steady / 11 / plane_for_rm / negative_world_yaw|203995|1131|0.071699 / 0.092790 / 0.011174|267 / 264|6.439995|
|steady / 12 / plane_for_rm / positive_world_yaw|206135|1142|0.074696 / 0.117344 / 0.012407|265 / 260|5.999995|
|steady / 13 / plane_for_rm / eligible_without_retained_mode|262412|1035|0.020389 / 0.030288 / 0.004011|0 / 0|10.000039|
|steady / 14 / tiny_step / gentle|1476303|3025|0.026411 / 0.035524 / 0.004640|0 / 0|10.000039|
|steady / 15 / tiny_step / standing|440697|1044|0.017471 / 0.031997 / 0.004223|0 / 0|10.000039|
|steady / 21 / slope_for_rm_high / gentle|1598456|3300|0.021107 / 0.034927 / 0.004195|0 / 0|10.000039|
|steady / 22 / slope_for_rm_high / standing|460544|1134|0.017136 / 0.034328 / 0.003974|0 / 0|10.000039|
|steady / 28 / inv_slope_for_rm_low / gentle|1223537|2517|0.021425 / 0.032679 / 0.004164|0 / 0|10.000039|
|steady / 29 / inv_slope_for_rm_low / standing|338463|817|0.017167 / 0.031349 / 0.003997|0 / 0|10.000039|
|steady / 35 / random_uniform_for_rm / gentle|1096892|2247|0.037352 / 0.046341 / 0.006146|0 / 0|10.000039|
|steady / 36 / random_uniform_for_rm / standing|313108|750|0.018413 / 0.033810 / 0.005059|0 / 0|10.000039|

五种G3均有gentle/standing；retained signed straight/world-yaw只在plane。所有126 profile行（含warmup和0曝光）、family人口曝光及每profile reason events/unique在完整JSON保留。family unique无法从profile unique直接相加重建，未补造。

## 原终止/timeout及域覆盖

全窗terminated mask=3，独立发生terminated的env=3；truncated mask事件=10025，没有group层global unique-truncation指标。原reason flags与phase事件逐项保留；timeout不等于技能失败。

run-local episode UID最终值来源是保存JSON：reset-ID counter增量总计10028、有reset增量独立env=7730、最大UID=6。这是评测内reset hook计数，非原训练episode总数或失败率。

有界trace控制点74个、未压缩记录63755887B，retention_limited=False；数据payload未读。本报告不能验证未打开转移中的全部action/queue/DR/pack127/force/torque，也不称可训完整WM数据。

原panel静态pending字符串保持原文，但不能抵消已返回真实runtime正证明；最终仍缺技能阈值与完整coverage/domain验收。

## 尚缺条件

- No saved actual per-env/profile error distribution/quantiles or required numerical graduation thresholds; scalar means and exposure counts do not certify skill.
- Per-condition unique ID sets overlap when an environment changes profile; never sum unique counts over profiles/conditions/phases. Actual population-control exposures partition controls.
- Recorded signed-turn counter requires measured net yaw>=2pi, live, same profile/phase/episode. It does not track command-instance/resample UID or fixed world-direction continuity, so it may span same-profile command resampling. Keep original complete_signed_cycle_events label; do not promote it to original per-command/cycle world-progress success.
- No cycle endpoint world displacement/duration summary is saved. Instantaneous moving_world_progress_abs_error is |actual projected velocity-.5|, not complete-cycle progress error.
- Original command vx=cos(theta-alpha),vy=0 yields ideal projected world velocity cos²(theta-alpha), so instantaneous target-.5 deviation can be nonzero even with exact command tracking. Uniform-angle analytic mean 1/pi is an ideal reference only, not actual sampling/policy evidence.
- Standing is the source mode1 bin, not all nonmoving. Gentle and other nonmoving commands may be nonzero. No independently filtered actual zero-command metrics can be obtained without prohibited trace reads.
- Only plane has retained straight/moving exposure. Other four G3 families have gentle/standing only in this window; no pure high-rate spin or unobserved command/family acceptance is claimed.
- Largest live duration is a maximum over IDs, not an every-ID sustained criterion. No survival/duration distribution or complete same-command duration is available from aggregate text.
- Reset/termination/truncation observations are events or scoped unique IDs, not independent trials. rough_route_boundary remains an original timeout; no reclassification as non-timeout skill failure.
- Trace is selected profile/IDs and sampled controls. No NPZ/gzip payload was opened or validated; trace completeness, pack127/xi/contact/actual torque and full WM dataset qualification remain unproved.

本次只做文本审查，未重跑评测/模型；旧false/原标签未覆盖。新scope待root普通Git补档，不新建trial/tag。
