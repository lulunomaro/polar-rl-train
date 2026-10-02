# Isaac Lab + MuJoCo 环境（2026-09-08 搭好）

## 0. 一句话
两套仿真都能跑了；**Isaac Lab 里能看到 N 台整车总装机器人同时在物理下站着/动**，
MuJoCo 里能开窗口看训练好的策略实机回放。真正开始训练的命令在 §4，你说开始我再按。

## 1. 装了什么（全部本地，无需下载）
| 组件 | 位置 | 版本 |
|---|---|---|
| Isaac Sim（pip 版） | `.venv-isaaclab` | isaacsim 6.0.1.0 + omniverseclient 2.71.1 |
| Isaac Lab | `third_party/IsaacLab-3.0.0-beta2.patch1`（editable） | 6.1.14（含 isaaclab_rl / tasks / assets） |
| torch / rsl_rl | 同上 | torch 2.10.0+cu128，rsl-rl-lib 5.0.1 |
| MuJoCo | `.venv` | mujoco 3.12.0（另有 `.venv-train` 的 3.8.1+mujoco-warp 供 mjlab 训练用） |
| GPU | RTX 3060 12 GB / 驱动 591.86 | 冷启动 Isaac 约 60-70 s，占 ~10 GB 内存 |

Isaac Lab 3.0 的命令行变了：**默认无窗口**；要窗口必须加 `--viz kit`（可选值 kit/newton/rerun/viser/none），
`--headless` 已废弃。

## 2. 机器人资产（两条路线都做了）
### 2.1 闭链原版（和 MuJoCo 一模一样：19 刚体 / 18 关节 / 6 条闭环 / 气弹簧）
```
.venv-isaaclab\Scripts\python.exe isaac\convert_robot.py            # -> isaac/assets/rm_vehicle_cc/
```
mujoco-usd-converter 把 `<equality connect>` 转成了 6 个 `PhysicsSphericalJoint`（并标了
`physics:excludeFromArticulation=1`），关节限位、质量、惯量、armature、摩擦全部带过来（已逐项核对）。
**但 PhysX 跑不稳**：16 台在第 0 步全部标准（base z 0.0529~0.0549，和 MuJoCo 一致），
到 0.2 s 就全部塌掉——闭合链在 PhysX 里被当成关节外约束软求解，扛不住 350 N 气弹簧 + 17 kg 车身。
所以闭链版留给“看结构/对几何”，训练不要用。

### 2.2 串联等效（PhysX 能训的那条腿）
```
python isaac\make_serial_plant.py                                   # -> robot/out_cc_linkfix/rm_vehicle_serial.xml
.venv-isaaclab\Scripts\python.exe isaac\convert_robot.py --xml robot\out_cc_linkfix\rm_vehicle_serial.xml ^
        --out isaac\assets\rm_vehicle_serial.usd
```
每腿 3 个驱动关节：大腿 rear1、膝 rear2、轮 wheel；膝角直接取解析闭链解出来的值
（docs/viz/model.json 的 stance：左 -0.097/-0.0865，右 -0.117/-0.0784），所以腿长、轮位置、
离地高度和闭链版完全一致。MuJoCo 里 kp=300/kd=30 能站住（残余下垂 ~0.05 rad）。

## 3. 看画面
```
isaac\isaac_gui.bat                     # Isaac 视口窗口，24 台机器人（--viz kit --hold）
isaac\isaac_reconvert.bat               # 改了 MJCF 之后重新转换
scripts\mujoco_pose_gui.bat             # MuJoCo 窗口：闭链整机在 stance 位被 PD 托住（可自由转视角）
sim_mujoco\policy_gui.bat               # MuJoCo 窗口 + v16 策略真跑（0.5 m/s 前进）
sim_mujoco\policy_gui_spin.bat          # 同上，小陀螺
```
命令行等价物：
```
.venv-isaaclab\Scripts\python.exe isaac\preview_robots.py --num_envs 24 --viz kit --hold
.venv-isaaclab\Scripts\python.exe isaac\preview_robots.py --usd isaac\assets\rm_vehicle_serial\rm_vehicle_serial.usda ^
        --serial --knee-kp 300 --knee-kd 30 --num_envs 64 --viz kit --hold
.venv\Scripts\python.exe scripts\mj_view.py --seconds 0                 # 一直开着
.venv\Scripts\python.exe sim_mujoco\onnx_play.py --model robot\out_cc_linkfix\scene_cc.xml ^
        --onnx train\deploy\rm_cc_v16_final.onnx --viewer --seconds 30 --const=0.5,0.0,0.22 --settle 1.5
```
顺手修掉的 MuJoCo 显示坑（这些就是“mujoco 里只有箭头/机器人不见了”的真正原因）：
1. `rm_vehicle_cc.xml` 是**纯机器人**，没有地板 → 直接打开它就是一路自由落体飞出视野。
   现在默认打开 `robot/out_cc_linkfix/scene_cc.xml`（含地板/灯光/天空盒/相机/keyframe）。
