# 合格闭环对照：当前候选不提升，保持母本

## 主结果

以下为两个 **新的实际执行用途**，并非把先前 V1 close 错误改成 pass。原教师参考和候选复测均完成原 N80 控制循环、冻结检查、原关闭语义、实际 wait 与资源释放；原教师还保留外部实际 `Popen.wait()` 回执。

| 原技能条件 | 冻结原教师参考 | 后训练候选 | 处理 |
|---|---:|---:|---|
| E3 requested recipe0..11，首次 episode recovery credit | **0 / 74** | **0 / 74** | 未获得恢复收益证据，不提升候选 |
| W35 moving，自然完整/同UID/非终止区间 | **19 / 63 = 30.16%** | **10 / 69 = 14.49%** | 维持原 scoped-best 母本 |
| W35 standing，同一原条件 | **26 / 26 = 100%** | **16 / 17 = 94.12%** | 单列，不混作运动成绩 |

**其他未完整区间全部保留：** W35 原教师 moving190、standing37；候选 moving143、standing33；未知组均0。重置、timeout、物理终止标记未删除。上表使用原条件分母，不是全任务/全部尝试成功率。

E3 的 normal recipe12 六环境不纳入74个 requested 恢复分母。另一个技能保持诊断是：原教师这6个初始normal环境首episode物理终止 **0/6**，候选为 **6/6**。它是小样本保持性警讯，不冒充恢复通过率或已经证明的根因。

## 对照资格与解释边界

- 原环境、资产2c/bae、物理/DR、原命令速度和接受谓词未改；N80、seed20260928，E3 160、W35 1600 controls。
- 两条路径均使用原 noisy/delayed raw35。参考动作是同一完整 A1 缓存中冻结的原 `pi.teacher` 的 RSL mean，无残差或history动作；候选保留已训练的unbounded残差。只加载 pi 到GPU，未把N1024训练容量裁成N80恢复训练。
- 同角色两次读入的是同一 A1 **storage container**，原母本 actor 的bootstrap provenance另列，未谎称container SHA就是母本文件SHA，也未重开母本PT。
- 两边执行资格合格，**不等于技能毕业**。当前是单seed、独立组，natural complete命令区间的UID/cohort分母不相等；同seed不自动证明pose/UID配对。因此 `relative_improvement`、统计退化/因果根因和matched-cohort效应仍为null。
- 原教师参考的 W35 moving Wilson95 为20.24%–42.36%；候选为8.07%–24.66%。这些是条件区间的描述性区间，不能代替独立多seed最终验收。

## 决策

**KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION。** H1、母本、旧候选与Registry均未修改。当前候选 E3 recovery 和 W35 moving 没有达到中间80%目标，更未获得逐专家90%及独立鲁棒性证据。没有为凑到3000继续相同方案。

下一阶段按质量反馈准备1–2角色短训练段、完整保存后释放资源评测，不再默认整批跑满才检查。执行器当前仅source准备，未启用实际训练；新单因子候选先分别验证残差bound和E3恢复时域，原reward/physics/DR/命令/验收不随之混改。模型偏差、传感/WM一致性及恢复奖励冲突仍是可证伪假设，不是已证实根因。

## 证据

- [合格原教师基线](<reports/QUALIFIED_EMBEDDED_TEACHER_ORIGINAL_SKILL_BASELINE_V1.json>)
- [合格教师/候选筛选决定](<reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json>)
- [原教师 W35 新数据首次分组评分](<reports/EMBEDDED_TEACHER_E3_W35_V1_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json>)
- [候选 W35 新数据首次分组评分](<reports/FROZEN_E3_W35_BATCH_V2_ADMISSION2_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json>)
- [原教师实际闭环与外部wait](<reports/ACTUAL_EMBEDDED_TEACHER_E3_W35_V1_20261103_022504/CLOSED_RESULT.json>)
- [候选实际闭环](<reports/ACTUAL_FROZEN_E3_W35_BATCH_V2_ADMISSION2_20261103_022504/CLOSED_RESULT.json>)
- [原disabled假设与单因子计划](<source_first_quality_failure_plan_v1/FIRST_QUALITY_FAILURE_PLAN_V1.md>)

此报告在Phase24之后生成，待Phase25与相关实际错误、源码、两组新数据评分和关闭证据一并归档。历史V1失败与V2零准入超时原样保留。目标保持active，未宣RM70实物场地验证。
