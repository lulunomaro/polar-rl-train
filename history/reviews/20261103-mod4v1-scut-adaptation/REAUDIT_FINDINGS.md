# MOD4v1 / SCUT 奖励与训练接口再复核

日期：2026-11-03。请求：重新核对是否一比一逐行适配、查找漏洞或 bug。复核基线是本阶段普通补充 `eac59d9e10f3305e12487123d7ab0d84d8764eff`，SCUT 固定来源 `1a26356d6f591734d4f6f666f5cead1a6925da67`。本次为已有阶段普通补充，不重建 trial、不改旧标签。

结论：**原版本不能称为整条程序一比一，也确有接口与生命周期 bug。** 本次修复下列10组问题，原失败报告保留。修复后的14项针对性检查与12项集成检查通过；目标定制 SDK 原生验证仍未执行，不能保证无剩余 bug，更不能据此宣称270mm技能完成。

源行号以 `project/isaac/mod4v1_scut/SOURCES.json` 绑定的原文件为准；目标行号见本次 `REAUDIT_LINE_MAP_DELTA.json`。旧 `LINE_MAP.jsonl`、`COVERAGE.json`、`REWARD_TERMS.json` 是原阶段证据，不覆盖；14,492行自动处理索引只说明各行的处理类别，不证明逐行动过、语义完全相同或所有原生分支均已运行。

## 已修复问题

| ID / 级别 | 原代码依据与原适配问题 | 修复及实际影响范围 | 验证 |
|---|---|---|---|
| F01 / P1 | base_env:3699、4047–4051、3115、3131；Airborne:712–909。原 `begin()` 在当次奖励前同时推进 observation/command hooks，把新探到的台阶状态提前用于当次奖励 | 恢复原调用顺序：done→reward；Airborne由原高度helper按common_step更新，StepUp/Stair在reward尾部和observation各调用一次。`ScutVecEnv`缓存同一返回观测，避免runner重复getter额外推进。主要影响启用状态机的jump270 | 重构台阶跃变：当次新增Stair奖励为0，reward尾部计时.02，observation原第二次hook后.04；重复getter只转换一次 |
| F02 / P1 | base_env:5124、5137与各状态机on_reset。原reward独立episode计时及ground/forward/near数据未在新姿态首帧正确刷新；统一失效缓存还会影响未reset的环境 | reset选中env计时清零；在manager将reset姿态写回后、构造观测时重新取其实际扫描，播种新局前扫历史。未reset环境继续使用同一control缓存。此按env缓存隔离是MOD4桥接选择，非逐字复制原全局invalidate | 只reset env1；验证其ground从.27变0、前扫delta归0，env0/2仍保留.27及原计时，第二次读取不再重复扫描 |
| F03 / P1 | base_env:4924–4949、5014–5022。原适配仅对部分状态置badmask，未恢复原速度越界终止；StepUp墙事件能把terminated改为timeout，消掉MOD4 closure/mimic重置 | 恢复原joint500、body linear100、angular200阈值及非有限检查；状态机mask后强制OR数值异常/closure/mimic。timeout与termination同时为真时RSL使用timeout & ~terminated，避免错误bootstrap | 墙事件+closure、101m/s、NaN角速度三例都保留强制termination；数值坏环境奖励归零 |
| F04 / P2 | 保存env.yaml.height_scanner为resolution.01、size(.02,.02)、offset(0,0,5)、max_distance1e6；原适配改为.05/(.1,.1)/(0,0,1)/4 | 直接读取保存配置。台沿附近网格平均高度能相差9cm，影响相对高度与腾空判断；两CLI profile均受影响 | 保存YAML字段一致性检查、台沿离散采样反例 |
| F05 / P2 | base_env:756–804；保存YAML左右wheel scanner均为空，helper回退到chassis ground；原适配却给每轮增加独立向下ray | 两轮地面高度恢复为机身scan；保留左/右轮实际body中心，未解析代入.27地面。左右重排只改变存储次序，成对量统一使用同一顺序 | .27地面、全无效ray回退env origin、部分有效ray平均三例 |
| F06 / P2 | base_env:210–274。原前扫起点+5m、max_distance取scanner、漏扫回退ground；原适配为+2m/5m且漏扫整批抛错 | 恢复起点、最大距离、有限mask与原fallback；forward_offset默认回到.10（保存配置实际仍.50）。关闭扫描profile不额外查询前扫 | 源码逐句核对；调用/回退的目标SDK实际raycast尚待原生验证 |
| F07 / P2 | base_env:3435–3472与Airborne:656–710是不同公式。原Airborne helper误用基础normalized-square，并硬编码基础ratio=.03、漏掉上下边界ratio回退、把0边距提前clamp | 基础分支保留归一化平方；Airborne位置项恢复弧度L1和速度计数；边界比例按原cfg，只有除数clamp。MOD4四motor替换SCUT rear2仍属明确语义替换 | 独立逐关节L1期望、改ratio=.10边界测试；两个CLI配方没有这些limit项非零权重，所以不谎称改变了已启用的生产奖励；可选V14分支受影响 |
| F08 / P2 | 原obs_input_scale_streams配置被适配函数忽略 | policy/critic分别按配置选择是否scale，clip仍先执行。保存配方原本两流启用，所以该固定配方数值不变 | 仅policy缩放场景中critic=1、policy=5 |
| F09 / P2 | stiffness/damping按actuator返回顺序拼接，未像torque一样按六动作名字重新排序 | 按实际pd.leg_ids+wheel_ids映射到奖励动作ids；避免SDK/actuator顺序不同使特权字段串位 | 特意打乱四腿与两轮顺序，输出恢复[10,20,30,40,50,60]及[1,2,3,4,5,6] |
| F10 / P2 | runner_config把actor_hidden_dims同时当critic_hidden_dims | actor/critic各读自己的保存字段。原配方两者恰好相同，当前配方数值不变；不同网络配置会受影响 | 人为设critic[32,16]并检查actor原结构保持；真实RSL合成rollout/update/save/load集成通过 |

