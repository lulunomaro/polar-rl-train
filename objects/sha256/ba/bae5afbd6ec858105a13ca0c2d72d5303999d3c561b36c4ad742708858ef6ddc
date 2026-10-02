# MOD4 最新策略本机驾驶

双击 **START_MOD4.bat**，或桌面的 **MOD4 最新策略驾驶** 快捷方式。启动独立驾驶控制窗，随后打开 MuJoCo 画面；首次加载 Isaac 物理约需半分钟。

在驾驶控制窗内按住 **W 前进 / S 后退**，松开停车；**X 或空格停车、R 复位、P 暂停/继续**。按钮前进/后退会持续行驶，点停车停止。速度滑条选择 0.1–1.5 m/s，默认 0.6 m/s，指令按 0.6 m/s² 平滑加减速。仿真窗口只用于查看和鼠标调整视角，驾驶键只在控制窗生效，因此不会与仿真快捷键冲突。

当前策略只训练平地直行；此入口固定转向指令为零、实际根部离地高度指令 0.25 m。根部高度是 USD 底盘根坐标原点至平地，不是最高点或底板净空。策略无探索噪声，没有 LQR、轮速辅助或姿态扶正控制；失败后保留现场，按 R 才重新开始。

**实际物理由本机 Isaac Lab / PhysX 运行，MuJoCo 负责显示。** 本机标准 Isaac 图形界面缺少 pip_archive 组件，轻量界面又触发 viewport 原生崩溃；本交付用已验证的无界面 Isaac 物理加独立 MuJoCo 绘图绕开此问题。画面是对实际31个刚体世界姿态的直播，直接从本次源USD抽取277个视觉网格，不借用旧底盘外观，不调用 MuJoCo 的 mj_step，不加入额外控制器。这是原 USD 策略的本机驾驶观察入口，**不是 MuJoCo 物理 sim2sim 验收**。

## 来源和环境

- model_8725.pt：2026-10-01 约 17:17 拉取时远端最新完整保存。下载时没有中断远端训练。
- 远端来源：MOD4_native_floor_continue10h_20260930/logs/2026-10-01_17-10-14_scut_flat_native_floor_1.5m/model_8725.pt。
- 原始权重、USD、运行参数和源快照均保存；DOWNLOAD_RECEIPT.json 记录下载指纹。
- 完整权重 SHA256：88e569e5c1ad1f0e2b0ee99938a76f487a247c62136e5b7d6fcea9242d089797。
- model_8725.onnx 已导出并与原 actor 核对，129 组输入最大绝对误差约 3.34e-6。
- 本次实际调用：C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe；Isaac Sim 5.1.0.0；Isaac Lab VERSION 2.3.2，Python 包 isaaclab 版本 0.54.4；GPU RTX5070Ti Laptop。
- 默认单车用 CPU PhysX，MuJoCo GPU 显示；单车 GPU 物理张量往返在本机较慢。保持 0.5 ms 物理步、100 Hz 策略、solver16/4，接触积分与原运行配置一致。画面接收约33 Hz姿态，控制窗显示实际实时倍率。
- 本机与远端 Isaac 版本不同；isaac/mod4 中只有本地 API 兼容适配，src_snapshot 保留远端原样。不能把本机短回放当远端验收或实车鲁棒性结论。

## 15 秒本机短测试

CPU PhysX 同权重、无探索、种子20260927，完成1500控制步，无失稳终止，无非有限数。前进稳态均速 +0.608 m/s，后退 -0.623 m/s；最大倾斜3.10°；根高245.2–258.0 mm；最后停车残速0.00232 m/s；最大闭链残差0.0584 mm，最大链轮耦合误差0.00120 rad。完整数据 isaac_cpu_smoke.json。这只是单条0.6m/s短轨迹，不等于1.5m/s、多种子、DR或地形毕业。

## 文件

- isaac_interactive.log：互动回放启动和运行日志。
- isaac_telemetry.json：当前实际速度、倾斜、车高、轮载荷和闭链/耦合误差。
- operator_command.json：独立控制窗写入的本机操控指令。
- local_playback_process.json：本机回放进程信息。
- run_manifest.remote.json、src_snapshot：原始远端配置和源快照。
- display/live_display.xml：仅绘图的静态mocap场景，31刚体、277视觉；无关节和动力学。不能拿这个文件训练。
- display/DISPLAY_SOURCE_AUDIT.json：各视觉网格的实际USD来源及三角面数量。
- display_status.json：直播几何世界位姿与 Isaac 数据的一致性检查。
- mujoco_display.log：绘图窗口运行日志。

关闭控制窗会同时停止它启动的本机回放，不影响远端任务。不要同时重复双击启动多个回放。
