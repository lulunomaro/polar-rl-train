# MOD4v2 P0 — HW300N60 独立候选迁移

## 1. 权威、状态与改动边界

本候选依据 [HW300N60 规格](<MECHANICAL_LIMITS_SPEC_V2_HW300N60.json>)：用户确认 **全伸展孔中心距 200 mm、行程 60 mm、全压缩 140 mm、标称 300 N**；主动 hip/crank 及 drive follower 无独立角度盒。旧 400 N 候选及旧上界恢复值均为已封存历史，不再作为当前硬件数据。

`hardware_spec_status="CONFIRMED"` 仅表示尺寸和标称力已获用户确认；`force_curve_calibrated=false`、`damping_calibrated=false` 单独保留。新包是配置完成的候选，不是目标 PhysX/100 Hz 反馈已验收的声明。

本分工只创建 [运动学](<package/kinematics_v2.py>)、[运行时适配](<package/runtime_adapter_v2.py>)、[参数](<package/model_parameters.json>)、[同源骨架](<package/reports/model_manifest.json>)、[运行要求](<package/runtime_requirements.json>) 和本说明六项。资产构建、USD/MJCF/contract 与父代理统一回归由其他分工负责；未改旧 package 或他们的资产。

## 2. 运动学 API 与坐标迁移

```python
from package.kinematics_v2 import (
    leg_configuration, mechanical_delta_bounds, boundary_report,
    check_joint_limits, set_configuration,
)

# Both inputs are ABSOLUTE continuous rotor coordinates.
values, pins_xz = leg_configuration(hip, crank, side="left", check_limits=True)
lo, hi = mechanical_delta_bounds("left")
report = boundary_report("left")
check_joint_limits(values, side="left", tolerance=1e-9)
set_configuration(model, data, left=(hip_L, crank_L), right=(hip_R, crank_R))
```

旧函数第二输入是 difference；新函数第二输入是 **绝对 crank**，调用端需明确迁移。`delta=crank-hip`，主动轴与两个 follower 保留原始多圈值；在 hip-local 坐标使用原中性骨架、杆长和有向圆交支路，再整体旋转，不独立 wrap 两个主动轴。

`check_limits=True` 检查当前机械等效约束与 neutral 连通支路，不读取旧 operating window。`check_limits=False` 仅作显式数学诊断；不可达或奇异闭链仍报错。`set_configuration` 先核验两腿和实际 MJCF 范围，再更新对应 qpos、只调用 `mj_forward`；不抬 root/落轮、不 `mj_step`，不把数学闭链等同实体无碰撞。

### 一次新规格几何求根结果

| 项目 | 左/右结果 | 含义 |
|---|---:|---|
| 机械差角下界 | -1.0863195404360622 rad | 原 CAD 低折止挡 |
| 机械差角上界 | +0.49192233306644084 rad | 200 mm 全伸展界，非旧 `.85` |
| 上界初始 bracket | [0.25, 0.5] rad | 少量倍增后有界二分 |
| 上界激活约束 | gas_slide:upper | slide = 0.020639441090129412 m |
| 低折 eye length | 左 152.60587454900532 / 右 152.60587454900526 mm | 机构止挡先于气缸全压缩 |
| 真气缸范围 | 140–200 mm | slide [-0.039360558909870585, +0.020639441090129412] m |

原旧 metadata 的 rocker 下界比同源 CAD 反解高 2e-7 rad；新规格使用 **-0.7828279184955527 rad**，因此本次下界 shift=0、无需旧候选的局部数值偏移。140 mm 是气缸下界，不把 CAD 低折时的约 152.606 mm 冒充气缸最短。

求根谓词使用 1e-12 SI 容差，二分宽度 2e-13 rad；报告的上界 eye 约 200.000000001 mm 是数值容差，不是额外硬件行程。API 默认约束容差为 1e-9 SI。

旧截图右腿 hip=-0.33050、crank=0.357203，delta=0.687703，超过新上界；其同源 eye≈208.153908265 mm 比确认行程多 8.153908265 mm。默认 `leg_configuration` 会抛 `ValueError`，不会改锚点、加行程或硬塞通过。该旧姿态的父代理统一回归尚未在本分工重复执行。

## 3. Gas 力近似与尺寸分层

全部配置读取 [参数](<package/model_parameters.json>)，源值来自所引用的 HW300N60 规格，不在 Python 中硬编码旧 400 N、旧 target 或旧 slider 上界。

- 约定 **全伸展时 300 N**；近似 `F=k*(target-slide)-d*slide_velocity`，正负作用于连接两端。
- k=2000 N/m、d=3 N·s/m 是沿用工程等效值，**不是新 300 N 气弹簧实测曲线或阻尼**。
- 两侧 slide target=0.1706394410901294 m；这不是 eye length。
- 零速度全伸展 300 N、全压缩 420 N，后者是该线性近似推算值，不是独立硬件测量。
- 新 target 与 140–200 mm gas 范围由资产分工写入 USD/MJCF/contract；适配器只核验一致性，不重写力模型资产。

