# 八专家质量优先路由：通过者保持，弱项单因子，缺测量先补证据

这是基于**已发布元数据**的后续路由计划，不是新的冻结评测、训练队列、统一成功率或90%毕业证书。未打开任何原模型/轨迹，也未修改Registry或母本。H1保持冻结并排除。

依据：当前 [E3/W35合格实测对照](<QUALIFIED_QUALITY_COMPARISON_E3_W35_V1.md>)；历史 [8专家PPO原scope评估](<../mod4v1_experts_fulldr_rm70_20261101/MOD4V1_EIGHT_EXPERTS_POSTTRAIN_FINAL_V1.md>)；[原E0/S50接受缺口审计](<source_original_acceptance_gap_review_v2/ORIGINAL_E0_S50_ACCEPTANCE_GAPS_SOURCE_V2.md>) 及 [原MasterPlan追加核验](<source_original_acceptance_gap_review_v3/EXACT_MASTER_PLAN_ACCEPTANCE_APPEND_V3.md>)。历史结果保持自己的算法/样本/时间标签，不混成新的A1实测。

| 专家 | 当前可用证据及限制 | 下一步路由 | 默认是否继续同方案堆量 |
|---|---|---|---|
| E0 | 历史原PPO20后body诊断改善、普通失败0；原完整profile二元接受分母仍未证明 | 保持当前scoped-best；先补原standing/straight/pure/transition/moving全profile接受authority与cohort。诊断MAE不当90% | 否 |
| E2 | 历史body诊断有改善，原world联合0/187；world参考点/getter相位仍须真实时钟证据 | 先验证原世界参考与cycle UID/同episode/符号/帧时钟，不以压低body MAE或改阈值冒通过 | 否 |
| E3 | 新合格参考与候选均0/74；另normal6首episode物理终止0/6对6/6 | 优先同权重零更新bound探针看保持性；然后视实测结果做独立恢复时域/奖励等单因子短段，不叠改；旧候选不晋级 | 否 |
| W35/W25 | 新合格teacher moving19/63、candidate10/69，standing26/26对16/17，partial全部保留；独立cohort | 先单独bound探针分清动作后处理与训练收益，后续必要时才短段新版本+独立复测。保持moving/standing分组 | 否 |
| CURB878 | 历史原scope当前最佳上行26/27、下行27/27、站立26/26；只有单seed有限窗口资格 | 先保留当前好源，独立多seed/原两轮same-episode端点接触holdout验证保持；没有弱项证据就不额外破坏它 | 否 |
| CURB113 | 历史原scope上行22/27、下行27/27、站立26/26；上行点估计尚低于90% | 单列上行失败分布；未来原owned-axis构造/一次freshreset后绑定须保留，采用1角色有限增量后立刻原上下行/standing复测 | 否，需失败原因与新版本 |
| SLOPE135 | 历史原scope上行27/27、下行27/27、站立26/26；仅单seed | 保留当前好源，独立多seed/原自身坡几何与接触判据检验保持，不拿Curb或S50谓词替代 | 否 |
| SLOPE50 | 历史20s own-axis普通失败0，但原fullramp接受predicate/cohort缺件 | 继续原接受authority/完整cohort核验；不拿无跌倒、边界/timeout或S135端点当成功率 | 否 |

## 共用决策规则

1. **先可解释测量，再谈增加量。** 旧26/27或27/27不是各自90%整体毕业；新0/74或moving比例也不自动证明因果根因。单seed、完整条件/partial、终止/timeout、区间UID与置信度各自保留。
2. **已表现好的源不为“全部训练过”而训练。** 保持母本及正常技能是主目标之一；多seed保持性验证优于在没有失败证据时继续扰动C878/S135。
3. **未获提升的方案不靠次数解禁。** 当前A1 legacy候选保持为候选，旧scoped-best仍有效；约3000仅规模过程参考，1–300实际增量也不是接受线。
4. **小批专家、短段闭环。** 新执行器只选择1–2角色，deferred不构造SDK；完整保存/实际关闭wait/原预算结算释放，再独立冻结评测。当前执行器尚未native启用，CPU恢复alias问题修复前不放行resume。
5. **先零更新消融，再训练。** bound探针只改变同权重forward `.05*delta→.05*tanh(delta)`，没有BPTT更新；若实测好转，后续训练收益须相对这个零更新探针比较，不能全归到训练。
6. 不动原2c/bae资产、命令速度范围、D0–D7、50/100Hz与物理参数、original atomic predicates或原C/锁/reserve/有限窗口。任何新声明必须有对应真实准入/模型/关闭/评分证据；暂无80%逐专家保底、90%最终、RM70实物验证或已排新训练队列的声明。
