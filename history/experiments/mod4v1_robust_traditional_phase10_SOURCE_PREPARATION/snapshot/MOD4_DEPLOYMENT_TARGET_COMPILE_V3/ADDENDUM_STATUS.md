# V3A：原值预检已过，CLI证据待补，尚未启动TU

- [父新recipe](<PARENT_DIAGNOSTIC_RECIPE_ADDENDUM.json>) SHA `e01bc544d435d325e81c1b0c0b73dbe988f551174cef16252465008970b00a24` 已读取；命名为 **PARENT_DIAGNOSTIC_V3A**，不是uVision继承exact或u4.422复现。
- 首次[保存原值预检](<ADDENDUM_PRECHECK_01.json>)：非空group/file文本 `[]`，不支持的数值 `[]`；没有重复解析原XML，没有native调用或TU。
- 新recipe明确所有C选择 `-O1 -Otime`，compiler默认启用warnings并保留原 `--diag_error=warning`；旧Optim/oTime/wLevel仅并列保留，不借原数字声称等价。
- 父后续已明确 **literal-only RTE**：只用project字面include/define/undefine/misc及compiler builtin；不从component声明注入 `_RTE_`、新target路径或生成头。原[门槛记录](<PLAN_GATE_01.json>)的两点是当时状态，bytes保持不改；新策略已经处理原RTE选择未决，不把它继续误报为未收到决策。
- 当前剩余为字段→CLI/default的可审据：候选 `interw→--apcs=interwork`、`OneElfS→--split_sections`、`uC99→--c99`，以及ARMCC5对v6相关字段、CPU `.fp`/LE/short-enum/wchar/default library的处理。已有短help未覆盖全部；**没有把“help未显示”说成开关无效，也没有在证据未齐前把候选argv冒称冻结完成**。
- native/compiler/assembler/version-query/链接仍全部0；[163 TU](<PLAN_GATE_01.json>)的首次预算全部保留。没有改stage1/V2、没有重新hash423 payload或重跑40检查。
- 待父提供可审reference/明确剩余映射后，再追加新的literal-argv冻结记录；不改旧RAW/GATE/FACTS/receipt。若映射仍未支持，继续遵守precompile-stop。
