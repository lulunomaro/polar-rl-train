# MOD4 串联腿底盘：MJCF + USD 交付包

源文件为 `底盘_MOD4.STEP`，277 个 CAD 零件全部保留为外观。源 STEP 只读，未改动；本包与旧 RM2025 交付包独立。

**默认训练文件保留 HiFi 外观。Isaac Lab 请加载本包的 `isaac/robot.usd`，闭环和链轮耦合已经直接写入 USD。不要重新用通用 MJCF 导入器生成 USD。**

## 文件入口

| 文件 | 用途 |
|---|---|
| `scene_training.xml` / `scene.xml` | MuJoCo 完整外观、地面、6 个力矩执行器；两文件内容相同 |
| `robot_hifi.xml` | 完整机器人 MJCF，无地面；包含浮动基座 |
| `scene_headless.xml` | 同样的质量、惯量、关节、闭环和碰撞，仅省去视觉网格 |
| `isaac/robot.usd` | 供 Isaac Lab 引用的机器人资产；同目录的 `meshes.usdc` 必须保留 |
| `isaac/scene.usda` | 带地面、灯光、相机和机器人实例的独立 USD 查看场景 |
| `view_joints.py` | 可拖拽滑块的关节拓扑预览；从动关节按闭环解跟随 |
| `robomaster_env.py` / `train_ppo.py` | 可运行的 MuJoCo / Gymnasium / PPO 接口 |
| `isaac/robot_cfg.py` / `isaac/smoke_test.py` | Isaac Lab 配置、六维力矩接口、目标机动态自检 |
| `reports/` | CAD 零件归属、实体测量、动力学、USD 运动学及故障检测报告 |

## 已完成的验证

- 23 个机器人刚体，22 个树关节，6 个外部闭环连接，4 个链轮 1:1 耦合，6 个执行器。MuJoCo 的 `nq=29, nv=28`，等式雅可比秩为 16，独立速度自由度为 12（浮动基座 6 + 电机输入 6）。
- 225 组运动姿态独立重建 USD 关节树，与 MJCF 的刚体位置最大差约 6.8 nm；USD 闭环锚点最大差约 9.7 nm。这是导出数值一致性，不代表实物精度。
- 224,000 个 MuJoCo 物理步，包含满力矩随机控制、10 倍输入被限幅、跌落、质量扰动及外力推撞：无非有限状态、无求解器警告，最大闭环偏差 0.176 mm。最大碰撞穿透约 1.81 mm；完整边界见 `reports/validation_report.json`。
- 4,096 步 PPO、80 次优化器更新及随后 1,000 步评估通过。仅证明接口和训练更新可运行，不是已收敛的跳跃策略。
- 19 类故障注入被自检识别，包括丢失闭环、耦合符号错误、关节父级错误、质量/惯量字段丢失等。

**本机没有执行 Isaac/PhysX。USD 已通过 OpenUSD 读取、结构、引用隔离和运动姿态检查；目标机必须先运行下面的动态自检。测试通过仅覆盖报告中的载荷、时间步长和配置。**

## 在 MuJoCo 查看与训练

在解压后的 `chassis_mod4` 文件夹内运行。推荐独立 Python 环境。

```bash
python -m pip install -r requirements-training.txt
python view_joints.py
python view_model.py --motion
python tools/validate_model.py
python train_ppo.py --steps 4096 --envs 4 --randomize
```

`view_joints.py` 中拖动左右髋、输入角差和轮子滑块，闭环杆件自动跟随；在画面上拖动鼠标旋转视角、滚轮缩放。它是运动学检查窗口。`view_model.py` 不带 `--motion` 时运行真实 MuJoCo 动力学，可用原生查看器施力拖动刚体。

正式训练可使用 `python train_ppo.py --steps 1000000 --envs 4 --randomize`。默认读取含 277 件外观的 `scene_training.xml`。MuJoCo 不显示窗口时也保留这些外观数据。`DummyVecEnv` 是 CPU 顺序步进，不能用这份短测推断 GPU 大规模并行吞吐。

## 在另一台电脑的 Isaac Lab 验收

把整个文件夹复制过去。配置按 Isaac Lab 2.x 的 `ArticulationCfg` / `ImplicitActuatorCfg` 接口编写；具体安装版本的 API 和 PhysX 模式由目标机验收确认。不要向 Isaac 自带 Python 安装本包 `usd-core`，使用它自带的 `pxr`。

在 Isaac Lab 安装根目录运行，按实际解压路径替换 `/path/to`：

```bash
./isaaclab.sh -p /path/to/chassis_mod4/isaac/smoke_test.py --device cuda:0 --num-envs 1 --steps 6000
```

