# V5：编码漏选头的静态补齐计划

**状态：STATIC PLAN ONLY；本V5没有payload或compile资格。**

## 精确候选（仅1项）
| 原archive member | bytes | 保存central CRC32 | 原excluded reason |
|---|---:|---|---|
| `StandardRobotpp-balance1/Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS/cmsis_os.h` | 53,065 | `61803e9e` | `selected_suffix_not_decodable_text` |
- 只过滤既有manifest.excluded中的该reason、Drivers/Middlewares、.h：结果1头，总53,065B；符合≤32头、每个<1MiB、总≤2MiB。
- 同域同reason另有[cmsis_os.c的excluded记录](<../DEPLOYED_BASELINE_AUDIT_V1/SELECTED_SOURCE_MANIFEST.json#L8410-L8414>)，但不是.h；未将它混为第二个头。器件头oversize等其它reason不纳入本编码类计划。
- CRC/size来自既有CENTRAL的唯一成员记录并与保存图一致；不是本轮重读payload后的CRC。具体charset和payload SHA仍UNKNOWN，未预设cp1252。

## 对冻结163TU的相关性
- 只使用保存的lexical图和V4 literal/actual -I元数据：31个保存的直接include站点；31个C根有可能可达该头。
- [main.c:23的保存边](<../MOD4_DEPLOYMENT_PORT_V1/BUILD_CLOSURE_FINAL.json#L2313-L2325>)→该member，central=true/provided=false；与已封存V4首error相符。
- 162个C TU已在literal/actual -I中选择原CMSIS_RTOS目录；ASM1未在该保存图建立到此头的路径。
- 条件预处理未计算；未可达的131C+1ASM不等于已证明无关，31C也不是实际编译依赖计数。该头内部/传递include尚UNKNOWN。

## 拟overlay（尚未落盘）
```text
<PARENT_NEW_VARIANT>/header_overlay/Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS/cmsis_os.h
-I<PARENT_NEW_VARIANT>/header_overlay/Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS
```
- 后续若另批准payload，应核原member/bytes/CRC，再记录实测SHA/codec；compiler使用原bytes，UTF8可读副本只供审阅。
- 本计划不构造可运行argv，不改原V4/device overlay；后续需要新输入variant/明确新预算，不能称本V5已编译。

## 执行与证据
- 第一遍JSON脚本因resolved.member=null字符串比较失败；原source/log保留。仅修正nullable成员比较，同四metadata第二遍成功；一处逆修改逐byte还原首脚本。
- [错误记录](<ERROR_REPORT.md>)；[20KB候选及全部可能TU IDs/站点/样例路径](<HEADER_OVERLAY_PLAN_V5.json>)；[实际摘要](<STATIC_RESULT_V5.json>)。
- 四份既有JSON metadata SHA及METHOD/脚本在封存时一致；未新parse项目、未扫/重hash423源码、未大lib hash。
- 0 ZIP/header/source payload读取或提取，0 native toolchain/C/ASM/link/UV/flash/target/旧40/QA/PHY/Git/agent/root-goal动作。
- 只穷尽上述保存manifest的限定编码漏选类别；不宣称所有依赖闭包、ABI或firmware资格已闭合。
