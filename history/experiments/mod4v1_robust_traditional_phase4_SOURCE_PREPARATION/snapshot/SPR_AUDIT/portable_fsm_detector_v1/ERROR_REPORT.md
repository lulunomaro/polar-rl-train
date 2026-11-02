# 新FSM port的attempt与修订记录

本记录不重写[原Python包的旧错误记录](<../../FSM_DETECTOR_V1/ERROR_REPORT.md>)，也不把BLOCKED IO记为成功。

## 1. Host attempt01：通过，但发现typed边缘遗漏

- [严格host构建01](<HOST_BUILD_01.json>)全部compiler/link exit0，所有object/exe实际存在。[新C运行01](<host_run_01.log#L1043-L1045>)为1042 reference步、46087 replay checks/0差异，native1652/0；CPP也实际通过。
- 随后源码审查发现`fd1_step(NULL,...,out)`的typed错误输出仅memset，contact wheel诊断留成0（会像proxy-unloaded），应为unknown=-1。原63场景的typed frame/既有context没有这条NULL-context路径，所以这不是原Python回放差异，也不是一次已执行的失败断言。
- [01源码](<revisions/host_attempt_01/fd1_detector.c>)、[01可执行文件](<revisions/host_attempt_01/fd1_host_tests.exe>)和原日志保留。01的测试缺口如实存在，不用最终数值覆盖。

## 2. Host attempt02：真实源码guard修订

- [02源码](<revisions/host_attempt_02/fd1_detector.c>)将NULL-context wheel诊断显式设-1；motor present位只接受1；强化context reason-list/轮proxy/timer/flag一致性检查，结构损坏锁存BAD_CONTEXT。
- [新增native测试](<fd1_native_tests.c>)直接检查NULL unknown、invalid presence2、坏context wheel/reason/timer、input/output及context别名、init/config别名等；无阈值/轨迹/原场景改动。
- [运行02](<host_run_02.log#L1043-L1045>)仍1042步/46087 replay checks零差异、native1993/0，实际[CPP通过](<cpp_run_02.log>)。
- 旧exe在同名目标被重新链接前，SHA检查后按字节复制到对应revision；没有删除/移动或通过改名绕过丢失事件。02的[exe](<revisions/host_attempt_02/fd1_host_tests.exe>)保留，源修订与binary对应关系见[构建02](<HOST_BUILD_02.json>)。

## 3. ARM attempt01：真实严格编译错误，非产物消失

[原日志](<cortex_m4_sp_hard/compile_01.log#L1-L23>)与[receipt01](<ARM_BUILD_01.json>)明确：M4 compile exit1，5条`-Werror,-Wmissing-braces`，均为`fd1_reason_list`首成员是array时的`{0}`嵌套初始化建议。此前宏probe通过，M7尚未开始，未产生ARM object。

这与旧IO的“exit0、Created→Deleted、actor未知”是不同事实；没有把正常exit1误报为缺产物删除，也没有防护设置/环境或license修改。

## 4. Host03/ARM02：仅补标准嵌套braces

- 改为`{{0,0},0,{0}}`，语义和数值预算不变；不抑制warning、不放宽任何flags。
- [最终C源码](<fd1_detector.c>)在[host03](<HOST_BUILD_03.json>)、[host03运行](<host_run_03.log#L1043-L1045>)、[CPP03](<cpp_run_03.log>)、[ARM02](<ARM_BUILD_02.json>)均有对应SHA/命令。
- Host03最终46087 replay checks/0、native1993/0，数值误差0；与02的MinGW核心object字节一致（初始化braces修订不改变其已生成代码）。最终exe因链接元数据不同，保留各自SHA，不混用。
- ARM02首次成功产生本新模块M4/M7两个object，保留大小/SHA、宏、fromelf、ELF/undefined-symbol核查。未运行目标代码或链接soft-double/libm/BSP。

## 5. 证据和未做事项

[Reference构造](<REFERENCE_GENERATION.json>)为新C接口生成固定fixture，未重跑原runner、未更新原RESULT/分数。4个源方法无step，逐场景表明确0行；native typed/配置值检查与C按值固定数组表示另列，未伪造63条运行轨迹。

从未发生本新功能exit0后缺object/exe的事件；每条编译均有产物guard，所有当前及早期exe最终再次SHA复核。旧blocked IO没有继续编译或归因猜测。无physics/GPU/Git/新agent/BSP/刷写/在线C3动作，原force/COM可信门槛、默认disabled/unbound不变。

## 6. Metadata seal01：生成顺序错误，非数值/编译失败

[首个seal日志](<seal_run_01.log>)和[原错误](<seal_error_01.txt>)记录`AssertionError: MANIFEST.json`：脚本先检查README指向MANIFEST的链接，再生成MANIFEST，顺序相反。此前写出的INDEX/VALIDATION标识仅是该次未完成metadata，未作为完成回执交付。[8件原样快照](<revisions/seal_attempt_01/seal_fsm.py>)连同旧INDEX/VALIDATION/脚本/log保存。

仅修正metadata顺序：先生成MANIFEST再验证完整链接；再读取已存在host/CPP/ARM结果与SHA，没有重跑reference、C测试或编译。最终成功receipt另列seal02，旧失败不覆盖。
