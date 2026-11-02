# 华南虎跳跃／上阶开源与本项目历史核查

用户要求：查华南虎跳上台阶的开源，并查历史 Git，确认本项目是否做过相关实验。核查日期：2026-11-02，Asia/Shanghai。本次没有启动新训练、推理、SDK 或物理实验。

结论：确实做过使用华南虎部分跳跃奖励的真实 PPO，并进一步做过真实 270 mm 台阶任务；现有记录不足以证明完整复现过华南虎某个成功上阶 checkpoint 对应的原机器人、状态机、地形课程、重置与训练配置。不能将本项目混合移植方案失败，概括为华南虎原版方案已被完整试过且失败。

## 开源是什么

官方仓库：https://github.com/scutrobotlab/wheeled-legged_RL 。本次 GitHub branches/main 实际返回 main=1a26356d6f591734d4f6f666f5cead1a6925da67，commit time 2026-10-08T08:40:30Z，message=fix gitignore。与 2026-11-01 的245源代码核查固定版本相同。

仓库公开 Isaac Sim / Isaac Lab / RSL-RL 训练、V14平地与粗糙地形任务、PPO/DreamWaQ/HIM/NP3O、播放及曲线工具和示例权重。本次没有下载或测试这些权重。README列出状态机和播放按钮，不构成 MOD4 在 270 mm 台阶上的量化成功证据。

直接查看固定版本的源码，关键区别如下：

1. manager.py 只实例化 enabled=True 的状态机。存在 jump_takeoff.py、stair.py，不等于某个训练任务默认用了它们。
2. V14 Rough-v1 继承 Flat-v1 的 airborne/落地准备，启用轮前扫描 StepUp，并设置地形及重置/命令逻辑。该路径不是仅复制几个奖励函数。
3. 当前检查的 V14/V25 配置没有启用 JumpTakeoff/Stair 的配置赋值；V14源码注释也说明旧 jump_takeoff_state_machine_cfg 已移除。不能把可选状态机的能力当作已启用配方。
4. StepUp 对轮前射线高度的时间差分判定台阶，调整高度命令并保持一段时间；没有给机器人直接施加起跳冲量。V14配置实际覆盖值：step_height_min=.12、step_height_max=.14、wall_height=.14，height bias=.16、hold=2s、max=.40。step_up.py内部的 .15/.25/.05 是回退值，不是这个 V14 任务实际值。超过 .14 的扫描突变量按墙转 timeout，因此不能原样套到本项目单级 .27 m 任务。它检测的是扫描时间差分，不是整个仓库统一的几何台阶高度上限。
5. 可选 stair.py 实现成功/失败事件、快速成功、高度进度、轮子高于参考高度及接触力等任务项；先确认真实训练启用配置，才可讨论其实际作用。
6. 当前启用的 airborne 落地奖励含空中轮力矩趋零20、触地前方向轮速10、轮速不足-10、关节限位-10、轮端前后居中10；空中部分普通奖励还会重新缩放。移植少数项没有复现这种完整阶段处理。

固定版本来源：

补充：另一聊天于2026-11-02 23:45提交fc0fbb73dd7532905fe9bf3c8396f51df960f2d8，核到了公开rough_rotation_stair/2026-07-23_16-23-21 checkpoint保存配置。官方pretrained README明确评价该模型上台阶能力；其保存配置关闭状态机，应与当前Rough-v1辅助流程区别。当前12–14cm扫描阈值不是此公开模型的能力上限，不能说没有专门上阶模型。保存配置与视频、270mm、MOD4验收尚未一一绑定。复用Git的history/reviews/20261102-scut-standing-step-video-115-128/REVIEW.md，不复制其源文件。

- https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/manager.py
- https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/step_up.py
- https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/stair.py
- https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py
- https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py

245已归档12份关键源文件与 Git blob逐字节核验；本次重新读取其完整相关配置/状态机，再通过网页工具读取固定版本主要文件。一次使用 urllib 直接取 raw.githubusercontent.com 源码的额外校验在25秒读取超时，branch API 成功；不将该次请求称为字节核验成功，也没有因此安装依赖或重试物理任务。

## Git 历史证明了什么

