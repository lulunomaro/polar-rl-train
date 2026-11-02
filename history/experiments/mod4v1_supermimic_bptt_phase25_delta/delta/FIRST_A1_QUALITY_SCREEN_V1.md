# 首轮 A1 质量筛选：保持母本，暂停同方案盲目扩量

## 原技能诊断事实

| 条件 | 成功 / 原完整条件分母 | 单列的未完整区间 | 结论 |
|---|---:|---:|---|
| E3 requested recipe0..11，首次 episode recovery credit | **0 / 74** | normal recipe12 的6环境另列 | 不提升候选 |
| W35 moving，自然完整、同UID、非终止区间 | **10 / 69 = 14.49%** | **143** | 保持原 scoped-best 母本 |
| W35 standing，同一原条件 | **16 / 17 = 94.12%** | **33** | 仅此站立条件的结果，不混作运动通过率 |

**这批数据是实际 N80 控制循环产生的诊断，不是合格最终验收。** E3 160、W35 1600 controls 均已真实执行，随后 close helper 因缺少静态项目依赖而报错。错误和全部输出保留；即使进程 RC0，也没有算作合格闭环。单 seed、条件分母与未完整/重置/timeout 区间均保留。尚无同口径实际教师对照，因此相对提升、统计退化及因果根因仍为 null。

## 已执行的质量优先措施

- 通过原 `STOP_AFTER_SAVE` 合作收拢训练，完整保存并实际 close/wait、结算、释放资源；没有进程信号、源码热改或物理/DR/速度/接受阈值调整。
- **不把更新次数、loss、吞吐或 RC0 当通过率；没有为凑到3000继续扩大当前方案。**
- Registry_v12 的母本/scoped-best、旧候选和 H1 均保持原样；新候选未被提升。
- 补齐冻结评测的完整依赖包，另建 V2 用途。原1800秒资源等待自然到期，**两角色未准入、未开模型或SDK**，不是新的0%技能成绩。外部已在运行的 standing 任务持有项目原私有GPU锁和有限环境共享锁；没有清锁、干扰或绕开原验收资源协议。
- 只读资源释放观察正在运行。下一次实际用途在资源满足原门槛后执行，不重放已消费的 V2 parent。

## 下一步看什么，而不是再凑多少步

1. 完成依赖正确且实际 close/wait 合格的原口径复测。
2. 用同一完整缓存中冻结的原教师建立真实参考，比较 E3 recovery 与 W35 moving/standing 各自的 n/N、partial 和失败分布。配置同 seed 不自动证明 pose/UID/cohort 已配对。
3. 再决定是否执行独立单因子分支：bound-only 或 E3 H32-only。两项目前均 disabled，尚未训练；不叠加、不改原验收。

原教师参考的 **CPU 软件路径**已经与原 RSL mean 做过4×N80比较，最大动作误差0，冻结STD/残差norm的负向测试通过；这不是实际母本的技能评测，也不是候选效果。

## 证据

- [首轮质量筛选与保母决定](<reports/FIRST_A1_ORIGINAL_QUALITY_SCREEN_SELECTION_V1.json>)
- [W35 新产生原始行的首次实际分组评分](<reports/FROZEN_W35_BATCH_V1_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json>)
- [V1 close 错误及实际控制事实](<reports/FROZEN_E3_W35_BATCH_V1_QUALITY_FACTS_WITH_CLOSE_ERROR.json>)
- [V2 原等待边界的实际闭环](<reports/ACTUAL_FROZEN_E3_W35_BATCH_V2_20261103_012611/CLOSED_RESULT.json>)
- [原教师参考 CPU 软件验证](<reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json>)
- [disabled 单因子计划](<source_first_quality_failure_plan_v1/FIRST_QUALITY_FAILURE_PLAN_V1.md>)

当前尚无逐专家90%与独立多seed鲁棒性证据，目标保持 active。此报告在 Phase24 提交之后生成，待 Phase25 追加归档。
