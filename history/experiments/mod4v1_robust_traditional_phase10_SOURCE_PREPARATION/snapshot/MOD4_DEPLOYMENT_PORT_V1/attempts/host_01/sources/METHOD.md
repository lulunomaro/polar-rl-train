# MOD4部署派生工程 V1 — 第一阶段锁定方法

- 仅写本目录；源为父选定的391个text，原source/source_original/ZIP/旧audit全部只读。不搜索其他微信目录，不打开原ZIP/.git，不运行旧uvproj/bat/postbuild/flash/hook。
- 先锁CENTRAL、SELECTED manifest与原Keil/关键caller的SHA，再静态解析唯一target的165个File成员、group/file include、include paths/defines、库、startup、memory/scatter与hook/flash设置。按中央目录与selected逐项分类；quote include只作有界词法闭包，条件预处理/系统头/外部SDK明确未证，不称已完成target link。
- 原391 payload总7724844 bytes，可逐一校验parent raw SHA/CRC并原bytes复制到derived/StandardRobotpp-balance1；before/保留字节索引为原型回滚依据。派生修改前保存before与hash；GB18030/UTF8-BOM/换行按原记录保留，patch仅ASCII新逻辑。不覆盖旧原型，不修改任何成绩。
- 只窄改：SendJointMotorCmd局部未初始化cnt改持久初始化计数；ConsoleStandUp废弃未赋值double joint_pos_l/r，改显式valid的raw-motor-rad qref4 provider；not-ready不读位置、不默认把零数组当姿态命令；新增默认UNBOUND的startup/manual-arm/feedback-freshness/fault/STOP/DISABLE adapter与单任务bridge。
- STOP与DISABLE独立动作；MIT0不是FD。未绑定时禁止FC与所有其他新CAN emission；无发送不等于已停住硬件。完成绑定且明确manual arm后，ENABLE_ONLY先于RUN，必须有显式enable授权及反馈ACK，qref只在standup有效域内使用。STOP/DISABLE是请求，不虚构真实电机行为。
- 不把旧MF9025/LK改名DM3519，不选MOD4轮型号/gear/ID，不把generic DM±10Nm或旧normal±7Nm当MOD4±40物理绑定。保留旧HSE12MHz/F407启动底座；旧leg/controller gains不动，model代理以后提供typed站起ref。
- 仅新纯C99 adapter/bridge做host synthetic smoke一次，显式CHECK总数<=40，固定toy绑定/时钟/反馈，不驱动真实CAN/SPI/目标程序。C++友好header；本轮不额外跑CPP/ARM/完整工程build/旧QA/PHY/FK/新agent/Git。
- 每次新编译记录argv/exit/artifact SHA；exit0产物缺失立即停该构建线。普通编译/测试失败保存原src/log/bin，不掩盖失败、不靠改预算/新参数通过。完整target构建/缺库提取/脚本或flash入口另等父批准。
- 第一交付两项实体：BUILD_CLOSURE.json（精确缺选member与hook事实）及派生patch/adapter源包（包含METHOD/SOURCE/before-hash/patch说明/new host事实）。不交仅泛方案。
