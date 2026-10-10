# E1 G3 完整退化审查后的接续工作单

# 华南虎持续学习与 MOD4 E1 退化：源码及实际参数审查

已审公开版本 `1a26356d6f591734d4f6f666f5cead1a6925da67`。本次取到114份源码/参数文件，6次HTTP超时原样记录。判断针对可见V14训练路径和已保存2026-07-30粗糙地形参数，不能替代其私有实现、完整训练日志或抗遗忘消融实验。

我们的实际问题位于同一E1策略连续更新过程中：G3 source32058→formal32063完整恢复actor/critic/std/optimizer、D1-D7、全局和私有CPU/CUDA流已经核验。新35mm几何的terrain_state_restored_exact=false是显式几何切换；没有证据说这次退化来自漏恢复优化器或物理状态。gate尚未训练，当前不能归因为路由器专家坍塌。E0冻结只能保护E0，无法自动保护仍在更新的E1内部旧能力。

|实际配对指标|32058旧源|32063短窗后|解释|
|---|---:|---:|---|
|35mm完整十波两轮退出，前/倒|24/27、26/27|19/27、27/27|未完成有效前缀全部保留|
|再含200mm后支撑，前/倒|17/27、25/27|13/27、26/27|倒退改善不抵消前进下降|
|旧world完整signed circle|62/64|56/64|最大abs cross .053276684→.060651110m/s，原容差与false不变|
|旧负向4π|5/8|2/8|正向仍8/8；不能拿均值掩盖逐环境有符号误差|
|旧±1.5直线误差，负/正|.024461027/.043439623|.026505746/.044777345|小幅变化；不是所有旧技能同时崩溃|

1. **旧任务一直有新rollout。** `SpecialModeUniformVelocityCommand`按迭代启用模式，end=-1表示一直保留。每次重采样在符合条件的非站立环境中做互斥概率分桶，桶顺序随机，剩余环境保持普通命令。不是每阶段覆盖上一阶段命令，也不是拿旧PPO轨迹直接重放。当前默认冲刺2000、低速旋转3000、中速旋转4000才启用；实际July30参数三者均从0启用，所以不能混用两份配置。[实现](https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/manager/mdp/isaaclab/commands.py)、[当前配置](https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py)。持续覆盖可能减轻遗忘是根据代码的推断，仓库没有在这些文件中给出与MOD4对应的因果消融证明。

2. **真实粗糙地形训练仍混有旧动作。** July30保存参数使用普通ActorCritic/PPO、24steps、LR1e-4/adaptive、std1；从flat model8000加载作finetune（resume_training=false）。基础vx[-2.7,2.7]、yaw±2π、10%站立；非站立且具备准入条件的环境中低/中纯转各15%，冲刺30%。低纯转yaw±[2π,3.25π]，中纯转±[3.25π,4.5π]，冲刺vx±[2,3]。这些比例不是整个训练批或地形族配额，不可拿来替换我们30/20/20/15/15地形比例。[实际env参数](https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27/params/env.yaml)、[实际agent参数](https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27/params/agent.yaml)。参数说明训练意图，不证明每种模式实际访问次数或最终保留率。

3. **按实际地形约束命令。** rough类继承flat_v2后换地形。普通平面和连续地形保留宽命令；stair_for_rm_rot覆盖速度±[.5,2]、非heading yaw[-1,1]，并关闭special mode和空中模式。先判断地形可支持的行为，再决定该环境采样哪些模式。[覆盖配置](https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py)、[实际地形命令管理](https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/source/agent_tasks/agent_tasks/manager/mdp/terrain/terrain_command_manager.py)。这与我们的S7净空限制一致，不能把高速旋转塞进E1跨坎/起伏/洞边。

4. **没有核到“MoE已经解决永久遗忘”的证据。** cli_args存在MoE/CMoE入口，包括router温度、负载均衡、expert辅助损失；已审注册V14和July30agent实际使用普通ActorCritic/PPO，没有对应的完整冻结专家实现与旧能力保持结果。冻结旧专家、只训练新专家、再训练gate是我们原计划的保护办法，不应冒称华南虎公开实验结论。PPO当前rollout的KL也不是长期旧任务记忆。未核到本路径使用EWC、旧教师蒸馏或经验回放来保证旧任务。[参数入口](https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/scripts/rsl_rl/cli_args.py)、[加载语义](https://github.com/scutrobotlab/wheeled-legged_RL/blob/1a26356d6f591734d4f6f666f5cead1a6925da67/scripts/rsl_rl/train.py)。

本项目可用的修复方向是**保留必要旧命令的在线采样，限制在已验收的平地与净空范围**。当前E1的RoughStraightCommand把五类地形所有环境都改为20%站立、其余BODY vx[-.3,.3]、vy=yaw=0；即便30%plane_for_rm也没有旧定向移动数据。这是最直接的分布差异。下一单轴修复应在既有平地族引入必要的旧直行和world yaw±1–2在线命令，起伏/坡/坎维持原低速yaw0；不能把world yaw1–2误写成4π移动，不能扩大S7或同时改reward/LR/DR/几何。

新命令范围必须核实际terrain assignment/净空、命令RNG完整保存恢复、初次新physical episode、实际采样直方图和两方向覆盖，再做自己的CPU/SDK/native/完整PPO预检弃权重和300s有界观察。已有clock、同几何和D0-D7证据按SHA复用，不再45min clock。候选须完整保存并复评原地形与flat/spin/world，不能用reward或健康代替保留能力。负4π属于旧诊断事实；E1不通过扩张S7高转速任务来追分。

本轮128已实际发布：只把冻结接近段.65m改.40m，仍15s、全十波、两轮200mm后支撑，32058和32063初始化配对。两轮前支撑预测仍>.2m，实际raw回放才算证据。128不更新权重，只判断窗口/接近段因素；原126/127失败保留，不宣称35mm全部通行、永久抗遗忘或RM70mm毕业。所有真实拒绝、CRC读者错误和锁定位拒绝并列保存，canonical828000/new0保持。


实际128 job/只读reader及新范围准入条件以同名JSON为准。所有旧once/main/resume关闭不可重跑；新命令修复是独立新范围，不能热改原338。
