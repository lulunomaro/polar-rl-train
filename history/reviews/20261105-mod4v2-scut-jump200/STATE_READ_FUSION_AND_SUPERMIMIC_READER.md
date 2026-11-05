# 状态读取候选与SuperMimic收尾读者

2026-11-06训练期间按交叉推进授权，只使用本机GPU和本地小测试来源开发，当前20k正式段、远端源码/INDEX、owner和once均未改变。sole15096本地身份一致、stdout/stderr为空，未另开SSH或生产读者。

`newton_sampling.py`将Newton solver缓存转为任务原wxyz/关节/速度/重力的11项状态输出，合并为一个Warp kernel并预分配输出。读取坐标和COM速度变换公式保持；不做物理步、动作或奖励变更。128与20000行本地合成状态测试最大差异4.77e-7，交替solver状态缓存读取正确。20k单组件Torch约0.747ms、融合约0.242ms，约3.09倍，仅本机5070Ti Laptop组件结果。

真实4环境测试在524次同一物理状态读取上比较，最大差异2.38e-7；构造/reset/DR/完整四优化器与replay保存恢复后第二次H32通过，0生产PT解码、0SSH。测试checkpoint来自本地新随机teacher，不当生产技能成绩。

第一次完整物理步交替测速器有实际错误：原Torch方法会重新绑定任务输出，后续融合仍写旧缓存，导致20638次约束和1次数值重置。原报告虽写passed execution true，不能称有效性能或物理通过，原结果完整保留。修复测速器为切回融合时重建输出绑定并每组reset，128环境ABBA四组各8controls实际结果：Torch1.2395/1.2725秒，融合1.3095/1.3913秒，0数值/约束重置，整体比值0.93014。即小批量整步慢约7.5%；不采用为下一正式段加速，也不把组件3.09倍冒称训练3倍。候选保留为待完整20k端到端实测，当前production_candidate_ready=false。

`N/review_supermimic_closed.py`为当前H32段准备了独立本地收尾读者，替代只识别PPO17Adam的旧脚本。正式运行要求POSTROUND_COMPLETED、owner完整退出/释放及模型SHA，唯一新final诊断once先写后解模。检查四个新优化器与对应更新计数、WM/pi/critic/aux有限、完整replay字段/环指针/无效样本streamcut/term|trunc、7组件DR/RNG/queues/counters、原fullPPO来源；不把BPTT优化器说成原PPO17Adam恢复。

读者同时复用正式返回中的完整训练/评测日志，并SHA核对后写出本地全文，避免另开SSH重读；all80检查真实400Hz轨迹、腿长/目标/命令/16reward/perbodycontact及重置。旧NPZ未逐tick记录physical_transition_valid，读者如实标记并对发生数值或约束重置的整个first episode作保守排除，raw flight数与无重置样本数并列，不能凭rewardflight毕业。首次本地selftest将evaluation80路径误作evaluation导致FileNotFoundError，原失败已记录；修正后仅本地随机test checkpoint/旧本地80轨迹通过，0生产PT/physics/SSH。本轮正式final仍未保存或诊断，不消费未来once。

当前段到北京时间2026-11-06 05:59:59.327921完整保存、安全退出后立即独立80。sole结束正式回传后先查原错误，再用新读者唯一诊断并对当前模型实际保存姿态原生回放。达成真实单200mm跳跃验收前不换Isaac Lab台阶地图。
