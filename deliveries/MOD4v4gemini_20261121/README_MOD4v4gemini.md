# MOD4v4gemini：对齐华南虎大 Yaw 架构 + 达妙 DM-J4310 实参 + 云台↔腿精确凸包碰撞版

本包基于 `MOD4v4_USD_MJCF_20261119_云台折叠复核.zip` 深度修复并对齐华南虎（SCUT `WheelBipe V14_2`）大 Yaw 训练与控制架构。底盘 v3 R3 训练接口（`policy_action_order` 6 执行器、19 原生传感器、`semantics.ScutRobotView`、整车总质量 `22.211176 kg`）100% 保持不变；全部实测指标记录于 `reports/gemini_fix_validation.json`。

---

## 一、核心修复与华南虎架构对齐一览

| # | 原包问题 / 需求 | 本包修正方案 | 涉及文件 |
| --- | --- | --- | --- |
| 1 | **大 Yaw 零位未对齐华南虎规范**：原 STEP 在收纳避让口袋姿态（偏离车头 `−149.6905°`）保存，`gimbal_yaw_joint = 0` 时枪管/镜头指向右后方，直接接入华南虎 `WheelBipe V14_2` 的 `body_quat_w[gimbal_yaw_link]` 世界航向锁或 `cos(q_yaw)/sin(q_yaw)` 小陀螺平移坐标变换会反向错位 `149.7°` | **全面对齐华南虎 `WheelBipe V14_2` 零位约定**：将 `gimbal_yaw_link` 内部几何、质心/惯量及折叠/UWB 子连杆安装角绕 `+Z` 旋转 `+2.6125924 rad (+149.6905°)`，使 **`gimbal_yaw_joint = 0` 时镜头/枪管严格朝向车头 `+X = (1, 0, 0)`**，`gimbal_yaw_link` 姿态四元数与底盘同向（`0.0000°` 误差）；同时将 `guide_ground_stow` 收纳关键帧的 Yaw 更新为安全口袋角 `−2.6125924 rad (−149.6905°)`，收纳世界坐标与原包误差 `1.39×10⁻¹⁶ m` | `mjcf/scene.xml`、`mjcf/scene_gimbal_actuated.xml`、`assets/robot.usd`、`assets/MOD4v4_physx.usd`、`cad/upper_limits.json` |
| 2 | **`gimbal_fold_link` 惯量虚大 64–95 倍**：质心落在零件包围盒外 `17.9 mm`，主惯量 `0.2529 / 0.2500 / 0.00395 kg·m²`，小陀螺自转产生巨大假陀螺力矩 | 对 `gimbal_fold_link` 三个 STEP 实体网格做精确有符号四面体体积分并按原质量 `0.78043 kg` 缩放：质心 `(0.04459, −0.04304, 0.07660) m`，主惯量 `0.001259 / 0.003797 / 0.004739 kg·m²`，回转半径 `0.0779 m` | `mjcf/*.xml`、`assets/*.usd`、`assets/import_contract.json` |
| 3 | **达妙 DM-J4310-2EC (24V) 电机实参写入**：原包云台三轴 `0` 转子惯量、`0` 驱动、参数未定 | 经 STEP 几何核验大 Yaw 主动轮（`base_link` 内 `(0.0798, 0.0290, −0.0113) m` 处 DM-J4310 输出端，`51` 齿，`r_tip = 40.03 mm`）与被动轮（`−云台yaw传动同步带轮_被动-1`，`51` 齿，`r_tip = 40.04 mm`）严格 **`51:51 = 1:1`** 同步带传动；折叠与 Pitch 为同轴直驱 DM-J4310。三轴统一写入达妙 **DM-J4310-2EC (24V, 10:1)** 官方参数：额定扭矩 **`3.0 N·m`**、峰值扭矩 **`7.0 N·m`**、额定转速 **`120 rpm (12.57 rad/s)`**、空载转速 **`200 rpm (20.94 rad/s)`**、等效输出转子惯量 **`armature = 0.0018 kg·m²`**（`1.8×10⁻⁵ × 10²`）及 24V 线性电压外特性包络 | `model_parameters.json`、`runtime_config.json`、`assets/import_contract.json`、`mjcf/*.xml`、`assets/*.usd` |
| 4 | **启用高精度云台↔腿物理碰撞（供后续 RL 训练）**：原包屏蔽了云台↔腿碰撞，且旧粗椭球/细中心胶囊放开后误触与漏检并存（`gimbal_uwb_tray_link`、`gimbal_uwb_arm_link`、`spring1/2_link` 甚至无碰撞体） | 基于 STEP 独立零件生成 **55 个轻量化精确凸包碰撞网格**（`mjcf/assets/v4_col_*.stl` 及 USD `convexHull` `Mesh`），覆盖云台全部 5 个刚体（`yaw / fold / pitch / uwb_tray / uwb_arm`）与双腿宽铝板/曲柄/摇杆/气弹簧；在 **MJCF 与 USD（`robot.usd` + `MOD4v4_physx.usd`）中全面开启云台↔腿物理碰撞**，同时补齐同侧腿闭链内部自碰撞过滤 | `mjcf/assets/v4_col_*.stl`、`mjcf/*.xml`、`assets/robot.usd`、`assets/MOD4v4_physx.usd` |
| 5 | **UWB 平行四杆耦合刚度提升**：原耦合约束未设 `solref/solimp`，快速折叠滞后达 `19.6°` | 补齐与腿部闭链一致的 `solref=".001 1" solimp=".9999 .99999 .0001"`，1.5 Hz 快速折叠误差压降至 **`0.083° / 0.113°`** | `mjcf/*.xml` |
| 6 | **华南虎双模式大 Yaw + 安全折叠适配器**：方便直接接入 Isaac Lab / MuJoCo RL 训练 | 新增 `tools/scut_gimbal_adapter.py`（同时支持 PyTorch 与 NumPy），提供：① 华南虎同款世界系陀螺航向锁 PD（`compute_world_heading_pd_torque` + DM-J4310 电压包络限幅）；② 小陀螺云台系速度投影（`project_gimbal_spin_translate_cmd`）；③ 三条 `(fold, pitch)` 组合避让不等式投影（`clamp_fold_pitch_clearance`）；④ **先回安全 Yaw 口袋角（`−149.69°`）再下折**的无碰撞收纳律（`plan_stow_targets`）；⑤ Isaac Lab `IdealPDActuatorCfg` 配置生成函数 | `tools/scut_gimbal_adapter.py` |

