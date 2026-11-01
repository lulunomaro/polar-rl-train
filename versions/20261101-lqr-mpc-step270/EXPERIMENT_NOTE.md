# MOD4 LQR / MPC 270 mm 台阶阶段归档

本阶段保存 2026-11-01 已完成的传统控制试错、源码、模型参数及结果。归档读取现有文件，没有重新运行控制器、仿真、评测或旧 one-shot 脚本。该阶段与仍在开发的 SuperMimic RL 阶段分开保存。父代理已在准备核验通过后确认：本 LQR 阶段先独立创建 trial/commit 并推送 `lqr`，后续 RL 阶段另行追加。下述准备回执中的未提交状态对应采集时刻，最终提交与远端验证以本次 Git 对象和工具回执为准。

## 来源与覆盖

- 本地只读来源：`F:\RMPOLAR-RL\traditional_control_20261101`。
- 原远端任务根：`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_MUJOCO_LQR_MPC_STEP270_20261101`。本次未连接远端；从原完整任务包读取远端保存的证据。
- 完整包：`MOD4_LQR_MPC_STEP270_20261101.tar.gz`，47,678,430 bytes，SHA256 `ff43f8ca52476a6886c22f1b957e8c9f4000e68fc896acf908d4f9b9ff38abfb`；与 [原归档回执](ARCHIVE_RECEIPT.json) 一致。
- 任务包有 610 个常规文件：609 条 [原文件清单](TASK_ARCHIVE_MANIFEST.json) 加清单本身。609 条原始大小和 SHA 已全部实算核对，零差异。
- 本地非缓存文件 442 个。任务包独有 220 个，包含本地未展开的历史结果、冻结源码和候选配置；本地独有 52 个，包括 SSH 环境注入工具、探针、配置、归档回执、动画/帧图和压缩包。两者交集 390 个均字节一致。
- 来源并集 662 个文件均有覆盖记录：340 个文本原件按原相对路径全文保存，共 52,208,127 bytes；322 个二进制或容器原件只保存真实路径、大小、SHA256 与来源位置。后者共 176,350,110 bytes，包含压缩包及成员，属于未去重的索引字节总量。
- 69 个本地 root `*.py/*.sh/*.md/*.json/*.csv` 全部保存。2 个模型 XML、完整模型参数/manifest、13 个 summary、26 个 JSONL、14 个独立 result 均全文保存。轨迹 JSON 也原字节保存，没有裁剪原始成功或失败证据。
- 二进制索引涵盖 277 个 STL、38 个 PNG、4 个 GIF、3 个压缩包。模型 STL 原件留在来源目录与完整任务包；XML 的资产相对引用保持原样，需要从原件恢复 STL 后运行。该来源并集中未发现模型权重文件。

[来源覆盖清单](_archive/SOURCE_COVERAGE.json) 列出每个原路径、字节数、原 SHA、Git 归档路径/归档 SHA、tar member 和本地来源；[大型原件索引](_archive/ARTIFACT_INDEX.json) 记录未复制原件的定位与实算 SHA。[报告索引](_archive/REPORT_INDEX.json) 对照所有全文文本、summary、result 与 JSONL。[准备回执](_archive/STAGE_RECEIPT.json) 保存本次只读采集的实际检查结果。

## 问题、实现与模型

本阶段目标是使用真实完整 MOD4 模型，令双轮在同一次腾空中完整跨越 0.27 m 竖直台阶，并在台顶真实承重且连续稳定至少 0.5 s。

[full_lqr.py](full_lqr.py) 使用 14 状态、6 输入、闭链与轮支撑降阶线性化的离散 LQR。[linear_mpc.py](linear_mpc.py) 使用 15 步有限时域受限 QP，在接近及恢复阶段滚动求解；蹬伸、收腿、展腿和飞行俯仰由 [hybrid_trial.py](hybrid_trial.py) 的分阶段反馈完成。MPC 地面预测未显式包含 D4 目标队列，不能从该实现推断已经解决飞行接触预测或反馈延迟。

模型为 31 个机器人刚体、30 个关节、6 个真实电机，`nq=37, nv=36, nu=6`，保留闭链、mimic、导轮和实体碰撞。源模型 SHA256 `f936e5cf6580299e5f89ac843b4ebc3c72f9d40d9131dbcb4fa1fa7779dc87d9`，400 N 派生模型 SHA256 `5d52284a618c95ac49c97666b00f9e4567d20abb4728e322dc8651f07f4ba0ee`；原始来源与几何清单见 [MODEL_PROVENANCE.json](MODEL_PROVENANCE.json)，参数见 [model_parameters.json](model_parameters.json)。源文件和原始弹簧参考位置均保留，q=0 时工程静态力约 441.28 N。

