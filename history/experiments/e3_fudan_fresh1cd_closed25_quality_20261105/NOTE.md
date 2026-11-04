# V17 — fresh1cd实际closed25，原0/74，保留母版

- 当前E3 goal-c490e4cc-b28b-440e-bde6-30ee956813f0 revision3 active/armed/max14，未完成，不pause/blocked/complete。H1/其它专家/Registryv12不变。[实测报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_FRESH1CD_CLOSED25_QUALITY_RESULTS_V1.md>)与[紧凑结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_FRESH1CD_CLOSED25_QUALITY_DECISION_V1.json>)已发布。
- W7零GO的原1800s超时及W8新namespace450stage/真实释放watch均保留；W8 root为/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_W8_ADMISSION2_20261105_013118_1793813478778262400，controller1626919/parent1626926/worker1627057，GO1793814178.5811079。实际fresh25/两Adam500/24m优化转移，零继承，不拼旧205。1200native控制/9600physics/2400feedback，未优化pending0。
- 全候选146165047B/SHA246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2，完整learner/两Adam/RNG/typed环境保存；warm1cd一实际读取，原learner/DR/history不应用，full_learner_resumeFalse描述起点而非不完整保存。所有inner/outer wait/cost/release/errors[]闭环，observer91f已completed0/output collected。
- 原N80 parent1627966/controller1627959，单80/160/seed20260928/原74+6/fullDR/一reset/0优化。实际父kindV4_FRESH1CD合格、collector全部execution检查true，无reader重跑；原0/74、normal物理0/6、请求物理27/74。observer705已completed0/output collected。
- CPUexportV1错误为删除的LEARNER_SOURCE_PATH名称，全部源IO0/ownsave0，旧源与error保留。新V2同closed前门+实际EXCLUDED前读排除，输入246ac第一次实际CPU一次解码；14pi派生338809B/SHA75ebfabe72d455ba7aba3f686f51f1cebbe6ac7b3e07c3a3530e490c1b773030，本地F:\RMPOLAR-RL\e3_fudan_recovery_alignment_20261104\FDNFRESH1CD_PI_ONLY_EXPORT_V2_20261105_021424_1793816064574366300\pi_export.pt，NOTfullresume。MuJoCo十条completefinite已完成0；双方0/5，但分项fresh高度0.198817/速度0.684080/XY5.325706，母版0.241437/0.038073/0.639393。没有native因果退化/全DR/硬件/视频同端姿态声明。
- 决策KEEP_REGISTRY_V12_E3_1CD_NO_246AC_PROMOTION，完整候选与母版保留。当前无本任务native/observer/background工作剩余，下一干预未部署；不得重跑旧一次入口/模型/raw为状态/Git。
- 最近核验Git7ee034128525a83dc3a33284bfe219eece934e26/trial-20261105-e3-fudan-fresh1cd25-original-admission（7ee为W7提交点时，不包含后续真实闭环）。本W7超时/释放/W8闭环/首次10proof/原N80/零IO错误+V2导出/MuJoCo/本报告等待一次有意义合并archive。原record_experiment全部校验＋短2pathspec/full staged-set核对；feature+唯一annotated tag，main只读，模型/raw/JSONL/geometry先跳再stat/read/hash。


# E3 fresh1cd Fudan / N20000×25：真实闭环质量结果

## 结论

**25次真实PPO已完整收口，独立原N80执行合格但起身信用仍为0/74；暂保留1cd，不晋升246ac候选。**

- 原74首episode请求与6个normal分开；normal物理终止0/6，不是normal技能通过率。请求组物理终止27/74是描述，不据不同run推因果。
- 名义31体MuJoCo，同五合法低姿×8秒，每条400控制：两策略均完整finite5/5，严格工程联合信用均0/5。分项实测见下，0/5不等于车身没有抬起。
- **KEEP_REGISTRY_V12_E3_1CD_NO_246AC_PROMOTION**。全候选保留，H1/其它专家/Registryv12与母版不变；总质量目标未完成。

## 真实训练与保存

| 分支 | PPO | 策略Adam | encoder Adam | 优化转移 |
|---|---:|---:|---:|---:|
| 新fresh1cd分支（N20000/T48） | **25** | **500** | **500** | **24,000,000** |
| 继承旧分支/旧迭代 | **0** | **0** | **0** | **0** |

仅1cd actor8＋critic8 MLP warm，encoder随机fresh、新latent列0、STD.5/两Adam/LR/private generator/计数fresh。真实母版14715029B读/hash/CPU decode各1，未套旧Adam/环境DR/history；43090只是source_iter，不累计旧205。新环境N20000/一fresh reset/noisy35×5；同一低8s/400time_out、PPO/core/physics/fullDR，不是PhysX位级resume。