---

## 二、定量实测结果（详见 `reports/gemini_fix_validation.json`）

| 测试项 | 原包 `MOD4v4` | `MOD4v4gemini`（本包） |
| --- | --- | --- |
| 默认零位（`qpos0` / USD `0` 态）枪管朝向 | 车体系 `(−0.8633, −0.5047, 0)`（偏右后 `−149.69°`） | **严格朝车头 `+X = (1.0, 0.0, 0.0)`**（与华南虎 `WheelBipe V14_2` 完全一致） |
| `12 rad/s` 小陀螺起转 + `±8°/2 Hz` 底盘俯仰（华南虎世界航向陀螺 PD + DM-J4310 包络） | 世界航向误差 RMS `4.69°`、最大 `10.01°`；稳态 Yaw/Fold 力矩达 `5.79 / 6.50 N·m`（`58.5%` 时间超 `3 N·m` 额定值过载） | **世界航向误差 RMS `0.56°`、最大 `1.16°`**；稳态峰值力矩 Yaw **`0.66 N·m`**、Fold **`1.84 N·m`**、Pitch **`1.46 N·m`**（**`0.0%` 超 `3.0 N·m` 额定连续扭矩**） |
| 正常展开行驶工作空间（`1800` 组腿长×摆腿×Pitch×360°Yaw）云台↔腿误触数 | 屏蔽碰撞（放开旧粗椭球有大量误触） | **`0 / 1800` 假阳性误触** |
| 收纳姿态 `360°` 逐度 Yaw 扫描云台↔腿真穿模检出率 | `0.0%`（漏检全部 UWB 托架/铝排穿模） | **`100.0%` 检出**（STEP 网格 `<3 mm` 干涉区间 `[−95°..+18°], [+57°..+118°]`，凸包实测触发 `[−95°..+17°], [+58°..+119°]`，边界精度 **`1°`**；安全收纳角 `−149.69°` 零接触） |
| 展开朝前 `(0°,0°,0°)` → 收纳 `(−149.69°,+54.5°,−53.85°)` 动态折叠全程碰撞步数 | 无执行器 / 直接下折必撞大腿 | `plan_stow_targets` 先转 Yaw 入安全窗再下折：**全程 `0` 碰撞** |
| USD 三套资产（`robot.usd` / `MOD4v4_physx.usd` / `robot_physx.usda`）零位关节帧误差 | — | 位置误差 `3.73×10⁻⁹ m`、姿态误差 `4.68×10⁻⁶ deg`，`enabledSelfCollisions = true` |
| 单线程 400 Hz 物理步进速度（含地面+自碰撞） | — | **`13,112 steps/s`（约实时 32 倍速）** |

