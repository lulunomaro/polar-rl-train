# MOD4 下一任务交接：先稳定提速，再轻度 DR，再地形

快照时间：2026-09-29T23:22:14+08:00。**快照不是实时状态；第一步必须运行只读检查。**

你接手的是正在训练的真实机器人策略任务。先阅读 01 和 02，不能把这个文件夹当作可直接重跑的安装包。

- 当前任务根目录：`/home/egde/rl_candidates/MOD4_scut_continue10h_20260929`
- 目标机：`egde@10.24.4.210`，RTX 4090。认证使用已有 SSH 配置或向用户取得；本包不存密码、token、私钥。
- 当前任务：华南虎平地训练结构适配 MOD4，速度从 ±1.2 扩到 ±1.5，再有条件扩到 ±2 m/s。
- 当前训练是否运行：快照 `stage=training`，已保存 iteration=5225，速度上限=1.5 m/s。运行中迭代通常高于最新保存迭代。
- 硬截止：**2026-09-30T04:33:53.155460+08:00（北京时间）**。不因接管、验证或改计划追加预算。用户没有授权新的 10 小时。
- 现在应做：观察监督器自动安排的首次提速回放，判断结果，而不是再次启动训练/探针。
- 接下来尚未实现：轻度 DR 的显式配置、隔离验证与训练交接；复杂地形适配。

## 阅读顺序

1. `01_LIVE_STATE_AND_PATHS.md`：实时路径、进程、已有结果。
2. `02_NEXT_TASKS_AND_DECISION_TREE.md`：逐项任务、通过条件与失败分支。
3. `03_READ_ONLY_COMMANDS.md` / `read_live_status.sh`：只读检查，避免双开。
4. `04_METRICS_AND_KNOWN_TRAPS.md`：判据、测量局限、已纠正的误判。
5. `05_SCUT_UPSTREAM_AND_DR_MAPPING.md`：上游真实配置与待实现 DR。
6. `06_SAFE_SWITCH_RECOVERY_AND_BUDGET.md`：安全保存/恢复协议。

`snapshot/` 仅是审计参考，不要覆盖目标机正在工作的源码。`next_task.json` 可机器读取；`PROMPT_FOR_NEXT_AI.txt` 可直接作为下一 AI 的任务提示。
