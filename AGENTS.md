# MOD4 Git 记录必须遵守

人类2026-10-09明确要求所有试错和所有报告都用Git记录。读取 [完整记录政策](docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md) 与 [既有追加工作流](docs/NEXT_AI_GIT_WORKFLOW.md)。

所有真实成功/失败/拒绝/回退保留独立ID和证据；所有保存的报告，包括同步/验证回执、读者错误、交接和后续补充都需提交。旧失败/false/raw不可改成pass，也不可只归档成功摘要。阶段报告可以合并一次记录，阶段归档后生成的报告必须再补入Git或如实标pending，不能遗漏。

使用archive_tools/record_experiment.py，唯一annotated trial并核验remote main/tag/peeled；推送失败只续已有objects。健康无新报告无需造trial。凭据禁止归档；权重和大型原件只SHA/路径索引。主训练、生产源与canonical预算不因归档修改或暂停，旧once不重跑。
