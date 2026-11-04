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
