# 视频式底盘搭阶后摆抬轮40分钟：结果

实际PPO 2406.636秒；计划2400秒。综合父db6e9ccf/iter25331完整恢复；训练真实台面支撑后的后摆抬轮与落轮站立，旧高速台阶BC关闭。没有自动延长。

实验候选：rearward_supported_stairs_20261114_010m，SHA c603747b992a6f58822d0eff7b10c94c73c366ea31fb3134778c372883924573。完整PT见weights/selected_specialist_student.pt。

| 保存点 | 低速双阶/4 | 辅助第一阶/2 | 平地/60 | 原快速正向/5 | 原快速斜向/20 | 下阶/5 | 前进MAE(m/s) |
|---|---:|---:|---:|---:|---:|---:|---:|
|model_005m.pt|0|0|60|4|0|5|0.032162|
|model_010m.pt|0|0|60|5|6|5|0.039313|
|model_015m.pt|0|0|50|5|8|5|0.172662|
|model_020m.pt|0|0|50|5|8|5|0.150111|
|model_025m.pt|0|0|50|4|6|5|0.153708|
|model_030m.pt|0|0|50|4|7|5|0.148733|
|model_035m.pt|0|0|40|2|2|5|0.208255|
|model_040m.pt|0|0|50|4|4|5|0.120591|
|model_final.pt|0|0|50|4|4|5|0.120591|

同协议父低速整程0/4、辅助第一阶0/2，见evidence/parent_low_speed_r1。原高速基线和新低速协议分开解释。全部失败和训练保护保留；实验候选不自动替代综合父。

## 原生复核

|科目|模型|条件|数量|
|---|---|---|---:|
|stairs|parent|fullDR|0/100|
|stairs|parent|nominal0|0/100|
|stairs|student|fullDR|0/100|
|stairs|student|nominal0|0/100|
|retained_traverse|parent|Step7_all_remaining_DR|173/200|
|retained_traverse|parent|nominal0|178/200|
|retained_traverse|student|Step7_all_remaining_DR|172/200|
|retained_traverse|student|nominal0|178/200|
|retained_gyro|parent|Step7_all_remaining_DR|99/100|
|retained_gyro|parent|nominal0|100/100|
|retained_gyro|student|Step7_all_remaining_DR|99/100|
|retained_gyro|student|nominal0|100/100|
|retained_landing|parent|Step7_all_remaining_DR|79/80|
|retained_landing|parent|nominal0|80/80|
|retained_landing|student|Step7_all_remaining_DR|79/80|
|retained_landing|student|nominal0|80/80|

两引擎协议分别解释。原生台阶精确逐环境成绩以post_native/stairs/RESULT.json为准；rough穿越、首6秒旋转存活、落地指令恢复沿用原L9协议，不混作完整地图或主动跳跃毕业。

修改范围：上行0.35–0.75m/s；上行30%辅助底盘搭阶起步，单列不冒充整程；仅真实上台面承重局部接触豁免；原0.6抬轮额度改为0.12支撑事件+0.48后摆抬升新增进度；真实落轮奖励沿用；落轮后恢复站高跟踪；旧高速台阶BC和在线示范池关闭，父综合及高站姿保留。原40/35/25配比、速度奖励、完整DR、35/78/6、MOD4电机与时序不变。每5分钟完整保存及检查记录在evidence/inspections。
