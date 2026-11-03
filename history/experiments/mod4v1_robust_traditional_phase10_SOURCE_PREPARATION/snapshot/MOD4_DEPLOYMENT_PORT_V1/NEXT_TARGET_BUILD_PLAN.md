# 下一次完整target构建的审批清单（本轮不执行）

1. 当前只是文件级闭包齐备：原165 member +新2C/2header=169，initial391+父supplement32都按raw SHA/CRC复制，427个derived文件。Windows大小写alias 6个有据；368个reachable lexical text node的include图含未求值条件，不等于真实预处理/可link。具体未知见BUILD_CLOSURE_FINAL。
2. 原target指定ARMCC5.06 update4(build422)，DevicePack Keil.STM32F4xx_DFP2.17.1，RTE CMSIS5.8.0。父需批准准确工具路径/版本、Pack来源与可读取范围；不可因已装ARMCLANG6就静默迁移compiler。C99=1、EnumInt=0/short-enum相关、FPU2、--diag_error=warning等照原flags；host GCC struct sizeof不代表ARMCC ABI。
3. AHRS.lib和arm_cortexM4lf_math.lib只是从父批准成员拷贝的opaque bytes。下一审批可仅静态检查各对象的CPU/Thumb/FPU/calling ABI/enum/wchar/符号兼容性，不执行算法；不得从M4lf文件名推hard-float ABI，更不换stub或删music以拼出假成功。
4. 之后批准时优先在隔离output编译实际derived source，允许只编译/链接、不启动uvproj的hooks或flash/debug。运行前再次核派生BeforeCompile/BeforeMake/AfterMake的run0/name空、UseTargetDll0/UpdateFlashBeforeDebugging0/UseExternalTool0。手工IDE/外部flash依然属于另一步，不将这些XML开关说成物理隔离。
5. startup/memory/HSE12MHz/CAN/IMU底座留原值。首次完整编译/链接需保存真实argv、依赖、警告/错误、map、全部U/重复符号、actual startup/vector/FLASH-RAM-CCM布局、lib/helper选择与产物SHA；失败留档，不靠放松诊断/临时伪造协议通过。
6. 默认无mdp1_services/config/clock/startup/反馈/arm绑定，旧chassis motor发送门被关；这不证明整个固件所有CAN来源静默、已停旧硬件或6轴原子截止期。实际MOD4 wheel型号/firmware/gear/ID/方向/zero/current-torque/stop与expiry等仍未知；旧MF9025/LK、generic DM±10Nm、normal±7Nm均不是MOD4物理参数。
7. 下一动态或刷写许可还需独立复核packet原子性、per-axis sample/arrival/age/fault/ACK、64bit monotonic提供者、single-owner并发、STOP/DISABLE sink与总线错误/电机故障/失联/硬件watchdog、每轴driver-rate envelope/量化/实际保持命令，及供电/机械支撑/急停。当前40个host CHECK仅接口候选，不宣称完成这些资格。
8. model代理sensor-only起立候选未来接显式motor-qref4 provider，先验证model→motor坐标/limits/时域；本轮未接其控制器、未选leg gains、未重写旧wheel stand-up PID，也未生成任何真实CAN/SPI动作。
