import io
p = r"D:/claude2/fangzhen/docs/SJTU_LEG_COMPARE.md"
t = io.open(p, encoding="utf-8").read()
t = t.replace("""* `check_mjcf.py`：总质量 **20.000 kg**，惯量全部满足 A+B≥C，6s 自由落体正常着地
* `sim_baseline.py`（无学习 PD）：16 s 站立→起立→行驶，max\\|pitch\\| 4.3°、roll 0°
* mjlab 冒烟：256 env × 3 iter 正常，reward 0.20→0.25 起步
* v2 重训：`rm_flat_v2`，2048 env × 3000 iter（进行中）""",
"""### 6.1 重训与复验（rm_flat_v2，2048 env × 3000 iter，1.8 s/iter）

* `check_mjcf.py`：总质量 **20.000 kg**，惯量全部满足 A+B≥C，6 s 自由落体正常着地
* `sim_baseline.py`（无学习 PD）：18 s 站立→起立→行驶，max|pitch| 4.3°、roll 0°
* 训练收敛：mean reward **123.46**，mean episode length **1000/1000**（20 s 满程不摔）
* `onnx_play.py`（部署端控制律 + 修正后 plant）：24 s BALANCED，双轮持续接触
* 工作空间解析校验：可达 hip→轮 = **[0.040, 0.460] m**，覆盖训练 0.18–0.34 与部署 0.20–0.40；
  最深蹲位（h=0.18）膝离地 **0.215 m** ⇒ 文档「大腿要比小腿短，下蹲时膝不能触地」成立 ✓

### 6.2 sim2real 就绪度矩阵（`train/eval_robust.py`，256 env × 500 步）

| 条件 | 存活率 | err_vx | err_wz | err_height | \\|pitch\\| |
| --- | --- | --- | --- | --- | --- |
| 标称 | 99.8% | 0.093 | 0.062 | 4 mm | 1.69° |
| 3× 传感器噪声 | 99.8% | 0.305 | 0.257 | 10 mm | 4.15° |
| 执行器延迟 2 物理步 | 99.8% | 0.095 | 0.060 | 4 mm | 1.71° |
| 轮地摩擦 ×0.45–0.75 | 99.8% | 0.094 | 0.062 | 4 mm | 1.67° |
| 加载 +5~8 kg 且质心前移 | 99.8% | 0.099 | 0.075 | 11 mm | 4.20° |
| 每 3–6 s 冲击扰动 | 99.8% | 0.108 | 0.066 | 4 mm | 1.73° |
| 指令打满 ±1.8 m/s / ±1.0 rad/s | 99.8% | 0.104 | 0.065 | 4 mm | 1.83° |

### 6.3 两条链路用 v2 模型复跑

* **sim2sim**（`prefix:=rm_vehicle`，MuJoCo 后端）：`INIT→IDLE→RL`，日志 `[ERROR]` 计数 **0**
* **sim2real**（单串口后端 + pty + 仿真 H7，DT7 输入）：`Serial port connected` →
  `DT7 requested controller state 3` → `INIT→RL`；DT7 要 +1.0 m/s 时轮速 **13.3/13.3 rad/s
  = 0.97 m/s**（前进 6.5 m），要 −0.5 时 **−6.5/−6.1 rad/s = −0.46 m/s**（回退 4.8 m），
  全程 |pitch| < 0.8°、高度 0.26 m 对应 z=0.1216 m；30 s 内 **rx 14758 / tx 29645 / CRC 错 0**""")
io.open(p, "w", encoding="utf-8", newline="\n").write(t)
print("compare doc finalized")
