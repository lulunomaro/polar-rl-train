# ARM Object Build v1 — M4/M7 compile-only证据

**6/6个ARM对象首轮编译成功。仅object，不是BSP/固件链接、主板BIN、ARM运行数值或WCET资格。** CPU目标为候选数学目标，不代表MOD4v1已绑定DJI-C/DM02或任何实板。

## 已有工具与原始记录

```text
C:\Keil_v5\ARM\ARMCLANG\bin\armclang.exe
C:\Keil_v5\ARM\ARMCLANG\bin\fromelf.exe
```

本轮独立调用的[version原文](<armclang_version_01.log>)：**MDK Plus5.26 / ARM Compiler6.10.1 / armclang[5d143200]**，exit0。fromelf[5d142900]的[help原文](<fromelf_help_01.log>)也exit0。没有下载/安装、更改license或调用armcc.exe。

version未给CPU时打印unspecified target是版本查询的默认信息；实际编译的target/CPU/FPU以下列完整参数、目标宏与ELF属性为准。

## 输入保持封存

| 输入 | SHA256 |
|---|---|
| [C1 ct_core.c](<../portable_core_v1/ct_core.c>) | `4ecca828e338736bf66dc3ed20bb1bb19659774956338cfd8f22267cdf1c18d6` |
| [C2 ct_kinematics.c](<../portable_core_v2_kinematics/ct_kinematics.c>) | `510ae88b6f2594b7f82214b607d687e7adaefbfaec83ef9b4739874430860fc4` |
| [QP v2-fast](<../portable_mpc_qp_v2_fast/boxqp_fast.c>) | `6484e5e5ceaba597ae620f03aff0022641248a776e2a8893dbfb614884ccad2e` |

没有为ARM修改旧source或压掉warning；对应头也只读复核。C1仍是r00基础观测移植，**不是父当前R03/R04/R13动态估计器**；state14解释仍遵循[父勘误](<../../reports/STATE14_SCHEMA_ERRATUM.md>)。

## 精确编译范围

共同参数：

```text
--target=arm-arm-none-eabi -mthumb -std=c99 -O2 -Wall -Wextra -Werror
-fno-fast-math -ffp-contract=off -mfloat-abi=hard -c SOURCE -o OBJECT
```

| 数学目标 | CPU/FPU参数 |
|---|---|
| M4候选 | `-mcpu=cortex-m4 -mfpu=fpv4-sp-d16` |
| M7候选 | `-mcpu=cortex-m7 -mfpu=fpv5-sp-d16` |

没有host SSE参数，没有链接器、startup、scatter/linker script、BSP或binary转换。全部原exe/argv/stdout+stderr/exit记录在[BUILD_RECEIPT.json](<BUILD_RECEIPT.json>)及每个目标下的原log；脚本为[arm_build.ps1](<arm_build.ps1>)，拒绝覆盖既有object/log。

## 6个对象

以下bytes是**含ELF头/section/symbol/relocation/attribute的文件长度**，不是flash占用、linked text或运行RAM需求。完整64字符SHA256在[OBJECT_SUMMARY.csv](<OBJECT_SUMMARY.csv>)和[JSON](<OBJECT_SUMMARY.json>)，对象为小型QA产物。

| 对象 | 目标 | exit | bytes | SHA256前16位 |
|---|---|---:|---:|---|
| [ct_core](<cortex_m4_sp_hard/ct_core.o>) | M4 | 0 | 22172 | `0ba5d9dad7d119c7` |
| [ct_kinematics](<cortex_m4_sp_hard/ct_kinematics.o>) | M4 | 0 | 10940 | `62980b5e7d693cc2` |
| [boxqp_fast](<cortex_m4_sp_hard/boxqp_fast.o>) | M4 | 0 | 6892 | `41cd86d4a5c7281f` |
| [ct_core](<cortex_m7_sp_hard/ct_core.o>) | M7 | 0 | 22228 | `48f492aef01829d4` |
| [ct_kinematics](<cortex_m7_sp_hard/ct_kinematics.o>) | M7 | 0 | 10904 | `520166d07304de9f` |
| [boxqp_fast](<cortex_m7_sp_hard/boxqp_fast.o>) | M7 | 0 | 6924 | `511af2e49003aa62` |

## 宏与ELF ABI证据

两个目标[宏探针](<target_probe.c>)均通过预处理guard，原文为[M4宏](<cortex_m4_sp_hard/target_macros_01.log>)、[M7宏](<cortex_m7_sp_hard/target_macros_01.log>)：

```text
__ARMCC_VERSION=6100100
__ARM_ARCH=7; __ARM_ARCH_7EM__=1; __ARM_ARCH_PROFILE='M'; __thumb__=1
__ARM_FP=0x6; __ARM_PCS_VFP=1
sizeof(float)=4; FLT_RADIX=2; FLT_MANT_DIG=24; FLT_EVAL_METHOD=0
```

`__ARM_FP=0x6`有single/half相关能力位，**没有double硬件能力位0x8**。这是选择的单精度硬浮点目标，不排除C库里软件helper依赖，也不证明实板FPSCR配置或浮点上下文保存。

全部object由fromelf `--text -v`读取，[M4示例ELF头](<cortex_m4_sp_hard/ct_core_fromelf_01.log#L4-L29>)、[M4 ABI属性](<cortex_m4_sp_hard/ct_core_fromelf_01.log#L1415-L1436>)与[M7 ABI属性](<cortex_m7_sp_hard/ct_core_fromelf_01.log#L1415-L1436>)：

- ELFCLASS32 / little-endian / ET_REL / EM_ARM，EABI revision5；不是可执行image。
- CPU_name分别cortex-m4/cortex-m7，CPU_arch=ARMv7E-M，Thumb2允许，非ARM状态指令。
- `Tag_ABI_HardFP_use=1`（single precision）与 `Tag_ABI_VFP_args=1`（AAPCS VFP传参）匹配；没有单靠ELF e_flags猜hardfloat。
- M4 Tag_FP_arch=6。M7 Tag_FP_arch=8被旧fromelf文字标作“ARM v8-A FP ISA permitted”，这是**FP ISA属性编码**，不是CPU升级成v8-A；CPU_arch仍明确v7E-M，single-use和宏均分别验证。
- denormal/exception/align等原属性保留，不把属性宣称为已测runtime舍入、FTZ/FPSCR或WCET行为。

## 仍未做的事

没有BSP/库链接，也未证明libm/memcpy等最终hard-ABI链接一致；没有board初始化/FPU使能/中断RTOS上下文、HIL/flash、ARM runtime unit、尾延迟/WCET、真实CAN、机械/电热资格或新机器人episode。对象编译通过只是后续集成的必要条件之一。

[inspect_objects.py](<inspect_objects.py>)只离线解析小ELF头与属性/哈希，[原检查日志](<object_inspection_01.log>)；[ERROR_REPORT.md](<ERROR_REPORT.md>)保留全部尝试状态。[INDEX.json](<INDEX.json>)、[VALIDATION.json](<VALIDATION.json>)与[MANIFEST.json](<MANIFEST.json>)列出source/头/object/log证据及旧封存物不变。所有新写入仅本目录。
