# E3：视频目标与Fudan参考训练方法对齐 V1

2026-11-04。此阶段完成参考动作分析、上游方法定位与静态模型差异检查，**尚未启动新原生训练**。旧20步PPO任务已结束；坏候选a3ce不晋升，保留1cd/iter43090，H1和其余专家冻结。

## 1. 用户给的视频明确了什么

- 输入：[9.866625秒视频](<C:/Users/lulu/Downloads/43171186822-1-192.mp4>)，1280×720；实际FFmpeg选取原视频每15帧，获得20个原分辨率关键帧，时间0.0、0.5……9.5秒。
- [时间序列图](<video_reference/TEMPORAL_CONTACT_SHEET.png>)；[解码时间索引](<video_reference/REFERENCE.json>)。
- 0–0.5秒：机身很低并接触地面，两条轮腿位于机身同一端，两轮也在地面；不是轮子悬空的抬腿姿态。
- 约0.5–1.5秒及5.5–7.5秒：明显的大幅摆腿伴随机身翻转，借地面支撑做动态自救，不是只在小角度站姿里伸腿抬高。
- 接触力、精确关节角/机械行程、机器人身份、控制代码和训练算法均非视频可直接测出的量。不同镜头的多次动作不拼成一个成功率；片中也有抬高再回落，瞬间直立不等于稳定起身合格。
- 本次E3目标定义为：**贴地且双轮接触的目标初态 → 摆腿/支撑翻身 → 落轮并稳定**。落轮稳定仍需仿真/实物按明确判据测量。
- 之前[扩髋演示说明](<../mod4v1_e3_belly_ground_rear_20261104/DEMO_NOTES.md>)中hip=-2.063rad、rootz=.1671m的两轮在空中，仍不是视频初态，不直接拿它当新训练reset。

## 2. 项目实际引用的Fudan来源

