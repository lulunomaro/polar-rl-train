# 统一 SCUT Rough-v0 两小时执行记录



## 2026-11-12：按用户新指令统一推进 SCUT Rough-v0，2小时

用户明确要求直接训练华南虎Rough-v0科目，不再分R0/R1/R2逐个短轮。本次从综合接续父R1第二轮005m（iter22959，SHA0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f）恢复完整PPO/RNG，统一使用保存rough_rotation_stair的全部9地形族与10级难度，同时训练行进、小陀螺与组合指令。7200秒PPO，每300秒完整PT保存、下载核验和检查；本条是授权与执行计划，尚非训练成绩。

参考的top-level curriculum为空、height-offset curriculum关闭，所有地形行从启动一起采样；不再要求独立15cm落高探针作为此科目前置门槛。当前MOD435/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、完整DR、20%名义/20%平地、−1.5e²和指数1.2保留；沿用2.2m/s上限和机身坐标语义，无云台观测。为4096env分散出生点，参考14列复制为70列，所有地形族仍在同一科目覆盖。

新目录：[统一科目README](../../..//sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)。原阶段历史、冻结及实车包保留；本轮新检查点未经比较不自动晋升。

初始4096env短探针和主训练收据见evidence目录；准备/启动/最终状态分别记录，不把计划写成成绩。

首次smoke4096_unified_r1在环境初始化失败：上传清单只包含Python文件，漏了既有remaining_reset_bank.json；没有PPO更新。原ERROR/SAFE_CLOSED/启动收据和上传清单保留。补齐完整support数据后另起r2短探针，不覆盖失败记录。


主训练实际首次更新：北京时间2026-11-12T02:57:38.481482+08:00，iter22960；完整PT已下载核SHA并实际读回检查35/78/6、actor/critic/Adam/RNG及9×10地形状态，全部参数有限。父PPO恢复17个optimizer条目，LR3e-5 fixed、clip0.1、epochs3。启动实际2.5/10/20ms、TGS32/4、完整DR、−1.5e²，airborne/air reset关闭。本轮正在运行7200秒预算，尚无最终成绩。
