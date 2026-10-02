# RMUC 2026 场地 · Isaac Lab 1024 环境训练地图

本包由你提供的 `RMUC2026_V2.0.0.stp` 转换，交付日期 2026-09-11。原 STEP 只读，未修改。

**已经完成 CAD 几何、USD 引用和 1024 个场地布置的离线验证。本机没有 Isaac Sim / Isaac Lab，尚未完成目标机 PhysX 实跑，不能把离线通过当作 1024 台机器人训练的性能保证。** 包内带目标机验收脚本，实际结果会写入 JSON。

## 1. 地图内容与交付范围

每个环境都有一整份场地地形；1024 份以 32 × 32 排列，共享 USD 网格引用。间距 X=34 m、Y=20 m，场地本体约 29.01 × 16.00 m。视觉和碰撞分离，不把完整 CAD 装配的机械细节复制 1024 遍。

| 地形 | 本包处理 |
|---|---|
| 平地跑、制动、原地起跳 | 保留 CAD 地板，提供路线与起跳高度指令 |
| 上下中心岛的斜坡、斜坡小陀螺 | 保留全部连接斜面，提供上下坡与定点旋转路线 |
| 中心岛一、二级台面与台阶 | 保留原台面、阶梯和中央结构 |
| 台面边缘凸坎 | 独立保留，未与台面合并抹平 |
| 双方飞坡与沟壑 | 保留起跳坡、沟底、对岸公路和护栏 |
| 双方起伏路 | 保留 CAD 连续波峰、波谷，不改成平路 |
| 公路下方狗洞 | 保留洞顶、洞内地板和侧壁，提供两个方向的专项路线 |
| 梯形高地、公路和其他斜面 | 保留连接关系，提供高地爬坡路线 |
| 固定木制底座、护栏等阻挡物 | 保留地形装配中的对应实体 |

来源是 STEP 内的 `DOCUMENT_A_ASM` 地面结构装配，共 420 个实体实例，加 1 个展示曲面集合。**未转换另一组基地、前哨站、能量机关、飞镖发射等机械装配本体**，因此这是地形通行训练地图，不是整份 1.25 GB STEP 的比赛机关视觉复刻或射击仿真场景。地形装配中的固定底座保留。色彩按部件类别近似设置，没有复刻印刷贴图。

`data/features.json` 列出地形类别、CAD 实体编号和边界；`reports/collision_audit.json` 逐件记录保留、简化或只作视觉的原因。厚度不超过 2.01 mm 的平面标记层只作视觉；接触使用其下方结构实体，避免重叠碰撞面。

## 2. 先打开哪一个文件

| 文件 | 用途 |
|---|---|
| `maps/arena_preview.usda` | 单场地，带灯光、相机，适合 Isaac Sim 中查看 |
| `maps/arena_1024.usda` | 1024 个完整地形实例，训练加载入口 |
| `maps/arena_1.usda` | 单环境调试 |
| `isaac/terrain_cfg.py` | Isaac Lab 地图加载配置，修正矩形网格的环境原点 |
| `isaac/route_commands.py` | 15 条路线的速度、旋转、起跳指令和完成判定辅助代码 |
| `isaac/shared_raycast.py` | 对所有环境共享同一个网格的地形射线查询 |
| `isaac/smoke_test.py` | 目标机碰撞、射线和运行速度验收 |
| `previews/map_routes.png` | 地形俯视图和 15 条路线 |
| `previews/terrain_details.png` | 中心岛、狗洞、飞坡、起伏路的碰撞几何局部预览 |

请保留整个目录结构；USD 使用相对引用，可整体移动到另一台 Windows / Linux 电脑。预览 PNG 是离线几何渲染，不是 Isaac 实跑截图。

## 3. Isaac Lab 目标机先验收

接口按 Isaac Lab **v2.3.0** 官方源码核对。使用 Isaac Lab 自带的运行环境启动，**不要向 Isaac 的 Python 强行安装本包的 `requirements-offline.txt`**。

Linux，在 Isaac Lab 目录执行：