## 一比一的实际边界

| 范围 | 当前证据与结论 |
|---|---|
| 基础奖励表达式 | 86个raw项由固定`_get_rewards`原AST载入，未改函数体；这不意味着86项都进入总奖励。trained_stair共37权重键、26非零；jump270为39键、28非零 |
| 保存配方 | trained_stair基础reward权重与保存YAML相等；原保存状态机关闭。jump270显式打开Airborne/StepUp/Stair、改检测高度及目标、加2项各weight1，属于任务配置变动 |
| 机器人语义 | SCUT front/rear关节到MOD4 crank/hip为几何/控制替换，rear2没有同义关节。导轮与mimic不冒充动作，碰撞集合使用MOD4实际非主轮body；这些不能称物理等价 |
| 资产 | USD SHA2c421a8e…、contract SHAbae3203a…，首次task import前绑定。31body/30DOF/6action，按名字解析。没有本次MJCF后端实现，也未将历史H1模型称MOD4v1 |
| 观测/动作 | actor35/critic78字段框架移植；保留MOD4 D0–D7噪声/偏置/100Hz反馈队列、原PD/DC/动作队列。不是原SCUT传感器、随机化或执行器的逐字复现 |
| 终止 | MOD4 .75rad姿态、chassis50N、低机身、.01m closure、.01rad mimic等继续保留；原SCUT40°/base1N/连续20controls未搬成同一规则。不能称完整MDP等价 |
| PPO与保存 | 原保存超参数映射至RSL5，24rollout/5epoch/4batch。合成数据真执行RSL/GAE/PPO/save/load，生产PT读取0；该证据不是目标SDK rollout。原H1 actor103/critic106不可隐式移植 |
| 逐行索引 | 来源17文件SHA/blob可核验；原14,492行索引包含排除的debug/其它任务、配置行和函数体。AST复用只证明公式来源，不能代替输入/调用时机/动态行为核对 |

## 仍需在任务层处理的缺口

1. 恒定vx=.6m/s没有独立台顶停稳命令阶段，与最后速度≤.03m/s的strict270验收目标不完全一致。本次保持显式配置，不为冒称“一比一”偷偷改成新奖励或改验收。
2. 台沿前机身scan仍在低地时，基础height项相对机身下地面，而新增Stair height项相对所检测台面，可能拉向不同高度；已有CPU反例是奖励语义证据，不是实际不可达性/因果结论。须用目标模型原生轨迹与分项曲线决定后续调整。
3. 目标定制SDK的raycast、reset后传感器刷新、实际actuator/material/contact数据布局及fullDR回读仍未验证。CPU测试不证明这些API在目标后端可运行。
4. 当前仅软件修复；未启动新physics/GPU训练，没有新的270mm实际成功证据，也未复用旧H1评测冒充MOD4v1。

## 本次保存的检查

| 报告 | 结果与含义 |
|---|---|
| REAUDIT_BEFORE_FIX.json | 9项：5失败、3错误、1通过。3错误是新回归测试要求的API尚未实现，非线上原生崩溃 |
| REAUDIT_AFTER_FIX_ATTEMPT1.json | 首批修复9/9通过；保存该时刻结果 |
| REAUDIT_AFTER_FIX_ATTEMPT2.json | 扩展重置扫描/轮下语义/PD顺序/critic配置后13/13通过 |
| CPU_REAUDIT_INTEGRATION_ATTEMPT1.json | 原12项集成检查全部通过；包含真实RSL CPU合成rollout/GAE/update与临时fixture保存读取；0生产PT/0physics/0GPU训练 |
| REAUDIT_NUMPY_ORACLE_ATTEMPT1.json | 14项中1失败：NumPy float64 linspace产生±.09999999999999998，runtime float32为±.10000000149，严格deadzone <.1掩码不同；属于oracle输入精度问题 |
| REAUDIT_NUMPY_ORACLE_ATTEMPT2.json | 将oracle命令输入统一为runtime float32后14/14通过；生产奖励未因此改变。26个非零raw项及一次dt加权总和，在9个合成样例与独立NumPy方程一致；容差2e-5只用于CPU数值比较 |

全部原false/报告均保留。读取过程中曾猜错共享`explicit_pd.py`文件名（正确为`explicit_pd_sdk_adapter.py`）、尝试不存在的state_machine路径、一次广域rg碰到无关目录权限拒绝，均未改文件或派生生产任务；后续按SOURCES/DEPENDENCIES精确定位。

本次没有新SSH、GPU扫描、budget/canonical写入、production checkpoint反序列化、旧once重放或历史目录清理。历史H1 476已关闭、477已评测；不再作为待评任务。下一步是使用原共享owner的真实资源释放/锁准入后执行本版本目标SDK原生验证，再推进实际RL与独立strict270验收。
