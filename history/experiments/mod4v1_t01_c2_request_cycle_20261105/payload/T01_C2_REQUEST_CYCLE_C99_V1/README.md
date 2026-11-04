# C2请求调用者：期限检查与失效隔离

[接口](<pc2_request_cycle.h>) / [实现](<pc2_request_cycle.c>) / [新mock检查](<host_check.c>) / [预声明协议](<build001/protocol.json>)。

本模块迁移[旧pc3_dispatch的guard顺序](<../SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c>)，改接已有[C3→C2传感控制链](<../T01_C2_SENSOR_CHAIN_C99_V1/pc2_sensor_chain.h>)。没有修改旧C3、CTK、C2参考/力矩算法、K或物理模型。

## 接口边界

- 使用独立pc2_requested_frame/pc2_enqueue_requested类型，避免把未执行内环的requested torque误当作旧pc3_actuation。
- 全零binding返回UNBOUND、无enqueue。所需bindings及执行顺序字段只是调用者声明，**不是硬件实现/标定/绑定的证据**；交付中没有真实binding/BSP调用点。
- 声明的执行顺序是：名义PD目标反解→目标D4→当前PD→有符号DC→motor gain→再次DC。此调用者**不加额外外环DC预裁剪**。实际内环/总线/功率/电机限制仍在外部，尚未接通。
- 复用命令enable/序号/issued/expires、反馈标记/年龄/有限性、原100Hz周期，以及计算后/入队后的时钟/年龄检查。TTL最多10ms；时间检查不等于执行抢占或硬实时上界。
- 正常路径至多一次enqueue尝试。回调报错、入队后过期或时钟后退时，清除输出valid、锁存、退出估计器armed并调用声明的disable_and_invalidate。后者必须真实失能并清空待发项；本模块/模拟回调没有证明物理停止、TX完成或取消已发报文。
- NULL/alias/未初始化属于前提错误，不保证外部失效隔离。调用者必须检查返回码并自行抑制真实驱动，勿复用旧frame。回调/context必须可信、非重入、不改输入；原子复制/并发/中断保证由真实适配器提供。
- 初始化只重建估计器/控制状态，不物理arming，也不清真实队列；调用者需先inhibit/drain再初始化。静态/支持直立先验仍需显式声明，不代表自然摊卧起立。

## 新测试范围

只使用内存mock时钟、队列与失效回调，没有CAN/硬件/物理步/旧raw或holdout读取。预声明3次正常请求、16个故障场景、2个NULL/alias前提场景；两次故障场景另有准备用正常请求。与同一现有C3→C2直接调用核对requested torque，不构成第二个独立算法oracle。

合成20rad/s反馈边界专用于检查**未额外DC预裁剪**：它与该fixture的编码器速度不一致，不是可信实车轨迹。当前层只核反馈标记/年龄/有限性，没有新增实际通道采样一致性或校准检查，真实绑定仍未完成。

## 已实际收集的结果

[结果与完整命令](<build001/result.json>)：job pwsh-aaaf650429fe486b已收exit0，不再启动build001。

- GCC C99/O2/Wall/Wextra/Werror/fno-fast-math编译exit0、原生执行exit0。
- 3次正常请求、16个故障场景、2个前提场景，246条断言通过。与同一现有传感控制链直接调用的原始请求差0；20rad/s人工反馈边界确认未多加外层DC裁剪。
- 命令过期/未来issued、enable、旧序号、反馈过龄、NaN、时钟后退、入队后超时/返回错误、传感mean错误和控制周期错误等分支均检查锁存与mock队列失效；all-zero binding无enqueue。NULL/alias前提未改对象，与物理停机保证明确分开。
- host cycle928B/frame72B，原生整批0.097096s含检查/进程输出，不是单步WCET。
- 新增单个请求调用者TU实际armclang编译：Cortex-M4 fpv4-sp-d16 hard对象3940B；Cortex-M7 fpv5-sp-d16 hard对象3988B，2/2 exit0。只检查新对象52字节ELF32小端/ET_REL/EM_ARM头；对象大小不是Flash/栈量。没有重跑旧ARM/数学QA，没有最终ARM链接/运行。
- 0物理步/真实硬件发送/旧case或holdout读取/新K；未操作试玩或V3回放。真实BSP、驱动顺序实现、通道一致性、校准、功率、硬实时和HIL仍未接通。

本轮实际代码为[请求接口](<pc2_request_cycle.h>)和[实现](<pc2_request_cycle.c>)；[检查脚本](<build_check.py>)使用exist_ok=False保留唯一build001，勿为归档重新执行。

T01原严格支持失败、三候选计数、J200落地失败和35项后续任务状态均不变；本模块不使T01毕业。
