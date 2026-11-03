# V6：一次精确CMSIS头payload后的独立compile-only输入variant

- 依据已读[parent scope](<PARENT_CMSIS_DEPENDENCY_SCOPE.json>)；先完成[只含1头的V5计划](<../MOD4_DEPLOYMENT_DEPENDENCY_STATIC_V5/HEADER_OVERLAY_PLAN_V5.json>)，V5及V3A/V4原失败全部只读。
- 当前Office/ACL catalog无机器人/Keil依赖专项；使用文件/Python标准库及已知ARMCC5u6 trusted CLI，不迁移ARMCLANG、不执行UV/hooks。
- 唯一原ZIP payload：`StandardRobotpp-balance1/Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS/cmsis_os.h`，53,065B / CRC `61803e9e`；ZIP本体expected 76,134,913B。仅此member原payload读取一次，核raw CRC/SHA，写本目录新raw overlay；不读其它payload/.git/程序、不整ZIP hash。
- 严格decode按UTF-8-sig、GB18030、cp1252尝试并记录实际结果；成功codec仅是严格可解码兼容性，不宣称唯一原始字符集。可另UTF8 readable供read工具审API/includes，compiler只使用原bytes。无法完成必要审阅则在native前停。
- 与已冻V4相同的163 TU/顺序/CWD/source/flags/macros/RTE/defaultwarnings/diag_error=warning；唯一compiler argv变化是新增精确CMSIS overlay -I、新V6对象输出。旧device-header -I保留。
- 每个实际argv在native前冻结，逐条严格逆变换恢复V4；不重parse项目、不重跑version、不大lib hash、不423源码重hash。
- Executor/ELF metadata reader复用旧V4：仅必要V6记录名/variant token、输出新目录；以原byte复制和严格逆变换记录，不泛称行尾变换byte-exact。
- 全部C162+ASM1各至多一次、main先、串行；首compiler error/exit0无产物或first-object关键ABI unknown/incompatible即停，保存prefix/failed/unstarted/原logs，不自动补下一依赖/诊断或重试。
- 第一真实成功object仅trusted fromelf属性/ELF头+AEABI，0反汇编/code dump；若到最后ASM，原已准许同bin armasm --vsn一次。0link，全部成功也需下一review，不执行库算法或target。
- AHRS/DSP旧属性只复用保存metadata；denormal差异不确定仍记unknown，不伪造链接/数值/hardware资格。
- 父startup仅1worker，本子任务串行C不启动PHY/GPU/新agent，不触碰其job；总CPU任务维持父要求≤4。
- 0旧40/QA/PHY/FK/Git/root-goal/旧source写/flash/debug/CAN/SPI/实际算法运行。V3A 1fail、V4 1fail不重置；V6是依赖确实改变的新variant，不把它冒称前两次的首次。
