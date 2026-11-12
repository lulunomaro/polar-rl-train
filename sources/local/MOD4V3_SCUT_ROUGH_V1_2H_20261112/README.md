# 华南虎 Rough-v1：统一跑场两小时

用户2026-11-12授权本轮；随后明确希望沿用已有Rough-v0成果，本轮从其100m完整检查点接续，不回退到R1。R1基线与既有实车包保留作比较。

- 父：Rough-v0 `model_100m.pt`，iteration23665，SHA `001028396205e7d44d69ac5af36cdbb638cc26b97daeea29439f84952a58f6e9`。
- 单一7200秒PPO窗，4096环境，每300秒完整PT保存、下载校验与回放。完整恢复actor/critic/STD/Adam/RNG；新地形新物理episode。
- 参考 `reference/rough_dash_env.yaml` 全部11类地形、10级，从启动统一混训。原13列扩75列以分散4096克隆；20%平地与20%名义参数独立交叉，Rough各族相对比例保留。
- 完整DR、35actor/78critic/6action、2.5ms物理/10msPD/20ms策略、TGS32/4、2mm单env保护、电机包络、−1.5e²及指数速度权重1.2保留。指令上限2.2m/s。
- 宽台阶15–35/40cm，格栅2–6cm，较陡坡比.15–.35、反缓坡、正反浅阶、随机起伏与短落差地形共同训练。
- 内部airborne奖励开启；按参考允许地形40%airreset，使用MOD4可行姿态bank和局部地面高度，避免把不同机器人腿长直接复制。7个actor控制模式槽保持原normal语义。主动跳跃关闭。
- LR3e-5 fixed、clip.1、3epochs、rollout24、seed66。没有额外分课或前置毕业门槛。

启动、探针和每五分钟实际记录见evidence/；完整配方见EFFECTIVE_RECIPE.json。正式轮末比较速度、地形穿越、旋转保持与落地；不只看训练奖励或单一引擎回放。

## 当前状态

4096环境短启动已完成：一更新9.434秒、numerical0、无容量漏接触警告；单env闭链reset476，未改阈值。该短探针不计入两小时主训练、不作为其父。训练盘重启后恢复记录见evidence/STORAGE_RESTORE.json。
