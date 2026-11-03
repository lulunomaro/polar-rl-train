# 两条当前主交付：摊卧起立与真实旧机工程接入

## 结论
旧机接入已有实体源码工程交付；首个真实摊卧启动试验未站稳。二者分别记账，不用host编译、合成跟踪或直立初始化成绩代替物理起立能力。

## 1. 工程接入第一阶段已交付
- [派生Keil源码包，5,900,131B/456entry](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_PORT_V1/mod4_deployment_port_stage1.zip>)，SHA `58ad988be5dcb53d0079d20bd6bff4852f079629a37fcfe9d33724631320fb8b`。
- [说明](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_PORT_V1/README.md>) / [完整阶段收据](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_PORT_V1/RECEIPT.json>)：独立派生427文件，原165+新增4个project成员齐备；423来源保持原字节，仅派生树内两份继承文件窄patch，另增2C/2header。
- 实际改动：初始化持久发送计数器，移除STAND_UP未赋值位置数组读取；显式motor-coordinate qref、时域/坐标/范围、人工arm、六轴fresh enabled-ACK及故障门；ENABLE_ONLY/RUN/STOP/DISABLE分离。缺参考不发默认零位置，默认无provider/config/arm。
- 首次严格C99 host检查40/0；完整target编译/link、真实CAN/SPI和刷写不属于这40项的资格。旧MF9025/LK、generic DM±10Nm/normal±7Nm未冒充MOD4执行器参数。
- [静态build准备](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_BUILD_PREP_V2/REPORT.md>)：本机ARMCC5.06u6.750与工程声明u4.422不同；34唯一include目录有一项路径缺失，其active需求未预处理证明；已知位置CMSIS/RTE版本也有差异。两库只作成员/代表对象属性检查，不是全部ABI/运行时认证。
- 父已单独发出[隔离首次compile-only范围](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_TARGET_COMPILE_V3/PARENT_COMPILE_SCOPE.json>)：明确采用u6作为新variant，不改封存工程；有效argv先冻结、每实际TU一次、首个真实错误即停、0link/UV/hooks/flash。此处只记录已发范围，不宣称编译已成功。

## 2. 真实摊卧启动首案未交接站稳
初态来自自然零力矩落稳的前倾姿态：机身约22°、rootZ约0.2371m、轮与导向轮接地。仅案例初始加载保存的qpos/qvel一次，此后无root覆盖/辅助力；IMU不强制直立，原20×0.5ms传感器与原执行器/接触/闭链路径保持。

|实际阶段|命令时间|
|---|---:|
|OBSERVE|0.00–0.30s|
|SHAPE_TO_STAND|0.31–2.30s|
|VERIFY|2.31–5.99s|
|INHIBIT，startup timeout6s|6.00s|

- 实际消费 **601 controls / 12,020 physics steps**；没有BLEND/BALANCE。不是计划1000/20000全部完成。
- VERIFY的3/4/5s估计pitch约0.672/0.698/0.674rad、关节参考误差约0.096/0.111/0.101rad，超过原交接门限0.15rad/0.04rad；不是已ready却未交接。
- 6.01s保存的实际pitch约0.6334rad、rootZ约0.2772m；6.00s PRE根节点x约13.195m，相对初态约13.16m前冲。双轮请求在3–5s达到正向限值。请求不当作独立实际驱动反馈或唯一因果证明。
- 轨迹落盘后的报告函数名错误导致无result：不存在的runtime_receipt应为真实queue_receipt。原[ERROR与实际prefix](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/results/startup_front065_nominal_v1/ERROR.json>)保持；[新报告入口修正](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V1/reporting_fix003/RECEIPT.json>)只改方法名、循环AST不变、0物理重跑，不回填伪result或完整0/1机器人统计。
- [独立保存轨迹诊断](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_FRONT_CAUSAL_001/REPORT.md>) / [接管条件解释](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_FRONT_CAUSAL_001/INTERPRETATION_NOTE.md>)：child一次601行，父另查最后一行；68.9MBphysics未作本次诊断读取。原0raw-open行政KeyError单独保留。

## 3. 下一版是明确待验证假说
[Startup V2方法](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V2/METHOD.md>)只授权新零步prototype：起立阶段改用已有14状态K的腿耦合反馈，局部忽略漂移的纵向估计误差；轮侧用编码器角速度阻尼，而不是尚未扶正时就使用正常平衡轮输出。原参考轨迹、观察器、交接门限、6s超时和驱动限幅不放宽。默认关闭，尚未授予新物理案、背倾/侧卧/fullDR或硬件资格。

整体Goal继续，动量/跳阶未执行旁支暂缓。原H1/H2/H4/H5/Stage1与R63失败均保留。当前新交付与首案证据PH10pending，未重复旧Git阶段记录。
