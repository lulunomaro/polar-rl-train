# SCUT 原训练源对照 V1（E0 先 Flat；SOURCE，不冒充运行态）
- 目标：逐科目复用华南虎真实训练配方；本件只读源码并写本报告，未改训练源、网络、奖励、当前 hour，未启动任何训练/测试、SDK、模型读取或远端操作。
- 技能目录只有 Office/ACL，无 RL 匹配；采用 FS read/grep/glob，未装依赖。SCUT 根：`C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL`。
- 版本锚：父会话只读核对 HEAD `b8ff79f3df855faf9dc92f4a282bd80c42649466`、origin https://github.com/scutrobotlab/wheeled-legged_RL.git；本子任务未运行 Git。此处是该本地树的源级事实，不证明历史训练或当前进程字节。
- 结论：旧 MOD4 的“SCUT reward”明确标为 **wheelbipe25_v3 配方+MOD4 适配/附加项**，与此树 **V14Flat-v0** 非同一奖励；源级差异成立，当前 hour 的实际值需父会话按本 purpose 的启动环境/实际源另证，不能由快照默认推出。

## 1. 实际注册 → EnvCfg → PPO → 奖励函数
- [wheelbipe 包入口](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/__init__.py#L1-L12>)只有版权；真正导入由 [agent_tasks:17–18](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/__init__.py#L17-L18>)显式触发 V14。
- E0 基线选 **`Robotics-Wheelbipe-V14-Flat-v0`**：[注册:17–25][reg] → `WheelbipeV14Env` / `WheelbipeV14FlatEnvCfg` / `WheelbipeV14FlatPPORunnerCfg`。不是 `Play`，不是 DreamWaQ/HIM/NP3O，亦不是按文件顺序挑第一个 PPO 类。
- [注册:28–47][reg]另有 Flat-v1/v2，各有自己的 EnvCfg；共用 Flat runner ≠ 任务/奖励相同。[注册:61–80][reg] Rough-v0/v1 配另一 Rough runner。
- [V14 Env:78](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py#L78>) → [V13 Env:35–38](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V13/env.py#L35-L38>) → `Wheelbipe25V3Env._get_rewards(self) -> torch.Tensor` [3474–4067][kernel]；V14 的 [_postprocess_reward_terms:1151–1171](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py#L1151-L1171>)先 super，再按 gimbal 模式抑制/添加项；v0 不启用该 gimbal-spin 配置。
- [V14 EnvCfg:468–590](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L468-L590>)继承 `Wheelbipe25v3FlatEnvCfg`；`events=EventCfgV14()`，`curriculum=None`；[plane 后处理:749–766](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py#L749-L766>)强制绝对高度、关闭状态机/扫描辅助。
- [PPO:259–270][ppo] V14Flat → [208–247][ppo] V13Flat → [26–51][ppo] 25V3Flat：T24 / max_iterations20000 / save500 / empirical_normalization=False；网络 actor/critic `[256,128,64]` ELU，init_noise_std=1.0。
- 真正继承到 V14Flat 的 PPO：value_loss_coef=4.0、clipped value=True、clip=.2、entropy=.005、epochs5、minibatches4、LR=1e-4、schedule=adaptive、γ=.99、λ=.95、desired_KL=.01、max_grad_norm=1.0 [238–247][ppo]。首个 25V3 类的 value_loss=2、512/256/128 不是它。
- 原训练入口 [train:95–96,178–245](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/scripts/rsl_rl/train.py#L178-L245>)：导入 task → Hydra 从 `rsl_rl_cfg_entry_point` 解析 → CLI 覆盖 → `gym.make(task,cfg)` → 对普通 runner 用 `RslRlVecEnvWrapper` → `OnPolicyRunner`；不是 play 流程。
- [train:249–275](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/scripts/rsl_rl/train.py#L249-L275>)：普通 checkpoint 模式仅 policy finetune、iteration 清零；显式 resume_training 才载 optimizer/iteration，之后通知进度、落 env/agent 配置、`learn(..., init_at_random_ep_len=True)`。这是上游源流程，不能替换本次要求的完整 learner 恢复。
- 原训练命令模板（未执行；在原IsaacLab Python环境）：`python scripts/rsl_rl/train.py --task Robotics-Wheelbipe-V14-Flat-v0 --num_envs N_ENV --headless`；只在显式完整续训时加`--checkpoint CHECKPOINT --resume_training`；参数定义见 [train:27–47](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/scripts/rsl_rl/train.py#L27-L47>)。上游max_iterations=20000是迭代数，不是本次N=20000环境数。

### 1.1 观测/动作语义接口：35相同不等于上游完整等价
- 上游普通Flat-v0最终 **actor35 / critic78 / action6**：基础28/32见 [25V3 cfg:183–199](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env_cfg.py#L183-L199>)；[V14 cfg:790–798](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L790-L798>)启用critic extra39并把单帧设71；[930–950,1089–1168](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L1089-L1168>)post_init独立再加ctrl7，28+7=35、71+7=78；v0 frame_stack=False且actor/critic history均1。71是附加前字段，不是最终critic维数。
- actor顺序为`command(vx,vy,wz)[3],height_cmd[1],ω_body[3],g_body[3],q_rel[6],qdot[6],raw_action[6],ctrl[7]`：[cat:3198–3214](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L3198-L3214>)；q/qdot按`_legs_act_idx + _wheel_idx`，轮位置两槽强制0；q raw编码，角速/重力/关节先延迟并加原noise。[ctrl:1744–1828](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L1744-L1828>)为`normal,stair,slope,recover,jump,height_target,state_time`；task_flag默认0维，不额外挤槽。
- critic顺序是相同**基础28**（即时无actor noise/delay）后接`root_lin_vel_b[3],obs_height[1],ctrl[7],priv_extra[39]`：[cat:3262–3296](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L3262-L3296>)；extra按`stiffness6,damping6,torque6,obs_lag4,act_lag2,wheel_body_v6,wheel_contact_state2,body_mass_scale1,material6`拼接并pad/crop39：[4667–4793](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L4667-L4793>)。
- [clip/scale:75–99](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py#L75-L99>)：先clip后scale；height_cmd×5、ω×.5、qdot×.1、obs_height×5，其余默认×1；height_cmd clip[0,1]、qdot±200、obs_height[-10,10]、其余列明块±100；actor/critic两流启用。
- 动作按`legs[4],wheels[2]`：[索引:2042–2045](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L2042-L2045>)由`find_joints`取得，腿匹配rear1/front1、轮匹配wheel，不在源外臆定USD解析后的左右序；[decode/apply:2763–2909](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L2763-L2909>)腿=`q_default+.5*a`并clip±3.14rad；**轮速模式不是wheel_action_scale=1**：[init:2027–2035](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L2027-L2035>)采用`wheel_vel_action_scale=10`，轮=`10*a`目标rad/s，最终限幅`cfg.max_wheel_vel100*1.5=150`；均有1–3步lag，云台独立而不占policy六维。值继承 [25V3 cfg:343–410](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env_cfg.py#L343-L410>)。
- MOD4快照 [obs:1206–1281](<F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/native_physx_probe_v1/source_runtime_snapshot/runtime/isaac/mod4/mod4_task.py#L1206-L1281>)actor同块形状但显式腿序`left_crank,left_hip,right_crank,right_hip`，critic把`base_lin_vel*.5`插在ω后，无原obs_height与39维priv extras，得38；上游critic把线速放基础28后且默认×1。故原A0完整learner沿用属于**明确MOD4接口差异**，不是原观测完全一致；不临时换维、切片或重置norm冒充exact resume。

## 2. E0/V14Flat-v0 原奖励：公式、权重、时间尺度
- 权重/参数唯一表：[V14 EnvCfg:834–914][weights]；计算：[25V3 Env:3474–4067][kernel]。下表“行”按前者/后者；均为 **raw term**，随后统一乘 weight×step_dt，不把 sigma 当标准差后再平方。
- 记 `g=projected_gravity_b`、`c=reward_command`；tracking 的 `c̄x/c̄z` 在命令绝对值<.1时置0；`ev=c̄x-vx_body*cos(pitch)`、`ew=c̄z-wz_body`、`eh=h_ref-h_cmd`、`dx=wheel_L_body.x-wheel_R_body.x`；所有 square penalty 用**未截断**误差。
- [高度函数:529–549](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L529-L549>)取 root world-z（可选高度 clip）；[target:1730–1740](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L1730-L1740>)取 effective height_cmd；v0 为绝对高度、非腿长模式且状态机关。
|term（完整非零集合，合并同类展示）|raw 公式|weight|权重行 / 公式行|
|---|---|---:|---|
|termination|`reset_terminated`（不是 timeout）|-200|870 / 3502|
|leg_joint_acc / leg_joint_vel|Σ腿主动关节 `q̈²` / `q̇²`|-5e-7 / -5e-3|871–872 / 3508,3515|
|joint_torque|Σ全部主动关节 `τ²`|-1e-4|874 / 3528|
|wheel_acc / wheel_vel|Σ轮 `q̈²` / `q̇²`|-1e-8 / -1e-5|875–876 / 3511,3524|
|wheel_power|Σ轮 `max(τ*q̇,0)`|-1e-4|877 / 3544–3546|
|lin_vel_z / ang_vel_xy|`vz_body²` / `wx_body²+wy_body²`|-.5 / -.05|879–880 / 3551–3553|
|action_smoothness_leg / wheel|Σ对应 action 子段 `(a-2a_prev+a_prevprev)²`|-.05 / -.01|881,883 / 3555–3561|
|action_rate|Σ六维 `(a-a_prev)²`|-.01|882 / 3554|
|flat_orientation_y_v / x_v|`[(2*exp(-cx²/3)+2)*gx或gy]²`|-2 / -2|885,890 / 3592–3600|
|flat_orientation_y_exp / x_exp|`exp(-gx²/.02)` / `exp(-gy²/.01)`|+1 / +1|886,891 / 3590–3591|
|track_lin_vel_xy / square|`exp(-clip(ev,±1)²/.5)` / `(.25*ev)²`|+1 / -1|894,896 / 3711–3725|
|track_ang_vel_z / square|`exp(-clip(ew,±.8)²/.25)` / `(.5*ew)²`|+1 / -1|898–899 / 3729–3739|
|stand_still_lin_vel|`(|vx_body|+|vy_body|)*1[|cx|<.1]`|-1|901 / 3573–3582,3748–3751|
|track_height_exp_tight / square|`exp(-clip(eh,±.15)²/.001)` / `(10*eh)²`|+1 / -1|906–907 / 3821–3833|
|no_fork / no_fork_square|`1[|dx|>.05]` / `(5*dx)²`|-1 / -1|909–910 / 3762–3782|
|undesired_contact|历史窗口中任一 undesired body 力模长>3N 的布尔值|-2|913 / 3905–3935|
- `.25` lin square、`.001` height tight、`.05m` no_fork 是继承值：[25V3 cfg:398,473–538](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env_cfg.py#L398-L538>)；没有凭空填参数。
- 表内零项（仍保留其0语义）：leg_joint_pair_pos_diff、wheel_air_spin、static flat_orientation_y/x、track_lin_vel_xy_tight、stand_still、height exp/soft/both_wheels、no_fork_exp/z_exp；v0 表中根本没有 huge_gap、no_fork_z、腿重力对齐 exp，不得擅加。
- [V14 cfg:736–757](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L736-L757>)：upright / orientation-y / height / height-upright gates 均关；standing deadzone 开且阈值.1。公式库支持 gate 不代表 Flat 实际启用。
- [cfg:1085–1087](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L1085-L1087>) dt=1/200、decimation4 → step_dt=.02s / 50Hz；[kernel:3998–4018,4058–4063][kernel] raw→hook→×.02→×weight→sum，**无 only-positive clamp**；非有限项归0，数值异常 reset env 整条奖励归0。普通终止单项是 -4/step，不是未乘dt的-200。

## 3. 原命令课程、重置、终止
- [命令:975–1045](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L975-L1045>)：5–15s重采样；standing=.1，heading=.5、heading stiffness5；普通 vx[-2.7,2.7]m/s，vy=0，yaw±2π rad/s，heading±π；special 只在 min episode length5s 后分配。
- 同处按训练 iteration 开启：dash 从2000、比例.3、vx±[2,3]；spin_low 从3000、.15、yaw±[2π,3.25π]；spin_mid 从4000、.15、yaw±[3.25π,4.5π]；按非standing环境互斥分桶。不是MOD4自己每40轮+0.5的陀螺窗口。
- [高度命令:1046–1083](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L1046-L1083>)两个 special-height 模式 disabled；[cfg:502,563–565](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L502-L565>) default .22m、height_range [.20,.42]。
- **定义≠启用**：[CurriculumCfgV14:365–477](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L365-L477>)虽有 RewardWeightProgression/竖直辅助力进度，普通 Flat 明确 `curriculum=None`；命令 special 的 iteration schedule 则仍生效。
- [reset cfg:586–590](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L586-L590>)启用预定义腿随机起始；[reset细节:198–225](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py#L198-L225>)positive .3 / negative .2、root start .25m、start reset1.5s、zero torque .2s；其余走原重置路径，不等于MOD4碰撞闭环bank。
- [EventCfgV14:35–357](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L35-L357>)有真实质量/COM/摩擦/执行器/外力随机化；旧“暂时禁用”注释不能盖过实例。obs延迟1–4、act延迟1–3在 [504–528](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L504-L528>)，也是训练流程组成。
- [dones:4863–5028](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L4863-L5028>)：20s episode timeout；reset body接触>1N 或 |roll/pitch|>40°，V14Flat需连续20控制步=.4s；NaN/Inf、主动关节速度>500、root角速>200、root线速>100立即终止，obs异常另有配置门控。
- [V14 contact映射:118–145](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py#L118-L145>)undesired含base/腿/云台/guide，reset在plane含base/云台/guide；[V14 dones:568–572](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py#L568-L572>)rough越界加timeout，不记termination罚；play还可关done，故不可用play还原训练。

## 4. 九专家映射：能对应的分支与明确缺项
- 九角色入口的源级清单：[stager:21–36](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/stage_e0_hour_nonpt_runtime_v1.py#L21-L36>)；下表是**能力/任务相近**映射，不宣称九个MOD4专家各自存在上游独立原版。
|MOD4角色|上游现存对应|缺项/限定|
|---|---|---|
|E0|Flat-v0：直接的普通平地基础训练|最先对齐此版本；不是旧25V3原样保留即可称V14|
|E2 directional spin|Flat-v0 spin_low/mid；更接近 Flat-v2 的 gimbal_spin_translate|并非独立 Spin task；MOD4云台/机体方向接口需另对齐|
|E3 recovery|Flat-v0预定义地面姿态随机起始；Flat-v1增加air reset/landing分支|没有注册独立 Standing/Recovery task；MOD4 E3事件峰值恢复reward不是该v0原配方|
|H1_normal|Flat-v1 / Rough-v1 的airborne/落地训练能作部分参考|没有注册独立 Jump task；主动起跳与“高处落下恢复”不同，不能把landing配置冒充H1完整跳跃课|
|W35|Rough-v0/v1的台阶、坡道混合地形|没有直接对应MOD4整张RM70/W35课程及其验收范围的原任务|
|CURB_PROTECTED878|Rough地形里的 stair/台阶族|无该保护878快照/独立curb专家原配方|
|CURB_INDEPENDENT113|同上|无该独立113分支原配方|
|SLOPE135|Rough地形里的 slope族|无该135专家/精确5°任务直接对应|
|SLOPE_INDEPENDENT50|同上|无该独立50分支原配方|
- [完整注册:17–180][reg]只有 Flat-v0/v1/v2、Rough-v0/v1及算法/Play变体，没有独立 Step/Jump/Standing/Spin 注册。旧 [README:29–44](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/README.md#L29-L44>)写的25V3 Jump/Fly名字不是当前实际注册证据。
- Flat-v2 的 [1185–1319](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L1185-L1319>)确有gimbal方向PD、yaw-frame速度/方向reward和原lin项抑制，不能只抽“自旋”字样而沿用v0公式。[E2入口:84–85](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E2_MOD4V1_SOURCE_V1/runtime/isaac/mod4/train_mod4v1_e2.py#L84-L85>)已有自己的directional runtime，但此处未证明与上游等价。
- Rough-v0 [1675–1781](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L1675-L1781>)继承 **Flat-v2**、terrain=`RM_ROTATION_TERRAINS_CFG_99`；helper开状态机后，post_init又关状态机/airborne/forward扫描；spin/dash从0开，wheel_power/joint_torque改-1e-5，仍带v2新增reward。
- Rough-v1 [1785–1807](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L1785-L1807>)继承 **Flat-v1**，保留airborne并开terrain command resample，lin权重1.25；[helper:567–637](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py#L567-L637>)terrain curriculum=True、按terrain过滤命令覆盖；台阶/坡道覆盖表在 [cfg_utils:281–441](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py#L281-L441>)。Rough runner [255–256,323–334][ppo]继承25V3算法(value_loss2.0)，不是Flat的4.0。
- Flat-v1 [1464–1668](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L1464-L1668>)air reset+airborne追加/缩放reward；[1090注释/代码](<C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L1089-L1097>)说明jump_takeoff_state_machine_cfg已移除，观测中jump字段或残留状态机源码不证明主动jump训练启用。

## 5. 已知MOD4源差异与移植边界（绝不热改本hour）
- [快照 rescue:1–49](<F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/native_physx_probe_v1/source_runtime_snapshot/runtime/isaac/mod4/scut_flat_rescue.py#L1-L49>)明确来源25V3；其orientation gain=`2*exp(-cx²)+2`，V14为`2*exp(-cx²/3)+2`，是明确公式差异。水平vx写成`sqrt(1-gx²)` vs `cos(Euler pitch)`在单位重力/标准Euler pitch支上可等价，**不把写法不同本身算reward差异**；真正另有上游tracking死区与误差clip，而rescue的lin/yaw exp直接用原command与未clip误差。
- [快照 defaults:208–236][oldcfg] vs V14：lin σ .25→.5、tight .2→0、huge_gap -1→无；yaw W .5→1、square系数.25→.5；height exp .7→0、tight W .3→1、square系数5→10；termination0→-200；torque -1e-5→-1e-4。以上只比较源码默认。
- [快照 RewardsCfg:1655–1709][oldreward]还含no_fork_z -2、腿重力align +.1/+ .1、全维action_acc、jump豁免等；V14表用no_fork_square、分腿/轮smoothness、joint/wheel acc/vel、姿态exp。接触罚前者chassis>50N，V14是指定多body历史>3N，语义也不同。
- [快照:1723–1753](<F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/native_physx_probe_v1/source_runtime_snapshot/runtime/isaac/mod4/mod4_task.py#L1723-L1753>)条件分支有route_progress/success和自定义jump shaping；[1783–1833](<F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/native_physx_probe_v1/source_runtime_snapshot/runtime/isaac/mod4/mod4_task.py#L1783-L1833>)有closure/mimic终止与自编gyro curriculum；这些都不是上表V14Flat原reward/原命令课。
- [E3 recovery:9–25](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/e3_recovery_runtime_v1.py#L9-L25>)显式mask若干高度项/软终止并新增recovery事件reward；[W35配置:14–47](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_SOURCE_V2_FINAL/runtime/isaac/mod4/config_mod4v1_w35.py#L14-L47>)是MOD4独立RM70场地/命令课，不能反向归为SCUT九专家原版。
- [原E0 entry:131–179](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E0_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/train_mod4v1_e0.py#L131-L179>)构造MOD4 cfg且γ=.9801/λ=.9025、clip_actions6；网络/STD/value/schedule取环境或默认，后续恢复还会带入learner状态。它与上游PPO有源差异，但不推断当前hour具体hyperparam。
- 允许适配：MOD4关节/body索引与正负号、弧度/米/秒/力矩单位、动作6维/观测35/38接口、轮半径/闭环几何与机械限位、同物理定义的高度/接触body映射、控制周期与积分尺度；每项应保持原term语义并明示机械差异，绝不以“接口适配”名义偷换奖励目标。
- 禁止自创：新alive/contact/route/jump/recovery项、改权重/σ/误差clamp、开关原本禁用gate、只保留部分好看的项、把rough/v1/v2混为v0、凭训练曲线临时捏课程。上游缺的科目记缺项，不捏造“SCUT原版”。
- 当前已给定窗口保持 N20000/T24、A0 actor35/critic38/6、256/128/64 ELU；learner/norm/17Adam/已学STD/mutableLR完整保全。**报告并不要求把STD重置为上游1.0，也不把当前learned LR换成源默认。**
- 下一步仅在当前hour完整保存、关闭、回收后按E0单科制定显式V14Flat-v0对齐变更；先核实实际启动环境+actual源，再做后续实现。此件没有runtime合格/九专家训练完成结论。

[reg]: <C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/__init__.py#L17-L180>
[ppo]: <C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/agents/rsl_rl_ppo_cfg.py#L26-L334>
[weights]: <C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py#L834-L914>
[kernel]: <C:/Users/lulu/Desktop/claude/mjcf/reference_repos/scut_wheeled_legged_RL/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py#L3474-L4067>
[oldcfg]: <F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/native_physx_probe_v1/source_runtime_snapshot/runtime/isaac/mod4/mod4_task.py#L208-L236>
[oldreward]: <F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/native_physx_probe_v1/source_runtime_snapshot/runtime/isaac/mod4/mod4_task.py#L1655-L1709>
