# 四张4090实际检查与原生复测接续

人类要求“找其他的卡，一共四张呢”。2026-11-04 00:08–00:09 +08通过既有授权transport有限串行检查72/210/86的四张4090，原canonical未写入，SSH全部关闭、SESSION恢复。检查原件为scope运行目录reports/FOUR_GPU_HUMAN_REQUEST_ACTUAL.json及86FIX1报告，归档索引保留。

| 主机/卡 | 空闲显存MiB | 已用MiB | 利用率 | 实际用途 |
|---|---:|---:|---:|---|
| 72 / GPU0 / 16828f91… | 18,285 | 5,932 | 58% | 原standing SCUT20训练中，worker1549198 |
| 72 / GPU1 / c27eecbd… | 24,203 | 13 | 0% | 选中；已有本任务模型、资产和定制SDK |
| 210 / GPU0 / 937bdb0b… | 23,890 | 199 | 0% | 卡空闲；HOME所在分区仅628,064,256B空闲，未启动或复制模型资产 |
| 86 / GPU0 / 90a66ae2… | 2,462 | 21,620 | 0% | compute PID614420占用约21.1GiB，属于大显存占用，未按低利用率冒称空闲 |

首读86遇到系统Python缺psutil，原失败保留；改用/proc/meminfo读取内存后仅重试86，未安装软件、未读模型或运行SDK。历史报告不会更新成实时资源证据。

00:08时72原canonical owner1549188仍live，共享authority及finite原锁不可得；不是没有空显卡。已选原host空闲GPU1，避免把跨主机复制资产、模型和重搭SDK作为本次找卡的前提。

唯一local控制器PID1904/create2026-11-04T00:12:50.208880+08，以原脚本 `action_clip_eval.py run --wait-release` 进行有限900s等待，不持远端锁，不新增训练窗或预算。最新实际：peer完整退出epoch1793722478.9888444（00:14:38.988844+08），allownwaited/settled/released；00:14:46.294161有限准入核canonicalNone、peer身份一致，随后首次消费diagnostic LAUNCH_ONCE。

实际诊断owner1551324/create1793722486.95，运行于72GPU1。冻结REV3的修复模块与same-final305f5a9e…保持，80firstepisodes/400controls/seed9137/0optimizer/0ledgerwrites；原生startup已由唯一控制器读到。结果以action_clip_eval1/reports/FULL_RETURNED.json与TRANSFERS.json为准，训练技能尚不据startup推断。活controller只本地读，不第二SSH/watcher/launch。

其它检查记录：一次猜测个人skills/stop-that-shit路径不存在，按已提供plugin实际路径读到；仅文件读取，无训练或资源操作。此skill不作为新增锁或审批依据。

本次为既有native阶段普通补充，原annotated trial不重record/retag。具体完整结果和下一步进入WORK_ORDER及后续报告。
