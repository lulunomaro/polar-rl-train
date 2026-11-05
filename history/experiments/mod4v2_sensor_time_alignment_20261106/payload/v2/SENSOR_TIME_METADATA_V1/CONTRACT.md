# 可选SIM传感器时间旁路元数据（未接父runtime）
- [publisher.py](<publisher.py>)仅stdlib。默认OFF，`sensor_packet()`逐字委派`super()`一次，不读时钟/包/DR；显式`configure_sensor_time_metadata(True)`后才在super前旁观时钟与窗口计数，super后发布`last_sensor_time_metadata`，返回同一原packet对象，values仍仅取原packet。没有model/SDK/DR/aligner依赖或额外step/forward。
- 调用方以后可自行用`class OptionalPlant(SensorTimeMetadataMixin, ExistingV2Plant): pass`，原继承类/工厂均未改。本轮未实例化实际Plant；启用/重置本side helper不重置原估计器、DR、原采样或RNG。
## 实际源语义
- `bridge_v2.V2Plant`继承v3 sensor_packet；V2 apply在step前累加qvel，step后读取的是dynamics PRE缓存gyro/accel。N个等间距样本位置[t−Ndt,t−dt]，`window_end_s`指最后样本，另有`aperture_end_s=t`。N20、dt=.0005时均值中心t−.00525，不是t−.005或packet名义本点。
- q4是发布源t的qpos endpoint。N0时qd/wheel_vel2退化为当前qvel endpoint；gyro/accel退化为已有cache，是否刚reset/forward不是此helper独立可证，因此timestamp=None。启动torque setter来源也None。即使q/qd端点已知，启动包整体仍非force-ready。
- D3只选择5个噪声/偏置后反馈通道；首调用用当前，后续延迟模式取上次来源，原packet名义epoch固定now−.01。source ledger只留上次描述，不读随机化配置、delay开关或私有队列，不从名义epoch推造当前窗口。
- current/previous来源必须与原packet.time_s匹配；漏周期或重复发布使其不匹配时，`packet_source_epoch_mismatch=True`、`usable_for_alignment=False`，全部歧义channel时间None；`known_pipeline_source`另留已知来源诊断，绝不改packet.time_s来掩盖。重复原packet对象保留旧标签但不给新样本/可用性信用。回退/计数归零清历史；已知坏来源影响下一延迟包也显式未知。
- `motor_tau6`并非D3队列成员：age>0且previous_torque存在时来自上次发布时ctrl快照，否则当前ctrl。已证明窗口时timestamp为最后PRE driver输出计算点t−dt，held_snapshot_epoch_s为该ctrl快照发布时刻；无来源时None。它是SIM保持命令，不是实测output torque、电流换算或现场力矩标定。
## 输出契约
- 顶层：packet_epoch_s、packet_arrival_s、source_frame_epoch_s/local source_frame_id、known_pipeline_source、source_selection_reason、reset/duplicate/mismatch/held标记、channels、usable_for_alignment；原packet的时间/值均不修改。
- channels含encoder_q4、encoder_qd4、wheel_vel2、gyro_B、proper_imu_B、motor_tau6；每个含timestamp_s/window_start_s/window_end_s/sample_count/kind/provenance/measurement_role/usable_for_alignment。boxcar另给period、aperture_end与均匀采样second moment，不把均值冒充瞬时采集。
- proper_imu_B是IMU位置BODY proper，不是chassis原点；均值BODY分量没有做旋转搬运。`measurement_role`始终区分encoder/IMU与SIM ctrl hold；values不进入本side dict。
- clock_error_bound_s、noise_error_bound、hardware_filter_delay_bound_s均None；这些SIM源代码标签不是硬件采集同步/滤波器标定。alpha_B永远None、force_input_ready永远False；不做差分、插值、误差包络或force输入构造，不依赖父signal_alignment_v1。
- 依赖现有V2/v3管线的固定PRE/endpoint/ctrl-hold语义；不证明外部改写packet数组、ctrl/cache、native时间或换publisher后的标签仍有效。显式硬件绑定仍待父决定。
## 本轮实际新stub结果与停止
- [STUB_RESULT.json](<STUB_RESULT.json>)：14/14通过，83次显式unittest assertion调用、30次预定fake source调用，失败/错误0。source调用含plain stub对照与原异常样例，不是实际DR或模拟电机。
- 覆盖默认OFF不读clock、同一返回对象/值/Python RNG cursor、首包与D3旧boot/旧mean配对、漏/重复/回退、held旧对象、时钟/计数未知、exact-bool、原super异常保持；不是物理管线动态验收，也非硬件时钟校准。
- 测试仅[test_publisher.py](<test_publisher.py>)的一次新运行；real model/FK/forward/physics/DR/旧QA/Git/Goal/新代理/硬件调用均0。旧publisher/bridge/CONTACT_PROXY封存三姿态/父aligner均未改，现交付后停止。
