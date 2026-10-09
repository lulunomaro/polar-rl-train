# MOD4 项目长期记录要求

人类明确要求（2026-10-09）：“记住我们的所有试错，所有报告都得git来记录”。本工作区MOD4工作必须遵循 `polar-rl-train/docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md` 与仓库 `AGENTS.md`。

- 所有真实试错、失败、拒绝、回退、修复和成功结果都保留；所有已保存报告、交接、同步/验证回执、读者/schema错误报告也必须进入Git。不能只提交成功摘要，不能事后覆盖旧false/raw/原分类。
- 每个实际试错有独立ID与来源/配置/检查点SHA/协议/结果；同一阶段可以一次归档多个报告与错误，阶段完成后的补充报告必须追加提交。已归档同SHA报告可在完整索引中引用原Git路径。健康巡检无新报告不必制造trial；若保存了新报告，仍应随阶段提交或明确列入待补清单。
- 新真实阶段归档用 `polar-rl-train/archive_tools/record_experiment.py` 生成唯一annotated trial，核验remote main/tag/peeled；push失败续已有objects，不重record/重标签。不能把仅本地生成文件称已记录。
- 凭据不输出/不入Git，必要脱敏记录原始与归档SHA及原因；权重/大型raw/NPZ/USD/ZIP等只入真实路径、大小、SHA索引，原件保留。不要为了归档重跑实验、热改或停止主训练、修改预算/复制canonical或重跑once。
- 本要求是记录约定，不产生新训练/S8/外部通信授权；继续遵守已批准计划、实际进程/ownreceipt优先与安全保存接管边界。
