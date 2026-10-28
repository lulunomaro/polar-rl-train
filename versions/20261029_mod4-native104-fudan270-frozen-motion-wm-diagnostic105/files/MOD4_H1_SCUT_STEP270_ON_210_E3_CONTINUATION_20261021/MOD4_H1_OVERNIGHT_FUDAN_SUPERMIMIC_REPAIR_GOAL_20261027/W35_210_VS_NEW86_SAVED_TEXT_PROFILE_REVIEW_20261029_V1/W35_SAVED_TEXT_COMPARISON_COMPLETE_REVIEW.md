# W35：210完整冻结回归与86部分回归的保存文本审查

210已完成请求的1200 controls（24.00s），含100 warmup/1100 steady（2.00s/22.00s）；86只完成906（18.12s），含100/806（2.00s/16.12s），原wall-time-limited状态保留。两份文本的同源模型、mean策略与原17个Adam648360/归一化不变证据成立；这不等于技能毕业。

本审查只读取指定两个JSON文本；未跟随其中路径，未读取代码、模型、NPZ、USD或其他原始数据，未联网或运行仿真。86使用原保存汇总，210从1200行指标按真实人口重算。输入字节SHA见同目录JSON。

## 全人口与moving子集

|指标（原保存字段）|86全窗906|210全窗1200|86 steady806|210 steady1100|
|---|---:|---:|---:|---:|
|forward_abs_tracking_error_mean|0.031742797|0.032051432|0.028955873|0.030037434|
|yaw_abs_tracking_error_mean|0.040080202|0.040254292|0.038869144|0.039382744|
|height_abs_error_mean|0.005125155|0.005149144|0.004972485|0.005039459|
|moving_world_progress_abs_error_population_weighted_mean|0.306139223|0.306177185|0.304795700|0.305254656|

210全窗人口control=24,000,000，moving人口control=991,848（4.1327%）；steady分别22,000,000/861,209（3.9146%）。86原汇总moving分母为725,679/595,040。

全人口MAE按各control人口加权。moving误差仅按每行实际profile_counts[7*k+4/5]人口加权，不能对control均值简单平均，不能用全人口forward/yaw小误差代替moving能力。原指标未在这两份文本中给出world-progress单位，本报告不补造单位或验收阈值。两窗时长不同且没有逐环境配对，不推断硬件/模型因果提升。

## 原终止原因

|原term|原timeout标记|86 warmup/steady/合计|210 warmup/steady/合计|
|---|---|---:|---:|
|time_out|True|0/0/0|0/9947/9947|
|bad_orientation|False|0/0/0|0/0/0|
|base_contact|False|1/3/4|1/3/4|
|closure|False|0/0/0|0/0/0|
|mimic|False|0/0/0|0/0/0|
|low_base|False|0/0/0|0/0/0|
|rough_route_boundary|True|839/13472/14311|839/17572/18411|

210 terminated mask事件4，truncated mask事件28352。timeout原因发生数合计28358，比truncated mask多6个重叠原因发生数；不能把原因相加当独立reset。原time_out和rough_route_boundary均属于timeout，后者不能重分类为技能失败。base_contact两机各4次，不能据此声称只失败4个独立环境；combined done union及unique env并未保存。

原阈值逐项保留在JSON：bad_orientation .75rad、base_contact 50、closure .002m、mimic .05、low_base -1.0；未修改奖励/重置阈值。

## 五G3与retained命令覆盖

|family|210 warmup人口control|210 steady人口control|本窗出现模式|210/86最终人口快照|
|---|---:|---:|---|---:|
|outside|0|0|未出现|0/0|
|plane_for_rm|610400|6714871|gentle, standing, negative_straight, positive_straight, negative_world_yaw, positive_world_yaw, eligible_without_retained_mode|6104/6107|
|tiny_step|383400|4217698|gentle, standing|3834/3835|
|slope_for_rm_high|411800|4529502|gentle, standing|4118/4117|
|inv_slope_for_rm_low|312400|3435929|gentle, standing|3124/3121|
|random_uniform_for_rm|282000|3102000|gentle, standing|2820/2820|

outside无人口不是缺失第六种G3；五种实际G3均有gentle/standing。本窗retained signed straight/world-yaw只出现在plane，其他四类没有这些命令覆盖。原profile literal为E1_G3_verified_plane_signed_straight_world05_yaw12_v1，radius1.0；pure_high_spin=false、position_correction=false。不能从profile名称补造未保存的逐帧命令范围。

最终eligible/linear/moving/standing是瞬时快照；恢复的audit sample/control histogram不能当本24秒新窗口。下表使用每control原保存计数重算，且与原2×42 warmup/steady直方图逐项完全相同。

