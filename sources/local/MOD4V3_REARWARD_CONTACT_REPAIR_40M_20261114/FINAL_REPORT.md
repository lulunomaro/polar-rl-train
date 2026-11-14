# 真正搭阶承重奖励归类修复：原40分钟剩余预算结果

本阶段实际PPO 1344.257秒；本阶段预算1344秒，前阶段1055.181秒，原整轮计划2400秒。综合父db6e9ccf/iter25331完整恢复；训练真实台面支撑后的后摆抬轮与落轮站立，旧高速台阶BC关闭。没有自动延长。

实验候选：rearward_contact_repair_20261114_final，SHA b2c2824c67f79b8db1bd979e35550380d2c5033aaf604846bb7a1730dac66d0b。完整PT见weights/selected_specialist_student.pt。

| 保存点 | 低速双阶/4 | 辅助第一阶/2 | 后摆中段/3 | 平地/60 | 原快速正向/5 | 原快速斜向/20 | 下阶/5 | 前进MAE(m/s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|model_020m.pt|0|0|0|50|0|0|5|0.128288|
|model_025m.pt|0|0|0|50|2|0|4|0.120975|
|model_030m.pt|0|0|0|50|0|0|5|0.123969|
|model_035m.pt|0|0|0|60|0|0|5|0.076232|
|model_final.pt|0|0|0|60|0|0|5|0.043191|

同协议父低速整程0/4、辅助第一阶0/2，见../MOD4V3_REARWARD_RECOVERY_40M_20261114/evidence/parent_low_speed_r1。原高速基线和新低速协议分开解释。全部失败和训练保护保留；实验候选不自动替代综合父。

## 原生复核

|科目|模型|条件|数量|
|---|---|---|---:|
|stairs|parent|fullDR|0/100|
|stairs|parent|nominal0|0/100|
|stairs|student|fullDR|0/100|
|stairs|student|nominal0|0/100|
|retained_traverse|parent|Step7_all_remaining_DR|173/200|
|retained_traverse|parent|nominal0|178/200|
|retained_traverse|student|Step7_all_remaining_DR|175/200|
|retained_traverse|student|nominal0|166/200|
|retained_gyro|parent|Step7_all_remaining_DR|99/100|
|retained_gyro|parent|nominal0|100/100|
|retained_gyro|student|Step7_all_remaining_DR|99/100|
|retained_gyro|student|nominal0|100/100|
|retained_landing|parent|Step7_all_remaining_DR|80/80|
|retained_landing|parent|nominal0|80/80|
|retained_landing|student|Step7_all_remaining_DR|78/80|
|retained_landing|student|nominal0|80/80|

两引擎协议分别解释。原生台阶精确逐环境成绩以post_native/stairs/RESULT.json为准；rough穿越、首6秒旋转存活、落地指令恢复沿用原L9协议，不混作完整地图或主动跳跃毕业。

修改范围：上行0.35–0.75m/s；上行30%辅助底盘搭阶起步，单列不冒充整程；仅真实上台面承重局部接触豁免；原0.6抬轮额度拆成0.12支撑事件+0.24独立后摆进度+0.24独立抬升进度；初始进度不领奖；新增3个后摆中段辅助姿态及194帧/4条真实单阶恢复参考，仅腿动作监督0.25；真实落轮奖励沿用；落轮后恢复站高跟踪；旧高速台阶BC和在线示范池关闭；仅真实搭阶承重期间禁用腾空奖励段，原状态位恢复；参考四阶段均衡；父综合保留1.0及高站姿.25。原40/35/25配比、速度奖励、完整DR、35/78/6、MOD4电机与时序不变。每5分钟完整保存及检查记录在evidence/inspections。

## 本轮判定与有针对性的后续

原两阶段总PPO 2399.4383149147034秒；没有追加预算。低速目标尚未实现，候选不替代综合父。

真实卡住父快照root越沿52.3mm、全机器人COM只越沿2.1mm，车身/导轮相邻1s平均支撑5.86N；现有成功参考却从185–205mm更深入姿态起步，未覆盖实际受阻到稳定承重这一段。25m参考抬轮后交学生未站起，同前缀交父可站起；起始和落轮接续都未解决。

冻结探针支持/airborne同现计数0，奖励归类冲突不能认定本轮失败主因。参考脚本姿态立即退出已在独立r2中改为原40deg/0.2s计时复核，真实受阻36条仍0恢复；训练和正式固定回放未改门槛。

下一项最小实验见NEXT_REPAIR_PLAN.md：复用已有17个真实受阻起点，先单独训练支撑转移和后摆，再以父全部6动作保留落轮接续；当前未自动启动。

## 收尾补充

全部固定回放与四项原生复核已关闭。落地原生评测的完整运行累计记录1次数值重置，原记录保留，不能称所有数值计数均为0；首回合成绩仍按原协议统计。额外“近最大目标腿长先后摆、再收腿”的36条真实受阻脚本测试也未稳定恢复，全部原件已保留，不作机构不可能的结论。当前模型仅平地60和下阶5回到原固定基线，快速正向0/5、低速0/4，所以没有晋升。完整PT本体已按普通Git对象核验12份，原归档提交b0091fe26b7980c46569d782417da26c66c33895；本次补交归档回执和最终口径，无任何新训练。