Native 1200控制、9600physics、2400feedback、24,000,000真实转移；完整保存的未优化pending为0控制/0转移。完整候选146,165,047B/SHA `246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2`。原inner/outer实际wait、结清/释放/errors=[]，GO至outer actual wait约1570.942秒，只是metadata解释，不另建/改写账本。

## 名义五姿末态均值

| 指标 | fresh246ac | 旧3e64（已发布） | 冻结1cd（本次实跑） |
|---|---:|---:|---:|
| 高度 m | 0.198817 | 0.182897 | 0.241437 |
| 倾斜 deg | 10.886 | 7.559 | 0.638 |
| 根速度 m/s | 0.684080 | 0.391495 | 0.038073 |
| 起终点平面位移 m | 5.325706 | 3.020520 | 0.639393 |
| 工程联合信用 | 0/5 | 0/5 | 0/5 |

工程条件含h≥.23、姿态/速度/角速度/双轮接触/车身脱地连续.5s；母版确实升高车身，但约.038m/s仍超过.03速度门。实测分项和严格信用分列，不把执行合格或0/5当作同样行为。相同31体/30坐标/原限位，50Hz策略/100Hz反馈/.0025物理、400N-k2000-d3、clean raw35/frame-major5，无外力/yaw/动画；不是native fullDR/硬件或视频整腿同端姿态验收。

## 错误与IO边界

W7原1800s preGO自然超时，0GO/SDK/PT/PPO，全部实际wait/结清/释放后新W8 admission才真正开训；不是重放旧失败root，也不将它记为技能失败。

本次原N80实际V4_FRESH1CD父资格与collector完整kind一致，全部execution检查true；无旧V3那种reader纠正。第一次CPU pi export仍导入已删除的LEARNER_SOURCE_PATH，ImportError发生在输入stat/read/hash/decode和ownsave前，全部IO0。旧源、marker、error保留；新V2仅改为实际EXCLUDED常量及读取前规范字符串路径/SHA排除，outer/remote AST＋静态import-name合同通过，未改14pi数学或重开旧输入。V2第一次真正导出时输入完整候选读/hash/CPU decode各1，仅下载338,809B派生14pi/82505标量，不是完整训练resume。

## 训练末态快照解释

本次1200控制正好是低位400控制timeout的第3个整数边界，completed_training_low_episodes为29,991＝9,997×3。末态low_height_mean=.1781000、height≥.23计数0可能反映刚reset后的统一初始姿态，不能把这个时点当作整段从未抬升或峰值高度证据。完整低位信用0/29,991也不等于奖励为0。独立原74与MuJoCo的失败结果单独成立，不靠该训练快照推因果。

## 完整证据与下一步

- [训练完整终态](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W8_FRESH1CD_ADMISSION2_20261105_014143/CLOSED_RESULT.json>) / [真实原门控GO](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W8_FRESH1CD_ADMISSION2_20261105_014143/FIRST_ACTUAL_ADMISSION.json>)。
- [原N80原始recipe与父资格](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNFRESH1CD_FROZEN_ORIGINAL_SCOPE_RESULT.json>) / [同五姿十条真实MuJoCo案例](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_FRESH1CD_MUJOCO31_LOWRise_RESULT.json>)。
- [零输入import错误与新V2纠正](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_FRESH1CD_EXPORT_V1_ZERO_INPUT_IMPORT_ERRATUM.json>) / [紧凑完整质量与保留决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_FRESH1CD_CLOSED25_QUALITY_DECISION_V1.json>)。

先用本次实际task_summary与独立结果限定下一项干预，不按25/205数字盲续，不更改原分母、判据、物理或DR。训练描述不是独立接受率，缺失的effective reward分解不当作已证明根因；下一实训需要独立有限目的和原资源门控。


## Archive boundary
Actual fresh1cd new25/dualAdam500/24m, base0 not old205 or43090, full146165047B candidate246ac, native1200/9600/2400 and0pending. W7 original1800 zero-GO timeout/allactualwait preserved, read-only release and W8 new450stage/GO/native10 proof then actual close included. Whole original N80 actual parent V4_FRESH1CD + matching collector already qualified,0/74/normal physical0of6, no reader requalification. Nominal MuJoCo10 finite cases: both0of5 but height/drift differentiated, no native causal regression or hardware/fullDR claim. Old CPUexport import failed before any model/ownsave IO; old error/source retained, newV2 only actualEXCLUDED imports/pre-read normalized path+SHA, same14pi math/CPU whole cache/solephysical read,338809B derived only. End1200 is400-timeout boundary, low_height.1781 is not whole-episode peak evidence; no unsupported reward-root-cause claim. All candidate/mother preserved, no promotion or goal completion. All current text/failures archived, original recorder validation/redaction/hash unchanged, only2 exact scoped git-add paths + staged-set equality to avoid Windows argv. No model/raw/JSONL/geometry stat/read/hash for synchronization, feature only/main readonly. Never rerun this record or physical purposes.
