# 华南虎到增强MOD4v1：本轮逐行适配结果

2026-11-03；基线commit `0e9c71a06d802723185fa54b2410915d931e6925`。这是既有阶段的普通补充，原trial和历史失败保留。

本轮已修改实际奖励/观测/终止/命令/训练代码，并核对最终继承链 `V14 → V13 → wheelbipe25_v3`。最新CPU检查为16+14+12=42项通过。目标定制Isaac SDK原生验证尚未执行，当前没有本适配的实际RL或270mm成功结果。

来源固定在SCUT commit `1a26356d6f591734d4f6f666f5cead1a6925da67`。原17个文件加上V13、命令模块、地形命令管理器共20个文本来源；全部SHA与Git blob逐一核对。增强USD与contract使用既有身份索引，本轮没有为归档读取USD、生产PT或大raw。

## 如何逐行检查

`LINE_ALIGNMENT.jsonl` 对20文件共18,540个物理行各保存一条记录，包含原文件key、原行号、函数、YAML字段路径、原行文本SHA和处理规则ID。空白/注释也单列；15,684行不是空白、注释或AST文档字符串。源代码仍在 `SOURCES.json`/`SOURCES_EXTENSION.json` 指定的既有路径，避免再次复制原树。

`LINE_ALIGNMENT_RULES.json` 的39类规则给出当前目标文件/行、处理理由、相关检查函数和native状态。读取时再应用 `LINE_ALIGNMENT_CORRECTIONS.json` 的35行分类修正：初版把V14构造段过宽地归入gimbal/debug，单帧policy返回也混入history分支；原索引保留，改正单列。原AST复用行引用其实际执行来源行，适配函数另列入口；一个原语句可能拆成数句目标代码，不能把相同行号冒充语义等价。函数范围映射只表示由该适配函数承担，未声称该原语句有逐字相同的目标语句。`LINE_ALIGNMENT_SUMMARY.json` 固定初版文件身份和计数，本轮SOURCE_INDEX包含修正文件。

以下是本轮重点改变的执行语句及其对应位置；目标行号的机器可读版本以RULES和本轮SOURCE_INDEX为准。

| 原来源与行 | 原语义 | 当前目标 | 本轮处理 |
|---|---|---|---|
| base_env:4863–4895、4915–4917、4995–5003、5017–5022 | 接触>1N、40°、连续20controls；timeout=max−1 | upstream.py `BASE_METHODS`；sdk.py `resolve_done` | 直接加载原done/duration函数，替换此前MOD4 .75rad/chassis50N/低机身规则；closure/mimic及数值强制重置继续立即生效 |
| base_env:3177–3179、3236–3238、4971–4992 | raw obs在clip/sanitize前统计；warmup后立即终止异常 | rewards.py `cache_raw_observations`；sdk.py `observations` | 恢复两个观测流的raw统计与按env清理 |
| vec_wrapper:181–185 | terminated或truncated结束；infinite horizon将truncated交给PPO | train.py `ScutVecEnv.step`；sdk.py `resolve_done` | 修复一律timeout & ~terminated的过度屏蔽；仅MOD4强制重置清掉timeout |
| base_env:4043–4051 | 当前奖励完成后推进command一次；resample height；state hook | commands.py `RewardTailCommand`；rewards.py `_resample_custom_cmd` | 恢复真正命令生成器，抑制Manager后续重复compute；不把新命令用于刚完成的奖励 |
| base_env:5592、5595、5601 | counter增长的env才重采height，保存新counter | rewards.py `_resample_custom_cmd`、`resample_height` | 不再空实现；无height wave/permission配置的支路保持关闭 |
| parent_env:171–181、376–379 | V13把状态机覆盖后的command写回generator | upstream.py `bind_base_functions`；rewards.py `_on_command_updated` | 继承链中此前漏接的同步已接回，原同步函数体未改 |
| current_env:225–247；train:267 | training iteration传给command模式门控 | train.py `set_training_iteration`；checkpoint.py `restore` | 每轮及恢复后同步，不让special modes永远按iteration0运行 |
| base_env:3107–3108 | 返回观测时推进动作历史 | rewards.py `finish_observation`；sdk.py `refresh_observation_context` | 从reward尾部移回观测入口，getter缓存保证一次 |
| base_env:3123、3128、3131 | 先捕获height，再推进observation状态 | sdk.py `observations` | height提前缓存；mode取状态更新后结果 |
| base_env:3262–3279 | critic基础28字段 | sdk.py `observations` | 保留clean基础28；不先拼入mode7 |
| base_env:3280–3288 | velocity3、height1、mode7、priv39 | sdk.py `observations` | 修复“尺寸78正确、位置错误”的接口bug |
| base_env:4261–4312 | clip后按stream执行scale | config.py `observation_component` | policy/critic分别执行；沿用前轮已修复逻辑 |
| base_env:210–297、826–898 | 同step首次请求前扫后缓存；命令方向参与查询 | rewards.py `forward_scan`；sdk.py `read_forward_scan` | 去掉提前查询造成的旧命令方向；延迟到原helper首次使用 |
| base_env:5030–5137 | 终态日志、重置状态、清理duration与缓存 | sdk.py reset hook；rewards.py `reset`/`refresh_reset_scans` | 保留选中env重置，避免清掉其它env的当步扫描差；终态日志在manager重建log后合并 |
| base_env:2098–2109；parent_env:48–54；current_env:118–145 | 基础列表被V13/V14覆盖，最终有害contact含guide | config.py结构名集合；rewards.py构造 | 29非轮body含8导轮；实际无gimbal分支终止为chassis+8导轮。不能用基类列表替代最终覆盖 |
| base_env:551–613；3435–3472；airborne:656–710 | 轮腿几何、rear2软限位 | rewards.py几何与`motor_stop_terms` | hip锚点取MOD4契约；无同义rear2，明确四motor替换；基础归一化平方和Airborne弧度L1分别保留 |
| train:275 | learn(...init_at_random_ep_len=True) | train.py `initialize_episode_lengths` | trained_stair恢复随机起始episode时钟；jump270显式从0开始 |
| trained_agent:policy/algorithm | 普通RSL PPO配方 | config.py `runner_config`；train.py实际rollout循环 | 两网络各读自己hidden_dims；24rollout/GAE/5epoch/4batch等原值保留，循环读配置 |
| train:253–259与原runner保存 | 完整学习状态续训 | checkpoint.py `save`/`restore` | FULL_V2记录观测语义；当前iteration表示下一轮，不额外+1；原子全状态恢复后一次fresh physical reset |

