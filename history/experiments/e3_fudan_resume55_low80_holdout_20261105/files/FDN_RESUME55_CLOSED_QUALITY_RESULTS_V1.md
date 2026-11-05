# E3完整55afa learner有限续接：实际质量

实际新增25 PPO、两Adam各500、24,000,000优化转移；继承base25/500/24m，累计50/1000/48,000,000。新N20000/T48窗1200控制、9600physics、2400feedback；未优化pending0控制。完整候选146,251,569B，SHA `8e27c2f35d5e1ed5ad2f71324e729bdbda9a10e1486b151ca1dd9384d3ecfe32`。原父actual inner/outer wait、成本结清/释放/errors=[]，GO到outer 1203.748s只是metadata解释，不改账。

**PRESERVE_CONTINUED_CANDIDATE_PENDING_HOLDOUT_KEEP_REGISTRY_V12_UNCHANGED**。原E3严格firstepisode信用 **0/74**，6normal物理终止0/6不是normal接受率；原分母、3秒request、连续25控制与门限未改、不拼reset。全部旧候选/H1/其它专家/Registryv12/1cd保持，目标未完成。

| 名义31体五姿指标 | 本续接候选 | 已发布源55afa | 本次实跑母版1cd |
|---|---:|---:|---:|
| 曾连续.5秒联合达标 | 5/5 | 5/5 | 0/5 |
| 最后连续≥0.5秒仍联合达标 | 5/5 | 0/5 | 0/5 |
| 末态高度 m | 0.241736 | 0.241784 | 0.241437 |
| 末态根速 m/s | 0.026676 | 0.032465 | 0.038073 |
| 端点XY位移 m | 0.521314 | 0.596205 | 0.639393 |

十条均8秒/400控制/finite；31机器人body/原限位/名义400N-k2000-d3/50策略100PD/.0025物理、无外力/yaw/动画、clean raw35/history5。候选五姿在结束时的当前连续联合good时长分别 **6.70、6.62、6.60、6.60、6.48秒**；本MuJoCo producer逐步good则stable+1/否则归零，返回时检查stable>=25，因此本次5/5是实际终点连续门限，不是旧native低80的ever+末帧good标签。与native fullDR、硬件、视频整腿同端分列；不把nominal5/5推广为原74或多seed通过。母版抬身与完整联合判据分开。

唯一学习动作是完整55afa再继续≤25：actor/critic/encoder/logSTD/mutable LR/两Adam/privategenerator原样恢复，不重新warm1cd、不重置学习率、不改STD/原奖励/26recipe/8秒timeout/物理/DR。sourceRoot7完整CPU一次read/hash/decode与unknown强immutable；源环境、history/queues/globalenvRNG/pending不应用，新sole reset/noisy35重复5，明确stream cut而非PhysX位级resume。实际fullresume和mutable状态见完整初始化/决定。

新seed20261002/03/04 holdout尚待独立原生确认，状态PENDING、非0分；旧55afa诊断集21/240与7个ever+末帧good不拿来配对因果；无matched native参考，paired差值null。后续需要实际终点当前streak≥25，旧未记录者保持null。

证据：[训练完整闭环](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W14_RESUME55_ADMISSION2_20261105_101210/CLOSED_RESULT.json>) / [原74与actual父资格](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNRESUME55_FROZEN_ORIGINAL_SCOPE_RESULT.json>) / [新名义五姿实测](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_RESUME55_MUJOCO31_LOWRise_RESULT.json>) / [一次pi派生收据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNRESUME55_PI_ONLY_EXPORT_STARTED_ONCE.json>) / [完整质量决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_RESUME55_CLOSED_QUALITY_DECISION_V1.json>)。全部源码/真实成功失败/报告归下一meaningful feature-only annotated trial，main只读；不为Git打开模型/raw或重放旧once。
