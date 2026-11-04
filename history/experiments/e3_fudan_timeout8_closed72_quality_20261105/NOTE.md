# V13 — timeout8真实closed72；原范围0/74；仍保留1cd

- 当前goal goal-c490e4cc-b28b-440e-bde6-30ee956813f0 rev3 active/armed/max14；目标是质量，不标complete/pause/blocked。
- [完整实测报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_TIMEOUT8_CLOSED72_QUALITY_RESULTS_V1.md>)与[紧凑选择](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_TIMEOUT8_CLOSED72_QUALITY_DECISION_V1.json>)已发布。本窗72真实PPO/两Adam各1440/69,120,000优化转移；累计205/4100/147,942,912，原始4096×64不能冒充N20000。完整保存48个未优化控制。
- 完整新候选SHA 3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e，1204253399B；母版1cd、4096祖先47937、上窗8af4与pi-only93753各自独立。完整learner续接实际CPU一次，环境/DR/history流切断fresh。所有原训练wait/cost/release闭环/errors空，无本任务native训练剩余。
- 原N80实际父1623792/worker1623801/controller1623785，单N80/160/seed20260928/fullDR/原74首episode+6normal。父actual qualification原本为true；collector忘改kind导致仅reader误报false，旧文件保留，新metadata-only reprocess已纠正，不重跑SDK/模型/父资格。结果0/74，normal物理终止0/6。
- MuJoCo相同5姿每条400control/8s全finite。新候选均值高度0.182897、速度0.391495、位移3.020520；母版0.241437/0.038073/0.639393；严格信用双方0/5，但母版确实抬高了身。不能称全DR/硬件/视频同端姿态成绩或native因果退化。
- Decision KEEP_REGISTRY_V12_E3_1CD_NO_3E64_PROMOTION，所有候选保留，H1/其它专家不动。下一步单一质量干预源分析尚未形成部署，不按205步数盲续。
- 原训练observer009、原N80observer895均completed0并已收输出；CPUexport和MuJoCo命令均完成0。旧once/roots不可重放，不为状态/Git开模型或raw。
- 最近已验证archive cce218551eba7d527e4b611a41bc6536c1f75039 / trial-20261104-e3-fudan-n20000-timeout8-real-fullresume-native，tagobj ede4f6dd6cd2a8aea2e087c04a2904f562662733。原record WinError206已在同一record短pathspec续完并归档，不重放record。本次72闭环、reader false+纠正、MuJoCo与质量决定等待下一有意义合并阶段archive；新archive务必使用短directory pathspec适配原record，避免Windows argv过长。feature-only/main只读。


# E3 Fudan / N20000 / 低趴8秒timeout：实际闭环结果

## 质量结论

**训练、完整保存及真实评测已完成；低趴8秒timeout干预本轮仍未显示起身质量改善，保留冻结1cd母版。**

- 原 N80/160/seed20260928：首episode恢复信用 **0/74**。正常6例另列，物理终止 **0/6**；不是正常技能通过率或整专家毕业率。
- 31体MuJoCo相同五合法低姿×8秒、每条400控制，候选与母版完整finite **5/5**，工程联合信用分别 **0/5、0/5**。母版抬高了车身；新候选仍低位后退。
- **Decision：KEEP_REGISTRY_V12_E3_1CD_NO_3E64_PROMOTION**。保留3e64完整候选和失败证据，H1/其它专家/Registryv12不变。总质量目标未完成。

## 真实训练量

| 阶段 | PPO | 策略Adam | encoder Adam | 已优化转移 |
|---|---:|---:|---:|---:|
| 已关闭前序：4096×64＋20000×69 | 133 | 2660 | 2660 | 78,822,912 |
| 本窗新增：20000/T48 | **72** | **1440** | **1440** | **69,120,000** |
| 完整learner累计（混合环境数） | 205 | 4100 | 4100 | 147,942,912 |

本窗native控制 3504、physical callbacks 28032、feedback 7008、真实转移 70,080,000。完整保存的 **48个控制/960,000转移未优化**，不是第73次PPO。累计205步不是205步N20000。

从1.2GB完整8af4源实际续接模型、critic、STD、LR、两套Adam和私有generator，读/hash/CPU decode各一次；当前母版/4096祖先读0。新N20000环境/DR/history/global环境RNG fresh reset，source48 pending未应用，不是PhysX位级resume。

本轮唯一任务干预是低趴recipe>=13专用400个已完成控制步的time_out=True；实际全局episode回读20.0s，其余fall/normal、PPO、奖励、物理与fullDR保持。它是经过实际运行的配置，不是已证明的历史根因修复。

原inner/outer actual wait、成本结清及释放均完成，errors=[]。GO到outer actual wait派生时长约 3606.470秒；只是metadata解释，不新建或重写canonical。