本轮物理来源是 CPU MuJoCo 3.12.0、0.5 ms 物理步、100 Hz 控制与反馈、implicitfast/Newton/100 次求解。早期 CUDA CEM 用于参数采样/排序，不是 GPU 刚体并行仿真。闭链终止为 10 mm，mimic 为 0.01 rad；原被动电机 damping 仍保留，与近期 PhysX damping=0 的配置差异在原报告中明确记录。没有为本归档修改原训练、生产源或预算。

## 实际协议与结果

最终统一验收以 [最终 V2 完整回归](results/FINAL_FULLDR_MATCHED_V2/summary.json)、[逐种子结果](FINAL_DR_TRIALS.csv)、[独立验收指标](FINAL_METRICS.json) 和 [最终证据 manifest](results/FINAL_EVIDENCE_V2/manifest.json) 为准。两策略共享完整 D0–D7 抽样，固定回归种子 5000–5063，每策略 64 次；另有 2 个名义用例，名义结果未并入 64 分母。LQR 一阶反馈预测为 0，MPC 为固定 5 ms，属于两套调定方案的同种子对照。

| 保存结果 | LQR | MPC |
|---|---:|---:|
| 名义末尾连续稳定 | 2.95 s | 2.79 s |
| 全 DR 首次腾空双轮完整越沿 | 58/64 | 58/64 |
| 全 DR 曾连续稳定至少 0.5 s | 25/64 | 28/64 |
| 全 DR 完整运行且末尾连续稳定至少 0.5 s | 8/64 | 6/64 |
| 全 DR 健康条件提前终止 | 4/64 | 20/64 |

“曾稳定”与“末尾稳定”分别保留。最终 10 ms 反馈延迟组每策略 33 个样本，末尾稳定均为 0/33；24 条健康提前终止均为姿态直立余弦低于 0.45。保存的最终指标给出最大闭链误差约 0.05365 mm、最大 mimic 误差约 `8.1771e-5 rad`，没有把这些控制采样统计扩展成逐物理 tick 结论。

名义 LQR/MPC 各有 1 个控制采样的短暂非轮接触。单独选出的全 DR 成功示例 LQR seed 5047、MPC seed 5063 在 100 Hz 保存记录中非轮接触为 0；两条姿态健康终止失败示例 seed 5014、5001 同样完整保留。MPC 本批最大求解约 25.15 ms，超过 10 ms 控制周期，记录本身不支持硬实时保证。详细解释见原 [RESULTS_20261101.md](RESULTS_20261101.md)。

## 历史失败、尝试 ID 与证据边界

26 个 JSONL 共 5,501 条保存记录，另有 14 个独立 result 文件。[逐记录定位索引](_archive/ATTEMPT_INDEX.jsonl) 为每条记录提供 `原相对路径#line-N` 形式的独立定位、原 ID、行 SHA 及原始状态字段。索引没有将跨目录重复结果或独立 result 副本宣称为新物理尝试，也没有按文件夹名字推断成功。所有源记录和报告的 success/false/stop/错误及早期宽松验收原样保留；空 JSONL 仍为空，配置存在未被写成已完成训练。

早期候选的旧 gyro 反馈、宽松验收、地面回退、失败搜索和修复前源码快照都与最终 V2 并列保存。最终版本仍使用仿真真实世界位置/速度、yaw 角及接触相位；实物状态估计、全反馈延迟、真实质量/惯量/弹簧标定尚未验证。仿真结果未被写成实机认证。

本次采集读者也有一条失败：首次列表脚本假设 tar 根名等于本地目录名，观察到实际根名后修正为 `MOD4_MUJOCO_LQR_MPC_STEP270_20261101`，失败发生在写入前，未重跑物理实验；原情况与修正保存在准备回执的 `capture-reader-01` 中。

## 采集与待提交清单

[采集脚本](_archive/capture_lqr_archive.py) 只读指定来源，逐 member 校验原 manifest，再补本地独有内容。340 个来源文本经过仓库现有凭据检测，零命中，归档字节 SHA 全部等于原 SHA，没有脱敏改写。SSH 工具只通过进程环境获取密码；没有归档含 SSH 凭据的 shell transcript，也未读取 OS 密钥目录或 credential store。

[Git 文件清单](_archive/GIT_FILE_LIST.txt) 列出本阶段待提交的仓库相对路径，包含本说明、所有采集证据、索引、准备回执和采集脚本。采集完成后的 Git index 为空，使用 `archive_tools/record_experiment.py` 生成唯一 annotated trial `trial-20261101-lqr-mpc-step270-v2-final`。远端目标仅 `lqr`；默认 `main` 及其它分支保持原引用，禁止 force push。按父代理最新确认先提交推送本 LQR 阶段，RL 阶段后续独立追加；远端 `lqr`、tag 对象、peeled commit 与 `main` 原 SHA 的验证直接作为工具输出返回，本说明保留准备与授权事实。
