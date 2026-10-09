# polar-rl-train

MOD4 强化学习项目的修复、训练、诊断和交接档案。仓库创建于 2026-10-03，默认私有。

本次从本机及 4090 目标机收集 **83 个资料目录、20,078 份文件**，为 **968 条有保存证据的试验/修复/验证记录**补建提交和注释 Git 标签。另有每目录一个 `version-*` 标签。包含成功、失败、无效探针、被否决方案及其他 AI 留下的资料。

## 从这里看

- [按阶段看修了什么](docs/REPAIR_TIMELINE.md)：人工整理的修复主线、重要纠正和未完成事项。
- [完整试验/修复标签表](history/INDEX.md)：每条记录的标签、类别和证据链接。
- [全部版本目录](history/VERSIONS.md)：83 个目录各自的来源、源码和交接说明。
- [原有 Git 记录](provenance/ORIGINAL_GIT_RECORDS.json)：播放器两个原仓库中仍可读取的 5 条提交，其作者/时间和文本差异保留，另有 `original-*` 标签。
- [下一位 AI 的记录工作流](docs/NEXT_AI_GIT_WORKFLOW.md)：新增修复/试错按版本追加，不覆盖旧失败或标签。
- [所有试错与报告的长期Git要求](docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md)：失败、拒绝、读者错误、同步与最终验证报告也必须记录，阶段后生成的报告补交。
- [当前生产状态快照](CURRENT_STATE.md)：归档时实际阶段与未部署候选；不会自动更新为实时状态。
- [项目代码入口](project/README.md)：当前生产源代码的固定副本及外部运行依赖。
- [归档范围与缺口](docs/ARCHIVE_POLICY.md)、[检查结果](provenance/ARCHIVE_VALIDATION.json)。

## Git 标签是什么

`trial-日期-编号-试验名` 对应一次有证据的试验、训练运行、修复/诊断、失败程序或保存源码变体。类别写在记录里；不是每个标签都代表一次成功训练。`version-local--...` / `version-remote--...` 对应原始资料目录的完整归档快照。标签直接指向本次创建的提交，可在 GitHub 的 **Tags** 或提交历史查看，也可以：

```bash
git clone https://github.com/lulunomaro/polar-rl-train.git
cd polar-rl-train
git tag -l 'trial-*'
git show <tag>
git switch --detach <tag>
```

这些是**补建的证据历史**：提交时间是真实归档时间，记录另列原试验日期及来源。没有把今天的提交伪装成当时提交，也没有根据目录名猜测作者。保存的运行源码快照可证明当时版本；仅有当前源码或报告的记录会明确写出证据等级。

## 收录内容

`sources/local/` 与 `sources/remote/` 保留原相对路径，包含代码、配置、报告、交接、备份和资产。`objects/sha256/` 是去重内容库，`provenance/capture_inventory.json` 记录原路径、字节数、时间、原始/归档哈希及采集方式。训练 `run_manifest` 的环境参数、源码指纹和可找到的 `src_snapshot` 一起保留；相邻运行配置差异有单独记录。

**模型权重和大型二进制轨迹没有上传到 Git。** [检查点索引](provenance/checkpoints.jsonl) 保留 11,429 个文件条目的路径、大小、时间和能从原凭据解析到的哈希；重复目录副本也计作文件条目。未读取权重内容，不伪造缺失哈希。原目标机/本机权重原样保留。大型日志保留明确标注的首尾摘录，详见归档范围。

## 以后每次修复怎么记

先写一份说明：问题、改动、配置/来源权重、检查协议、实际结果和仍失败的项目。再把改变的代码/配置/证据连同标签一起推送：

```bash
python archive_tools/record_experiment.py --id yaw6-regression-01 --title "6rad/s 回归复核" --kind evaluation --note-file notes/yaw6.md --files project/isaac/mod4/env.json reports/yaw6.json --validation "协议与结果见报告" --push
```

这是用法示例，需替换为真实文件。脚本拒绝覆盖标签、夹带已暂存的无关改动或提交权重/明文凭据。历史批量构建脚本仅用于本次首次归档，不应重跑来改写既有标签。

仓库只记录项目，不会启动训练、变更目标机预算或停止现有任务。上游代码与资产的原许可证/来源保留，[第三方说明](docs/THIRD_PARTY.md) 不替代原许可。
