# R62实际关闭：名义2/2，固定TRAIN1/4，未提升为保底策略

## 当前目标与边界

沿用goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，最近实读revision9/round6/max12 active/armed；不重建/resume/complete/blocked。cwd F:/RMPOLAR-RL，Python314 -B/BLASOMP MKL1/最多4物理CPU，当前已无在跑父PHY。无GPU/SSH/PPO/canonical/专家index/新agents/Mnemon写。现catalog只有Office/ACL，无robotics匹配，文件/CLI/read-before-edit/glob/grep。

完整scope/模型/旧H1/H2/H4/H5见[旧接续](<CONTINUATION_R60.md>)、[V2执行前接续](<CONTINUATION_R62_V2_PREEXEC.md>)。旧H5仍40/64，270mm/完整RM/自主接触/实机BSP/HIL/WCET未毕业。Stage1V1 immutable。新AIR002及全部R62/启动器修订/此note都post-PH7、PH8pending；PH7真实223577994e0f750e0ae062ce9ffee204273c90a2已归档，不重复record/push。

## 实际执行与来源

候选为sealed [AIRref002 core](<MINIHOP_AIR_PITCH_REF_V1/attempt002/controller.py>) 844e9655...，[entry](<MINIHOP_AIR_PITCH_REF_V1/attempt002/run_manual_air_pitch_ref_v1.py>) c51aab52...。默认feature/operator false；本实验显式true。h=.25estimatedpitch+.04estimatedpitchrate，clip[-.10,+.03]、rate1；flight临时q_start+h，firstcapture anchor连续，原push/observer/driver/limits/gates不改。不能把零步/名义成功冒鲁棒稳定或硬件资格。

[V2名义review](<R62_AIRREF_ADMISSION_V2/PRE_EXEC_REVIEW.json>) SHA f4f240632d90a7fe67443a5294d34b95b0469555063075b9f837576217301fbb 已由父read JSON及MD，ready仅名义。父新[名义approval](<R62_AIRREF_ADMISSION_V2/PARENT_LAUNCH_APPROVAL.json>)绑定protocol76200c85...、sourceindex29d5374e...、review、V4 launcher2c2e0022...。旧V1review/HOLD/更正历史保留，旧V3未运行。

父job pwsh-d66aaaf988f94d50：真实V4按原flat通过后匹配RM，已COLLECT exit0，2例各800controls/16000steps。名义flat/RM均原gate PASS；RM guide/hard0、mainrear firstflight2.38s、endstable3.91s、mainmesh air .182557m。

独立[pairedV2 review](<R62_AIRREF_PAIRED_LAUNCH_REVIEW_V2.json>) SHAd9dd3e1969289fbb4f025d28a8cb7e0f08f5c5320525f864873f7cb453a84966，父read完整MD与关键JSON；ready条件性不代许可。父调用纯metadata validator实际核两名义result.config==D2锁定enabled profile、actual SOURCE_MANIFEST候选core/entrySHA和原pass/mainfirstflight，再写[单独paired approval](<R62_PAIRED_PARENT_APPROVAL_V2.json>)，绑定双result/双manifest、script5727c24f...、sourceindex/review。

父job pwsh-fc922ff4ff8c4f9b：固定4602/4605/4606/4610、2workers、oldR60 configs只case/cohort+featuretrue变动；已COLLECT exit0。4例各800/16000，全部complete、0software_error/0unstarted。总实际新消耗4800controls/96000steps；不是16fixture的synthetic计数。两个batch组配置/源冻结后无内部调参、换seed或baseline重跑。

## 真实逐例结论（负结果保留）

父[分析脚本](<record_r62_closed_facts_v1.py>)仅读取小result/batch/baseline metadata，0raw/mesh重hash/模型/PHY，重算原gate一致。已生成并read[事实报告](<reports/R62_AIRREF_NOMINAL_AND_PAIRED_FACTS.md>)/[JSON](<reports/R62_AIRREF_NOMINAL_AND_PAIRED_FACTS.json>)。

| case | 原gate | guide/hard ticks | mainrear firstflight | endstable | 失败项 |
|---|---|---:|---:|---:|---|
| nominal flat | PASS | 0/0 | 不适用 | 4.55s | 无 |
| nominal RM6cm | PASS | 0/0 | 2.3800s | 3.91s | 无 |
| DR4602 | PASS | 0/0 | 2.3950s | 4.65s | 无 |
| DR4605 | FAIL | 4/0 | 2.4390s | 4.67s | guide仍4ticks |
| DR4606 | FAIL | 0/2 | 2.2110s | 4.31s | hard仍2ticks，maxpitch .813733rad |
| DR4610 | FAIL | 0/0 | 2.4945s | 3.99s | 保守最终full-collision behind-bar界未通过 |

四例原local **1/4**，相同seed baseline **2/4**；mainrear firstflight4/4，联合1/4，无新增local改善、4610退化。DR receipts逐值全相同，但不是所有2k信号位相同证明。4606旧hard5/guide5→hard2/guide0虽有部分接触减少，仍原FAIL；4605guide4不舍入。4610无guide/hard但conservative bbox false不能直接推成实际bar接触/真实mesh重叠，待小结果分析。

该4例看过旧R60结局后挑选（2旧pass+2机制fail），不是独立holdout或可靠率估计。名义pass不能覆盖DR回归，002仍DEFAULT-OFF实验，不替换最终保底，不放阈值或为通过再换seed。R60 fresh16仍10/16，H1/H2/H4/H5全部旧数不变。

## 下一工作：只读因果，不启动R63或第三h变体

仍只复用两个旧agents：

1. C abf2088f-af10-479a-9108-202785031447：新R62_AIRREF_RESPONSE_CAUSAL_V1，仅读旧R60/新R62 4606和4610共4控制trace各800行+仅新4606 physics一次。聚焦actual flight hGoal/h/ref、requested腿轮τ/可观察限幅、capture anchor，以及新4606首hard实际身份/面/阶段。父“早期请求40Nm可能遮蔽h”只是待证假说；无同stage真实τ则unknown，requested触限不冒DC/硬件饱和。可从实际源/字段用预声明1e−9重建flight请求诊断，禁止执行旧controller或新gain/PHY/QA；fullDR2kq仍unknown、不用名义递推。主文<=100行。
2. model e4e6c8f2-f08d-4df1-9150-945c804e8c2a：新R62_FINAL_SCOPE_REGRESSION_V1，SMALL RESULT ONLY，旧R60/newR62 4610小result+必要bounds源，比较final minX/firstbar back/root及姿态，解释保守界回归；0raw/mesh重建/模型/PHY/Git/H5，不放scope gate、不选新目标/gain。主文<=70行。

两任务当前pending，不填未来结论；先收实测后决定结构策略，R63代码/PHY未存在。其它idle Mnemon agents不动。父两个PHY job已完整收集；16新增软件fixture/元数据准备等foreground也已settled。所有新资料PH8pending，下一归档应有新cutoff而非重复PH7。
