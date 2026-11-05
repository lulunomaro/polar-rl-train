# 冻结8e27：三seed原生fullDR低姿holdout

**首episode连续0.5秒信用 22/240（9.17%）；终点当前连续≥0.5秒 0/240（0.00%）；曾获信用且末帧good 12/240。**

| Seed | 首episode连续25信用 | 严格终点当前连续25 | 曾信用＋末帧good | 首episode物理终止 |
|---|---:|---:|---:|---:|
| 20261002 | 9/80 | 0/80 | 3/80 | 0/80 |
| 20261003 | 7/80 | 0/80 | 5/80 | 0/80 |
| 20261004 | 6/80 | 0/80 | 4/80 | 0/80 |

## 五个原合法姿态，每姿跨seed分母48

| Pose | 首episode连续信用 | 严格终点连续25 | 曾信用＋末帧good |
|---|---:|---:|---:|
| 0 | 8/48 | 0/48 | 3/48 |
| 1 | 7/48 | 0/48 | 6/48 |
| 2 | 3/48 | 0/48 | 2/48 |
| 3 | 1/48 | 0/48 | 0/48 |
| 4 | 3/48 | 0/48 | 1/48 |

## 语义与边界

Strict terminal = first_episode_ever_credit AND first_episode_physically_live_at400 AND terminal_current_good_streak_controls>=25。current_streak在第400控制同原pre-reset hook保存，逐步原good更新，不拼reset。旧兼容字段ever+末帧good单列，不当严格终点。原55afa历史21/240使用不同三个seed，旧严格终点未记录仍null；两批不是配对因果。

末帧仍第一episode的失败分量：`{"height_ok": 0, "upright_ok": 0, "speed_ok": 113, "angular_ok": 15, "wheels_ok": 0, "chassis_ok": 0, "joint_good": 121}`（可重叠）。根速mean=0.03188907208483822、median=0.029258464463055134m/s；历史最长good中位14.0控制，当前末段good中位0.0控制。物理未终止不等于联合连续通过；不从这些观测强推某一DR、reward或optimizer的因果根。

三独立constructor cfg.seed=20261002/03/04；每80=五legalpose各16、400控制8秒、原sole fresh reset/fullD0D7/2c-bae/31体/50policy100feedback/.0025/TGS32,4/400N-k2000-d3/closure.01m per-env reset/mimic.01不变。每case整份Root8 N20000源一次物理read/hash/CPUdecode/whole未知根CPU缓存，只有14pi/82505scalar frozen mean GPU；组实际3次，无learner/optimizer/newPPO或source DR/history投影。

原实际privateGPU_EX/finite_EX/ownerNone+reserve/fresh资源/1800门控、SDKclose/actual child+outer wait及cleanup释放均通过。母版native参考未运行，paired差值null，不以同seed或名义MuJoCo5/5声称native因果。原E3上轮0/74单列未重测，不并入240；H1/其它专家/Registryv12/1cd保持，保留完整8e27，不作整专家毕业或硬件/视频整腿同端宣称。

[完整分析](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_RESUME55_LOW80_HOLDOUT_ANALYSIS_V1.json>) / [实际scope与资格](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_SCOPE_RESULT.json>) / [原闭环](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_CLOSED_RESULT.json>)。本阶段全部源码、旧静态定位失败与最小修复、实际原生结果/报告待meaningful feature-only唯一annotated trial及远端核验；main只读，不为Git重开模型/raw/旧物理/once。Goal active，未完成。
