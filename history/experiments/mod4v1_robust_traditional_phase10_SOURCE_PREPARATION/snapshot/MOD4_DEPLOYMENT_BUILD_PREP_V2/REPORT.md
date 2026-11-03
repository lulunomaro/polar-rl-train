# MOD4 deployment build-prep V2：静态工具/ABI准备

## 结论
- 已完成工具版本、实际project路径与两库成员/代表对象属性准备；**没有target编译/link或build许可升级**。
- 原指定5.06 update4/build422与当前批准路径的5.06 update6/build750存在明确版本差异，未改project、未迁ARMCLANG、未安装/替换工具或库。
- 以下匹配只属于静态候选线索；实际target对象ABI、全部DSP对象、条件预处理、最终符号与布局尚待独立批准的首次build。

## 精确工具
- 路径固定`C:/Keil_v5/ARM/ARMCC/bin/`；仅四个工具各一次`--vsn`，另查三个工具静态help；[完整argv/版本](<TOOL_VERSIONS.json>)、[help记录](<TOOL_HELP.json>)。
| 工具 | 实际版本 | exit |
|---|---|---:|
| armcc | MDK Plus5.26 / ARM Compiler5.06 update6 build750 | 0 |
| armar | 同上，Tool4d35df | 0 |
| armlink | 同上，Tool4d35ed | 0 |
| fromelf | 同上，Tool4d35e3 | 0 |
- [派生project:13–21](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L13-L21>)仍声明5.06u4.422、STM32F407IGHx、Cortex-M4/FPU2。
- 版本查询不等于compile许可证、内建宏、真实预处理或link成功；未查用户环境/credentials或其它安装位置寻找替代版本。

## 实际include / Pack / RTE
- [路径事实](<PATHS_AND_PROJECT.json>)来自实际project XML，而非仅旧审计表：36条include记录，34唯一目录；33存在。
- 缺少的唯一include目录是`../application/protocol`。这是目录缺失事实；本轮未预处理，尚不知是否有active头依赖落入该目录，未造stub/空目录。
- 全部13个明确检查的ARMCC标准头路径存在；工程本地CMSIS/device候选头也存在。存在性不等于版本/条件分支/依赖完整证明。
- 固定已知Keil Pack位置的STM32F4xx_DFP2.17.1 PDSC存在，实际vendor/name/release与STM32F407IGHx节点匹配；[精确设备链](<STATIC_FACTS.json>)。
- 该节点宣告Cortex-M4/little-endian、FLASH1MiB、SRAM128KiB、CCM64KiB；这是Pack描述，未测芯片/未生成map。
- CMSIS5.8.0 PDSC在`C:/Keil_v5/ARM/PACK/ARM/CMSIS/5.8.0/`精确候选位置未见；其它Pack缓存/用户位置**UNKNOWN且未搜**。
- [RTE声明:3716–3727](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L3716-L3727>)是CORE5.5.0/package5.8.0。
- [现存旧RTE头](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/RTE/_standard_robot/RTE_Components.h>)仅空include-guard，注释仍旧target；新target同名RTE目录未生成。未让UV生成或修改它。
- [工程本地cmsis_version:34–38](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/Drivers/CMSIS/Include/cmsis_version.h#L34-L38>)宏为Core5.1，文件注V5.0.2；不要与RTE CORE5.5/package5.8混称同版。
- [project SFD字段:36](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L36>)指STM32F40x.svd，该精确Pack路径未见；当前PDSC对F407宣告STM32F407.svd。属于debug元数据差异，未改字段，也未据此判compile失败。

## 两个授权库：只列成员和属性
- 输入只用stage1内的[AHRS库](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/components/algorithm/AHRS.lib>)与[DSP库](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/components/algorithm/arm_cortexM4lf_math.lib>)；未重hash423来源或原ZIP。
- `armar -t`实际均exit0：[完整成员表](<LIBRARY_MEMBERS.json>)。AHRS为1成员；DSP为272成员。
- 有界只提取3个对象到本V2目录：AHRS唯一成员，以及DSP的float/int各1代表；[精确argv与提取对象SHA](<LIBRARY_ATTRIBUTE_COMMANDS.json>)。
- 同路径fromelf仅`--text -v`，无`-c/-d/-s/-g`；没有disassembly、data/debug内容dump或执行库算法。日志仅ELF头/section信息、生产者/属性。
| 属性 | AHRS唯一对象 | DSP两代表对象 |
|---|---|---|
| 格式/CPU | ELF32 LE ET_REL EM_ARM/EABI5，v7E-M，Thumb2 | 同左 |
| 浮点 | FP_arch6 / SP HardFP_use1 / VFP_args1 | 同左，实际section级属性 |
| wchar / enum | wchar2 / 最小容器enum1 | C区段wchar2/enum1；不把其它缺tag当0 |
| producer | ARM Compiler5.06u4.422 | ARM Compiler5.05 build41 |
| denormal | tag2：允许相关FTZ符号语义 | tag1：代码可要求IEEE denormals |
- [AHRS原属性:2616–2641](<AHRS_ahrs_o_attributes_stdout.log#L2616-L2641>)；[DSP float区段:1587–1653](<DSP_arm_abs_f32_o_attributes_stdout.log#L1587-L1653>)；[完整分scope标签](<STATIC_FACTS.json>)。
- DSP含`Tag_nodefaults`，保留file/section上下文；只检查2/272，不提升成全库属性一致。AHRS覆盖1/1也不等于算法、重入性或实际AHRS时域已合格。
- 生产者argv只是对象内元数据，未执行其中旧路径/命令，也未沿其路径查找其它项目。

## 兼容线索与仍待决定事项
- [实际flags:312–339](<../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx#L312-L339>)保留C99、EnumInt0、`--diag_error=warning`；CPU/LE/SP/短enum意图与上述样本无已见反证。
- 仍需实际新target对象证实VFP参数ABI、enum/wchar/对齐、有效group/file覆盖选项、CRT/libm/helper及库公共声明契约；不从FPU2或M4lf文件名直接推导全部相容。
- AHRS与DSP浮点属性的denormal要求不同；FPSCR/FZ、运行时数学语义、软double/helper与数值行为均未测，未调用任何算法检验。
- 准确u4.422工具并未在批准的四路径得到；采用现有u6.750属于明确版本选择，需父另定，不能静默视作原指定版本。
- 尚需父明确CMSIS/RTE来源与旧SFD字段处理策略；本轮不安装包、不生成RTE、不改stage1 sealed source。
- project成员类型计数为162个C、1个ASM、2个库、4个header。未来候选预算可据此按每实际TU一次、唯一隔离output、首个真实错误即停提出；**这不是本轮执行许可**。
- 下一次若批准，保存实际compile argv/依赖/警告错误和每对象ABI；全部编译通过且ABI问题明确后才进入受控首次link，保存map/U/重复符号/FLASH-RAM-CCM布局，不放松诊断/删music/换stub拼成功。

## 边界与收据
- 受信工具14条纯版本/help/成员/属性命令全部exit0；compile/link/UV/hook/flash/target/真实CAN-SPI/PHY/FK/host40重跑/旧QA/Git/新agent均0。
- stage1文件未写；只核少数本任务元数据引用，未重新全量hash423来源，库输入只复核size/mtime稳定；[静态收据](<RECEIPT.json>)。
- 本轮结论是**静态准备已完成，有已知工具版本差异与未证依赖，未批准/未执行完整target build**；stage1仍默认UNBOUND，不增加MOD4发送/刷写资格。
