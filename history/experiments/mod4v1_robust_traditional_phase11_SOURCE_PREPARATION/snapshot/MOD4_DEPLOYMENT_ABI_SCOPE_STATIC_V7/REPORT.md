# V7：AEABI分scope静态复核，不是继续构建许可

**结论：该7804B既有物件的18/26「FILE-only未知」理由已由官方规则和分scope证据解除；可提交剩余161 C＋1 ASM的独立续编审批。当前新增ARM工具、compile/probe/link均0，原V6账目不变。**

## 官方依据与边界
- catalog无ELF/机器人匹配skill；已先用web_fetch读取[官方Addenda32](<https://github.com/ARM-software/abi-aa/blob/main/addenda32/addenda32.rst>)与[AAELF32 Build Attributes](<https://github.com/ARM-software/abi-aa/blob/main/aaelf32/aaelf32.rst#build-attributes>)，两文自声明2026Q3／2026-11-03。main未锁git commit；实际短引文及fetch receipt SHA见[规则证据](<OFFICIAL_RULES.json>)，不是博客或猜测编译器默认。
- [Addenda32省略规则](<https://github.com/ARM-software/abi-aa/blob/main/addenda32/addenda32.rst#default-values-for-public-tags>)原文："The effect of omitting a public tag in file scope is identical to including it with a value of 0 or “”, depending on its parameter type." 另有Tag_nodefaults例外。
- [继承规则](<https://github.com/ARM-software/abi-aa/blob/main/addenda32/addenda32.rst#inheritance-of-public-tag-values>)："A tag value given explicitly in a scope overrides a value that would otherwise be inherited." 关系为FILE→SECTION→SYMBOL；同scope给同tag不同值才是错误，合法下级override不是冲突。
- Tag18=0原文为"The user prohibited the use of wchar_t when building this entity"；Tag26=0相应禁止enum。这里分类为UNUSED契约，不是实际sizeof=0、不是由反汇编证明未使用，更不是编译器默认2/1。
- 新[独立reader](<scoped_attrs_v7.py>)按官方精确empty-scope／nodefaults公式解析；private ARM vendor内容保留opaque，不把私有tag18解释成public wchar属性。Section/symbol属性从r2.09起deprecated/optional；本次主动尊重这些已存在scope，不宣称所有consumer必须处理。

## 既有物件的逐代码段结果
输入为[原V6物件](<../MOD4_DEPLOYMENT_TARGET_COMPILE_V6/objects/001_main.c.o>)（7804B，SHA `8f39c7f715a84fd46df710a19ec69309677b0014c542f555285527247b1a1f51`）；仅静态读取，未执行。

| Section ID／名称 | flags／字节 | 有效18 | 有效26 | 来源及分类 |
|---|---:|---:|---:|---|
| 1 `.rev16_text` | 0x6／4 | 0 | 0 | FILE省略＋无nodefaults，经继承为规范0；UNUSED |
| 2 `.revsh_text` | 0x6／4 | 0 | 0 | 同上；未强灌函数段2/1 |
| 3 `.rrx_text` | 0x6／6 | 0 | 0 | 同上；未强灌函数段2/1 |
| 4 `i.Error_Handler` | 0x6／2 | 2 | 1 | 此SECTION显式值；wchar2／enum最小合适容器 |
| 5 `i.SystemClock_Config` | 0x6／180 | 2 | 1 | 此SECTION显式值；不是由FILE推断 |
| 6 `i.main` | 0x6／126 | 2 | 1 | 此SECTION显式值；不是由FILE推断 |

- flags 0x6是ALLOC＋EXECINSTR。真实public SYMBOL scope=0，未读symbol-table项；public原始块为FILE＋SECTION[4,5,6]＋SECTION[1,2,3]。所有代码段18/26的unknown=0、同scope冲突=0。
- 2/1函数组的Tag_conformance显式"2.09"；内建组仅另列align/optimization。enum=1表示最小合适容器，绝不等于所有enum都是1字节。
- 与[既存fromelf文本](<../MOD4_DEPLOYMENT_TARGET_COMPILE_V6/logs/first_object.fromelf.stdout.log#L468-L514>)的section ID、名、flags、size、分scope tag逐项吻合；没有再次运行fromelf。FILE CPU=13／profile77／Thumb2=2／FP=6／HardFP=1／VFPargs=1／denormal=2保持旧观测；denormal2不证明当前FPSCR或IEEE逐渐下溢。

## 本轮真实执行与不变记录
- [方法](<METHOD.md>)与[六项旧输入快照](<INPUT_SNAPSHOT.json>)先冻结；一次新QA运行恰好4个fixture各解析1次：继承/nodefaults、multi-section＋SYMBOL override/default、预期同scope冲突、预期边界截断。**19断言／0失配**，后二者是应捕获的fixture，不是被隐去的任务失败。
- 然后新reader仅解析真实物件1次；**64项metadata核对／0失配**。详见[fixture结果](<FIXTURE_RESULTS_01.json>)、[真实scope及逐字段来源](<OBJECT_SCOPE_RESULT_01.json>)和[首次日志](<review_01.log>)。无旧QA／旧reader执行，无额外物件probe／源码树hash／archive读取。
- [旧reader:27](<../MOD4_DEPLOYMENT_TARGET_COMPILE_V6/elf_attrs_v3.py#L27>)、[V6原gate:174–185](<../MOD4_DEPLOYMENT_TARGET_COMPILE_V6/FIRST_OBJECT_GATE_V6_01.json#L174-L185>)、[原ledger](<../MOD4_DEPLOYMENT_TARGET_COMPILE_V6/EXECUTION_LEDGER_V6_01.jsonl>)及原result均只读。V6历史仍是**成功compile1、post-ABI认可prefix0、原gate=false、162未启动**；V7新增解释与这些原记录分列。

## 下一审批与保留未知
- 该物件类型契约均为原请求2/1或规范UNUSED；此窄范围足以移除两项file-parser未知，不等于所有ABI问题完成。后续如另批，须明确新分scope gate策略与执行计划，保留旧V6停止记录；本轮没有自动接续任何TU，也没有重编main。
- 剩余161 C＋1 ASM的依赖/属性、所有库成员ABI、link地址/容量/符号、工具consumer对deprecated scope的处理、RT库/denormal一致性、target执行/FPSCR/WCET/板级MOD4绑定仍待各自证明。
- 四个新fixture只覆盖所述有界路径，不是通用ELF解析器资格；实际未出现SYMBOL，synthetic SYMBOL映射测试不冒充真实symbol-table分支覆盖。无robot任务、PHY、旧40、Git、新agent或root goal操作。
