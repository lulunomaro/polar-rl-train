# MOD4v4gemini 轮腿底盘模型（对齐华南虎大 Yaw + 达妙 DM-J4310 + 云台↔腿精确凸包碰撞修正版）

> **[MOD4v4gemini 更新说明]** 本包已完成：① 对齐华南虎 `WheelBipe V14_2` 大 Yaw 零位规范（`gimbal_yaw_joint = 0` 朝车头 `+X`，收纳安全角更新为 `−149.6905°`）；② 修复 `gimbal_fold_link` 虚大 64–95 倍惯量与质心；③ 写入三轴达妙 **DM-J4310-2EC (24V)** 电机实参（`3 N·m` 额定 / `7 N·m` 峰值 / `0.0018 kg·m²` 转子惯量，STEP 核验大 Yaw `51:51 = 1:1` 同步带）；④ 生成 55 个精确 CAD 凸包并在 MJCF 与 USD 中开启云台↔腿物理碰撞；⑤ 提供 `tools/scut_gimbal_adapter.py` 华南虎小陀螺航向锁与安全折叠接口。完整变更与实测对比请查阅 **`README_MOD4v4gemini.md`** 与 `reports/gemini_fix_validation.json`（下方保留原包背景说明供对照）。

MOD4v4 以修正镜像腿的《短杆串腿底盘》独立装配为几何来源。离线导出的整车 STEP 回读了 **465 个零件实例、344 个零件定义**，左右腿各 95 个实例。USD 和 MJCF 的显示网格都从这份 STEP 生成。底盘训练接口沿用 MOD4v3 R3，并与本地华南虎 WheelBipe V14_2 的关节和观测定义对照。

| 用途 | 文件 |
| --- | --- |
| CAD 总装 | `cad/MOD4v4.step`，在仿真 ZIP 外单独交付 |
| MuJoCo 交互查看 | 双击 `打开关节查看器.cmd`，在「轮腿」页可直接拖动左右整腿。「上装 → 收纳姿态 · 导轮贴地」加载整车收纳预设，按 `R` 回到双主轮接地的模型默认姿态 |
| Isaac Sim / Isaac Lab（PhysX） | `assets/MOD4v4_physx.usd`，可以单独复制 |
| MuJoCo | `mjcf/scene.xml`，连同 `mjcf/assets/` 复制 |
| 通用 OpenUSD | `assets/robot.usd` |
| 编辑 PhysX 兼容层 | `assets/robot_physx.usda` 和同目录 `robot.usd` |

## MOD4v3 训练接口

动作顺序为 **左前髋、右前髋、左后髋、右后髋、左轮、右轮**，与 v3 R3 包的 `policy_action_order` 和两版 MJCF 执行器顺序一致。髋轴在模型默认姿态的绝对角均为前 `+0.7783382074 rad`、后 `−0.4806332577 rad`。四个主动髋轴可以连续转动。v3 R3 每侧五个被动转轴的一侧限位对应同一个连杆止挡，另一端由气弹簧 200 mm 伸长限位确定。同侧前髋减后髋的可达区间约为 9.8922° 至 100.3188°。如使用训练顺序为「左前、左后、右前、右后、左轮、右轮」的 R1 检查点，将其输出按 `[0, 2, 1, 3, 4, 5]` 排列后再送入本接口。「左整腿转角」和「右整腿转角」拖动同侧两根髋轴一起转，保持前后髋角差。单独拖前髋或后髋会改变连杆开合。

`semantics.ScutRobotView` 对策略提供原来的 30 个关节坐标和 31 个底盘刚体。关节方向、单位、初值、`front3` 的派生公式、动作变换和奖励坐标均继承自 v3。MuJoCo 中原有的关节、刚体、传感器和执行器继续沿用原索引。Isaac 通过名称解析刚体和关节，另从接触传感器自己的名称表中查索引。

八个导轮沿用 v3 的名称和接触分组。左右的 `bottom2`、`bottom3` 在 v4 分别装在侧面靠前、靠后的位置，实际转轴为竖直方向。另四个前后支撑导轮为水平轴。

