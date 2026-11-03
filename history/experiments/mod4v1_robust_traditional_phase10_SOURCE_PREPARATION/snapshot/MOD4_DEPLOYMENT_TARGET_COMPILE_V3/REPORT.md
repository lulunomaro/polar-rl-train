# V3：首轮compile前门槛停止

**状态：STOPPED_BEFORE_ANY_TU_UNRESOLVED_EFFECTIVE_PLAN。** 这是参数计划未决，不是编译器错误、ABI失败或许可证失败。

## 已实际保存
- [原值链计划](<RAW_TU_PLAN_01.json>)：163 TU、71 profiles、target/group/file独立XML值与XPath、每TU来源pin/当前stat、候选隔离object/dependency路径。
- [小facts](<FACTS.json>)、[门槛状态/163未启动ID](<PLAN_GATE_01.json>)；有效argv/flags全为null，未声称完成可运行argv冻结。
- C162+ASM1，输入存在性全部通过、保存的来源SHA pin全部有；这些pin继承stage1记录，**不是本轮重新hash163/423 payload**。

## 真实覆盖值，不盲套target
| 层级 | Optim | oTime | wLevel | EnumInt |
|---|---:|---:|---:|---:|
| target | 1 | 0 | 2 | 0 |
| Drivers/STM32F4xx_HAL_Driver（29 TU） | 2 | 1 | 0 | 2 |
| Middlewares/FreeRTOS（10 TU） | 2 | 1 | 0 | 2 |
| Middlewares/USB_Device_Library（4 TU） | 2 | 1 | 0 | 2 |
| stm32f4xx_hal_pcd.c file override | 0 | 2 | 0 | 2 |
| croutine.c file override | 0 | 2 | 0 | 2 |
| usbd_core.c file override | 0 | 2 | 0 | 2 |

- [target原文:312–339](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L312-L339>)；[HAL group:492–559](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L492-L559>)；[first file:565–614](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L565-L614>)。
- 当前armcc短help定义-O0/-O1/-Otime等CLI，不定义这些uVision整数selector及空VariousControls继承；没有把0/1/2凭数字近似转成argv。
- 父另报已安装XSD只见twoBits/sevenBits值域，尚非映射语义证据；子未额外搜/读schema，不将schema存在当已解决。
- literal include/defines与RTE component声明分开保存。没有猜加_RTE_或新target RTE路径；direct variant的隐含宏/路径策略仍待明确。

## 预算和隔离
- [163未启动列表](<PLAN_GATE_01.json>)：successful_prefix=[]，failed_TU=null，failed_compile_diagnostic=null；不是失败了163次。
- C/ASM编译、native工具、link、UV/hook/flash、PHY/FK、host40/旧QA/Git/新agent全部0。
- [armasm版本查询](<ARMASM_QUERY_DEFERRED.json>)也未执行，原一次预算保持未消耗。
- 没有安装/生成RTE、补空头/stub、删music或改stage1/V2；没有根goal动作。
- 父提供可审映射或另定显式diagnostic-override variant前，保持当前停止状态；不得冒称uVision继承exact或u4.422复现。