|profile index/family/mode|warmup人口control|steady人口control|210保存最长连续秒|210 steady signed cycle事件|86保存signed cycle事件|
|---|---:|---:|---:|---:|---:|
|0 / outside / gentle|0|0|0.000000000|0|0|
|1 / outside / standing|0|0|0.000000000|0|0|
|2 / outside / negative_straight|0|0|0.000000000|0|0|
|3 / outside / positive_straight|0|0|0.000000000|0|0|
|4 / outside / negative_world_yaw|0|0|0.000000000|0|0|
|5 / outside / positive_world_yaw|0|0|0.000000000|0|0|
|6 / outside / eligible_without_retained_mode|0|0|0.000000000|0|0|
|7 / plane_for_rm / gentle|216506|2895019|19.640258789|0|0|
|8 / plane_for_rm / standing|124140|2035825|20.000267029|0|0|
|9 / plane_for_rm / negative_straight|54908|167257|3.539997339|0|0|
|10 / plane_for_rm / positive_straight|59454|169715|2.939997911|0|0|
|11 / plane_for_rm / negative_world_yaw|61136|426738|6.519994736|720|444|
|12 / plane_for_rm / positive_world_yaw|69503|434471|6.319994926|694|428|
|13 / plane_for_rm / eligible_without_retained_mode|24753|585846|15.540165901|0|0|
|14 / tiny_step / gentle|302500|3278474|18.000221252|0|0|
|15 / tiny_step / standing|80900|939224|18.000221252|0|0|
|16 / tiny_step / negative_straight|0|0|0.000000000|0|0|
|17 / tiny_step / positive_straight|0|0|0.000000000|0|0|
|18 / tiny_step / negative_world_yaw|0|0|0.000000000|0|0|
|19 / tiny_step / positive_world_yaw|0|0|0.000000000|0|0|
|20 / tiny_step / eligible_without_retained_mode|0|0|0.000000000|0|0|
|21 / slope_for_rm_high / gentle|330000|3490586|18.000221252|0|0|
|22 / slope_for_rm_high / standing|81800|1038916|18.000221252|0|0|
|23 / slope_for_rm_high / negative_straight|0|0|0.000000000|0|0|
|24 / slope_for_rm_high / positive_straight|0|0|0.000000000|0|0|
|25 / slope_for_rm_high / negative_world_yaw|0|0|0.000000000|0|0|
|26 / slope_for_rm_high / positive_world_yaw|0|0|0.000000000|0|0|
|27 / slope_for_rm_high / eligible_without_retained_mode|0|0|0.000000000|0|0|
|28 / inv_slope_for_rm_low / gentle|251700|2678779|18.000221252|0|0|
|29 / inv_slope_for_rm_low / standing|60700|757150|18.000221252|0|0|
|30 / inv_slope_for_rm_low / negative_straight|0|0|0.000000000|0|0|
|31 / inv_slope_for_rm_low / positive_straight|0|0|0.000000000|0|0|
|32 / inv_slope_for_rm_low / negative_world_yaw|0|0|0.000000000|0|0|
|33 / inv_slope_for_rm_low / positive_world_yaw|0|0|0.000000000|0|0|
|34 / inv_slope_for_rm_low / eligible_without_retained_mode|0|0|0.000000000|0|0|
|35 / random_uniform_for_rm / gentle|224700|2408223|18.000221252|0|0|
|36 / random_uniform_for_rm / standing|57300|693777|18.000221252|0|0|
|37 / random_uniform_for_rm / negative_straight|0|0|0.000000000|0|0|
|38 / random_uniform_for_rm / positive_straight|0|0|0.000000000|0|0|
|39 / random_uniform_for_rm / negative_world_yaw|0|0|0.000000000|0|0|
|40 / random_uniform_for_rm / positive_world_yaw|0|0|0.000000000|0|0|
|41 / random_uniform_for_rm / eligible_without_retained_mode|0|0|0.000000000|0|0|

210 steady负/正world-yaw各720/694，共1414次完整有符号world cycle事件；86各444/428，共872次。事件不是unique env，不是完成率。210 plane straight最长连续约3.54/2.94s，moving约6.52/6.32s；gentle/standing约19.64/20.00s，其余四G3约18.00s。每profile最长值既不是每环境持续时长，也不证明所有moving环境连续完成22s steady。保留原float32时长，不新增精度门槛。86输入汇总没有保存每profile连续时长，因此不推算。

## 验收仍缺的证据

- No saved per-profile tracking/height/world-progress MAE or tail/quantile; aggregate errors cannot certify each retained command/family/sign.
- Signed world cycles are completion events, not distinct successful environments; no saved unique-environment success denominator or per-environment all-sign completion proof.
- Continuous-duration maxima are saved per profile, not a population survival distribution or a duration assigned to every environment. Straight/moving maxima do not cover the entire 22s steady window per mode.
- The five G3 families are represented, but retained straight/world-yaw coverage occurs only on plane in this case; do not claim those modes on the other four families or pure high spin.
- Original termination checks remain unchanged. Four non-timeout base_contact events are observed; no statement that every environment satisfies uninterrupted full criteria is supported.
- The saved original criteria text has termination parameters but no full legacy quantitative graduation thresholds/required population pass rate or per-profile sustained-error criterion; original graduation cannot be reproduced from these two texts.
- The 86 run is wall-time-limited at 906 of 1200 controls. The 210 run completes its requested 1200, but unequal horizons and unmatched per-environment trajectories prevent a hardware or causal skill-improvement conclusion.
- The retained profile literal world05_yaw12 and radius1.0 are saved; actual per-step command vectors/ranges by profile are not available in the two permitted inputs, so numerical command coverage beyond saved labels is unverified.
- Authoring-mesh ground support queries are explicitly not contact-force certification.
- No complete typed WM transition dataset is established: aggregate metrics and selected32 artifact metadata do not supply pack127/ingress/executed action/queue/xi-DR/terminal-before-reset/dt fields for all transitions.

结论：210请求的冻结执行覆盖完成，86请求覆盖仍为部分；技能毕业保持PENDING，不继承原legacy毕业标签，不提升模型来源资格。本次只做文本审查，不是新PPO/评测/WM训练。全部新文件交root普通Git补档，未创建trial/tag。
