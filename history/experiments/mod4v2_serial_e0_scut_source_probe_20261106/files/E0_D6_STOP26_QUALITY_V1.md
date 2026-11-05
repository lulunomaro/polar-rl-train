# E0 D6旧配方 STOP_SAVE闭合与独立评测（非SCUT完全对齐/非毕业）

- 实际N20000/T24，26新PPO，17Adam各+520，12,480,000优化transitions；没有20更新硬停，因核实参考配方不一致按原STOP_SAVE完整边界退出，未热改源/奖励/物理，无退款/新账/扩窗。
- 完整candidate `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V2_E0_HOUR_WINDOW_FULL_LEARNER_MIGRATION_20261106_023350_1793903630723043100/roles/E0/production/model_mod4v2_migration_complete_U026.pt`，104430359B/SHA `f326418aea63a9a73b06fb887de88426b856c904048aa5fcea3d4c3c994b487b`；原RSL实记iter32029，Adam17642120、LR1e-05，不是推算label。旧母本与此前candidate均保留。
- 实际SDKclose/child和outer wait/原costsettle/资源释放semantic合格；GO到outer 1416.268s仅解释元数据，不冒称有效PPO/整小时或重写账。
- Timing（Python调用wall不等于GPU纯kernel时间）：startup 379.71493220329285s；rollout step调用994.3320806026459s；PPO update调用5.422072887420654s；完整save1.8241655826568604s；loop排save 1004.3546187877655s。未运行满一小时是明确源配方修正停止，不是假装小时已完成。

## 独立原E0 N80/fullDR/1000ctrl/20s/seed20260928

|项目|实际结果|
|---|---:|
|execution资格|合格；实际wait/FINAL-intent/ERROR/释放已核验|
|发生物理终止的env|42/80|
|mimic终止|0|
|bad_orientation终止事件|80|
|timeout事件|38|
|max当前mimic|0.001544081rad|
|替代传动保留原mimic健康门|.01rad未改|
|max当前闭环|0.001585130m|
|vx/vy/yaw MAE|{'body_vx_m_s': 1.4797293877601623, 'body_vy_m_s': 0.04273185477592051, 'yaw_rate_rad_s': 2.3378375056385994}|
|max raw/applied action|2025.723388671875/6.0|
|完整原始二元/profile grader|缺失，null；不编毕业|

D6这一次实际评测未再发生mimic终止，但姿态和跟踪仍不合格；不同候选/不同物理后端单cohort不作配对因果改善。42个独立env物理终止与80次姿态事件不是同一分母。RC0/26更新/mimic0都不等于技能成功。原终止和健康阈值未放宽、无reset拼接。

## 用户原版SCUT要求

已核当前purpose源+选定环境：RM_SCUT_TERM_W0、value_loss2，实际注册V14Flat-v0 termination -200（每control原dt.02后为-4）/value_loss4，另有sigma/deadzone/clamp/命令课程/终止差异；不是改两个数字就称一致。参考链见[完整源报告](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_ORIGINAL_TRAINING_ALIGNMENT_V1.md>)。上游critic78，现完整A0 critic38是明确MOD4兼容接口适配，不以shape或名字相同声称原版观测全等；保已学STD/normalizer/Adam/LR，不切片伪exactresume。

新奖励/命令/课程/终止仅允许逐项上游源公式和原权重、机械/量纲/接口必要映射，缺项明确；不自造reward、混Flat1/2/Rough或把landing充起身。新源码尚待交付/原生证据；其他8专家未启动。正式E0 source/旧Registry不改，不晋升f326，goal664仍active。所有真实失败/诊断/D6修复/训练/评测/配方差异与本报告待下一meaningful feature-only唯一annotated归档；不为Git开模型/raw或重放旧once/物理，main只读。

证据：[train close](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/reports/MOD4V2_E0_HOUR_WINDOW_FULL_LEARNER_MIGRATION_20261106_023350_1793903630723043100/CLOSED_RESULT.json>)/[eval close](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/reports/E0_HOUR_FROZEN_20261106_030530_1793905530766727100/CLOSED_RESULT.json>)/[quality JSON](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_D6_STOP26_QUALITY_V1.json>)/[actual recipe](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_HOUR_CURRENT_RECIPE_SOURCE_READBACK_V1.json>)/[stop receipt](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/E0_HOUR_SCUT_ALIGNMENT_STOP_REQUEST_V1.json>).
