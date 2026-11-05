# 显式频道时间＋有界历史对齐（观测接口，不是力反馈控制器）

## 本次实际交付

- [实现](<../signal_alignment_v1.py>)：仅Python标准库，无MuJoCo/NumPy/DR/控制器/力模型导入。
- [一次新合成验证](<check001/result.json>)：224断言，仿射量最大绝对差2.77556e-17；真实model/forward/FK/物理/旧raw/求力/硬件发送均0。
- [固定协议](<check001/protocol.json>)：未在结果后放宽1e-11算术比较容差；[验证源码](<../verify_signal_alignment_v1.py>)只创建新合成信号，不读取机器人轨迹。
- 本目录check001已消费，不作为后续例行QA重跑。

## 接口与严格区分

`ChannelSpec(name,dimension,rate_bound_abs,curvature_bound_abs)`声明各轴一阶/二阶变化界；这些界必须由调用方另行证明/标定，不通过两个样本反推“已知”。

`ChannelSample`携带真实来源中心、start/end、sample_count、point/sampled_mean、来源说明，以及可选clock/noise/窗口二阶矩界。`None`表示未知；缺时间用`push(name,None)`，禁止补成packet.time。

`SignalAligner.push`按每频道保存至多8个样本；相同来源相同内容只算held，改内容的同epoch包或时间倒退锁存，需显式reset。reset只是软件历史复位，不是电机停止/自然起立。

`query(now)`取所有频道最新中心的最小值作为公共**计算时刻**，从每频道历史找实际两端观测，做凸权重插值；不外推、不把现在的数值直接换旧标签。默认最大age30ms、bracket gap20ms，使用的源窗口起点也须新鲜。没有新公共时刻则不给重复导数样本。

输入主动hip/crank必须已为真实连续角；本接口不会独立wrap两轴或改变机械分支。角速度/加速度与载荷等物理约束仍属上游/下游责任。

## 平均窗口不是瞬时样本

若连续信号逐轴二阶导界为B2，一阶导界B1，窗口实际采样关于声明中心的二阶矩为V，则解析误差预算为：

`0.5*B2*((t-t0)*(t1-t) + w0*V0+w1*V1) + B1*(w0*clock0+w1*clock1) + w0*noise0+w1*noise1`。

单端点命中时第一项的插值部分为0，窗口偏差部分仍保留。任一必要界未知则`error_bound_abs=None`，保留原因，不给0占位。此字段是**基于声明成立的连续信号解析包络**，不是已认证的浮点/硬件总误差界；check001比较另带1e-11算术容差，因此解析0也不表示计算/传感器零误差。`numeric_bounds_complete`仅表示上述声明齐全，不是校准概率或系统资格。

恒加速关节位置使用线性插值并非严格精确；新测试核对其曲率界包住偏差。曲率gyro的20点均值存在8.31250e-7偏差，未因统一计算时刻抹掉。20点/0.5ms例的窗口方差约8.3125e-6 s²。

## 另一个已交付组件及接线边界

[生产时间旁路](<../SENSOR_TIME_METADATA_V1/publisher.py>)与[契约/结果](<../SENSOR_TIME_METADATA_V1/CONTRACT.md>)已由原E4完成并停止：14个新stub测试/83断言/30次fake source调用，真实模型/物理/旧QA均0。父已读实际源码/结果并对照现有bridge字段；未重跑child测试。

这是两个分别验证的接口，**不是实际Plant端到端测试**。producer的`endpoint/sampled_boxcar/held_command`与本接收器`point/sampled_mean`需要显式归一化与measurement role检查；point的start/end应在已知单点时明确设为自身时刻，未知窗口仍未知。当前未提供自动归一化、SensorInput或runtime接线，不能直接把producer dict丢给接收器就声称完成。

## 明确保留的未完成项

- `force_input_ready=False`、`hardware_sync_proven=False`、`alpha_B_rad_s2=None`始终保留。本模块不制造alpha、编码器qdd、IMU到chassis-origin补偿、力矩标定/符号/独立力通道。
- proper_imu_B仍是IMU位置的proper观测，不是CONTACT_PROXY所需chassis-origin proper；对齐不等于完成杆臂补偿。
- motor_tau6在现有模拟发布器中是driver保持命令，不是实测电机输出力矩。测试中的仿射motor信号只验证数学传输；真实保持量的跃变缺有限曲率界时仍未知，不把插值输出当实测力矩。
- 来源D3标签需由实际生产链另外提供；若packet名义epoch和实际source不一致，保留不一致/不可用于对齐状态，不从当前窗减10ms猜值。
- 没有SensorInput/CONTACT_PROXY/FSM/控制器自动接线；原3ms skew门、.55 cap和.8 trusted阈值均未改。没有补填相同时间戳来绕过这些门。
- 新发布器/本接口均为可选旁路；旧runtime、K、PD→D4→当前PD→DC→gain→DC、碰撞及筛选门均未改。M1接触门失败未变，本阶段真实新增物理0，能力进度仍0/36。
