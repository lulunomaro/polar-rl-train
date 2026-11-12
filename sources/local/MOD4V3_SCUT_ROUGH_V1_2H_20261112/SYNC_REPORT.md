# Rough-v1 最终同步回执

统一两小时Rough-v1的执行源码、配方、全部完整PT本体、每五分钟读回/回放、原始短探针、读者修复、恢复原训练盘记录和已收齐5组正式PhysX评测已通过7897代理推送，TLS校验开启。

- 权重与源码提交：`1ca57d0030e8552af02c9a67f6c7428710c07d95`；固定annotated tag：`trial-20261112-mod4-scut-rough-v1-2h-final-01`，远端peeled匹配。
- 本阶段完整训练PT 26份；实际从Git对象逐个读出全部28个PT，包括短探针原件，大小与SHA均匹配。均为完整普通blob。
- 实际训练父为Rough-v0 100m/iter23665/SHA0010283962…；未回退R1。目标机SSH超时导致其余5组评测待收齐，不能称验收完成或GPU已释放。最终比较和接续选择见FINAL_REPORT/DECISION，不覆盖原实车包。
- 原远端main引用保留；分支mod4v1-experts-fulldr-rm70已同步。回执文件随本次独立sync提交归档，最后的远端确认只作工具输出，不产生递归回执文件。
