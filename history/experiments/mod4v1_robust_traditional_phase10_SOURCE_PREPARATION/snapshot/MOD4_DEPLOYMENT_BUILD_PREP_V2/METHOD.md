# MOD4 build-prep V2：静态工具/库属性准备

- 只写本新目录；stage1 seal/工程/423来源只读，不重新全量hash、不重跑40check/旧QA/PHY/FK/CPP/目标compile/link/UV/hook/flash/Git/新agent，不安装或替换工具/包/库，不删除music。
- 精确候选工具仅C:/Keil_v5/ARM/ARMCC/bin/{armcc,armar,armlink,fromelf}.exe：先查存在性，再分别只运行--vsn；可查armar/fromelf --help的静态命令说明。不用ARMCLANG替换。project要求5.06update4/build422，实际不一致逐项明确。
- 读取stage1最终闭包/派生uvprojx作为include/flags/Pack/RTE实际来源；只查这些声明的路径及已知Keil安装下相应Pack固定版本、工具include内实际标准头。不会扫描用户目录/环境/credentials或其他微信文件。
- 两个库仅使用父已授权build_supplement001的AHRS.lib与arm_cortexM4lf_math.lib。允许受信工具列archive成员/对象ELF属性；不disassemble、不大dump代码/数据、不执行算法。若工具要求对象而非archive，最多有界提取供属性读取的独立member到本目录；不一次全库落盘。库完整覆盖与代表样本必须分开，无法确认的ABI写UNKNOWN。
- 每条工具argv/stdout/stderr/exit/产物保存；工具错误保留，不靠换compiler/库/宏/诊断伪造兼容。最终<=120行报告给已知兼容/实际不一致/未证理由与下一次隔离compile预算待批。