```bash
./isaaclab.sh -p /绝对路径/rmuc2026_training/isaac/smoke_test.py --num-envs 1 --headless --device cuda:0
./isaaclab.sh -p /绝对路径/rmuc2026_training/isaac/smoke_test.py --num-envs 1024 --headless --device cuda:0
```

Windows，在 Isaac Lab 目录执行：

```powershell
.\isaaclab.bat -p "D:\实际解压目录\rmuc2026_training\isaac\smoke_test.py" --num-envs 1024 --headless --device cuda:0
```

脚本每个环境投放一个动态球体接触探针，检查其接触面、有限状态、PhysX 射线结果，并检查所有环境的共享网格射线；记录初始化耗时和运行速度。默认 100 步预热 + 500 步测量，物理步长 0.005 s。去掉 `--headless` 可以查看第一环境。结果写到 `reports/isaac_runtime_1024.json`，应为 `PASS_RUNTIME_MAP`。

这个成绩只代表地图与 1024 个探针。**机器人 articulation、控制频率、传感器、奖励计算、渲染和 PPO 的真实吞吐仍要在你的目标 GPU 上测量。** 首次加载可能需要 PhysX 烘焙；可用 `tools/build_layout.py --num-envs 64` 等先建立较小布局。不要根据本包 ZIP 大小推断实际显存占用。

## 4. 接进现有机器人训练环境

以下代码在 `AppLauncher` 启动 Isaac Sim **之后**导入。把解压包的 `isaac` 目录加入 Python 路径：

```python
import sys
sys.path.insert(0, "/绝对路径/rmuc2026_training/isaac")
from terrain_cfg import make_terrain_cfg

# 修改你现有环境配置中的 terrain，保留原来的 robot、执行器和训练配置。
env_cfg.scene.num_envs = 1024
env_cfg.scene.terrain = make_terrain_cfg(num_envs=1024)
```

`RMUC2026TerrainImporter` 会把 `scene.env_origins` 设置成随包 JSON 中的 34 × 20 m 矩形原点。**不要再用默认方形 `env_spacing` 自己计算机器人出生位置。** 路线坐标是单场地局部坐标，需要加对应 `scene.env_origins`；不要加两遍。

复位和路线管理的接口示例：

```python
import torch
from route_commands import RouteCommands
from shared_raycast import out_of_arena

# base_height_m 必须填写你的机器人在所选复位姿态下，base 原点到轮子落地面的竖直距离。
# 它不是车高。需要由你的机器人配置提供，下面的变量不是本包擅自指定的尺寸。
routes = RouteCommands(scene.env_origins, base_height_m=robot_reset_base_height_m)
env_ids = torch.arange(scene.num_envs, device=scene.device)
root_states = routes.reset(env_ids)  # 默认按 15 条路线循环分配；reset 的 route_ids 可自定义
scene["robot"].write_root_state_to_sim(root_states, env_ids=env_ids)
# 同时执行你已有的关节、执行器、传感器和控制器复位函数。

# 每个控制周期调用，yaw_rate 必须是世界航向角的导数；不要直接混用机体系角速度 z。
events = routes.update(root_pos_w, yaw_w, yaw_rate, wheel_grounded, stable, control_dt)
velocity_command_b = events["command"]  # [vx, vy, wz]，机体平面速度 / 航向角速度
jump_height_command = events["jump_height_command"]
# 将上述指令和你的任务观测对接；将 progress_reward、success 接到原任务奖励中。
escaped = out_of_arena(root_pos_w, scene.env_origins)
# escaped 加入终止条件，防止机器人离开所属场地，保留原任务摔倒/超时等终止条件。
```

这不是完整 PPO 任务，也没有训练好的策略。需要保留你已有的姿态稳定、力矩/功率、关节限位、接触、滑移奖励，以及机器人模型的正确拓扑和控制器。`stable` 与 `wheel_grounded` 应来自机器人状态和接触传感器，不能常量置真。15 条路线的速度范围是初始课程参数，不是这台底盘已验证的能力。

完成判定包含：飞坡必须先经过受支撑的起跳区域，之后离地，再到达对岸；狗洞必须实际经过洞顶以下区域；原地跳必须达到高度且离地后落地；小陀螺按命令方向的净转角累计，左右晃动不算完成。它们是辅助判据，仍需通过实跑审查策略是否出现其他取巧行为。

