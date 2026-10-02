**RM2025 修正版 MJCF / HiFi 交付包**

默认训练入口是 `scene_training.xml`，包含完整 HiFi 外观。`scene.xml` 与它完全相同。模型保留真实连杆闭链和六路电机动作，动作顺序为左 hip / crank / wheel、右 hip / crank / wheel。

**直接使用**

- MuJoCo：加载 `scene_training.xml`。固定步长为 0.0005 s；本包控制周期为 20 个物理步，即 100 Hz。
- Isaac Lab：使用 `isaac/robot_closed.usda` 和 `isaac/robot_cfg.py`。USD 已显式设置闭合关节、链轮耦合和碰撞过滤。
- `robot_hifi.xml` 是无地面、根位置归零的 MJCF 资产。它仍包含闭链约束。
- `scene_headless.xml` 是可选的无外观版本，默认训练入口保持 HiFi。

在包目录执行 MuJoCo 检查和训练：

```powershell
python -m pip install -r requirements-training.txt
python tools/validate_model.py
python train_ppo.py --steps 1000000 --envs 4 --randomize --output runs/my_policy
```

四个髋部驱动已按用户确认的 **DM8009P、24 V** 配置：20 N·m 额定、40 N·m 峰值、保守采用 160 rpm 空载转速、每台电机装配质量 0.93 kg。9:1 是电机内部减速比，输出端扭矩无需再乘 9。外部链轮传动比为 1:1。参数依据见[达妙原厂使用说明书 V1.0](https://doc.switch-science.com/media/files/0eacb9ba-85e6-4761-93df-92773000fddb.pdf)。

MJCF 的硬件峰值限幅为 ±40/±40/±6 N·m。包内 `RoboMasterEnv` 和 Isaac `TorqueInterface` 每个物理步额外实施 DM8009P 的 24 V 扭矩—转速包络。该包络根据说明书额定点和空载点构造，是工程近似。自写训练器时必须保留这层处理；单独加载 XML 只获得静态扭矩上限。峰值扭矩的持续时间、电源总功率限制和热模型尚未实测。

**本次修复**

1. 重设了不存在限位块/小腿干涉的中立姿态。STEP 实体检查发现，旧中立姿态每侧约有 183.45 mm³ 相交。修正后的左右装配在该处对称；0.5 mm 间隙边界为旧零位 −58.128°～−11.839°。新零位对应旧 knee = −35°。训练限位再向内留 2°，最终每侧约 **−21.128°～+21.161°**。该结果来自修正后的 CAD 表面，并非真机测量。髋关节 ±0.65 rad 是训练工作范围。
2. 同步重设了两条曲柄差动限位、气弹簧滑动零位和解析闭链初始化。所有标量关节在新中立姿态均为零。重置时只能改变浮动基座，或调用 `kinematics.set_configuration`；不得独立随机化闭链中的被动关节。
3. 轮毂电机的可见旋转外壳跟随 wheel，固定颈部和安装后盖跟随 shin。STEP 中融合的电机表面按 39.2 mm 的壳体/颈部边界分割用于显示；内部转定子并未由该 STEP 单独给出。
4. 轮子 STEP 的橡胶胎与铝轮毂分别计质量和惯量；裸轮约 0.20194 kg。加上暂估 0.30 kg 电机转动部分后，wheel 刚体约 0.50194 kg。转动部分轴向惯量参考值为 4.656e-4 kg·m²，已计入轮体，wheel armature 为零，避免重复计算。MF9025 总质量 0.65 kg、内部质量分配仍为待标定参数。
5. 修正了四个达妙电机每台由两个 CAD 零件构成、旧模型却每个零件都计 0.65 kg 的重复计重问题。现为每个装配 0.93 kg。当前已建模总质量约 **14.65179 kg**，包含原模型的 1.1 kg 电池假设；未给出的云台和弹仓载荷不代表已建模。
6. 源 STEP 小腿销距确为 **258 mm**，保留该值；轮胎接触中心间距修正为 **471 mm**。报告中的 256.5 mm 和轮距增量没有直接作为修复输入。HiFi 中 0.4554 kg 的轮体数值来自将电机、后盖和轮子统一按同一密度计算，不能当作硬件称重值。

当前结构为 1 个浮动基座、20 个 hinge、2 个 slide、6 个执行器；6 条点闭合约束和4条链轮耦合等式。MuJoCo nv=28，中立等式雅可比秩为16，独立速度自由度为12。261个原CAD实例均保留；分割两侧电机外壳后为263个可见几何体。机器人使用24个碰撞图元，另有1个地面。

**Isaac Lab 交付与验收**

本包采用保留真实闭链的 USD 结构。6 个闭合点通过 articulation 外的 spherical joints 约束，4 个链轮通过 PhysX mimic 约束保持 1:1。这符合 NVIDIA 的[闭链装配方式](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/robot_setup_tutorials/rig_closed_loop_structures.html)和[mimic 方程](https://docs.omniverse.nvidia.com/kit/docs/omni_usd_schema_physics/latest/physxschema/class_physx_schema_physx_mimic_joint_a_p_i.html)。

MJCF 两条固定 tendon 在选定的连续闭链分支上用于限制 crank−hip；USD 通过闭合约束与相应的 knee 限位限制同一运动分支。气弹簧则由两个 slide 的弹簧驱动显式表示。MuJoCo 接触参数与 PhysX 没有逐项等价关系；USD 使用 contact offset=1 mm、rest offset=0、32/8 次位置/速度迭代作为待目标机验收的起点。微小库仑摩擦差异、求解器柔顺性和高速冲击响应尚未跨引擎标定。

在装有 Isaac Lab 的另一台电脑，从 Isaac Lab 目录运行：

```bash
./isaaclab.sh -p /path/to/rm2025_fixed/isaac/smoke_test.py --device cuda:0 --num-envs 1
```

Windows 使用同目录的 `isaaclab.bat -p`。脚本按 Isaac Lab 2.x 的 `ArticulationCfg`/PhysX API 编写；本机没有 Isaac Sim，**未声称已在 Isaac/PhysX 执行通过**。其他大版本或其他物理后端应重新适配和验收。

脚本启动前检查完整的刚体、关节父子关系、锚点、惯量、限位、6个外部闭合点、4个mimic、30组排除、自带外观和气弹簧预载。缺少 PhysX mimic schema 会直接失败。运行后每个物理步检查真实刚体锚点间距和链轮误差，任一失败立即停止。仅比较自由度个数不能证明闭链存在。

1个环境通过后，再使用 `--num-envs 64` 验收目标并行规模。闭链的GPU吞吐和显存占用应在目标电脑测量；本包没有虚构可并行环境数量。示例按每个环境独立引用USD以保证约束关系重映射；更换为物理复制流程后需重跑检查。

接入自己的RL任务时：

```python
# 在 AppLauncher 启动后导入；将本包 isaac 目录加入 Python 路径。
from robot_cfg import make_robot_cfg, TorqueInterface
from audit_import import audit_stage, RuntimeGuard

robot_cfg = make_robot_cfg("/World/envs/env_.*/Robot")
# 创建场景和 Articulation 后，分别审核每个实际 Robot prim。
# sim.reset() 后：
control = TorqueInterface(robot)
guard = RuntimeGuard(robot)
# 每个物理步：
control.apply(action)  # [num_envs, 6]，含电压包络和气弹簧预载
robot.write_data_to_sim()
sim.step()
robot.update(0.0005)
guard.check()
```

**氮气弹簧参数暂定**

按用户要求，先交付模型，再完成弹簧选型。包内当前模拟值为每侧500 N（伸长端）、球头中心距150～200 mm、50 mm行程、压缩力比1.25、等效刚度2500 N/m、阻尼3 N·s/m。这些是临时设计值，**不是选型定稿，也不构成已完成跳台/飞坡的结论**。可在 `model_parameters.json` 查看；修改该JSON不会自动修改已经生成的XML或USD，需要同步重建。整机比赛质量和轮毂绕组尚未确认。

**检查结果与文件**

- `reports/validation_report.json`：当前XML的49.2万物理步回归，包括驱动、饱和命令、跌落、推扰、质量变化和4000个RL接口步；记录闭合误差、穿透、限位越界和模型SHA256。
- `reports/import_guard_tests.json`：故意破坏约束、父子关系、惯量和预载等12种故障的拒绝测试。运行时部分使用模拟遥测，不能作为PhysX执行结果。
- `runs/smoke/training_report.json`：4096步PPO更新及1000步评估，只验证训练接口，不是已收敛策略。
- `reports/model_manifest.json`：当前零位、质量、部件修复变换和分割归属。
- `reports/reference_manifest.json`：旧模型的历史参考，用于解析坐标转换。
- `reports/source_geometry_audit.json`：STEP实体限位间隙和轮胎/轮毂实体积分数据。
- `DELIVERY_MANIFEST.json`：本压缩包的文件SHA256和验证摘要。

独立的USD静态审核/导出环境可安装 `requirements-usd.txt`；Isaac使用其自带pxr运行。生成器和STL等中间文件不参与物理步计算。
