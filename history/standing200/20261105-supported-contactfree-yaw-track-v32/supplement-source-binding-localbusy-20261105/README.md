# V32冻结源接入准备（尚未部署）

本目录把已经归档的V32站高、蹭沿、支撑收腿、忽略底盘与导轮接触终止、偏航与轮距奖励接到实际V30使用的旧SDK。奖励公式仍引用`scut_recipe_v32_supported/reward_model.py`原SHA；V31/V32原候选及草稿报告全部保留。

已从Git `bf5a683e3009ab7f73fdce3faeab3bc71189f890` 读出与V30冻结清单一致的sdk/checkpoint/train源码。新增11项本地源转换与轻量数组检查通过；没有读PT、连接SSH、启动SDK或推进物理。

- 将实际单台阶场景与flat原PPO/配置分开绑定，修正旧eval200闭包仍保留rough奖励与命令元数据的问题，保留真实地形射线传感器。
- 完整恢复只允许静态命令字段`_mode_enabled`从原3模式变为一个关闭模式；其它命令tensor仍严格同形复制。actor/critic/STD/Adam/LR、全RNG、原DR组件队列与一次fresh physical reset均沿原恢复函数。真实恢复通过与否仍由运行回执判断。
- 保留9个单body接触传感器，运行时核body名称和一个course filter。实际points/normals/force映射仍待有限原生验证。
- entry直接引用已冻结V18入口；owner直接引用原有限canonical owner，修正嵌套旧wrapper未替换内部任务名的问题。
- 独立评测记录reset前target、实际关节/力矩、原终止原因、加权奖励，以及400Hz底盘支撑/蹭沿力、轮距和目标高度；奖励回执在物理reset前缓存。

`LOCAL_BINDING_REVIEW.json`是最初生成草稿，`reports/SCUT32_NATIVE_BINDING_PRE_CORRECTION_SOURCE_20261105.json`保留其精确源码。只使用`LOCAL_BINDING_FINAL.json`中的本地最新源码SHA；`prepare_local.py`已经执行，禁止再运行。旧`scut_recipe_v32_supported/FROZEN_FINAL.json`继续描述公式候选，不用于校验这里的接入修复。

当前03:09本地广CIM仍有foreign jump200 collector70820和E3 W9 collector68888及其父70872。未打开SSH，V30 closed once仍未消费。释放后先完成唯一V30 closed回传与现有轨迹原生审查，再完成本目录的部署清单/controller与新任务冻结，按原canonical/privateGPU/finite准入做必要有限原生接触/命令恢复检查；这些步骤通过后才生产。原预算、严格reserve、增强D0–D7物理和完整保存边界保持。
