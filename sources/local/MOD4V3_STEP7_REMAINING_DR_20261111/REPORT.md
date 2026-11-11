# 剩余DR合并轮：启动准备

2026-11-11，Asia/Shanghai。用户已明确开训。已在独立support快照实现合并范围，父push020m固定；不改变原冻结/旧运行/原始报告。源差异与范围见PLAN/README。

64env×320策略步固定父权重探针完成，无PPO更新；COM、质量、startup摩擦跨reset无变化，719步不重采/720步选中env重采通过，native气弹簧阻尼范围与实际采样相符。numerical0、最大主动关节速度68.31rad/s；闭链峰2.402mm，12次单env闭链reset，完整保留，不把它写成零reset或整批失败。4096同协议短测正在执行，主训练尚未启动。

此文件为准备状态；实际启动、训练完成及选择结果后续追加，不将计划当完成。

## 主训练实际启动

4096env×320步固定父探针完成：numerical0、关节峰114.24rad/s、闭链峰3.007mm，665次closure单envreset，push5069次。参数读回/生命周期检查全部通过；不把reset写成零或增加整批门槛。探针退出并释放GPU后，主轮已于2026-11-11 09:25:12（Asia/Shanghai）启动，PID976445。实际PPO更新起点约09:25:49，目标2400s，首个300s检查点按更新时钟。

STARTUP实际profile flat_remaining_dr，父push020m SHA与iter22141一致。RESTORE完整actor/critic/std/Adam及RNG、fresh物理episode；PPO fixedLR3e-5、clip.1、epochs3回读一致。首update iter22142、actor_changed=true，完整model_first_complete.pt存在并SHA核对；新增DR字典实际包含COM/friction/Kp/Kd/gas damping/material/push timer等字段。没有沿用上一轮新增字段未落盘的问题，仍不承诺精确物理瞬时状态续接。

主训练中的刚开始closure重置主要集中首个update，后续按原单环境重置继续记录；numerical保持0。运行源码对照上传快照SHA一致，不热改。五分钟本机监测已启动，训练结束后用相同新DR样本配对父、主冻结与本轮检查点。尚未有本轮固定任务成绩，不能据rollout均值宣布适应完成。

## 首个5分钟检查点

model005m iter22203、实际301.465s，SHA71df98c5d5c50f1407175cd60b7c4760618287cf5477a760884061494ec71594，完整11,044,601bytes已下载并核对。名义MuJoCo固定回放：前进2.0→2.10064（10/10）、2.2→2.33392（10/10），后退/旋转/高度.20/.40各10/10，全部无reset。不是fullDR同源成绩。训练继续numerical0；新增分布的闭链单envreset保留，原2mm阈值和原权重不变。

准备轮末配对脚本时，原字符串缩进替换未命中，读代码发现native damping镜像/名义中和和ground命令清除遗漏；在该脚本首次执行前已修正，见EVALUATOR_PREPARATION_FIX。此更正仅改尚未运行的评测脚本，不改训练中support，没有无效评测结果冒充通过。


## 10至20分钟检查

完整检查点010/015/020m均已下载并按远端SHA核对，均包含完整PPO和新增DR字典。名义MuJoCo回放2.0/2.2速度分别：010m为2.13523/2.38568，015m为2.12125/2.37876，020m为2.17302/2.44698m/s；后者两个前进任务因超速均0/10，其余四项各10/10，所有这些名义回放无reset。它们没有证明完整DR适应完成，不能抹去超速或凭训练均值替代固定成绩。训练numerical继续0，2mm闭链单环境reset照常累计，运行source没有修改。


## 25和30分钟检查

025m iter22443、1504.341s，名义2.0→2.05548、2.2→2.28967；030m iter22501、1801.557s，名义2.0→2.03992、2.2→2.25583。两份六正式任务各10/10，全部无reset；前面010–020m超速记录保留。完整PT下载核SHA，numerical仍0；完整DR同源配对尚未执行。


## 本轮完成

主训练和配对评测正常保存关闭。最终选择remaining_010m，2.0→1.90988（4/10）、2.2→2.18903（6/10）；正式任务39/60、reset=0；详细结果见FINAL_REPORT.md，原始证据未覆盖。
