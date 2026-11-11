# 剩余DR合并轮：启动准备

2026-11-11，Asia/Shanghai。用户已明确开训。已在独立support快照实现合并范围，父push020m固定；不改变原冻结/旧运行/原始报告。源差异与范围见PLAN/README。

64env×320策略步固定父权重探针完成，无PPO更新；COM、质量、startup摩擦跨reset无变化，719步不重采/720步选中env重采通过，native气弹簧阻尼范围与实际采样相符。numerical0、最大主动关节速度68.31rad/s；闭链峰2.402mm，12次单env闭链reset，完整保留，不把它写成零reset或整批失败。4096同协议短测正在执行，主训练尚未启动。

此文件为准备状态；实际启动、训练完成及选择结果后续追加，不将计划当完成。

## 主训练实际启动

4096env×320步固定父探针完成：numerical0、关节峰114.24rad/s、闭链峰3.007mm，665次closure单envreset，push5069次。参数读回/生命周期检查全部通过；不把reset写成零或增加整批门槛。探针退出并释放GPU后，主轮已于2026-11-11 09:25:12（Asia/Shanghai）启动，PID976445。实际PPO更新起点约09:25:49，目标2400s，首个300s检查点按更新时钟。

STARTUP实际profile flat_remaining_dr，父push020m SHA与iter22141一致。RESTORE完整actor/critic/std/Adam及RNG、fresh物理episode；PPO fixedLR3e-5、clip.1、epochs3回读一致。首update iter22142、actor_changed=true，完整model_first_complete.pt存在并SHA核对；新增DR字典实际包含COM/friction/Kp/Kd/gas damping/material/push timer等字段。没有沿用上一轮新增字段未落盘的问题，仍不承诺精确物理瞬时状态续接。

主训练中的刚开始closure重置主要集中首个update，后续按原单环境重置继续记录；numerical保持0。运行源码对照上传快照SHA一致，不热改。五分钟本机监测已启动，训练结束后用相同新DR样本配对父、主冻结与本轮检查点。尚未有本轮固定任务成绩，不能据rollout均值宣布适应完成。
