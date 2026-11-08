# MorphMimic 对华南虎到 MOD4 迁移的评估

2026-11-08，北京时间。阶段ID：morphmimic-scut-transfer-assessment-01。性质：文献与源码研究、旧方向取消；没有新技能实验。

## 人类指令与实际范围

人类：“先放弃之前的工作，取消定时任务，现在开始看这个项目，他是可以不同机器人同一个策略适配的对吧，是不是很适用我们的蒸馏华南虎？”随后要求“继续”。本聊天停止旧跳跃训练、自动接续和重复教师测试，改研究MorphMimic。旧100小时与修复后训练授权不再触发旧任务。

本地实际核验时间2026-11-08T18:05:09+08:00：C:/Users/lulu/.codex/automations目录存在，mod4-10或本聊天ID匹配项为0；匹配本聊天mod4v2运行根的Python进程为0。app工具view仅返回已渲染卡片，不据此推断内部状态；取消后的本地inventory是本次可见证据。本次没有创建新automation、chat或Goal，没有连接SSH、载入PT、执行物理或优化器。远端不新增探针，历史owner已释放仅引用既有证据。

## 核定来源

- 项目页：https://lzyang2000.github.io/morphmimic/
- 作者论文：https://lzyang2000.github.io/morphmimic/static/morphmimic.pdf ，9页，Table I与III-B至III-F、Appendix B。
- 公开仓库：https://github.com/lzyang2000/morphmimic ，本次源码固定HEAD 770394b4a0cad9effbf807a6c03435d1699733d0。
- v0.1 tag对象70511b3da574403edbc2c89cc84d793a6182898b，peeled 41c8382f127a6f5109bfe047445a9180f71f1fc0；当前HEAD与发布tag不混称同一版本。
- 本地参考仓库C:/Users/lulu/Desktop/claude/mjcf/reference_repos/morphmimic，仅浅克隆/读取git对象，未安装依赖或运行项目。
- 检查README.md，robots/spec.py、morphology.py，env/actions.py，model/policy.py、state.py，train/distributed.py、multi_robot.py，constants.py。路径均相对公开仓库src/morphmimic，README除外。

## 它确实实现了什么

Unitree G1、AgiBot X2 Ultra、Booster T2参与联合训练，统一为29个功能关节、14个跟踪body，共享世界模型和完整策略权重；125维形态描述包含驱动尺度、kp/kd、力矩上限、几何和质量。normalizer、默认姿态、关节范围、参考动作、replay与部分尺度仍各机独立，不能把“一套权重”称为完全相同的全部运行状态。

三个机器人使用同一人体动作源，但分别重定向为各自参考；对应clip/frame的潜在指令对齐。策略在learned world model上通过H32想象轨迹更新，不是MuJoCo接触求解器本身可微。项目基于作者独立实现的SuperMimic，不是SuperMimic原作者源码。

Table I完整动作接口，128,786个共同clip、deterministic首次到末帧测试：

| 策略 | G1存活率 | X2存活率 | T2存活率 |
|---|---:|---:|---:|
| 各机专用 | 99.797% | 99.818% | 99.860% |
| 三机联合共享 | 99.747% | 99.891% | 99.886% |
| 只训G1，目标机器人动作参数 | 未跨机测试 | 7.7% | 1.9% |
| 只训G1，保留G1动作参数 | 未跨机测试 | 87.7% | 1.6% |

同源训练机器人共享策略的表现接近专用策略。直接迁移也受动作参数和IMU坐标影响，不能把7.7%单个设置代表全部X2迁移条件；论文另报告调整T2模拟IMU位置可改善G1迁移。因此本报告的结论是没有“任意新机器人零训练通用”的证据，而非所有直接迁移必然失败。三机联合总16.3 GPU小时，对比三个专用合计13.9，不据此承诺本项目必定省算力。实机实证是G1，另两机共享策略结果为仿真。

## 为什么需要轮腿适配

Translator.from_names要求29个canonical关节都能找到唯一native对应，缺关节或多对一直接拒绝；它不是任意DOF的图结构或padding/mask控制器。CanonicalJointPositionAction统一输出29个位置目标。morphology.py还假设人形大腿/小腿/手臂拓扑和正kp。

本聊天MOD4是6主动输入、30物理DOF与闭链/从动坐标，腿位置控制与轮速控制并存。被动DOF数量接近29不能当29个独立人形驱动。单改robot名、关节符号或125维形态向量不能使公开策略直接运行。

作者human/five-point接口的蒸馏，是其运动目标编码器到稀疏目标编码器的对齐；不是已经实现了SCUT黑盒actor到MOD4 actor蒸馏。

## 对华南虎迁移的判断与可执行设计

判断：方法方向适合，公开预训练权重不是轮腿即用模型。华南虎与MOD4都能定义双轮、左右腿和机身的功能对应，值得借鉴共同表示、形态条件和跨机动作潜在对齐；实际收益尚未验证。

建议先做有限的轨迹模仿适配，再决定是否必须联合共享世界模型。若目标仅为一个MOD4学生，不必为了“一套策略”先重训华南虎教师或所有人形分支。最小候选链路为：

1. 复用已保存的华南虎真实轨迹，提取机身姿态、相对轮心轨迹、腿长/腿角、轮速和接触阶段；按实测表现选择片段，不把所有轨迹当成功示范。
2. 以MOD4真实机构做可行重定向，约束闭链、CAD止挡、气缸行程与驱动能力。参考要对应动作含义，不逐数值复制原6维电机输出；轮子连续转角按轮速/轮相位需要另行处理。
3. 将共同任务目标与MOD4状态送入学生，以MOD4真实仿真数据适配动力学。共享策略候选需为轮腿定义canonical状态和混合位置/速度动作、各机动作映射和各机统计；形态描述扩展轮半径、连杆、气缸和驱动参数。
4. 先验证平地支撑、前进跟踪和受控压伸迁移，再讨论接触上阶；真正200mm地面自主起跳越沿落台另验。以上是研究建议，未实施或开训。

已有教师证据必须保持原分类：SCUT_MANUAL_JUMP_AND_STAIR_CONTROLLER_20261106.md记录检测适配后13cm为7/8双轮登顶、20cm为1/8。20cm案例2.99s先接触立面、3.27s越沿、最长双轮台顶支撑7.39s，但严格静止仅0.045s，未满足地面自主起跳与0.5s落台稳定。可作为接触上阶候选轨迹，不能据MorphMimic改称已验证200mm自主跳跃教师。

## 记录与未执行项

本次仅增加研究结论与方向覆盖，保留所有旧报告、检查点与annotated trial，不修改foreign/mod4v3/其它账本或进程。无新动力学验证、迁移性能、训练速度或成功率结论。

本次读者错误保留：第一次本地automation检查因CODEX_HOME环境变量未设置产生Join-Path/Get-Content错误，该输出不能证明取消；改用上述绝对路径后确认0匹配。一次rg使用了错误工作目录，0写入后在repo根正确读取。早期论文比较口头结论由本次直接读取Table I补足，评估以表中完整条件为准。没有为修复读取错误重跑任何旧物理测试。

AGENTS/WORK_ORDER/CURRENT_STATE的当前字段记录本次取消，其旧值另存历史字段。外部状态与workspace AGENTS按路径/字节/SHA及冻结对象关联EVIDENCE_INDEX；本报告与源码固定commit进入同一研究阶段Git记录。
