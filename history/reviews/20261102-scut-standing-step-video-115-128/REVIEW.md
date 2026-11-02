# 华南虎站姿上台阶：视频1:55–2:08与官方训练记录核对

这是分支内的只读视频/公开源码研究，没有启动训练、修改主线源/奖励/预算或操作主线controller。检查的官方main为1a26356d6f591734d4f6f666f5cead1a6925da67（2026-10-08），本次API再次确认。

## 结论

有相关训练和公开预训练模型。最直接的证据是官方pretrained/26_infantry/readme.md第29–35行：作者把rough_rotation_stair/2026-07-23_16-23-21明确描述为“调小陀螺调出一个上台阶很牛逼的”，并指明2026-07-30_09-16-27是它的轻量化版本。这比仅从stair.py/step_up.py名称推断更直接。

但没有找到这个本地视频与该具体checkpoint的一一对应声明；不能断言视频就用了该模型，也不能断言它已验证270mm站姿攀爬。

## 本地视频观察

用户视频40727022201-1-192.mp4，总时长161.366625s，1280x720。逐段抽取115–128s，2fps概览，115.05–116.55s及124.25–126.25s约0.1s间隔密集帧，并观察8张原分辨率局部放大图。全部由当前模型原生视觉查看。

- 约1:55–1:57：从低层靠近台沿，轮腿伸缩和机身抬升后到低平台，再过下一层；随后在平台行驶、转向、下台。
- 约2:03–2:06：另一视角/场景，低速接近台沿、轮腿伸展、身体抬高并把轮子带到上层，之后恢复行驶。
- 这与用户所说站姿/攀爬式上阶相符，动作呈台沿附近的轮腿协调。不能由这些二维帧保证双轮全程持续接触：台沿遮挡接触，部分帧存在快速抬轮，视频不是接触力测量。视频也没有可用标尺证明台高270mm。

## 已公开训练实例：2026-07-23_16-23-21

原始README、env.yaml、agent.yaml已经逐字节保存于primary/，Git blob与GitHub API响应核对。权重未下载或读取。

- 文件目录：pretrained/26_infantry/rough_rotation_stair/2026-07-23_16-23-21。
- 有model_1000.pt（1367221B，Git blob a52bbf91101302a1427273af553f941fb425ba8b）、model_500.pt、model_0.pt、TensorBoard事件，以及exported/2026-07-23_16-23-21_1k.onnx（204282B，Git blob f4ee54c21b9cb901982e1e3f9ffaaf26707a76aa）、policy.pt（215122B，Git blob 565edab1aa30d52a6b58e515ab7ad421313af248）。这些是目录元数据，不是本地模型/新物理验证。
- agent.yaml：OnPolicyRunner/ActorCritic/PPO；actor/critic 256,128,64；24步rollout；5epochs/4minibatches；gamma .99/lambda .95；lr .0001/adaptive/desiredKL .01。
- 来源明确指向平地2026-07-19_09-14-50/model_8000.pt（agent.yaml第51–55行），与README训练链相符。
- env.yaml：35维actor观察、78维state、6动作；enable_state_machines=false（845行）；wheel_forward_scan_cfg.enabled=false（916–917）；jump_takeoff_state_machine_cfg.enabled=false（2338–2339）；stair_state_machine_cfg.enabled=false（2431–2432）。因此不能把这份模型的爬阶能力归因于后来代码里的step_up或stair状态机。
- 这份保存配置是粗糙地形/小陀螺训练：高度命令.2–.42，速度/偏航/高度/姿态追踪和碰撞终止等奖励；地形curriculum启用。主terrain.sub_terrains包括条障、坡、微小阶梯和反阶梯、平地、随机起伏；其中阶梯每级.005–.015m或.025–.04m、宽.1m。不能把这些微阶梯配置冒称270mm单级站爬专项训练。

## 当前main的可训练任务与辅助

已注册Robotics-Wheelbipe-V14-Rough-v1，使用WheelbipeV14RoughEnvCfg_v1与WheelbipeV14RoughPPORunnerCfg。env_cfg.py1785–1796调用_apply_v14_rough_runtime_cfg；cfg_utils.py570–576打开状态机和wheel_forward_scan。manager.py60–61实例化StepUpStateMachine。

step_up.py28–97实现：轮前raycast高度的时间差分识别台阶，短时抬高height command；改后的height command进入policy/critic观察和高度奖励（wheelbipe25_v3/env.py1251–1260）。它不直接给定完整电机爬阶轨迹。

当前V14实际覆盖值为step_min .12、step_max .14、wall .14m，height_bias .16m、hold2s、max .40m（env_cfg.py721–735）。不能拿step_up.py的兜底默认.15–.25冒充当前实际值。如果前向扫描的单拍高度差超过.14m，进入wall timeout；所以不能把它原封不动称为270mm站爬方案。另一方面，当前Rough-v1地形列表确有low/high_speed_stair，声明每级.15–.35/.15–.40m；地形生成范围不代表策略已通过这些高度，也不保证该辅助会允许所有跃变。

stair.py与jump_takeoff.py是另外的可配置状态机，manager.py57–64按enabled才实例化；文件存在不能代替启用证据。

## 证据界限与下一步判断

回答“有没有对应训练”：有相关粗糙地形PPO训练、公开模型和作者明确爬阶评价，且当前main有轮前扫描抬高身体的辅助链。回答“是否有与这段视频一一对应、专门训练270mm无腾空站爬的完整配方”：尚未找到证据。

本分支结论只建议把站姿攀爬作为独立技能定义来研究，观察轮腿协调/台沿支持，不能继续把它与首次飞行整轮跨270mm的验收混同。没有在本分支执行训练/部署或改写现有跳台任务。

## 取数失败保留

本轮一度GitHub recursive tree读取超时；数个raw.githubusercontent.com源码请求TLS握手超时，manager.py及terrains.py成功且与已有245冻结字节相等。随后GitHub contents API取得上述README/两份YAML和exported元数据；也用245保存tree的Git blob核对关键本地source，均匹配。另一次重取env.yaml/轻量版env.yaml超时；重取原版env.yaml成功，轻量版env.yaml本轮未取得，未推断其配置。所有这些失败仅公开HTTP读取失败，不是训练/技能失败。
