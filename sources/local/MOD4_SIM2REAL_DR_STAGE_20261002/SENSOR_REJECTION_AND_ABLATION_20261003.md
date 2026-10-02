# 2026-10-03 传感器候选拒绝及受控诊断交接

本文件优先于 PLAN_AND_HANDOFF.md 中“配对仍在进行”的历史状态。生产仍在 MOD4_scut_spin_rate_20261002；传感器候选没有正式接管，没有 SENSOR_PRODUCTION_STARTED 或 SENSOR_TRIAL_ACCEPTED。不能把候选 attention_required 当成主训练故障。

## 已完成的真实验收

成熟 model14817 / 3 rad/s 的两 seed、站跑/自转、white_v1 sensor off/on 配对通过。四份 on 和一份 off 重新仿真，另外三份 off 为有证据的冻结基线复用，不是八份新仿真。见 frozen3rad_sensor_decision.json 和 FROZEN_BASELINE_REUSE_RECEIPT.json。

最新正式 model15150、seed20261002 的切换前回归中：sensor off 站跑通过所有已训练组；sensor_v1 的 +1.5m/s 组仅 6/8 通过，低于原 80% 实验准入。自转 ±1/±2/±4 和启停反向两边都通过。initial root/q 与权重严格配对，见 latest4rad_before_handover_decision.json。没有放宽门槛，没有从零训练。

传感器开启时失败样本（索引用 per_environment.group_ids，不连续切片）：

| 环境 | 组 | 失败项 | off | on | 原门槛 |
|---|---|---|---|---|---|
| 35 | +1.5 匀速 | 峰值倾角 | 1.433° | 25.760° | ≤12° |
| 35 | +1.5 匀速 | 最长双轮低载 | 10ms | 15.5ms | ≤15.01ms |
| 65 | +1.5 匀速 | 峰值倾角 | 2.481° | 12.047° | ≤12° |
| 53 | +1.0 匀速 | 峰值倾角 | 2.154° | 15.263° | ≤12° |
| 4 | −1.5 匀速 | action delta | .0674 | .2005 | ≤.18 |
| 4 | −1.5 匀速 | 左/右滑移近似 | .0670/.0683m/s | .1882/.1555m/s | ≤.15m/s |

所有上述样本的实际感知 lag 为 1 个控制步，即10ms。这个相关性尚未隔离证明延迟就是原因。倾角25.8°是实际姿态异常，不能仅归为接触统计或滑移代理问题。滑移仍是输入网格最低支撑点近似，不是 PhysX 接触流形；低载不是腾空。

交接保护已恢复原监督器1577904；实际 trainer2009619继续 cap4/white_v1，源model15150完整恢复。00:45:51新run最新model15400（SHA5174cc3c…）已CPU回读actor/critic/optimizer/std/iter共68浮点张量完整有限。生产源指纹全部匹配，没有双开。原监督器照常安排已有4档复核，不能再次运行旧候选一次性交接 main，或重复给已经结清的旧段记账。

## 已启动的唯一诊断

新脚本 isaac/mod4/run_sensor_ablations.py 在候选目录，只冻结 model15150、seed20261002，各80env×1500控制步15秒，顺序验证：

- sensor_noise_v1：原偏置和噪声，感知延迟固定0；
- sensor_delay_v1：原每回合0/10ms感知延迟，偏置/噪声固定0。

两种消融消耗相同RNG序列，与full sensor_v1配对；CPU已验证原full profile输出逐元素精确不变、相同随机状态、无串回合、因果延迟。没有改主训练代码、物理、硬件、奖励、PPO或验收门槛。主训练并行时账本仍合法增加，诊断自身不做PPO。

worker2101415 / child2101457仅为启动时定位，需查真实/proc身份。输出 reports/sensor_ablation_model15150_20261003/status.json、comparison.json及各attempt报告；日志 supervisor_sensor_ablation_20261003.log。若原监督器启动已有评测，脚本停止自己的probe并用新唯一attempt路径接续，最多三次，错误/部分日志保留。不重复启动、不覆盖报告。

旧候选源保存在 reports/sensor_ablation_source_before_20261003；ABLATION_SOURCE_FREEZE_20261003记录新诊断源。旧SPIN_SOURCE_FREEZE是消融前候选，不代表现在候选代码，后续正式验收必须按实际选定版本重新冻结，不能绕过源核查。生产root自己的源冻结仍完全匹配。

