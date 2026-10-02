# MOD4 MATLAB / Simulink 仿真交付

参考 [Particlela/WBR_simulation](https://github.com/Particlela/WBR_simulation)，固定提交 `83414c0be55632b7aa1d4dc9feaa0f5f63d5d93e`。本机实际运行 MATLAB R2024b，完整结果与图表已保存。

## 一键复算 MATLAB

在 MATLAB 命令窗口：

```matlab
cd('交付包解压目录/matlab_mod4_wbr_20260917')
addpath(pwd)
run_mod4_wbr
```

需要 Control System Toolbox。已包含符号生成的 `wbr_linear_matrices.m`，无需重跑符号推导。若删除缓存或改变动力学，重新生成需要 Symbolic Math Toolbox 和旁边的固定参考仓库快照。不要把上游 `function` 目录整体加入路径，其 `lqr.m` 会遮蔽 MATLAB 同名函数。

独立运行站立 Simulink 模型：

```matlab
open_system('MOD4_WBR_Balance_20260917.slx')
sim('MOD4_WBR_Balance_20260917')
```

该模型内嵌数值 Acl 和初始条件，展示固定腿长、无扭矩饱和的站立恢复；不包含 CAD 接触和 RL 策略。已与 MATLAB 对应响应做数值交叉验证。

## 数据说明

- `mod4_extracted_parameters.json`：只读提取的质量、COM、惯量、CAD Jacobian、闭链动能得到的竖直等效惯量和电机参数。
- `results/summary.json`：LQR、36 组原始增益表、6 个闭环工况、120 个模型随机化样本、10 个弹簧不确定性高度工况、机械负载与起跳预算。
- `results/feasible_gain_schedule.json`：排除 11 个参考 motor hip 超限格点后的 25 组原始增益。此检查仅验证参考关节限位，不等同于全地形 roll/接触部署验收。
- `results/mod4_wbr_simulation.mat`：全部状态、扭矩、参考轨迹和高度试验原始曲线。
- `results/*.csv`：各闭环工况完整 12 秒轨迹，以及完整精度 A、B、Kd、Ud。
- `results/figures/`：MATLAB 曲线与 CAD 姿态图。CAD 图为静态渲染，不是新完成的接触仿真。
- `MOD4_MATLAB_WBR仿真报告_20260917.pdf`：图文说明和后续任务。
- `UPSTREAM_LICENSE.txt`：MIT 许可证，保留上游作者声明。
- `TASKS.md`：完整接触仿真与实车落地前的检查任务。

## 控制与力矩约定

状态顺序 `[s, ds, yaw, dyaw, alpha_left, dalpha_left, alpha_right, dalpha_right, pitch, dpitch]`；角度均为 rad。仿真内部状态相对平衡参考，车体参考 pitch 为 0，左右腿参考摆角不是 0。

虚拟输入 `[left_wheel_torque, right_wheel_torque, left_leg_swing_torque, right_leg_swing_torque]`。四个腿 motor torque 通过 CAD 虚功映射得到，顺序 `[left_hip, left_crank, right_hip, right_crank]`，不等同于四个虚拟输入。

电机模型：四个 DM8009P，24 V；轮电机 DM3519、替换减速箱总比 15.8。电机包络、转子惯量、效率为现有工程参数，非完整硬件实测。

气弹簧：每支 `F = Fref - 3500*q - 3*qdot`，q 单位 m。`Fref=300..700 N` 定义在 gas_slide 的 q=0，并非整行程力恒定。竖直补偿的 KP/KD/KI 是等效轴向增益，不应直接作为电机 position PD。

标称 q=0 眼距约 179.36 mm。因此 500 N 仿真参考力按当前线性曲线对应 200 mm 眼距时约 427.8 N，不能当作订购“全伸展标称 500 N”的型号依据。电机 armature 按相对关节转动加入惯量交叉项，禁止只加到绝对轮或腿惯量上。

## 模型限制

10 状态模型是小角度、固定腿长、理想滚动近似；不包含 roll、导轮抢载、轮胎接触变化、硬限位碰撞、台阶边缘、离地飞行、落地、屋顶接触或热模型。120 个模型样本有界不等于 RL、sim2sim 或 sim2real 通过。

竖直 1 DOF 模型检验“控制器不知道真实弹簧力”的高度偏差，加入积分后可以消除稳态偏差，但瞬态仍达数厘米。左右不等力的总力在这个模型中可以抵消，不能用它证明抗 roll。狗洞静态顶隙仅约 1.57 mm，不能用无屋顶的高度试验认证动态通过。

额外 payload 为 0，14.2 kg 是 CAD/材料估算，不是比赛整车实测质量。

## PDF 重建与可选 CAD 重新提取

已有数据和图像下，用 Python + reportlab 运行 `build_report.py` 可以重建 PDF。`extract_mod4.py`、`create_pose_assets.py` 是原 CAD 工作区的可选提取/渲染工具，需要完整 MJCF、277 个 CAD 网格和原运动学文件；它们不是 MATLAB 数值复算的依赖。
