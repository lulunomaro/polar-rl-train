# SPIN_STOP_CAUSAL_V1 — 四条 TRAIN 的只读 stop 窗口分析

## 结论与边界
- **真实漂移与观测偏差同时存在；本小样本不识别唯一因果。** 不改 R26 总体 0/8、R27 both 总体 2/8（总体数由父任务给定，未重算）。所选四个小 result 的 `transition_proposed_pass` 均为 false。
- 只读 TRAIN seed201/202：R26 baseline 与 R27 both 各两条，四条均2600行100Hz；没有打开其他 TRAIN 或 H1/H2/H4/H5 heldout/raw，没有新physics、编译、旧QA、gain拟合或控制器实现；未接触父R52。
- [方法](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPIN_STOP_CAUSAL_V1/METHOD.json>)、[四路径/32小输入SHA锁](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPIN_STOP_CAUSAL_V1/SOURCE_LOCK.json>)先于窗口脚本执行；46项所用源码与实际case manifest一致，root runner与batch副本相同；两seed的baseline/both DR receipts逐字段相同。
- [精简结果](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPIN_STOP_CAUSAL_V1/SUMMARY.json>) / [有界明细及列schema](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPIN_STOP_CAUSAL_V1/WINDOWS.json>) / [receipt](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPIN_STOP_CAUSAL_V1/RECEIPT.json>)。每case仅保留816个窗口行的统计/少量快照，没有导出新raw。

