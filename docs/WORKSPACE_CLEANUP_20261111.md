# 本机 mjcf 历史副本清理（2026-11-11）

人类要求清理本机 mjcf 内大量重复、无用或已有 Git 的日志和文件。本次只处理本机存储，不启动、恢复、停止任何训练或自动化。

已删除或收起 462,263 份文件：238,399 份与 Git 内容一致的外部副本、223,727 份 Git 稀疏检出历史文件、100 份已压缩保存的旧大日志、6 份已迁移的中转件及 31 份字节码缓存。另合并 190 份相同模型/轨迹，原路径仍可读。C 盘可用空间从初次扫描约 8.49 GB 增至约 63.40 GB，增加约 54.92 GB；快照差含正常系统并发写入，不把硬链接的重复逻辑大小当实际节省。

100 份旧大日志从约 5.59 GB 压缩至约 243 MB。所有 F 盘保留件及恢复索引合计约 710 MB。固定 Git 提交恢复和压缩日志恢复均已实际抽查通过；238,399 个删除路径不存在、190 组硬链接原路径同源、当前 H3 工作区干净、数值源码 SHA-256 未变。

历史恢复来源是 `polar-rl-train` 的提交 `0876a1f8dd1698dc49b7e25b9b315a18055b2582`。清理前远端 `main` 与该提交相同。历史失败、原始报告、Git 对象与标签保留。

## 本次处理

- 对根目录旧 `MOD4_*` / `RM2026_*` 阶段副本逐文件计算 Git blob SHA-1 和 SHA-256，只删除内容与可读取 Git 对象一致的副本；保留每个原路径到 Git 路径、提交和哈希的映射。
- 仓库使用 Git cone sparse checkout 收起 `versions/` 和 `history/evidence/` 的旧展开副本；保留当前源码、归档工具、全部 `sources/`、`objects/`、`history/reviews/`，以及当前源码实际引用的 `history/evidence/MOD4_E1_G3_MATCHED_REVIEW_20261010/`。没有提交历史文件删除。
- 旧 `.staging/` 中转包迁至 F 盘，原件与迁移件 SHA-256 一致后删除 C 盘副本。
- 未在 Git 中找到一致副本的旧大日志/清单，压缩至 F 盘 `closed_text/<SHA256>.gz`，逐文件完整解压核对 SHA-256 后删除展开件；原路径映射保存在 `large_text_relocation.json`。
- 已结束阶段中内容相同的模型/轨迹采用 NTFS 硬链接合并存储，原路径继续可读。只处理指定的 `.pt/.pth/.npz/.npy/.onnx`；不合并日志等可追加文件。
- 清除环境之外可再生的 Python 字节码缓存。

H3 项目、其他 Git 仓库、环境、CAD/原始资产、本地播放器目录、包含 ledger/canonical/budget 的文件、现有 F 盘目录联接及其目标保持原样。没有改凭据、预算或运行进程。无法访问和无法证明冗余的文件不删除。

精确数量、空间变化、未处理项和内容索引见同目录 `WORKSPACE_CLEANUP_20261111.json`。大清单放在 `F:/RMPOLAR-RL/mjcf_workspace_cleanup_20261111/`，Git 仅记录其路径、大小与 SHA-256。

## 恢复

需要某个被收起的仓库历史目录时，在仓库运行：

```powershell
git sparse-checkout add versions/具体阶段目录
git sparse-checkout add history/evidence/具体阶段目录
```

恢复全部 Git 展开文件可运行 `git sparse-checkout disable`，会重新占用约 35 GB。通常只恢复需要的阶段。

恢复外部重复副本的单个文件：

```powershell
python -B archive_tools/restore_workspace_file_20261111.py "MOD4_具体阶段/reports/具体报告.json"
```

该工具读取 F 盘 `deletions.jsonl.gz` 或 `large_text_relocation.json`，从固定提交或压缩归档取回内容，校验大小与 SHA-256，拒绝覆盖现有文件或穿过目录联接。

旧中转包的原路径与 F 盘新路径见 `staging_relocation.json`。模型/轨迹硬链接不会造成原路径缺失；历史冻结原件以后需要修改时，应先复制成新版本，避免原地改写共享内容。