---

## 三、下游 RL 训练接入指南（参考华南虎 `WheelBipe V14_2`）

1. **纯底盘 6 维策略兼容模式（MuJoCo `mjcf/scene.xml`）**：
   - `nu = 6`、观测与动作索引与 `MOD4v3_HW300N60_R3` 完全一致；云台被动保持在车头 `+X` 展开位。
2. **小陀螺锁航向 / 云台扰动 / 折叠联合训练模式**：
   - **MuJoCo**：加载 `mjcf/scene_gimbal_actuated.xml`（`nu = 9`，索引 `6, 7, 8` 分别为 `gimbal_yaw_joint_motor`、`gimbal_fold_joint_motor`、`gimbal_pitch_joint_motor`，直接力矩输入 `±7.0 N·m`）。
   - **Isaac Lab (`MOD4v4_physx.usd`)**：
     - 直接调用 `tools/scut_gimbal_adapter.py` 中的 `make_isaaclab_mod4v4_gimbal_actuators()` 注入 `ArticulationCfg.actuators`：
       - 普通地形抗扰训练（华南虎模式 A）：`gimbal_yaw` 设 `stiffness=0.0, damping=0.5`，每回合采样 `yaw_vel_target ~ U(-π, π)`；`gimbal_fold` 与 `gimbal_pitch` 设 `stiffness=40.0, damping=1.2` 保持 `0`（或在 `clamp_fold_pitch_clearance` 可行域内随机采样）。
       - 小陀螺锁世界航向平移（华南虎 `WheelbipeV14FlatEnvCfg_v2` 模式 B）：读取 `gimbal_yaw_link` 世界航向与角速度，调用 `compute_world_heading_pd_torque()` 输出力矩，并用 `project_gimbal_spin_translate_cmd(vel_yaw_xy, q_yaw)` 将云台系平移速度指令直接旋到底盘系。
       - 碰撞惩罚 / 终止监测：本包已开启云台↔腿物理碰撞，在 `ContactSensorCfg` 中监听 `GIMBAL_CONTACT_BODIES = ("gimbal_yaw_link", "gimbal_fold_link", "gimbal_pitch_link", "gimbal_uwb_tray_link", "gimbal_uwb_arm_link")` 即可直接用于 RL 的 `undesired_contact` 惩罚或非法姿态终止。
       - **折叠/收纳安全互锁**：收纳态（`fold = +54.5°, pitch = −53.75°`）下不可乱转大 Yaw（车头零位系下 `[−95°..+18°]` 与 `[+57°..+118°]` 会撞大腿/气弹簧）；折叠前请调用 `plan_stow_targets()` 先将大 Yaw 转入安全口袋角 `−149.69°`（安全裕度窗约 `[−175°, −100°]`）再下折。
