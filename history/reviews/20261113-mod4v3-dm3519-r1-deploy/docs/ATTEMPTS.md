# 本阶段真实尝试与结果

本阶段从旧 LQR ZIP 创建独立固件，冻结策略沿用 R1 round2/005m，iteration22959。无新增训练，无实物端口操作，无烧录。用户确认只换两个轮电机、独立 DM3520；最终把标定参考从先前讨论的后折姿态改为模型初始零位。

| 实际尝试 ID | 当次结果 | 证据与处理 |
|---|---|---|
| keil_attempt1 | 失败 | 旧工程指定 ARMCC5.06u4，本机只有u6。保留 `reports/keil_attempt1.log`，仅更新副本工程的编译器版本。 |
| portable_attempt1_windows_reader | 读取器失败 | MinGW编译为32位，Python为64位，ctypes报WinError193。初版runner未及时写报告，错误与缺失的C测试输出如实记入 `portable_attempt1_reader_failure.json`；未据此宣称通过。 |
| portable_attempt2_linux | 部分通过/整体失败 | 16组参考向量通过；7项控制/协议测试中使能回包等待测试失败。证明驱动在70ms后确认使能时，被策略40ms间隔检查误拦。 |
| portable_attempt3_handshake_fix | 通过 | 仅在已经生成首个策略目标后检查策略间隔；使能确认仍有自己的100ms上限。7项控制/协议测试和16向量通过。 |
| keil_attempt2 | 失败 | 新板级文件没有声明已有的 `hUsbDeviceFS`，1个编译错误。加入与原USB文件一致的extern声明。 |
| keil_attempt3 | 通过 | 全工程0错误0警告；ARMCCu6，首次成功链接含完整策略权重的固件。 |
| upper_attempt1 | 通过 | Linux真实PTY串口：命令合同、100ms失鲜、明确重使能、CRC、逐字节遥测、断连。未使用ROS替身。 |
| keil_attempt4_optimized | 通过 | 新RL源码组O2、2ms任务使用绝对节拍等待。全工程0错误0警告。此时临时零位参考为后折姿态。 |
| portable_attempt4_rear_pose_config | 通过 | 后折参考的临时配置下，7项控制/协议与16向量通过；后来由用户新指令取代。配置原文保留在 `reports/superseded`。 |
| ros_attempt1 | 失败 | Ubuntu22.04/ROS2Humble可用，但默认GCC11不提供上游需要的 `<format>`；失败发生在真实RMCS executor构建，新插件未在该次运行中构建。 |
| gcc13_extraction_attempt1 | 失败 | 初次取包遗漏新版仓库拆出的x86-64编译器包，g++软链接目标不存在。没有更改系统apt源或全局安装。 |
| gcc13_private_packages_attempt2_arch_packages | 下载验证通过 | 从同一Jammy工具链索引补齐架构包，校验每个deb的SHA256。GCC13.4.0及库私有解包成功。原第一次取包清单和失败记录保留。 |
| portable_attempt5_model_zero | 通过 | 最终模型初始零位；新增零位映射验证，共8项控制/协议测试及16参考向量通过。 |
| keil_attempt5_model_zero | 通过 | 模型初始零位版本，全工程0错误0警告。 |
| keil_attempt6_final | 通过 | 补齐RL板级文件的编译开关边界后，最终全工程0错误0警告。Code91780、RO216924、RW848、ZI58576字节。 |
| ros_attempt2_gcc13 | 通过 | 原版钉住的RMCS utility、executor，加本次底盘插件，共3个真实ROS包构建成功。保留上游头文件安装提示，未改写上游格式化或调度代码。 |
| ros_loopback_node_attempt1 | 通过 | 真实独立ROS节点，99帧命令、369条合成状态回传。验证vx/wz/height、ARM、超时、禁止自动重使能、明确重使能、ESTOP和状态话题。 |
| ros_loopback_rmcs_attempt1 | 通过 | 真实RMCS executor加载新插件，95帧命令、367条合成状态回传，同样8项链路检查通过。 |
| archive_attempt1 | 提交前拒绝 | Git对中文路径加引号，归档范围校验将其与未转义路径比较，发生断言。没有创建commit/tag。保留原未提交草稿、清单及ZIP，在同一阶段修正为NUL分隔路径并恢复提交。V1 ZIP保留，V2补齐此归档修复和证据。 |

编译器包、RMCS、手册、权重来源都有原路径和SHA。早期修复前的完整源码快照没有逐次另存；原失败日志、具体报错和修复说明保留，最终源码及其哈希完整归档，不能把这些日志称作每次旧源码的完整快照。

## 最终证据和未完成项

最终冻结 C 策略4个原交付文件会在封装时逐字节核对；最终 `VALIDATION_SUMMARY.json`、`FIRMWARE_PATCHES.json`、`SOURCE_INDEX.json` 和 `DELIVERY_MANIFEST.json` 提供来源、改动与交付哈希。生成的AXF/HEX明确标为MODEL_ZERO_UNCALIBRATED，配置中的实车标定标志为0。

软件验证不包括：实车正反方向/零偏/IMU测量；DM3519真实转矩、外置传动和温升；STM32上实际推理/PD/CAN时限；完整相机/自瞄/云台联调。先前的气弹簧200mm起立结果属于原标称执行器MuJoCo证据，不当作本次换电机的实车结果。

普通文件搜索遇到不存在的预期输出文件，并非额外物理或策略实验；没有为补报告重跑旧训练、旧起立试验或已消费的正式试验。
