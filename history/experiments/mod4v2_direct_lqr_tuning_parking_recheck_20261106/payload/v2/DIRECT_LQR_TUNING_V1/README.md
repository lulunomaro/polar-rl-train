# 2026-11-06 14:18后：直接LQR实调与独立停车复核

这次实际改控制反馈、重新求DARE并跑车，不是继续加观测旁路。共**6个全CAD DR闭环例+2个长平面速度例**；未改P0机构/气弹簧/电机限值/PD-D4-DC链、未用真值入控制、未复跑旧case。旧FF失败、E1及全部原验收门保留。

## 改了哪些实际参数

[训练前协议](<PROTOCOL.json>)固定原版和两个反馈方案，新seed530300共用相同episode参数和初始姿态；实际K差已核实（前两候选最大元素差16.0651），不是只改标签。

| 方案 | 真正改动 | 速度RMSE m/s | 停车RMS m/s | pitch RMS rad | 固定工程分，低更好 |
|---|---|---:|---:|---:|---:|
| 原版 | 既有v2 K/P25配置 |.04217|.05377|.02094|2.80886|
| rate/velocity | Qpitchrate×4、Qvelocity×2.25，重新求K |.04095|.05190|.02805|2.96853|
| 上述+柔顺差动 | 再将差动Kp120→90、Kd4→6 |.04361|.05225|.02847|3.07494|
| 停车优先R4 | 保持原Q/腿120–4，仅R×4重新求K |.04455|**.04581**|.02110|**2.67693**|

前两个方案更差，已排除，不隐藏或推广。[最初训练比较](<TRAIN_SELECTION001/RESULT.json>)保留。由于加大角速度反馈使pitch明显变差，才在实测后预声明[最后一个候选](<THIRD_GAIN_CANDIDATE/PROTOCOL.json>)：提高输入代价R降低反馈带宽，不再加反馈；总共3个改变参数的候选，不再搜索。

**R4训练综合改善4.697%，仍未达到原先固定5%选优线**，原结论不改，也未冒称正式赢家。但原停车门从.05377>.05变成.04581<.05，所以另立[独立停车诊断复核](<STOP_RECHECK/PROTOCOL.json>)，只检验这个具体改善是否跨抽样复现，不改变原分数/选优线、不是为了凑过而换系数。

## 独立新seed530301，R4固定不再改

| 指标 | 原版 | R4停车优先 |
|---|---:|---:|
| 停车RMS m/s |.06533393|**.05478596**|
| 速度RMSE m/s |**.05961540**|.06140074|
| pitch RMS rad |.02383942|**.02179238**|
| roll RMS rad |.01274937|**.01102632**|
| 固定工程分 |2.98760|**2.69147**|
| whole低支持评分点 |24|17|
| 原严格case pass |false|false|
| 原100Hz足迹scope |true|true|

同episode DR/初始姿态一致，控制输入仅R设置不同。停车改善**16.145%**，与训练抽样的**14.811%**同方向；独立综合分低9.912%。代价是追速略差，停车仍高于.05原门，whole点也仍在。故保存为**停车优先试验配置**，不是统一最优/正式默认/鲁棒全过。没有扩带或改原接触阈值。

每例12s/1200控制/24000物理、各fresh模型/DR一次。六例累计7200控制/144000物理，仅2份独立DR参数设置；三候选是在训练设置上的受控参数实验，不充独立样本。[一次最终小结果汇总](<FINAL_SUMMARY001/RESULT.json>)、[对照CSV](<FINAL_SUMMARY001/comparison.csv>)只读小result/meta，未读raw或重放。

## 2m/s、刹停、反向的实际长平面工程基准

为明确“车到底会怎样跑”，固定原版/R4各跑一条28s程序：0–2站，2–10命令+2m/s，10–15刹停，15–23命令−2m/s，23–28刹停。完整P0机构/质量/闭链/碰撞体、.5ms Newton100/100Hz、原观测与执行链保留。

**这里是明确标注的额外长平面fixture，不是最新CAD全场，不作为T02或DR鲁棒验收。** source模型构建器原flat分支的用途在本benchmark显式记录，未伪装为CAD地图；名义状态，无人为扶正/中途重置。

| 实测 | 原版 | R4 |
|---|---:|---:|
| 正向7–10s均速 m/s |2.05033|2.06345|
| 反向20–23s均速 m/s |−2.05044|−2.06365|
| 第一停车14–15s RMS m/s |.01227094|.01239303|
| 第二停车27–28s RMS m/s |.01202404|.01212716|
| 全程pitch峰 rad |.02221586|.02375516|
| 全程完成 |true|true|

各2800控制/56000物理，完整28s没有fall/中途重置。原版在此名义速度基准更准，所以R4并非全场景替代品。两个fixture例不充全CAD成绩。[原版结果](<FLAT_SPEED_BENCH/flat_baseline_530302_001/result.json>)、[R4结果](<FLAT_SPEED_BENCH/flat_effort4_530302_001/result.json>)和37qpos的100Hz CSV保存；未为归档重读/hash，未汇成伪硬件/连续扫掠资格。

## 可复用代码，而非口头参数

- [停车优先recipe及实际K参考](<PARKING_TRIAL_RECIPE.json>)：只有`effort_weight=4.0`；代码仍用新v2 Ad/Bd/Q/R求K，不套旧K。
- [可选控制器工厂](<../controller_parking_trial_v1.py>)：`build_controller(gain,config,geometry=public_geometry,profile='parking_R4')`；`profile='original'`保留原版。它不导入仿真真值/DR参数，不覆盖共享默认runtime。
- [实际运行入口](<run_tuning_case.py>)、[独立停车入口](<STOP_RECHECK/run_tuning_case.py>)和[完整速度程序](<run_flat_speed_benchmark.py>)均保留。已消费case不重跑；新实验须新plain ID并先声明协议。

示例（本目录的上一级R2为workdir，必须使用**新case ID**）：
```powershell
$env:OPENBLAS_NUM_THREADS='1'; $env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B DIRECT_LQR_TUNING_V1/run_flat_speed_benchmark.py --variant effort4 --case YOUR_NEW_CASE_ID
```

本轮无新代理/安装/新框架/旧QA/刷写/真实电机命令。MPC未在本轮改动，C/C++/硬件闭环资格仍未完成。数据没有证明36项或95%可靠性；只是终于做了有结果的实际LQR参数对照。14:19读Goal为revision30 paused/disarmed；恢复接口提示仅用户可恢复，当前由直接人类消息执行，未假称已恢复自动goal。
