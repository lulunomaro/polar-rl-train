# 狭窄派生 patch / 第一阶段工程资格

1. `derived/StandardRobotpp-balance1` 已复制391份原bytes，来源/SHA/CRC/编码见SOURCE与COPIED_ORIGINALS。修改前的两个原文件另存before，统一diff与可逆old/new片段记录SHA。原selected/source_original/ZIP完全不写，原型可原样回滚。
2. `application/chassis/chassis_balance.c`：include新bridge；ChassisConsole先做本周期capture/gate；仅普通运行及STAND_UP映射可运行，OFF/SAFE请求STOP，calibrate/debug/offhook等未审模式不开放；ChassisSendCmd先最后freshness/clock/expiry复核，未RUN不进入旧发送者。没有安装provider/人工arm时默认NONE，不自动FC，也不将“静默”冒充真实停机。
3. ConsoleStandUp废弃未赋值double joint_pos_l/r和相关theta_transform读取。只从本周期owned decision取得valid raw-motor-rad qref4，并写4个set.pos；旧机械clip和旧wheel PID保持原式。missing qref不初始化位置为0、不读旧栈垃圾，bound状态发独立STOP请求而非position。q坐标转换/范围/cookie由外部实证provider提供，非MOD4默认参数。
4. SendJointMotorCmd的cnt改static uint8_t cnt=0，保留原pacing结构。legacy RUN内部自动FC分支加always-false retired-path gate：enable只走显式ENABLE_ONLY action sink；在反馈enabled ACK齐备前不RUN。默认没有sink/provider，所以没有真实CAN/SPI动作。STOP与DISABLE枚举与sink请求独立，MIT0不称FD。
5. `MDK-ARM/standard_robot.uvprojx`：只改派生target/output名称、追加application/mod4_port include及4个新C/header成员，禁用自动flash-before-debug/TargetDll flash入口；原compiler/MCU/12MHz时钟/旧gains/库路径保留。BeforeCompile/BeforeMake/AfterMake原run0不启用。手动IDE/外部flash工具不构成本工程硬件隔离保证，本轮零目标build/执行/刷写。
6. 新C99 gate caller-owned fixed POD；bridge为单chassis-task owner的显式安装facade，启动无config/clock/packet/stop callback fallback。外部必须绑定map/codec/ranges/原始motor-q坐标/startup/time/STOP sink，六轴实际反馈时效及fault、显式operator arm和enable授权；enabled-ACK不齐仅ENABLE_ONLY。source失联/clock/fault锁存到重新显式init；本周期最后复核失败清RUN/qref并请求DISABLE。
7. 新服务只声明接口，不自行选择DM3519/DM8009P/gear/ID，也不执行原MF9025/LK与±10Nm当MOD4映射。未来model代理站起API可通过qref provider连接；当前没有复制新leggain或把Python候选接入旧target。
8. host仅新gate+bridge+synthetic smoke，一次<=40 CHECK，不运行旧工程main/uvproj/bat/hooks、不编译旧controller/BSP、不访问CAN/SPI/PHY。旧发送循环仍非atomic6轴/ACK/post-return deadline/WCET资格；完整target link及库/Pack/脚本审查另待父批准。