先做平地、上下坡和低速度起伏路课程，再加入飞坡、台阶、狗洞。狗洞需要你自己的降身高姿态/指令和相应复位配置；一个通用 base 高度不能替代蹲伏控制或机体净空验证。全身模型不够低时，不应把洞顶删除或把穿模算成功。

## 5. 地形观测：1024 份网格与洞顶

Isaac Lab v2.3.0 的默认 `RayCaster` 从提供的路径寻找首个匹配网格。因此不要把它直接指向包含 1024 个实例的父路径，也不要假设从空中向下扫描的高度图能表达洞内空间。相关官方源码链接见 `SOURCES.md`。

本包的查询接口只为一份场地建立 Warp 网格，在发射射线前减去各环境原点，得到命中后再加回来：

```python
from shared_raycast import SharedTerrainRaycast
sensor = SharedTerrainRaycast(scene.env_origins)
# [num_envs, rays_per_env, 3]，方向为单位向量，姿态旋转需调用方完成。
hit = sensor.cast(ray_starts_w, ray_directions_w, max_distance=5.0)
valid = hit["hit"]
distances = torch.where(valid, hit["distance"], 5.0)
```

向下扫描用于地面；从洞内向上/前方扫描用于顶棚和入口。该接口只查询静态地形，不包含机器人本体和其他动态物体。没有命中会返回 `inf`，必须用 `hit` 掩码处理后再进入策略。不要让理想射线观测与实机传感器能力脱节；加入噪声、延迟、遮挡等应在你现有观测流水线中实施。

## 6. 碰撞和实际尺寸

- 单场地 **64,771 个碰撞三角面、32,188 个顶点、1 个静态三角网格 collider**；视觉 143,152 个三角面。1024 份场地共享 USD 原型，实际 PhysX 缓存/内存共享程度需目标机测量。
- 碰撞使用 `MeshCollisionAPI approximation = none`，没有 RigidBodyAPI。不要改成整场地凸包，也不要把地形挂进机器人的 articulation。
- 静摩擦 0.9、动摩擦 0.8、恢复系数 0、contactOffset 2 mm、restOffset 0，是可调整的训练初值，不是实测赛场摩擦。共享材质会影响所有环境；逐环境域随机化可优先放在机器人接触材质/执行器等已有随机化管线上，不要误把全场统一改材质当成逐环境独立随机。
- 原 CAD 两半场地面各有约 **1.5°** 倾斜，已保留。**不要另加 z=0 无限地面**，否则会填掉沟底或改变接触高度。
- 两条狗洞路线中心线沿竖直方向的几何净空约 **247.21 mm**，这是给定 CAD 的结果，没有强行改成 250 mm。此数值不是全机器人运动净空或可通过保证，碰撞接触偏置也不包含在该几何值内。
- 世界坐标单位 m，Z 向上。`world = CAD_mm × 0.001 − [0, 1.624343676510544, -1.6413436764950495]`；不旋转、不缩放地形特征。

## 7. 离线检查与复核

当前报告：`reports/offline_validation.json` 为 `PASS_OFFLINE_MAP`，1024 个实例共用一个场地原型，所有 USD 引用在包内；独立原 CAD 网格射线校验 **3,770 条全部通过**，其中洞顶/地板各有 360 条。最大射线距离偏差约 **0.265 mm**。被简化实体的双向采样及顶点距离最大约 **0.746 mm**，这是采样结果，不是严格全曲面 Hausdorff 上界。

`reports/route_gate_tests.json` 是人工构造事件的回归检查，不是训练成绩。`reports/source.json` 保存源文件 SHA-256；`MANIFEST.sha256.json` 用于传输后检查包内文件。

在独立普通 Python 环境中可运行：

```bash
python -m pip install -r requirements-offline.txt
python tools/verify_package.py
python tools/validate_map.py
python tools/check_route_commands.py
```

完整 STEP 未放入 ZIP，避免重复携带 1.25 GB 原始文件。包内包含生成后的网格数组、USD、来源实体和校验参考；原 CAD 到网格的源工作记录保留在交付电脑的 `rmuc2026_work` 目录中。