明确上游：[yly-true/fudan_rl_wheel_leg，固定8204e853dfd2ed06d85a322e1a998c3d20a3be2c](https://github.com/yly-true/fudan_rl_wheel_leg/tree/8204e853dfd2ed06d85a322e1a998c3d20a3be2c)。其README列plane/jump，继承Wheel-Legged-Gym并致谢复旦星云ega；本阶段不将其叫作已验证的校方官方getup实现，也不与SCUT或SuperMimic混为一谈。

一次聚焦只读委派核对了既有env/config snapshot；其中缺失的rsl模块从上述固定commit公开源在内存读取，未运行/训练。关键源：

- [网络](https://github.com/yly-true/fudan_rl_wheel_leg/blob/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/jump/wheel_legged_gym/rsl_rl/modules/actor_critic_sequence.py#L39-L207)
- [PPO与encoder更新](https://github.com/yly-true/fudan_rl_wheel_leg/blob/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/jump/wheel_legged_gym/rsl_rl/algorithms/ppo.py#L47-L283)
- [存储与GAE](https://github.com/yly-true/fudan_rl_wheel_leg/blob/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/jump/wheel_legged_gym/rsl_rl/storage/rollout_storage.py#L105-L263)
- [Runner与保存](https://github.com/yly-true/fudan_rl_wheel_leg/blob/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/jump/wheel_legged_gym/rsl_rl/runners/on_policy_runner.py#L50-L297)
- [环境](https://github.com/yly-true/fudan_rl_wheel_leg/blob/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/jump/wheel_legged_gym/envs/base/legged_robot.py#L256-L452)
- [配置](https://github.com/yly-true/fudan_rl_wheel_leg/blob/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/jump/wheel_legged_gym/envs/base/legged_robot_config.py#L276-L315)

### 核准的方法

PPO + 五帧历史线速度估计，不是SM/BPTT，也不是RNN：原25维obs×5仅作为encoder输入125→128→64→3；z监督scaled机体系真线速度(×3)。actor输入当前obs25与stop-gradient(z3)，实际28→128→64→32→6；critic输入priv141与rollout时存下的z3。六个高斯STD可学习，初值.5。

4096env、48步；PPO 5epoch×4minibatch，γ=.99、λ=.95、clip=.2、entropy=.01；主Adam LR1e-3，KL目标.005、自适应÷/×1.5且限1e-5…1e-2。独立encoder Adam LR1e-3，在PPO之后同批次数MSE监督；不是PPO梯度穿过encoder。PPO clip-norm1、encoder .1。固定obs尺度与噪声，无已读EmpiricalNormalization调用；advantage按整rollout标准化。

原timeout处理为reward加γV_t并由done切GAE；并非用terminal_obs计算V。原Runner漏存encoder Adam；两阶段clip都传整个actor_critic且只各自optimizer.zero_grad，有跨阶段残留梯度作用。若适配时补齐完整保存与分组裁剪，应明确为本地修正，不声称原样复现。

### 不照抄的内容

已查jump与plane相关snapshot的reset是默认直立关节/姿态，随机6D速度±.5；没有找到这次贴地后腿课程。jump的高度/腾空/收腿奖励、gx²+gy²姿态项与倒地1秒重置不是getup任务方案。它们不直接覆盖本次E3目标。

本车当前35维观测/critic38及母版网络与上述结构不同：引入history/encoder后应建立明确的新适配版本；知识迁移/暖启动与完整旧Adam续训分开，不切权重或计数假装resume。

## 3. 当前E3初态确实未覆盖这个目标

父实际读取了[固定初态选择](<../mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/e3_reset_bank_cache_v1.py#L34-L72>)：同一个root_height最接近.25的腿关节形状，仅给机身roll/pitch±30/60/90度，12种加正常1种，不是整腿后置贴地初态课程。

[恢复期处理](<../mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/e3_recovery_runtime_v1.py#L9-L25>)已有恢复期height/linvz奖励屏蔽及bad_orientation/base_contact暂缓；[现有成功事件](<../mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/e3_public_recovery_phase_v1.py#L5-L13>)使用带符号直立进度，gz<-.984807753、速度<.03、角速度<.2，stable计数每50Hz控制+2、达到50即连续.5秒，而非50个控制步。

## 4. 模型一致性先补齐，勿用错模型解释训练

[实际静态差异结果](<LOCAL_NATIVE_MODEL_CORRESPONDENCE.json>)比较了旧MuJoCo演示与当前2c/bae原生资产契约，未加载checkpoint、未启动SDK/GPU或物理episode：

- 旧场景总质量14.2001407kg，原生契约14.2941403kg。按同名核对23个body，chassis及左右shin的M/COM/I不同；其它body名字尚未对齐，不据此推断零件缺失。
- 被动膝/rocker及气弹簧等范围也不同。旧气弹簧slide范围[-.02165194,.01672693]m，原生[-.02670468,.02063944]m。
- 报告内局部joint raw range=[0,0]未同时读jnt_limited，**不得解释成锁死在0**；需补限位使能再解释这些项。
- 四个旧目录顶层XML均不匹配原生source_mjcf SHA fbb0393883d31ac96f8cd58a184585470222f7daf96af6aa5d0748a1752c366c。下一步定位同源MJCF/配置并统一显示模型，尚无完整几何/关节frame/backend等价结论。
- [当前原生髋范围](<../mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json#L949-L980>)是±.5rad，曲柄[-1.2,.9]；这是现配置，不是新测得的实物硬限位。不会从异车视频直接抄范围或任意扩气弹簧行程。

## 5. 当前进度与下一步

已完成方法定位、视频分析及上述静态差异检查；唯一源码委派已结束。没有新原生训练、梯度、模型保存或成功率可报告。

下一步：核实同源模型及本车真实可达贴地双轮接触姿态 → 最小Fudan history/速度encoder/PPO适配与目标reset课程 → 原计账/资源准入下有限E3学习 → 指定起身与原E3保留独立测试。保留母版和全部失败，不把新增更新数当成功。

本阶段与此前两次演示资料的Git合并归档待做；模型、视频/图片/轨迹只作引用，不为Git重开。