## 上装三轴与收纳

| 物理关节 | 父部件 | 随动部件 |
| --- | --- | --- |
| `gimbal_yaw_joint` | `base_link` | `gimbal_yaw_link`，连同折叠和 pitch 部件 |
| `gimbal_fold_joint` | `gimbal_yaw_link` | `gimbal_fold_link`，连同 pitch 部件 |
| `gimbal_pitch_joint` | `gimbal_fold_link` | `gimbal_pitch_link` |

USD 和 MJCF 的大 Yaw、折叠和 Pitch 均以 SolidWorks 保存姿态为零角。UWB 平行四杆的连杆和托架各有一个从动关节，两者由折叠轴带动。读取仿真器原生关节表时可看到这两个从动坐标，底盘策略仍使用 v3 R3 的训练接口。

大 Yaw 内圈座、Yaw 底板、圆盘盖、下铰座和两颗六面垫柱一同随 Yaw 转动。折叠支架带动 Pitch 总成，四面铝排随各自的直驱连接件转动。`reports/step_membership.json` 记录每个实例所属刚体及对应 CAD 配合。三根主轴线来自 STEP 中的同轴圆柱面，UWB 四杆的销孔来自保存的轴承位置。

| 上装关节 | 仿真轴行程（相对 CAD 保存姿态） |
| --- | --- |
| 大 Yaw | 连续转动 |
| 折叠 | −32° 到 +54.5° |
| Pitch | −54° 到 +55° |

折叠和 Pitch 有三条组合约束，单轴行程内的可拖范围会随另一轴位置变化。当前收纳预设取 Yaw 0°、折叠 +54.5°、Pitch −53.75°，四个支撑导轮和后方双主轮同时接地，两侧气弹簧均为 200 mm。MJCF 可加载 `guide_ground_stow` 关键帧，USD 的同一组静态姿态参数记录在 `assets/import_contract.json` 的 `upper_mechanical_limits`。

四个支撑导轮和后方双主轮贴地时，按两侧气弹簧全伸 200 mm 测得小腿 MOD3 最高约 **305.7 mm**。新版预设的上装最高约 **254.9 mm**，比旧预设低约 0.6 mm。镜头护板距 Yaw 圆盖约 1.15 mm，UWB 连杆距 Pitch 支撑板约 0.20 mm。STEP 扫角到接触前，上装还能降到约 254.0 mm。继续下压 Pitch 时镜头护板先碰 Yaw 圆盖，折叠超过约 +54.85° 时 UWB 连杆碰 Pitch 支撑板。收纳时部分 Yaw 角会让上装碰到大腿。`reports/stow_geometry.json` 记录接地点和 STEP 实体间隙，`reports/stow_pose.png` 标出整车高度和 250 mm 目标线。这些角度和高度用于静态仿真检查。

整车质量为 22.2112 kg。可回读实体的质量和惯量按 STEP 体积及保存材料在刚体之间重新分配，缺少材料数据的实体采用名义密度。只有曲面可回读的两个随动件进入显示组，独立惯量仍留在 CAD 分组估计中。两根铝排按原文件的 6061 密度计入 Pitch 组。上装对外接触使用简化椭球，显示网格来自 STEP。

## 缺项与验证

活动配置没有可回读实体的有 9 个实例，包含两个 C620 实例、Z 向链路、NUC 支架和一个缓存质量为零的 yaw 总装。原拨爪的离线曲面重建外伸，STEP 和仿真均暂缺该实例。另有 3 个导入定义带缺面记录。名称与原因见 `reports/step_roundtrip.json`，原装配预览和 STEP 重建对照见 `reports/assembly_compare.png`。

`reports/v3_compatibility.json` 记录训练接口的回归。`reports/validation.json` 和 `reports/continuous_joints.json` 记录腿部、触地、多圈及气弹簧行程。`reports/viewer_verify.json` 记录启动、收纳、复位的接地状态和整腿多圈检查。`reports/physx_usd_import.json` 记录 Isaac Sim CPU PhysX 的导入和三轴运动。旧策略在 v4 上的闭环起立尚未实测。
