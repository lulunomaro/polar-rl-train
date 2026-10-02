# MOD4 过 247.2 mm 狗洞姿态修复任务

请修复 MOD4 的 Isaac Lab 训练模型和任务配置。不要只改奖励函数；当前机器人描述本身把目标姿态排除在可达空间之外。

## 已由本机 MuJoCo + STEP 精确 B-Rep 验证的目标

- SolidWorks 高度基准：主驱动轮下切线到腿最高点 `223.36 mm`。
- 左右对称实际姿态：
  - `hip = +0.4502909721 rad`
  - `crank = -0.6360285683 rad`
  - `input_difference = crank - hip = -1.0863195404 rad`
- 机械限位首次接触：源 CAD 输入差 `-0.6363195404 rad`；当前 MJCF 相对零位下为 `-1.0863195404 rad`。
- 该点被动关节目标：
  - `rocker_pin = -0.7828279185 rad`
  - `coupler_pin = +0.9027785273 rad`
  - `knee = -0.7613787030 rad`
  - `distal_pin = +0.8152830435 rad`
  - `gas_pin = +0.1559996367 rad`
  - `gas_slide = -0.0267546844 m`

## 当前模型错误

1. `input_difference` 下限是 `-0.7 rad`，它只是旧的保守工作区，不是真实机械硬限位，目标姿态因此不可达。
2. knee、rocker、coupler、distal、gas pin/slide 的范围也停在旧工作区边界，必须按上述 B-Rep 接触点同步扩展。
3. CAD 中有 8 个直径 30 mm 的底盘导轮，但训练碰撞模型没有它们。中央 4 个导轮中心为车架坐标 `x=±0.048 m, y=±0.1005 m, z=-0.163 m`；前后 4 个为 `x=±0.259 m, y=±0.131 m, z=-0.135 m`。用低摩擦解析圆柱碰撞体实现，避免三角网格 collider。
4. 在目标姿态的刚性平面上，中央导轮先接地，主驱动轮下缘约离地 `1.80 mm`。这是 CAD 包络关系，不要强行让两者精确共地；可用合理接触柔度和尺寸随机化覆盖轮胎变形。

## 必须同步修改

- MJCF 参数、关节范围、reset/command clamp、观测归一化和自检。
- Isaac Lab 使用的开链等效 USD/URDF 及 `robot_cfg.py` 限位；不能指望 MJCF 闭链 equality 被 PhysX 自动保留。
- 中央和前后导轮的解析碰撞体与 collision filter。
- 狗洞 curriculum：先姿态跟踪，再低速进入，再完整穿越；奖励至少包含姿态、净空、前向进度、碰撞白名单、动作平滑和电机热/力矩约束。
- 域随机化覆盖整机质心、载荷、接触摩擦、轮胎/导轮半径、洞高和传感延迟。名义全模型离实际地面最高约 `244.934 mm`，对 `247.2 mm` 洞只剩 `2.266 mm`，训练成功不能替代实车尺寸复核。

## 验收标准

- 重置到目标姿态后不夹紧、不开裂、不出现 NaN/solver warning。
- 3 s 保持测试中，左右 `input_difference` 到达 `-1.0863±0.002 rad`，车身俯仰绝对值 `<0.01 rad`。
- MuJoCo 闭链最大残差 `<5e-4 m`；Isaac 侧开链 DOF/关节语义由导入后自检确认。
- 中央导轮产生地面接触，前后导轮在水平目标姿态不误接触；主轮间隙与 CAD 的约 `1.8 mm` 一致。
- 247.2 mm 狗洞中无顶碰，且在随机化最差样本下报告通过率和最小净空，不能只报告平均 reward。

本地基准报告：`hard_stop_brep.json`、`grounded_hard_stop_pose.json`、`dynamic_hard_stop_report.json`。对照图：`solidworks_vs_mujoco_hard_stop.png`。