## MOD4v1模型与任务替换

| 项目 | 实际替换与后果 |
|---|---|
| 资产 | 增强USD `2c421a8e…`、contract `bae3203a…`，首次task import前绑定；31body、30DOF，6个动作按名字解析。实际原生读回仍待完成 |
| 动作/PD/DR | 四腿crank/hip和两轮；导轮/mimic不是动作。原MOD4 PD、DC限幅、物理队列、D0–D7不换成SCUT原执行器/随机化，因此不能称整MDP相等 |
| 接触 | 数据先按sensor.body_names重排到robot.body_names，再按名字分组；SCUT的gimbal在MOD4不存在，按V14自身无gimbal分支选chassis+guides，而非虚构gimbal |
| 配方 | trained_stair原37键/26非零基础奖励，状态机关闭；jump270为39键/28非零，额外启用两个Stair项和Airborne/StepUp/Stair，是明确任务改动 |
| 命令 | trained_stair恢复保存的ranges/heading/special/standing10%与5–15s重采样、height .2–.42、20s。jump270是.6/0/0、height .25、8s、无heading/special/standing |
| 地形 | 当前显式单270mm台面代替原9类rough generator；原按地形命令/高度覆盖与边界reset未移植。terrain manager:129–137无generator元数据即禁用，V13:143–147、316–325走基础fallback。不能把它写成“与训练无关代码” |
| 初始状态 | 当前采用MOD4 ground-start；不搬原SCUT airborne/预定义倒地reset或云台控制。不是公开rough训练的全流程复现 |
| 观测 | actor保留MOD4噪声/偏置/100Hz反馈延迟；critic字段顺序对齐SCUT，数值来自MOD4实际状态和组件。新增USD惯量/质量来自constructor，不用旧PT覆盖 |
| 数学 | +π/−π端点、quat_inv的eps1e−9、inverse rotation的conjugate代数对齐本机Isaac原函数CPU行为；目标定制SDK的坐标实际回读仍待验证 |
| 验收 | strict270是独立400Hz测量器，未替代为SCUT成功事件。本轮未运行独立native evaluator，没有新策略成功记录 |

## 测试及错误保留

| 实际报告 | 结果 | 范围 |
|---|---|---|
| LINE_PARITY_ATTEMPT6.json | 16通过 | 终止计数、timeout、raw异常、真实命令源码与SDK父方法CPU采样、继承同步、观测顺序、导轮覆盖、角度端点、延迟扫描等 |
| LINE_PARITY_REGRESSION_ATTEMPT3.json | 14通过 | 全26个启用基础奖励的独立NumPy方程，9个合成样例及dt一次；扫描、限位、PD字段与重置回归 |
| LINE_PARITY_RSL_INTEGRATION_ATTEMPT3.json | 12通过 | 真RSL5在合成输入上24rollout/独立GAE/PPO更新/临时fixture完整存取，以及状态奖励可选分支 |

合计42项是CPU检查数量，不是42个真实episode，也不代表每个原生条件组合。没有生产PT反序列化、新physics或GPU训练。

本轮Attempt3/4曾依据基类排除导轮；相应fixture通过但语义判断错误。追到V14覆盖后已纠正，Attempt5验证接触分组，Attempt6再验证V13同步。此前报告保留，不回改成最终版本证据。前三轮regression/integration也各自保留，最新结果以上表为准。

读者错误另见 `LINE_ADAPTATION_ISSUES.json`。首次生成行表遇到尚未分类的箭头可视化helper，在写任何行表前拒绝；补上可视化规则后生成成功。这是静态索引工具错误，没有原生运行副作用。

仍待实际验证的事项是：目标SDK的构造/字段/延迟队列/完整D0–D7读回、实际mesh扫描、reset传感器刷新、400Hz manifold与独立技能评测。jump270恒速.6未包含台顶停稳阶段；基础height与Stair height在沿前可能有不同参考。它们是明确保留的任务设计问题，不能靠逐行索引消除，也未在此轮偷偷改成另一套奖励。

本轮软件对齐完成后按原owner/canonical/private/shared的实际资源准入进行一次native验证，再推进实际RL与独立验收。旧H1 476已闭合、477已评测，全部once保留已消费；本轮没有新SSH/controller/预算操作。