## 时间语义：先配时，再谈偏差
- 实际[baseline runner:24–44](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/run_transition_case_v3.py#L24-L44>)与[both runner:24–44](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/run_spin_stop_v1.py#L24-L44>)：`estimate_time=t`先取sensor/算request；`ground_truth_before`在apply前；`time`和`ground_truth`在既有20子步后，约`t+0.01s`。
- 本案实际[V4grade:1–11](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/physics_bridge_v4_grade.py#L1-L11>)用**当前freejoint qpos/qvel**算root姿态/速度，不是旧body-xmat缓存真值。collision/site cache另标，通常落后0.0005s；未用它推2k逐点接触或电功率。
- [estimator:126–133](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/sensor_core_v4.py#L126-L133>)仅将state前7项age-view：pitch对应控制时刻；vx、Euler heading-rate仍持source-epoch值。窗口sensor age均约10ms；gyro/rates另有20采样boxcar孔径，source-end标签不是瞬时测量。
- `e_v(source)`把估计vx与source timestamp匹配的旧`true_before`比较；四条扫描共10400行source配对缺失0。`e_pitch(now)`比较age-view pitch与当前`true_before`。heading-rate统一用body gyro+真实RPY换算Euler rate，不把gyro_z直接当yawrate。
- 实际正转stop在`t=10.000s`切零；负转stop在`t=22.010s`切零（浮点累计调度，非理想22.000s）。对应300/399个stop控制样本，持续3.000/3.990s。
- 下表是**每stop末1s、100样本、true_before**的均值，XY为整个实际stop的真root端点位移；不是旧grader的最后2s/true_after统计。旧[grader:8–33](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/transition_grader_v1.py#L8-L33>)仍按nominal phase与`row.time-.01`评分，原分数保持不变。

## 实际窗口数值
`v`单位m/s，pitch误差rad，yawrate单位rad/s；ΔXY为m，均为描述统计。

| case | stop前旋向 | 真ΔXY | 真v均值 | 估v均值 | e_v(source) | e_pitch(now) | 真yawrate均值 |
|---|---:|---:|---:|---:|---:|---:|---:|
| R26/201 | +4π | 0.2942 | 0.0151 | 0.0369 | +0.0212 | -0.00024 | +0.0832 |
| R27 both/201 | +4π | 0.2526 | -0.0266 | -0.0006 | +0.0239 | +0.00244 | +0.1557 |
| R26/202 | +4π | 0.2603 | 0.1338 | 0.1027 | -0.0298 | -0.02828 | +0.1517 |
| R27 both/202 | +4π | 0.2508 | 0.1151 | 0.0863 | -0.0281 | -0.02563 | +0.1614 |
| R26/201 | -4π | 0.1635 | 0.0397 | 0.0422 | +0.0026 | -0.01504 | -0.1203 |
| R27 both/201 | -4π | 0.1357 | -0.0089 | 0.0011 | +0.0098 | -0.00871 | -0.0272 |
| R26/202 | -4π | 1.1861 | 0.5467 | 0.4426 | -0.1037 | -0.08407 | -0.0495 |
| R27 both/202 | -4π | 0.5892 | 0.0701 | -0.0162 | -0.0879 | -0.06955 | -0.0599 |

- **202负转后的漂移是真的。** 真root的1.1861/0.5892m位移不由估计器积分生成；both改善此样本，但仍保留source-aligned速度偏差及约-3.98°pitch误差，不能把全部差异解释为10ms配时。
- both/202末控制样本：真vx=+0.02579、估vx=-0.07004；真pitch=+0.01508、估pitch=-0.05508rad。表中均值与末样本不同，未以单点代替窗口。
- 201并非“both全面成功”：其原first_stop连续合格段从0.91s变0.48s，原stop完成项变null；最后1s的post真值yaw阈值越界样本9→12。原final_stop合格段则0.94→1.92s。四个原transition结果仍false。
- 202负转末1s的post真值速度阈值越界样本100→10，yaw越界0→2；它说明描述窗口改善，不替代原grader仍未通过的final_stop项。

## 参考、I项与状态切换
- 所有八个stop的`shaped_w`都在实际零request后**2.09s**才到零；这与既定yaw加速度6rad/s²的参考斜坡一致，不等于检测到2.09s的driver迟滞。[shaper调用与参数](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/spin_base_v1.py#L14-L23>)。
- [centering:16–21](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/spin_center_controller_v1.py#L16-L21>)按operator `abs(yaw_rate)>4`启用：所有stop前0.5s为50/50 active；每case两stop合计0/699 active（全组0/2796），common修正全零。日志inactive时`error_xy=0`是代码置零，**不是位置误差测为零**；这是两方案共有机制，不单独解释方案差异。
- both外层gain1.5首次出现于stop后1.80–1.83s；mix首次正值1.89–1.92s，满mix2.08–2.11s。gain在门限附近有短暂0/1.5切换；它只是外层系数，实际gravity innovation/分项gate和校正向量未独立记录，不等于有效校正量必为非零。
- **both从startup已不同**：0s外层gain1.5；0.09s mix开始、0.28s满mix；新旋转命令到来又blend-out。两方案虽同seed/DR，stop前轨迹历史也不同，不是同一初始状态下只改stop。
- [capture:20–42](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/spin_stop_capture_v1.py#L20-L42>)是10个低速ticks后把**估计distance**捕到P25 ref0，并复制shaper、yaw I、old_shaped_w、previous，再每tick增减mix0.05；不是root pose reset。Spin分支始终运行，mix>0时capture分支也运行，并非瞬时单分支切换。
- both/201在stop+2s与末样本的capture ref0分别保持-0.231539、-0.509979；both/202分别保持+0.316472、+0.703131。202负转末估计distance=0.910593，仍不同于ref0；这些都是内部标量，非绝对世界位置测量。
- [PI:32–35](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/spin_base_v1.py#L32-L35>)仅在desired未超自身wheel-common剩余峰值预算时提交I。**实际I值、是否抗饱和冻结、capture enabled/low_ticks标量均未记录**；只证实源码复制I而非清零，不声称已观测到windup，也不声称它已被排除。

## requested、可见反馈与driver-limit证据
- 轮顺序取row6的2/5；`raw_requested_tau`是控制请求，`actual_tau`是最后一个既有0.5ms子步写入的`d.ctrl`，不是独立实测轮扭矩。`wheel_rate2`是延迟boxcar反馈，不是该末子步的瞬时速度。
- [实际motor链:19–25](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/physics_bridge_v3.py#L19-L25>)仍经过inversePD target、D4队列、当前状态PD、两次signed DC及motor gain；轮target另限±60rad/s。[signed四象限clip](<F:/RMPOLAR-RL/traditional_control_20261101/control_core.py#L127-L130>)用当前真实joint速度。两seed记录的motor gains均1，不能用D0增益解释本组gap。
- 八个stop里request轮峰值最高4.6620Nm、可见末子步ctrl峰值最高3.3271Nm；两者命中±5.7759098绝对峰值的次数均0。request到末子步ctrl的逐轮RMS差为0.539–0.810Nm，但含时间/PD/队列差异，**不是单独的饱和证据**。
- 绝对峰值未命中不排除速度相关DC边界或中间子步限幅；缺preclip raw、applied/processed target、clip mask和同瞬时dq，具体发生时刻/次数/因果贡献为unknown。小result里的`command_envelope_clips=0`也不是driver clip计数。
- 不以100Hz请求乘延迟轮速推瞬时电功率；电流、电压、铜耗、回充及温度未知。未用接触缓存升级触地、无滑移或独立支撑许可。

## 最多两个下一TRAIN单因素假说（仅提出，未实施）
1. **低速观测偏差是可分离贡献。** 保持capture策略、gain数值及stop前历史方案一致，仅对预注册stop窗的低速accel校正开/关作paired TRAIN；同步记录有效innovation/gate。若source-aligned pitch/vx偏差先改变且真位移随后改变，增加支持；反例也保留。
2. **capture/积分历史与common-yaw预算有独立贡献。** 固定accel方案和stop前控制历史，仅capture开/关；补录两分支I、参考、混合和各2k target/preclip/clip阶段。检验真vx改善是否伴随yaw hold损失；不调gain、门限、cap，也不预判windup为主因。

## 封存与失败保留
- 首次新提取只因输出体积111180B超过预锁98304B而失败，未写窗口结果；[原脚本](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPIN_STOP_CAUSAL_V1/revisions/extract_attempt_01/extract_windows.py>)和[原log](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/SPIN_STOP_CAUSAL_V1/revisions/extract_attempt_01/extract_01.log>)保留。第二次仅无损去重JSON键名，统计/窗口/阈值/96KiB cap不变，输出92991B。
- 两次新扫描合计20800行、始终只有四个unique trace；随后只读新明细。raw SHA仅转录producer记录，未重算raw归档hash，实际size/mtime稳定；32小输入末次SHA另核。无新成功率、控制候选、许可、板级或发送链资格。
