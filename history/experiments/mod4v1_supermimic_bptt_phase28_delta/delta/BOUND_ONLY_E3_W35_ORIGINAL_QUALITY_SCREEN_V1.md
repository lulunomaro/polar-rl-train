# 零更新 bound：原技能质量筛选 V1

新探针已完成实际控制、原关闭与等待、原资源释放和源码/冻结检查。动作只把同权重残差映射由 `.05*delta` 换为 `.05*tanh(delta)` 后总clip6，优化器更新为0，观察差异不归作训练收益。

| 原条件 | 原教师 | 原unbounded候选 | 本次bound探针 |
|---|---:|---:|---:|
| E3 original_requested_first_episode_credit | 0/74（0.00%） | 0/74（0.00%） | 0/74（0.00%） |
| W35 original_moving_natural_complete_nonterminal | 19/63（30.16%） | 10/69（14.49%） | 14/60（23.33%） |
| W35 original_standing_natural_complete_nonterminal | 26/26（100.00%） | 16/17（94.12%） | 13/22（59.09%） |

## 完整分母与保持诊断

- W35 moving partial（原教师 / unbounded / bound）=190 / 143 / 178；bound unknown=0，original reset=118，物理term=0，trunc=118，Wilson95=[0.1443956173664283, 0.35436270377601964]。partial不混入原conditional完整区间成功率，也不消失。
- W35 standing partial（原教师 / unbounded / bound）=37 / 33 / 36；bound unknown=0，original reset=16，物理term=0，trunc=16，Wilson95=[0.3873481847631513, 0.7674418380352814]。partial不混入原conditional完整区间成功率，也不消失。
- E3正常recipe12（reference）首次物理term=0/6，独立于requested recipe0–11的74个恢复分母。
- E3正常recipe12（unbounded_candidate）首次物理term=6/6，独立于requested recipe0–11的74个恢复分母。
- E3正常recipe12（bound_probe）首次物理term=0/6，独立于requested recipe0–11的74个恢复分母。

W35原分组数据完整性已验证：`True`。同一seed但自然区间/episode并非已匹配cohort；matched UID/pose、relative、因果及统计提升均保留null，不把点估计差当因果。

## 选择

保持Registryv12 scoped best与所有母本/H1，暂不晋级候选；没有调度新训练，不为3000继续旧质量欠佳方案。80/90目标需要原接受与独立multi-seed，不由这一次点估计完成。

[机器证据与所有分组](<reports/BOUND_ONLY_E3_W35_ORIGINAL_QUALITY_SCREEN_V1.json>)；[原教师/旧候选合格对照](<QUALIFIED_QUALITY_COMPARISON_E3_W35_V1.md>)。
