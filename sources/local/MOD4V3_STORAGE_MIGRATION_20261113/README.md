# 210训练主机：训练数据搬到Windows数据盘并清理（2026-11-13）

用户要求先释放Linux系统盘，再继续训练。已完成。旧210与现地址10.24.3.125的SSH主机密钥一致；未把地址变动误认成另一台机器。

| 项目 | 实际结果 |
|---|---|
| 源目录 | `/home/egde/rl_candidates` |
| Windows数据盘 | `/dev/nvme0n1p5`，NTFS，UUID `EF3105C85DD986BD` |
| 新实体目录 | `/mnt/mod4_windows_data/MOD4_training_data/rl_candidates` |
| 兼容入口 | 原目录变为指向新实体目录的Linux符号链接，原训练路径可继续使用 |
| 内容校验 | 130,878个文件逐一核对SHA256，41个符号链接逐一核对目标 |
| 校验总字节 | 64,798,659,796，逐文件清单见evidence/VERIFIED_FILES.jsonl |
| Linux空间 | 约734MiB → 61.35GiB；df显示62G可用、使用率90% |
| 清理旧PT | 114份，747,242,984字节；均与已发布Git中的完整普通blob一致 |
| 清理缓存 | 两个已安全关闭作业的DerivedDataCache，1,310,807,332字节 |
| Windows余量 | 清理后约505.69GiB，df显示506G可用 |

先复制，再对源和目标的全部普通文件计算SHA256，验证链接和文件计数后，才移除Linux原件。迁移原始清单、复制日志、校验回执和完成回执均在evidence；临时Linux原件目录已移除。复制不承诺保留NTFS不支持的所有POSIX权限元数据，文件内容和链接目标已经逐一验证。

已在/etc/fstab记录该数据盘的自动挂载，备份位于/etc/fstab.mod4_storage_20261113.bak；准确条目和修改前后SHA在evidence/PERSISTENT_MOUNT.json。Windows下从该数据分区根目录进入MOD4_training_data即可查找，不推断Windows盘符。

旧PT仅在本地完整文件的规范Git blob OID、SHA256与已发布HEAD相符时才列入可删除索引；LFS指针、未入Git和已修改文件不纳入。每个已删文件的旧位置、SHA256、Git实体路径、blob与已发布提交在evidence/CLEANUP_COMPLETE.json，可据此从Git取回。当前成功示范40分钟实验整个目录、当前PLAN引用的权重和符号链接目标均保留。旧原始证据和其余训练文件位于Windows盘，不按失败或通过状态删选。

迁移后使用原生训练Python从原路径读入25分钟候选，SHA8215a43a…一致，iter25288，actor35/critic78/action6，17项Adam状态和success_replay_state齐全，见evidence/POST_MOVE_RUNTIME_CHECK.json。存储变更未启动新训练轮；当前候选的后续rough对照在MOD4V3_STAIRS_SUCCESS_REFRESH_40M_20261113继续记录。

本次Git走127.0.0.1:7897代理、保持TLS校验，只追加实验分支和trial标签。清理开始时远端main已为2fbc883d…，区别于本轮训练启动时的dc7259b…；本次不回滚或修改main。查询方法调整见evidence/GIT_QUERY_NOTE.md。
