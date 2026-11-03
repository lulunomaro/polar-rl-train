# V6：首C真实成功，FILE-only属性gate停止；SECTION证据另列

**状态：PARTIAL_V6_MAIN_OBJECT_COMPILED_FILE_ONLY_ABI_GATE_STOP_SECTION_EVIDENCE_PENDING_REVIEW。**

## 一次精确新输入
- 原ZIP仅1个批准member payload读取一次：53,065B、CRC `61803e9e`、raw SHA `51420495a86c8aea829f63a156c475c225bf9c51429e0bb210eb35db0b1fd1ba`。
- UTF8-sig/GB18030 strict都在byte1090失败；cp1252 strict成功只是实测可兼容codec，不宣称唯一原charset。compiler用[原bytes overlay](<cmsis_header_overlay/cmsis_os.h>)，不是[UTF8审阅副本](<readable/cmsis_os.h>)。
- 已actual read真实6个FreeRTOS includes、guard、类型、kernel/thread API；注释样例include不当真实依赖；详见[输入receipt](<HEADER_INPUT_RECEIPT_01.json>)/[审阅记录](<HEADER_REVIEW_01.json>)。
- native前冻结163实际argv；相对V4仅新CMSIS -I/新V6输出，旧device -I和所有flags/macros/CWD不变；严格逆变换163/163。executor binary token逆变换成立、reader原byte复制。

## 首个真实object与停点
- main.c armcc exit0；stdout/stderr均空，object 7,804B，SHA `8f39c7f715a84fd46df710a19ec69309677b0014c542f555285527247b1a1f51`。
- trusted fromelf `--text -v` exit0：ELF32 little ET_REL EM_ARM；ARMCC5.06u6.750 producer metadata，不是u4重现。
- [原gate](<FIRST_OBJECT_GATE_V6_01.json>)依旧false：旧reader只取AEABI FILE子属性，FILE没有tag18/26，于是wchar/enum为UNKNOWN并立即停。
- 重要限定：[已生成native SECTION证据](<logs/first_object.fromelf.stdout.log#L489-L505>)在函数sections4/5/6明确wchar_t=2、enum为最小够用容器1；不是所有enum都1byte。另intrinsic sections1/2/3只另列align/optim。
- 所以不得说“整个object无18/26”或“已证ABI不兼容”。这是FILE-only reader的scope局限；[单独scope note](<SAVED_ATTRIBUTE_SCOPE_NOTE_01.json>)保留观察，原reader/gate/result/argv未改，未自动放行。

| 实际FILE属性 | 值 |
|---|---|
| CPU arch / profile | 13=v7E-M / 77=M |
| Thumb / FP arch | 2 / 6 |
| HardFP_use / VFP_args | 1 / 1 |
| FP_denormal | 2：允许保留FTZ零符号，非runtime渐进下溢证明 |
| wchar18 / enum26 | FILE UNKNOWN；上述函数SECTION为2 / 1 |

## V6实际预算（不重置旧失败）
| 项目 | 实际 |
|---|---:|
| C / ASM尝试 | 1 / 0 |
| compiler成功prefix / object | 1 / 1 |
| ABI gate后认可prefix | 0 |
| 未启动C / ASM | 161 / 1 |
| 直接native：armcc / fromelf | 1 / 1 |
| armasm版本 / link / probe / 停止后TU | 0 / 0 / 0 / 0 |
- [实际compile结果](<COMPILE_RESULT_V6_01.json>)保留162个unstarted；[ledger](<EXECUTION_LEDGER_V6_01.jsonl>)没有TU_ACCEPTED事件。
- V3A原1C fail、V4原1C fail保持不变；V5是0compile静态计划。本V6新输入只证明这次main可编译，非完整预处理/target闭包。

## 后续边界
- 不修reader、不重编main、不另probe、不继续剩余TU；仅保存当前object和native SECTION证据，需父另明确scope-aware属性审阅/继续判定。
- AHRS/DSP仍只旧有限样本；denormal2/1差异不推成链接或runtime兼容。未大lib hash、旧项目parser/version/旧40重跑。
- 0 link/UV/hooks/flash/debug/target/CAN/SPI/算法运行/PHY/FK/QA/Git/新agent/root-goal；父startup worker未触碰。
- 原源/header前后pin一致，仅检查本次TU与批准输入/小metadata，不全423 payload重hash；大argv留本地，不附长文本。