| 原日期／commit | 实际工作与证据 | 能得出的结论 |
|---|---|---|
| 2026-09-29～10-05；docs/REPAIR_TIMELINE.md | SCUT平地/粗糙地形适配、自转和课程相关修复 | 早已借鉴SCUT，但不是270 mm跳台复现 |
| 2026-10-07；e6d6290ba780442b486c833e1d285b518b0fe914 | 原V14_2 USD、公开model_15000、32环境30s闭链测量；非MOD4、0PPO | 确实运行过华南虎原机器人/策略做诊断，不能当上阶训练 |
| 2026-10-19；cf8894e78b7c034b9ced6bde9745bbe8d3382502 | SCUT起跳竖直速度、轮位于机体下方、空中轮力矩趋零；复旦补飞行/收腿/伸腿/姿态项；原生产RewardManager回读、actualGO、PPO和模型保存 | 真实训练，非仅写方案；但属于混合适配 |
| 2026-10-19；3778db1e16f5da80a6e11a555d8aa2373f503bba | 首轮完整结束：H1新增72更新，17Adam656820→658260，完整final cf5ae0b9b7fda2811b618f88dc5c35b65bb7d8826d8e72ee554ecba64d4d6db5；随后续训 | 证明完整训练轮实际发生。局部MuJoCo诊断约4.7cm腾空，但请求准备门槛未满足，不能算270 mm技能 |
| 2026-10-21；e4f46a96a2cda5b5bc9e3621a532e9917bc412ed | 原专家评测后换到真实270 mm静态台；32环境native诊断31起跳、0上阶 | 有真实台阶实验；该条是诊断，不能当PPO结果 |
| 2026-10-21；2874aedc26db486ea19e4a2328ee2f746af1d6e6 | V92原owner/worker/actualGO及正PPO；H1 model_update1 16867131B SHA9daf2d264830a1633549f468f5a9337d49428c885dde1f397b50d9f6f81fb0f2，Adam674760 | 已进一步进入真实270 mm PPO；不是只有native、也不是成功证明 |
| 2026-10-22；0fdb24bd67cbb0442c706de643aa7cc3b15cb989 | 前向/净空奖励修复，空中轮力矩权重20→.5等 | 后续已持续修改，不能统称原样SCUT方案 |
| 2026-11-01；7b045e78a82e92b8b3c03b32e9ba68edafb6d972 | 245再次核查原版奖励/状态机；明确没有替换当前奖励 | 是源码审阅，不是新一轮SCUT训练 |

10月19原人类指令已经保存在Git：要求参考华南虎跳跃奖励，并允许复旦补足。实际实现仅在ready的public4请求行启用适配项；普通行保持原奖励。push-vz权重1、wheel-below-base权重2是MOD4适配值，非声称华南虎已发表同值；零轮力矩20/sigma1.5保留。这里既没有移植完整原训练流程，也没有完整移植其地形/重置课程。

对应Git内路径：

- history/experiments/20261019-scut-fudan-public4-jump-reward-one-hour-three-experts.json
- history/evidence/MOD4_SCUT_FUDAN_JUMP_REWARD_20261019/MOD4_SCUT_FUDAN_JUMP_REWARD_20261019/reports/THREE_REAL_GPU_ACTUAL_PPO_LEARNING_METADATA_VERIFIED_OR_PENDING.json
- history/experiments/20261019-scut-fudan-second-hour-closed-source-and-local-behavior.json
- versions/20261020_two_linux_policy50_series/H1_STEP270_ACTUAL_PPO_E3BRIDGE5_CLOSED_V92_20261021/files/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/reports/NEXT_ACTUAL_H1_STEP270_PRODUCTION_PPO_E3_CONTINUING_V92_WORK_ORDER.json
- versions/20261101_mod4-human10mm-depth-stair-supermimic-admission246/SCUT_UPSTREAM_JUMP_STAIRS_REWARD_REVIEW_V245_20261101/reports/ROOT245_PRIMARY_PINNED_REWARD_STATE_MACHINE_AND_TERMINATION_REVIEW.json

以上是已核查的具体范围，不宣称恢复了电脑上全部历史。目录名中的“第十八小时”等不能直接累计为18轮完整、相同任务且有效的训练。

## 对当前路线的意义

当前455不是华南虎原奖励：是已保存50Hz前馈与学习残差、实际onpolicy PPO、参考跟踪reward，actor还接收59维计划参考。无online MPC接管，但也不是自主depth-only策略。

455完整关闭后的实际456评测已经完成：80个首episode，0严格成功、0首次整轮越沿、0双轮leading-cross，80曾腾空；17姿态终止、63跑满8s，平均6.58175s。当前模型原生审图看到三个选例台前撑住、另一个倾倒，不能用存活时间当成功。与446相比存活略增，仍没有解决上台。456中个别轮台顶接触力最大52.967N；完整双轮足迹台顶支持时长仍0，不能误报所有台顶力恒0。

更有价值的后续工作是将“接近台沿、起跳、轮净空、整轮越沿、实际台顶落地稳定”逐阶段和真实rollout对齐，并明确验证哪一个原版配置真正产生其上阶行为。当前证据不足以把问题简单归于RL不可行，也不足以保证多训一小时会成功。本次仅完成研究与迁移，不以查阅请求自行启动新训练或修改奖励。
