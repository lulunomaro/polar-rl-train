# 7a 实际父权重 + 物理时间延迟 DR：已完成单个5分钟试验

日期2026-11-10。父权重SHA `884cd07b3942df9c8484b905994e302906c84151f6f9c5d079a417ec98158f24`。实际使用原PhysX/PPO框架与独立support快照，没有修改共享生产来源、plant、冻结Step6记录、原奖励、电机包络或100Hz PD。原始进行中报告留在REPORT_INITIAL_IN_PROGRESS.md，不用旧“运行中”口径覆盖最终状态。

用户后来明确“先不开启训练”；此后只做固定权重和状态诊断，没有新训练。唯一已执行训练窗为adapt_005m_r1，300.478秒、4096环境，iteration20838→20905（67更新）。完整恢复actor/critic/STD/Adam/RNG，再覆盖LR为固定3e-5、PPOclip=.1、3epochs、4minibatches、rollout24；原entropy=.005、valuecoef=4。

最终权重SHA `bc22ea7a34c7310f56baeb676ca40bdc0a26da00cf1f0f21a7b124f0a490698f`。路径和实算SHA见ARTIFACT_INDEX.json。该权重未晋升，未实现DR前进目标。

## 实现及实际时钟

独立ScutFlatPhysicalDelayEnv维护物理步级动作和sensor历史。physics2.5ms、policy20ms、PD10ms；reset按组抽样0/5ms，episode内固定；sensor仅4:22，上一原始策略动作22:28不被执行延迟覆盖。buffer5ms不等于力矩5ms生效：原PD下一次10ms刷新才应用新的目标。保留原继承DR与奖励，以便先检验时序修正。

timing_probe_r1漏flat_terrain依赖失败，原始ERROR保留；r2计数通过（32动作tick、33sensor采样、动作槽误差0）。r2不是整机能力证明。parent_fixed10_r1有推理tensor重置上下文错误，修正后r2使用了wxyz初态helper，写入原生xyzw导致整组能力数据无效；后续统一isaaclab.utils.math.quat_from_euler_xyz，再得到有效r3。所有失败和无效结果保留，不改成pass。

## 结果应按引擎/DR分别解释

名义MuJoCo、物理buffer各5ms、10初态结果：新权重前进2.0平均误差.04206m/s，前进2.2误差.09992（最差.10069），后退1.5误差.12749，yaw14.137平均误差.06117rad/s，高度.20/.40误差4.616/1.817mm，既有科目均通过，无reset。详见ADAPT005_REPLAY_RESULTS.json。这不是训练DR PhysX验收。

有效配对PhysX协议：7科目×10初态=70环境；height=.28m；300步/尾120；deterministic DRseed6600。记录的mass/gains/wheel_mu/delay初始量完全相同。该日志未记录逐项COM/关节摩擦；后续专项960环境审计补做了这些显式镜像。瞬时噪声同分布，不声称逐位相同。

|任务|父权重|新5min|既有结果|
|---|---:|---:|---|
|+2.0m/s|1.59787|1.52882|均0/10|
|+2.2m/s|1.61928|1.37099|均0/10，10个样本全部变慢|
|-1.5m/s|-1.39888|-1.40386|均10/10|
|yaw14.137rad/s|13.55482|13.92713|3/10→7/10|
|height.20/.40|均通过|均通过|各10/10|
|combo.9+1.2|.74576/1.19663|.75848/1.17296|仅报告，不设新门槛|

训练窗done_totals：numerical10、fall2、timeout4089，完整保存后退出。脚本未改既有单环境恢复行为。有效固定科目回放无终止。此前sequential10初态组采用不同起始高度，单独保留，不混为此配对协议。

## 退化诊断与下一步

时序统一和小学习率显著减轻旧7a的名义灾难性掉速，却仍未实现当前DR的前进目标。不能把名义回放通过当成DR适应成功。完整排查见相邻 `MOD4V3_FORWARD_REGRESSION_AUDIT_20261110/REPORT.md`：

- 新权重在恢复名义参数/零延迟后仍更慢，存在真实闭环策略退化。
- 同观测轮输出没有统一减小；腿/轮交叉回放定位到腿姿态与轮速闭环协同变化。
- 继承DR里COM重复累加、摩擦分组全量写回覆盖、外力hold不递减已由4环境原生读回确认。它们在本试验中仍保留，尚未修复。
- 100Hz显式轮速环有高频振荡；提高PD频率不能独立恢复新策略。
- 直行总奖励随着变慢下降，不能断言“慢走是奖励最优”；命令采样、优势估计与多任务权衡仍有具体排查位置。

当前停在诊断结论与最小修复建议，未自动追加训练。没有新部署或完整SCUT对齐声明，未改已冻结Step6。

## 证据

`ATTEMPTS.json`逐项记成功/失败/无效；`evidence/`保留原始收据、错误、启动日志；`baseline/`保留原输入支持源码；`support/`为本独立试验源码；`ARTIFACT_INDEX.json`索引权重与轨迹，不提交二进制。所有本阶段报告随Git trial归档。
