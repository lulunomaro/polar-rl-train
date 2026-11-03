# V3A：首次真实C编译在器件头依赖处停止

**状态：PARTIAL_FIRST_REAL_C_PREPROCESSING_ERROR_NO_OBJECT_NOT_FULL_TARGET_BUILD。**

## 实际结果
- [事前逐TU literal argv](<LITERAL_ARGV_V3A_01.json>)已冻结163条；随后仅启动真实首个C TU **main.c**。
- 使用已批准的 **PARENT_DIAGNOSTIC_V3A / 现有ARMCC5.06u6 build750路径**，不冒称u4.422复现。
- [实际compiler stderr](<logs/001_main.c.stderr.log#L1-L4>)：
```text
../Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f4xx.h:149
Error #5: cannot open source input file "stm32f407xx.h": No such file or directory
main.c: 0 warnings, 1 error
```
- compiler exit=1；本次不是许可证报错、未知开关报错或exit0产物消失。**没有生成object**，所以没有fromelf/实际ABI/CPU/FPU/enum/wchar/denormal结果。

## 消费预算与未启动
| 项目 | 实际 |
|---|---:|
| C TU尝试 | 1（main.c） |
| ASM TU尝试 | 0 |
| 成功compile prefix | 0 |
| failed TU | 1 |
| 未启动C / ASM | 161 / 1 |
| fromelf / armasm --vsn / link | 0 / 0 / 0 |
- [实际结果及162未启动ID](<COMPILE_RESULT_V3A_01.json>)、[执行ledger](<EXECUTION_LEDGER_V3A_01.jsonl>)保留；每TU最多一次，没有重试。
- 原[0TU门槛记录](<PLAN_GATE_01.json>)和[RAW原值链](<RAW_TU_PLAN_01.json>)是事前记录、bytes不改；本报告和[新facts](<FACTS_V3A_FINAL.json>)为其后的真实编译事实，不再把当前消费数说成0。

## 诊断variant的明确偏差
- [父Addendum](<PARENT_DIAGNOSTIC_RECIPE_ADDENDUM.json>)和[AC5决策](<PARENT_AC5_DEFAULTS_DECISION.json>)选择所有C统一-O1/-Otime，默认warnings+原--diag_error=warning；原Optim/oTime/wLevel保留旁列，不由数字推断等价。
- v6*/vShortEn/Wch按本variant明确不应用；选择AC5自己的endian/enum/wchar/default library，不臆造switch，也尚无object证明结果。
- include/Define/Undefine/Misc仅project字面及compiler builtin；不从RTE声明注入_RTE_、新target include或生成头。

## 当前依赖结论与隔离
- 条件预处理真实走到器件族头的具体器件include后失败；既往169个project成员提供完备和词法图不等于条件预处理闭包已完备，原stage1/V2也未声称后者。
- 本轮不搜索原ZIP/Pack给这个头补来源，不改-I、不放stub、不降warnings、不删除music；器件头在原档/Pack中的供应仍UNKNOWN，应另定有界补依赖范围与新attempt/variant，不能再把main.c当本V3A首次。
- 已仅复核事前metadata/argv/保存日志，失败TU源在前后与stage1 pin一致；未全量重新hash423 payload。
- [read编码观察](<READ_ERROR_01.txt>)：派生原始族头对read工具非UTF8，未转换/写回旧source；本报告引用实际compiler保存的include行，不声称读工具已解码该头全文。
- stage1/V2写入、UV/hook/flash/target/CAN/SPI、PHY/FK、旧QA/40、Git/新agent/root-goal动作全部0。
- 尚无target代码生成、链接、固件、实机或MOD4物理绑定资格。