Windows 对应使用 `isaaclab.bat -p C:\path\to\chassis_mod4\isaac\smoke_test.py --device cuda:0 --num-envs 1 --steps 6000`。

通过后，`isaac/runtime_report.json` 才会出现 `PASS_RUNTIME_BOUNDED`。再增加环境数复测。关闭 HiFi 外观不是扩大环境数的前提；本包的 277 个视觉实例均不参与碰撞，碰撞由 26 个图元承担。不要预设闭环在某张显卡上的最大并行数量。

训练项目可导入 `make_robot_cfg()`。每个物理步通过 `TorqueInterface.apply(action)` 写力矩，再 `robot.write_data_to_sim()`、`sim.step()`、`robot.update(dt)`。该接口保留弹簧预载，并按估计的电压/速度包络限制电机力矩。接入自己的任务时保留 `RuntimeGuard`，不要只检查关节数量。

六维动作顺序固定为：

```text
left_hip, left_crank, left_wheel_spin,
right_hip, right_crank, right_wheel_spin
```

`hip` 和 `crank` 都相对机身驱动；`knee` 是闭链从动关节。单独随机初始化所有关节会破坏闭合。复位可用全零关节位姿，或使用 `kinematics.set_configuration()` 的闭链解；四个链轮跟随关节也必须同步复位。

## 几何和参数范围

| 项目 | MOD4 值 / 来源 |
|---|---|
| 大腿髋—膝销距 | 215 mm，CAD 圆柱轴线测量 |
| 小腿膝—轮轴销距 | 258 mm，CAD 圆柱轴线测量 |
| 两侧轮胎中心距 | 437.6 mm，按橡胶接触环的中心测量 |
| 轮胎半径、宽度 | 62.5 mm、20 mm |
| 当前模型质量 | 约 14.20 kg，CAD 体积 + 材料/电机质量假设；不是称重结果 |
| 四个腿部电机 | 用户已在本次 MOD4 转换中确认：四个均为 DM8009P、24 V；STEP 名称仍写 DM8009 |
| 轮驱 | DM3519，替换减速箱，总减速比 15.8；本 STEP 含该减速箱几何 |
| 氮气弹簧 | 每侧 700 N / 150–200 mm 眼距 / 1.25 力比，为可调仿真候选值，未验证为 MOD4 实装规格 |

左右腿实际销距一致。模型零位重新选在闭合、无初始碰撞的中间姿态；相对零位髋范围 ±0.5 rad，输入角差范围 −0.7…0.4 rad，膝范围约 −0.5414…0.3393 rad。膝、摇杆和弹簧行程共同限制所选连续分支，MJCF 中不依赖 tendon 限位。

源 CAD 的限位块已针对输入杆、摇杆和小腿做实体距离检查，包含 2° 膝角越界余量后最小距离约 1.364 mm，弹簧眼距约 156.72–197.83 mm。检查范围见 `reports/operating_clearance.json`；没有声称穷举了所有零件间的 CAD 碰撞。

减速箱内部齿轮用输出端等效转动惯量处理，不求解齿面接触。输出齿轮、外壳、轮毂和轮胎跟轮轴转动；固定座、后盖、电机定子与小腿相连。内部不可见齿轮的视觉网格固定在载体上，其精确旋转和各级齿轮惯量尚未辨识。每个 CAD 零件的质量及归属都列在 `reports/model_manifest.json`。

腿电机反射惯量、3519 裸电机 0.16 kg 的质量假设、减速箱效率、弹簧力、材料密度仍需实测标定。没有把未出现在 STEP 中的云台、电池、弹药额外加到模型里。比赛跳跃能力还取决于整机负载和实测动力参数，本包不作已能跳过比赛地形的承诺。

## 调整气弹簧参数

`model_parameters.json` 是参数记录，并非 MJCF 的热更新文件。修改弹簧参数后可运行：

```bash
python -m pip install -r requirements-usd.txt
python tools/apply_parameters.py --gas-force 700
python tools/validate_model.py
python tools/audit_model_parity.py
python tools/test_import_guard.py
```

该工具同步四份 MJCF 和 USD 的电机/弹簧数值；`--gas-force 0` 可用于无弹簧力对照。改变质量、惯量分配或机械限位需要重新做几何和动力学审计，工具不会静默改动这些项目。修改后原有验证报告失效，应重新验收；Isaac 侧同样重新运行动态自检。

模型采用米、千克、秒、弧度；USD 转动限位和角度驱动已按度制转换。坐标为 `X = −CAD Z, Y = −CAD X, Z = CAD Y`，左右沿用 STEP 装配命名。上实机前需标定编码器零位及方向。
