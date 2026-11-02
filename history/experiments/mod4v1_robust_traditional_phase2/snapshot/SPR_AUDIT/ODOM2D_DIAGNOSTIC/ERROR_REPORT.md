# Recorded-data diagnosis — 操作/错误记录

- [analysis_attempt_01.log](<analysis_attempt_01.log>)：纯stdlib解析4个已记录trace并计算FK/积分，exit0。3200行全部处理，没有异常FK、时序配对缺失或SHA冲突。
- [refine_attempt_01.log](<refine_attempt_01.log>)：只导入本目录自己的纯数学parser，追加已记录通道消融与路径导出，exit0；没有parent/producer代码import。
- 两次分析没有失败回放、改写raw或丢弃困难case。也未对源数据重新生成physics/IMU。
- `ground_truth_before`、packet timestamp、age与raw顶层after time已分开；0.5ms缓存阶段混采与boxcar aperture保留为限制，没有使用新sim/forward来“补齐真值”。
- Producer旧result xy起点与本报告0s起点口径的小差额保留双方原值，没有当成损坏或静默改原件。
- 本轮没有旧C unit重跑、父进程操作、板/CAN/SSH/训练/Git/安装；封存QP及旧包只读哈希复核。
- [INDEX.json](<INDEX.json>)列出raw引用、producer匹配范围、派生结果与脚本SHA；[VALIDATION.json](<VALIDATION.json>)给出复核结果。当前没有异常traceback文件。