## 接续动作

先读消融实际结果及逐环境失败项。同一seed的因果证据不可直接当多seed鲁棒性。若只有无延迟noise档通过，优先把噪声/偏置作为第一训练档，再单独准备延迟；需要同候选两seed站跑/自转配对和实际参数回读。不能盲重跑full sensor_v1或降低原验收标准。如果noise也失败，继续隔离传感器通道/降低压力范围，并明确这是课程变化而非硬件标定。

再次接管必须针对最新正式权重、新唯一输出名及实际旧父/trainer身份，先关闭旧父启动权限、完整保存边界退出、结清尚未记账尾段并取得同一canonical锁。不得再次结清15150之前已经结清的段。20k及PPO预检不得和现有20k生产并跑；PPO预检计同一预算、权重弃用，正式完整暖启动。新阶段实际部署后才替换Ubuntu Rich。

原预算总180000秒，两个20h扩展早已应用，禁止追加/清零charged/复制账本。每2小时线程巡检保持。移动0.15→0.3→0.5m/s净世界进度、目标高速原地120rpm和Rough适配仍是后续任务，不宣称已经实现。传感器档稳定后优先真实接入移动SDK，不能全部剩余时间只叠纯转。


## 2026-10-03 对照已完成（本段为最新）

同15150、seed20261002、相同初始root/q和RNG的两个80env15秒冻结消融已完成，comparison.json已下载为本机ABLATION_COMPARISON_20261003.json。noise-only已训练64个样本全部通过原实验准入，最坏峰tilt6.283deg，无所核查指标违规。delay-only虽然各组87.5%或100%满足原80%组门槛、原admission布尔仍true，但存在真实严重异常：env75@+1.5峰29.541deg、双轮低载20ms、间隙2.013mm；env53@1m峰22.811deg；env4@-1.5 delta.2086、滑移代理.2045/.1521。不能以组通过率掩盖这些样本，或声称10ms延迟已安全适应。

本组受控对照指向延迟引起的鲁棒性不足，仍仅针对该checkpoint/seed，不冒称所有阶段/实车的普遍原因。先选择sensor_noise_v1（偏置/噪声且lag0）作为下一候选；10ms延迟需独立逐步适应/验证，当前不原样强切full sensor_v1。噪声档尚未生产部署，需要同最新成熟策略两seed站跑/自转配对、实际参数回读、完整PPO及保存边界接管。延迟消融的原true与失败样本都保留，不改门槛。

主root model15583第二次4rad/s技能和flat回归通过，当前原父1577904正在顺序执行同候选两个seed nominal/white的原定多seed复核（实际eval2199662只是读取时定位）。这是监督器主动保存后的冻结评测，无trainer是计划内，不是故障；不要抢发重复探针或重复启动。4档多seed最终结果未齐，完成后可能按既定规则到6，先读实际cap/状态再重基新DR候选。读取时canonical剩66606.55s约18h30min，无active_segment，冻结评测不扣PPO。本次没有新增预算。


## 2026-10-03 03:15 最新正式晋级结果

model15583的4rad/s两个seed20261002/20261003、nominal/white_v1、flat/spin全部8份15秒回放已完成，四对初始root/q严格相同，父receipt rate4p0_model15583_multiseed.json pass=true。纯4档四报告实际+3.9903至+3.9958、−4.0176至−4.0260rad/s，全部纯4组8/8技能与存活通过，最坏峰tilt1.2542deg。原window影子未改，非实车认证。

原父已把候选上限改为6并开始rate4p0_model15583_next_short.log的短物理预检，当前eval2208477仅定位；没有正式6档trainer时不能说6档已经学会/开训。只有新档短/全量物理和完整PPO预检通过后才从正式15583暖启动，预检权重弃用。white_v1保持，新增sensor_noise_v1仍未部署，不能同时升yaw和加传感器DR。继续查父实际stage/cap/receipt。

传感器候选env仍旧4档，仅15150噪声消融证据，不能冒充最新6档兼容性。后续按当前成熟cap重基噪声首档，做最新正式权重两seed回归/实际回读与安全接管；不要盲启动旧sensor one-shot。移动0.5m/s目标保持，需接续真实SDK/多周期净进度/PPO适配，不能所有剩余预算只提高pureyaw。读取时原账本余66606.55秒约18h30min（冻结期间不扣），无新预算。
