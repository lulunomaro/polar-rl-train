# 供未来新case使用的私有执行链遥测（默认关闭）

[纯记录mixin](<../actuation_telemetry_v1.py>)与[MOD4v2可选plant](<../bridge_motor_telemetry_v2.py>)只旁观原方法，不重写或重算执行路径。现有运行入口未导入此adapter；本阶段没有新机器人模型、物理case或旧case重跑。

## 数据边界

每次原100Hz执行中，逐2kHz子步保存：

1. 原第一次signed-DC `clip`的输入/输出、真实改变掩码及当时轴速度。
2. 原电机增益后第二次signed-DC `clip`的输入/输出与改变掩码。
3. 原机械功率阶段后实际写入并保持的 `d.ctrl`，以及PRE tick/POST time。

每个`clip`、原执行函数及原接触评分回调均只调用一次，返回原对象；不插入积分、额外限幅、随机数、目标延迟或传感器采样。逐轴changed duty是**该限幅调用输入与输出实际发生变化的占比**，不是到达限幅轨的占比，更不是电流/热降额或硬件交付证据。最终保持力矩是仿真执行请求，不等同实测电机力矩。

这些字段仅供私有评分/诊断，**不得送回LQR、支撑力proxy或FSM**。公开SensorPacket完全未改，IMU窗口/编码器端点/电机反馈时刻仍应分别处理；同一packet epoch不是瞬时同步证明。

## 新干运行验证，非真实机器人验证

[预先定义协议](<check001/protocol.json>)与[实际结果](<check001/result.json>)：6种新的预设向量，复用冻结原执行方法/原clip方法，裸调用与新mixin开启/关闭三路对照。涵盖第一次clip后gain<1、gain>1后的第二次clip、过空载速度的有符号制动、5/10 tick D4和机械正功率缩放；另测开启后关闭不发布旧窗口。

- 761断言通过；保持力矩逐元素差 **0 Nm**。
- 基础每路120个**干运行时钟子步**，加关闭切换20步，总计380个stub时钟调用。
- **真实模型构建0、真实物理步0、旧case/raw读取0**。原方法里的`mj_step`名称在该测试的独立globals中只指向不积分的时钟stub；接触bucket同样为stub。预设q/dq并非自洽机器人轨迹。
- 仅证明新记录路径的数据传递/调用顺序等价，不是独立动力学、执行器标定、全车接入、硬件发送或WCET资格。

## 使用与当前限制

仅在将来的独占新case里由调用者显式使用`TelemetryV2Plant(model, motor_telemetry=True)`，继续原reset/DR/传感器/控制流程，执行后由私有writer立即消费`motor_telemetry_window`和`motor_telemetry_summary`。默认OFF；窗口只保留最近一次执行，异常时检查complete，不复用旧窗口。当前约束为每case新plant；已记录后若手动reset，不将上次窗口当成reset后数据，须等下一次执行生成新窗口。

M1和原v2低速旧结果的2kHz实际限幅占比仍是**未知**；本模块不补测、不追算或回写旧成绩。各接触门、LQR/K、P0原资产、当前runtime均保持原样。全车真实集成尚未测试。
