# 0/5ms过渡段中止补充

本轮原计划40min；用户指出应为Step7 DR后，在015m完整checkpoint保存后中止，后续预算见MOD4V3_STEP7_FORWARD_SQUARE_RANGEFIX_20261111/PLAN.json。此段只0/5ms，不能称完整Step7适应。实际已保存005/010/015m并完成CPU名义MuJoCo既有任务回放，所有原始结果/日志位于evidence/training_round。

| checkpoint |2.0指令实际m/s|2.2指令实际m/s|六项门槛结果|
|---|---:|---:|---|
|005m|1.932583|2.117567|各10/10，无reset|
|010m|1.984605|2.198196|各10/10，无reset|
|015m|2.094102|2.322711|各10/10，无reset|

这些是名义MuJoCo物理5ms回放，不能替代实际Step7DR下PhysX任务。015m nominal2.2实际2.3227已有正向过冲但仍在原±.15门槛。没有正常FINAL/SAFE_CLOSED，不能补写PASS；有完整015m模型SHA和实际退出/GPU释放证据。保存报告包括旧monitor结束补充、handoff SIGINT记录、全部检查与回放日志，需随本阶段归档。