2. 初始高度：MJCF 里 qpos0 的 base z=0（轮子埋进地里 73 mm）→ 现在 `--auto-z` 按轮轴实测把车身
   降到轮胎刚好接触（stance 位是 -18.8 mm）。
3. 查看器相机默认不跟机器人 → 现在 `mjCAMERA_TRACKING` 锁 base_link。
4. 不加平衡控制时机器人会往后倒（它是两轮自平衡的）→ `--no-balance` 只适合拍静态图（`--steps 30`）。

## 4. 真开始训练时用什么命令（现在先不按）
Isaac Lab 侧（GUI + 多机器人，rsl_rl）：
```
.venv-isaaclab\Scripts\python.exe third_party\IsaacLab-3.0.0-beta2.patch1\scripts\reinforcement_learning\rsl_rl\train.py ^
        --task <RMVehicle-Serial-v0> --num_envs 4096 --viz kit --headless? (不要 headless)
```
需要补的工作（下一步）：给串联等效写一个 `ManagerBasedRlEnv` 配置（obs/reward/termination 照抄
`train/rmvehicle/src/rmvehicle/env_cfgs.py` 的 mjlab 版本），注册成 `RMVehicle-Serial-v0`。
MuJoCo 侧继续用 mjlab（v16/v17 的既有训练链不动，这是基线）。

## 5. 已知问题
- 闭链 USD 在 PhysX 下站不住（见 §2.1），需要改成“串联等效 + 解析闭链映射”或给 PhysX 加硬约束迭代设置
  （Isaac Lab 3.0 的 solver 参数在 `isaaclab.physics.PhysicsCfg` / 后端扩展里，还没接）。
- Isaac 的 `GroundPlaneCfg` 会去 Omniverse CDN 拉 USD，本机拉不到 → 预览脚本用本地立方体当地板。
- `.venv-isaaclab` 是 Python 3.12（uv 管的），和训练的 3.13 环境分开，别混用。


## 6. 这次实测到的 Isaac 物理细节（下次调参就照这个来）
* 强制写入解析闭链 stance 之后，spawn 状态是**逐位精确**的：base z=0.0531，max|q-q_stance|=0.0000 rad，
  24 台全部标准（`--serial` 与闭链版都验证过）。
* 但 Isaac 里跑 0.2 s 之后会往**后仰 15°**、轮子**陷进地板 ~15 mm**：
  1. 轮子下沉 = 接触偏置问题。mujoco-usd-converter 写的是 `newton:contactGap = 0`，
     PhysX 只有穿透之后才产生接触；我在 `UsdFileCfg.collision_props` 里加了
     `contact_offset=0.012 / rest_offset=0`，从 22 mm 降到 15 mm，还需要继续调
     （下一步：`--dt 0.0005`、或在 `isaaclab.physics.PhysicsCfg`/后端扩展里加大 solver 迭代、
     或把轮子换成 sphere 碰撞体）。
  2. 后仰 = 整机质心在轮轴后方约 30 mm（这是真机就有的性质，所以它是两轮自平衡车），
     预览脚本里的轮平衡 PD（`--bp/--br/--bpi/--kvx/--kx`）只能压到 -15°，
     真正要站直得用训好的策略（v16）或者加高度/前馈项。
  3. 所以 `--balance 0 --hold` 的窗口是“每 50 步把姿态钉回解析 stance”的**展示模式**，
     看结构/看画面用；它不代表物理能站住。
* 视口截图 API：Isaac Sim 6 / Kit 2.71 的 `IApp` 已经没有 `write_viewport_to_file`，
  `omni.ui.Workspace.get_window('Viewport')` 也没有 `capture_content`。
  要出图走 `--enable_cameras` + `isaaclab.sensors.CameraCfg`（RTX renderer），或者 `--livestream 1`
  在浏览器里看 http://localhost:8211。目前 Isaac 侧只能肉眼看窗口，MuJoCo 侧有 PNG。


## 7. 地图（RMUC2026 7v7）
Isaac 侧现在用 `--field` 铺实测地图（和 mjlab 课程同一份 `cad/out_map/field_dims.json`）：
```
isaac\isaac_field_gui.bat
# 等价：
.venv-isaaclab\Scripts\python.exe isaac\preview_robots.py ^
  --usd isaac\assets\rm_vehicle_serial\rm_vehicle_serial.usda --serial --field --env-x0 -6 ^
  --knee-kp 600 --knee-kd 60 --kp 600 --kd 60 --num_envs 24 --steps 80 --balance 0 --iters 16 --viz kit --hold
```
MuJoCo 侧：`sim_mujoco\policy_gui_field.bat`（`robot/out_cc_linkfix/field_cc.xml`）。
注意 mjlab 的训练任务 `RMVehicle-CC-Field-v0` 本来就是地图课程（7 列：平地/上下坡/上下台阶/障碍/颠簸），
不是平地；`--field` 只是把同一张地图搬到 Isaac 窗口里给你看。
