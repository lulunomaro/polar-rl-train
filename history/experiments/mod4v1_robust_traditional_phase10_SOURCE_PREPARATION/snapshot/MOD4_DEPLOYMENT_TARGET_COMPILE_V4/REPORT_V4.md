# V4：单器件头overlay后，真实首C在下一依赖处停止

**状态：PARTIAL_V4_FIRST_REAL_C_ERROR_NEXT_DEPENDENCY_NO_OBJECT_NOT_FULL_BUILD。**

## 新输入与事前差异
- 这是父另授权的新输入variant **PARENT_DIAGNOSTIC_V4_ONE_DEVICE_HEADER_OVERLAY**，不是V3A自动重试，也不再叫V3A第一次。
- 父单文件[receipt](<../DEPLOYED_BASELINE_AUDIT_V1/device_header_supplement002/RECEIPT.json>)提供原bytes器件头：1,350,860B、CRC `9a578ca0`、SHA `a0e7f720b1c7c311ceb7a8ab3afba31a35d377a7ebeb6ded3237f771d9d7b786`，本轮事前/事后均核一致。
- [163条V4 argv](<LITERAL_ARGV_V4_01.json>)在native前冻结；[差异](<ARGV_DELTA_V4_01.json>)逐条逆变换精确还原V3A，只有新增overlay -I和新V4输出路径。未重新解析项目、未重跑旧version/compile。
- u6/-O1/-Otime/default warnings+--diag_error=warning/显式AC5 defaults/literal-only RTE全部保留；无新stub、生成RTE或宏/诊断调整。

- 元数据措辞校正：初始delta把executor token逆变换说成byte-exact；实际仅在LF/CRLF归一后逐字相同（无逻辑变动）。原delta bytes保留，最终facts分别给raw与归一结果；全部163条compiler argv的严格逆变换仍成立。
## 真实首error
- [实际stderr](<logs/001_main.c.stderr.log#L1-L4>)：
```text
Src/main.c:23 Error #5:
cannot open source input file "cmsis_os.h": No such file or directory
main.c: 0 warnings, 1 error
```
- 首个真实V4 main.c编译exit=1；原器件头missing错误本次未再出现，但这不证明完整条件预处理闭包。
- 没有object，因此未调用fromelf，CPU/FPU/VFPargs/enum/wchar/denormal实际ABI全部仍UNKNOWN。

## V4预算（与V3A分开）
| 项目 | 实际 |
|---|---:|
| C / ASM尝试 | 1 / 0 |
| 成功compile prefix / objects | 0 / 0 |
| 未启动C / ASM | 161 / 1 |
| fromelf / armasm版本 / link | 0 / 0 / 0 |
- [真实compile结果](<COMPILE_RESULT_V4_01.json>)与[ledger](<EXECUTION_LEDGER_V4_01.jsonl>)保留完整failed argv、stdout/stderr、162个未启动ID；无自动重试。

## 隔离与结论
- V3A原1次缺器件头失败、其日志/argv/报告保持原样；本V4失败也不覆盖它。
- 只复核保存的metadata/输入和实际日志：失败TU前后SHA与stage1 pin一致，新增header未改；未全量重新hash423 payload。
- 下一缺失输入是否在原档/Pack、应怎样供给：UNKNOWN，本轮不查询/补入；需要另行明确依赖范围与新attempt/variant。
- 未改旧source、include策略、警告等级；0链接/UV/hooks/flash/debug/target/CAN/SPI、算法运行/PHY/FK、旧40/QA/Git/agents/root-goal动作。
- 这次只是保真保存的新依赖推进与下一首error，不是完整target build、firmware、物理MOD4绑定或发送资格。
