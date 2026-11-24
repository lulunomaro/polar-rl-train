# MOD4v3 × Livox Mid-360 预先建图、实时点云台阶检测与实车部署指南

本目录已完成面向 **Livox Mid-360** 激光雷达的全链路导航、先验点云建图（`.pcd` -> 多层 `2.5D`）、实时三维点云台阶/横梁检测与动态障碍物剔除重规划方案。

---

## 1. 传感器与底盘安装外参（`mid360_extrinsic.json`）
- **雷达型号**：`Livox Mid-360`（水平 `360°`，原生俯仰 `-7° ~ +52°`，盲区 `0.10 m`，测距噪声 `1.5 cm`，`200,000 pts/s` 非重复玫瑰扫描）。
- **推荐安装姿态**（已写入 `mid360_extrinsic.json`，实车按结构 CAD 修改 `pos_base_m` 与 `rpy_deg` 即可）：
  - 位置：`base_link` 前上碳板 `[+0.145, 0.000, +0.085] m`
  - 姿态：`rpy_deg = [0.0, +18.0, 0.0]`（前倾下俯 `18°`：将正前方垂直视场由 `[-7°, +52°]` 下移至 `[-25°, +34°]`，既能直接扫到车前 `~0.45 m` 处的 `200 mm` 台阶立面与踏面，又完整保留 `360°` 四周墙面用于 `FAST-LIO2` 定位）。

---

## 2. 预建好的全赛场 `.pcd` 先验点云图与多层 2.5D 导航图
所有赛场均已在 `maps/mid360_prior/` 下预建好三套配套产物：
1. **`<course>_prior.pcd`**：标准 `PCL v0.7` 二进制三维先验点云地图（`x, y, z, intensity`，可直接加载至 `FAST-LIO2` / `icp_relocalization` / `CloudCompare` 进行实车重定位）。
2. **`<course>_pcd_nav25d.npz`**：纯由 `.pcd` 三维点云离线重建的 `2 cm` 多层 2.5D 导航地图（自动分离地面/踏面 `height`、低矮悬空横梁/隧道净空 `ceiling`、可爬台阶 `semantic=2` 与高墙 `semantic=3`）。
3. **`<course>_stairs.json`**：从点云地图自动提取的全部可爬台阶走廊中心、宽度、台阶高度 `step_height_m` 及法向攀爬航向角 `climb_yaw_deg`。

### 实车比赛场地 `.pcd` 一键建图命令
实车用 `livox_ros_driver2` + `FAST-LIO2` 扫完赛场保存 `scans.pcd` 后，只需运行：
```powershell
python build_mid360_prior_maps.py --from-pcd path/to/scans.pcd --name rmul_venue
```
即可自动滤除噪点、分离桥洞/横梁与地面、提取全部台阶法向并生成 `maps/mid360_prior/rmul_venue_pcd_nav25d.npz` 与 `maps/elevation/rmul_venue.npz`。

---

## 3. 实时点云台阶检测、跳跃障碍识别与动态避障架构（`mid360_stair_nav_detector.py`）
支持两种运行模式（`50 Hz` 单步耗时 `< 1 ms`）：
1. **`fusion` 模式（比赛默认：先验地图 + 实时 Mid-360 点云融合）**：
   - 静态地形基底由先验 `.pcd/.npz` 提供，彻底消除近身盲区与遮挡；
   - 实时配准 `Mid-360` 三维点云，统计前方台阶立面/踏面实时点云命中数（`Mid360台阶点`），并检测高于先验地面 `> 0.14 m` 且顶高 `>= 0.275 m` 的**未建图动态障碍（敌方哨兵/步兵/装甲块）**：
     - **严禁误识别上阶**：若动态障碍阻挡台阶助跑道或落足区，立即否决 `g_step -> EMPTY`（零误触发上阶姿态撞车）；
     - **实时 `A*` 动态绕障**：自动膨胀 `0.24 m` 机身安全半径写入 `dyn_blocked`，在 `0.16 s` 内重规划绕开敌方机器人再正对台阶上高地。
2. **`online_pc` 模式（无先验图 / 未知场地纯实时点云模式，`--sensor-mode mid360_online`）**：
   - 在 `12.8 m × 12.8 m`（`2 cm` 分辨率）世界对齐滚动子图中累积运动补偿后的 `Mid-360` 三维点云，结合近场自由空间锥插值，在**零先验地图**下直接输出 `g_step = [d1, h1, d2, h2]`（自动上 `110~250 mm` 单/双阶与斜阶）及 `g_jump = [d_front, d_back, z_top_rel, z_land_rel]`（按 `Space` 手动大跳横梁/高台）。

---

## 4. 仿真游乐场与实车 ROS 2 启动方式
- **仿真桌面一键体验（`.pcd` 重建先验图 + `Mid-360` 实时三维点云显示，按 `P` 切换点云开关）**：
  双击根目录 `Run_MOD4v3_Mid360_PCD_Nav_WASD.bat` 或 `Run_MOD4v3_LiDAR_Nav_3v3_5v5_WASD.bat`。
- **实车 ROS 2 (`livox_ros_driver2` + `FAST-LIO2`) 启动**：
  ```bash
  python3 mid360_ros2_nav_node.py \
    --prior-map mid360:suite_rmul2027 \
    --extrinsic mid360_extrinsic.json \
    --lidar-topic /livox/lidar \
    --odom-topic /Odometry
  ```
  （若订阅 `livox_ros_driver2/msg/CustomMsg`，加上 `--custom-msg`；若在无先验图场地测试纯实时点云上台阶，设 `--prior-map none`。）
