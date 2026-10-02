# MOD4 氮气弹簧位置—力曲线审计（隔离候选）

## 事实与坐标

- MOD4 每侧弹簧跨接大腿侧 A 孔与小腿侧 B 孔；`gas_slide` 正方向使孔距增加。
- MuJoCo `q=0` 时 A—B 距离 `L0=0.1793606227642732 m`。因此 `L=L0+q`。
- 4090 当前训练的 USD 允许 `q∈[-0.0267046843609,+0.0352033350025] m`，即孔距约 152.656–214.564 mm。
- 原选型文件中的 150–200 mm、全伸长 700 N、压缩比 1.25 均标记为**未验证候选**，不能当作实测硬件。

## 现行训练的真实模型

训练通过 `gas_spring_preload()` 在每个控制步令隐式滑动关节驱动的目标位置为 `F_ref/k`。当前 `F_ref=500 N`、`k=3500 N/m`，因此弹性轴向力（不含阻尼、约束反力）是

```
F(q) = k * (F_ref/k - q) = 500 - 3500 q  [N]
```

并非全行程恒定 500 N。按 USD 行程边界算，约为 376.79–593.47 N。`q=0` 的 500 N 是**模型参考力**，不是厂商标称力。若仅暂按未验证的 200 mm 全伸长长度计算，`q=0` 是压缩 20.64 mm；这条训练曲线隐含全伸长预充力约 427.76 N。

## 华南虎 V14 的形式

其 `env_cfg.py` 设定线性模式、`spring_offset=0.06076 m`、`linear_down=400 N`、`linear_up=600 N`、`linear_length=0.07 m`，并随机化 ±50 N。`_apply_spring()` 逐步读取弹簧滑动关节 `spring_pos`，算

```
F = 400 + (600-400)/0.07 * max(0, 0.06076-spring_pos) + random_offset
```

随后给滑动关节施加 effort target。其 `spring_pos=0` 在无随机偏移时是约 573.6 N。这个偏移属于**华南虎自身装配坐标**，不能直接复制到 MOD4。

参考：

- https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py
- https://github.com/scutrobotlab/wheeled-legged_RL/blob/b8ff79f3df855faf9dc92f4a282bd80c42649466/source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py

## 可比较的 MOD4 曲线候选

保持 `F(q=0)=500 N`，仅把斜率改为华南虎的 `200/0.07=2857.14 N/m`，USD 行程边界弹力为约 **399.42–576.30 N**。与当前 376.79–593.47 N 差别较小，不能凭这一步宣称解决前倾。是否改变预载，要看同一检查点、同一 seed 的确定性受力 A/B，随后还需要重新训练和同协议验收。

隔离阶段的**待验候选**为 `F(q=0)=400 N`、`k=2857.14 N/m`，在 USD 行程边界约 **299.42–476.30 N**。这不是华南虎整车弹簧的照抄；只借用了其线性压缩模型与 200 N / 70 mm 斜率。若同检查点测试表明车身虽更平但高度、轮接地或存活明显恶化，则不得切换正式训练。新阶段的 `launch.py` 只在显式启动它时使用这条曲线，原训练目录完全保留。

在获得实物弹簧力—孔距曲线或至少额定力所对应的孔距前，此候选只供隔离仿真使用，不作实车选型结论。