## 4. 显式 pre-build 接入

下面仅为部署模板，未在 Isaac/PhysX 中运行：

```python
# Start a NEW process; before importing the selected source task.
from package.runtime_adapter_v2 import prepare_environment, apply_runtime_cfg
receipt = prepare_environment(opt_in=True)

import selected_mod4_task as task  # existing deployment chooses the real module
cfg = task.SelectedEnvCfg()       # existing deployment chooses the real cfg
report = apply_runtime_cfg(cfg, task, prebuild=True)
# Construct the environment only after checking the receipts.
```

1. `prepare_environment` 要求显式 opt-in、CONFIRMED 规格及运行选择开关；核验本候选 USD 存在、contract 范围与 gas law 一致，拒接已导入的 MOD4 task。
2. 本包选择资产路径来自适配器自身目录，不依赖仓库绝对路径。source/provenance 的绝对路径只是出处记录，不是运行时读取依赖。
3. 把 `RM_DIFF_MIN/MAX` 覆盖为新几何端点；生成的新动作子类也不读取旧 `.85` 默认和旧训练 soft inset。
4. `apply_runtime_cfg(...,prebuild=True)` 是调用者对 env 尚未创建的明确声明；函数检查 live handle/重复适配/合同与资产对应，不声称能发现任意外部 live env。只改新 cfg，不 monkeypatch 原 task 或运行中的 articulation。
5. 实际设置 `sim.dt=.0025`、`decimation=8`，即 50 Hz policy；TGS32/4、closure 每环境 reset 10 mm、mimic .01 rad。旧 source 可能不读取 `RM_POLICY_HZ`，故不能仅靠环境变量宣称时钟已应用。

### 延迟动作 ABI 与共同多圈

`make_mechanical_action_class(task_module,soft_delta_window=None)` 创建原 `DelayedJointPositionAction` 的子类。仅覆盖 `process_actions`：显式调用原 `_DelayMixin.process_actions`，跳过旧 Delayed 类的差角投影；原 mixin 的 `super()` 仍进入原 base action 的 scale/default offset。delay queue、hold/resample、reset、apply_actions 与电机反馈调用路径继承原实现。

每腿仍是 crank,hip 顺序。先按当前 `crank−hip` 为目标 `raw_delta` 选择最近的 `2*pi` 等价表示，再投影到新机械区间；随后按当前hip为两个目标共同添加同一个 `2*pi*k`，不独立wrap两轴。原始delta直接钳位会把目标hip=3、crank=−3误投影到低折止挡，父源码检查已发现并修正；修前源码留在attempts，未当作SDK运行失败。四 leg position + 两 wheel velocity 的 6 维接口、35 维 raw/history、网络、reward、D0–D7 DR 和训练预算均不改。训练软窗口默认 `None`；显式给定时只与机械区间取交集，不修改物理范围。

## 5. 验收账本

- [x] 一次内存编译两份 Python，未生成 pyc。
- [x] 一次有界新几何端点求根/side；未做姿态网格、动态仿真或大规模 CPU 测试。
- [x] 同源 neutral canonical SHA256 保持 `d445410780f83cdd3a4332f5295093b4cbb42674a5aa1bfa96bd4a529b9bd8e9`。
- [x] 源码气弹簧范围/力参数取可替换 sidecar，硬件确认与力曲线标定状态分列。
- [x] 父统一完整MuJoCo3.14模型实编译、USD实际值与单一SI spec对比等100项检查通过；共同±2pi、CAD stop、140–200mm/300N端点、旧208mm截图拒绝、mesh依赖/质量等已实测。另0.3秒隔离机制CPU动力学有限，最大闭链误差约.171mm<原10mm（重力暂置0诊断，未改资产重力）。见VALIDATION.json。
- [x] 新runtime目标层Torch CPU源码ABI stub 9项通过：显式opt-in、旧RM_DIFF窗口替换、原delay/scale一次调用、原apply/reset继承、输入不变、common-turn、跨±pi相对角、真实机械上下界。见RUNTIME_TARGET_CPU_VALIDATION.json；明确不是Isaac/PhysX或100Hz反馈验证。
- [ ] 目标 Isaac/PhysX class ABI 与 closure/mimic 行为；实际 100 Hz feedback binding。此适配不实现或假称验证外层反馈 hold。
- [ ] 新硬件全力曲线/阻尼、真实实体接触及全转干涉标定。

未启动 SDK、GUI、GPU、训练、旧权重/旧 raw 或 Git 写操作。旧专家没有自动晋升为新 D0 plant 专家；数学可解、实体接触、动力学稳定与策略性能分别记账。
