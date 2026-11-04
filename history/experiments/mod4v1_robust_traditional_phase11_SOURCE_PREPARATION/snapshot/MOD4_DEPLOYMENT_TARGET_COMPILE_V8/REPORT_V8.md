# V8：原UNSTARTED C-only独立前缀实际结果

**PARTIAL_V8_PREFIX_STOPPED_PRESERVED_NO_RETRY_NO_LINK**；先落最低result/ledger，后作本saved-only报告；旧V6/V7不改账。

## 本轮实际计数

| 项 | 真实结果 |
|---|---:|
| 新C尝试／exit0且保有非空物件 | 39／39 |
| 新scope认可prefix／sealed reader调用 | 38／39 |
| 未启动新C／原ASM | 122／1 |
| 重编main／ASM/fromelf/version/probe/link/UV/flash | 0／0 |

- 首个停止类别：`READER_CAPACITY_STOP`；对应TU：[stm32f4xx_hal_i2c.c](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_i2c.c>)。详见[最低编译结果](<COMPILE_RESULT_V8_01.json>)、[执行账本](<EXECUTION_LEDGER_V8_01.jsonl>)、[首次wrapper日志](<compile_01.log>)。
- 原始stdout／stderr：[stdout](<logs/040_stm32f4xx_hal_i2c.c.stdout.log>) / [stderr](<logs/040_stm32f4xx_hal_i2c.c.stderr.log>)；未编辑诊断、补header或重编。
- 保留编译物件：[停止物件](<objects/040_stm32f4xx_hal_i2c.c.o>)，58720 B；SHA `8e01341b4c39ce543c2c114a1bddcba11371731ec87bcb4865f6285263a0e1a0`。
- 本例物件58720B未超64KiB；容量分类来自e_shnum超过256。最小stop记录未保存具体section数；本轮没有再解析/扩cap补齐属性，不由容量停止推断ABI不兼容。
- [首个不认可物件的完整scope/错误记录](<attributes/040_scope.json>)：成功编译与该gate认可分列；容量或格式不支持不被冒充为真实ABI不兼容。
- reader stop分类：`READER_CAPACITY_STOP`；原始错误：`unsupported extended/invalid section indices`；capacity detail：`SECTION_COUNT_EXCEEDS_SEALED_256`。

## 执行前锁定与首次metadata失败保留

- [父C-only grant](<PARENT_CONTINUATION_SCOPE.json>)与[唯一suffix修订grant](<PARENT_METADATA_SUFFIX_REPAIR_001.json>)均先读。catalog无匹配ARM/ELF skill，采用文件/Python标准库和指定installed ARMCC5u6；无ARMCLANG迁移。
- 首次prepare因我方误写旧ledger扩展名退出1，在冻结前0 native；[原partial报告](<PRE_NATIVE_STOP_REPORT_01.md>)、[原最低stop记录](<PRE_NATIVE_STOP_RESULT_01.json>)与first script/log/snapshot原字节保留。
- 后续仅父批的`.json`→`.jsonl`一字节派生；[patch](<PREPARER_SUFFIX_ONLY_001.patch>)及[inverse/SHA receipt](<SUFFIX_REPAIR_RECEIPT_001.json>)证明原executed脚本未覆盖、exact byte inverse成立。一次新metadata freeze成功后才进入本唯一native wave。
- [冻结PREEXEC](<PREEXEC_V8_01.json>)先于native，含[161 argv/source计划](<LITERAL_ARGV_V8_01.json>)及[路径逆变换](<ARGV_DELTA_V8_01.json>)。唯一argv变化为-o物件路径；stdout/stderr改V8，原CWD/includes/两overlay/macros/flags/CPU与warning policy完全保留。
- 所选161 C共3227070B在首个native前fresh比V6 saved pins；two raw overlay headers前后pin不变，执行TU源before/after相等。未做423全树或全部间接header hash/重新解析project。

## 属性策略、历史和资格边界

- 新成功对象各只调用sealed V7 reader一次；保留64KiB/256section/1024symbol等上限，未扩cap、无fromelf fallback/额外probe/测试循环。每个EXEC section和真实SYMBOL的18只接受2或规范UNUSED0，26只接受1或规范UNUSED0；完整scope来源留存。
- 原V6非type FILE gate未改。规范UNUSED0不是实际sizeof0；现存SYMBOL数量及真实metadata覆盖以各物件JSON为准，不把旧四个synthetic fixture算本轮QA。
- 原V6历史仍compile成功1/postABI认可prefix0/gate=false；V7对既有main的静态解释独立保留。本轮不重编main、不回改旧账，也不把继承main加进新scope-prefix计数。
- 原ASM计划仅冻结、始终UNSTARTED。所有后缀在首次错误/容量/未知处停止；后续修复、余下C/ASM、库ABI及link均待独立决定。
- compile-only不是全target/libABI/link地址容量/固件/target执行/FPSCR/WCET/实际MOD4校准；旧MF9025/LK与新Damiao映射仍未绑定。无机器人/PHY/old40/oldQA/Git/新agent/root-goal动作，V8和suffix修订全部在PH10 cutoff外。