## 名义MuJoCo末态五姿均值

| 指标 | 本次3e64 | 上次8af4（已发布） | 冻结1cd |
|---|---:|---:|---:|
| 高度 m | 0.182897 | 0.182898 | 0.241437 |
| 倾斜 deg | 7.559 | 7.560 | 0.638 |
| 根速度 m/s | 0.391495 | 0.308785 | 0.038073 |
| 起终点平面位移 m | 3.020520 | 2.396440 | 0.639393 |
| 工程联合信用 | 0/5 | 0/5 | 0/5 |

原工程条件含高度≥.23m、姿态/速度/角速度、双轮接触与车身脱地连续.5s。母版速度约.038m/s仍高于.03门，0/5不等于没有抬起。新候选名义高度未提升且后退/速度更大；不据此声称native因果退化或timeout本身单独导致该差异。

这是相同31体/30坐标名义MuJoCo、clean raw35、50Hz策略/100Hz反馈/.0025物理；不是native fullDR或硬件验收，也未覆盖视频整腿同端姿态。没有额外抬升/yaw/动画。旧比较只读取已发布紧凑JSON，没有重开模型或旧raw。

## 评测reader误报已原样保留、仅metadata纠正

原父实际wait后的V3_TIMEOUT8 qualification为true，全部检查通过。collector仍比较V2_N20000 kind，独立一个reader条件误报false；其他11项execution检查为true。[专门erratum](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNTIMEOUT8_FROZEN_COLLECTOR_KIND_ERRATUM_V1.json>)与旧false输出并存。新reader只读取已闭环JSON，将kind识别对齐实际V3，不重跑父qualification、collector、SDK、模型或物理；原0/74/recipe rows丝毫未改。

## 完整证据

- 完整候选 1,204,253,399 bytes，SHA256 `3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e`，留于原production。
- 派生pi-only 341,625 bytes、14张量/82505标量，明确不是训练resume；只下载小artifact，完整源不为状态或Git重开。
- [真实训练闭环](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W6_TIMEOUT8_20261104_231152/CLOSED_RESULT.json>)
- [原N80 outcome、原父资格与reader修正](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNTIMEOUT8_FROZEN_ORIGINAL_SCOPE_READER_V2_RESULT.json>)
- [MuJoCo十条实际案例](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_TIMEOUT8_MUJOCO31_LOWRise_RESULT.json>)
- [完整紧凑结果与保留决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_TIMEOUT8_CLOSED72_QUALITY_DECISION_V1.json>)

## 训练任务中的实测描述与缺口

[本窗任务摘要](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W6_TIMEOUT8_20261104_231152/CLOSED_RESULT.json#L1042-L1079>)记录低位已结束79,976回合，工程credit=0；末快照低位均值高度0.18822m，达到0.23m的仅10/9997。这些是训练任务描述，不代替独立原74成绩；零credit也不等于零reward。有效逐项reward权重、奖励分解及peak增量未出现在指定JSON中，源码可覆盖默认值不能当成本轮effective回读。

## 下一步

停止按205这个累计数字盲续低位漂移候选。下一单一干预假设：从保留1cd仅warm-start actor/critic MLP，重建fresh Fudan encoder/STD/双Adam/LR/计数，保留已验证低位timeout8，其它physics/DR/奖励及Fudan PPO配置不变。新谱系从0计数，不能拼接本谱系Adam、计数或声称full learner resume；先准备一个有限25更新质量pilot，保存后看同口径实测，不以25本身作为通过条件。当前只有最小worker源码在准备，尚未stage/dispatch/训练。现有证据支持优先更换整套learner起点的对照，未证明reward或Adam单独是原因，暂不先改奖励。


## Archive boundary
Actual W6 N20000/T48 closed72/full learner cumulative205; both Adam1440 new, 69120000 optimized transitions, 48 pending controls fully saved but not optimized. Candidate3e64 preserved, no promotion. Actual original N80 parent qualification was already true; local collector stale V2 kind misread V3 as false. Both false output and exact metadata-only kind correction preserved, no physical replay/requalification. Actual five-pose nominal MuJoCo has both0/5 but candidate stays low/drifts3.020520m and mother raises body. Do not equate actor behaviors or claim causal native regression. Training79,976 low episodes credit0 is descriptive, not zero reward. No effective reward decomposition proof; next fresh1cd learner-start hypothesis remains source preparation, not deployed. Preserve host file-observation edit denial corrected by read-before-edit; no native effect. All text and failures snapshot; original recorder validations retained, only git-add invocation shortened to its exact two scoped paths and full staged-set checked to avoid prior Windows argv error. Main untouched. Never rerun this record or physical tasks for synchronization.
