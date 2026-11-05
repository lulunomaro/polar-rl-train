# MOD4v2 P0：运动学与运行时迁移

> **已被新硬件事实取代的历史 gas 候选，非发布就绪包。** 用户 2026-11-05 14:42 新给定 300 N / 60 mm 行程 / 200 mm 中心距；中心距定义与完整力曲线待独立 HW300N60 规格确认。下面的旧 400 N / 上游 slider 数值仅记录此前候选的历史求根，不作为新硬件事实。运行时选择已加硬件规格状态门槛；本目录资产未据此重写。连续主动轴、同源运动学、原 delay ABI 与旧差角投影移除这些确定代码可复用。

## 状态与边界

这是独立 v2 包的 **opt-in / pre-build 适配代码**，不是 live articulation 或现有训练进程的热补丁。旧资产、旧代码、Registry、训练预算、PPO 网络、35 维 raw/history、actor 权重、reward 与 D0–D7 DR 均未在本分工中改动。

- [共同规格](<MECHANICAL_LIMITS_SPEC_V2.json>)：CAD 下止挡与被动单侧约束是一组等效止挡，不声称新建了 part145 的实体网格接触。
- [运动学](<package/kinematics_v2.py>)：读取 [v2 参数](<package/model_parameters.json>) 与 [同源中性骨架](<package/reports/model_manifest.json>)，无 simulator 的 import-time 副作用。
- [运行时适配](<package/runtime_adapter_v2.py>) 与 [运行要求](<package/runtime_requirements.json>)：显式选择新资产，保留原动作队列、hold/resample/reset、base action 的 scale/default offset，以及原 apply_actions/电机反馈调用路径。
- 当前分工的实际执行仅为内存语法编译、少量几何端点求根及一次源数据微差定位；未启动 Isaac SDK、GUI、GPU、动态仿真、训练或旧 PT/raw，也未写 Git。

## 1. 新运动学 API：第二输入现在是绝对 crank

```python
from package.kinematics_v2 import (
    leg_configuration, mechanical_delta_bounds, boundary_report,
    check_joint_limits, set_configuration,
)

values, pins_xz = leg_configuration(hip, crank, side="left", check_limits=True)
lo, hi = mechanical_delta_bounds("left")
report = boundary_report("left")
check_joint_limits(values, side="left", tolerance=1e-9)
set_configuration(model, data, left=(hip_L, crank_L), right=(hip_R, crank_R))
```

这与 [旧运动学:21–43](<../traditional_control_20261101/kinematics.py#L21-L43>) 的 `hip,difference` 输入不同；调用端需明确迁移，别把绝对 crank 再加一次 hip。

- `delta = crank - hip`；在 hip-local 坐标解析原中性骨架的两个固定有向圆交支路，再整体旋转。返回主动轴及两个 drive follower 的原始多圈值；不把它们各自 wrap 到 ±π。
- 被动角使用与 neutral 连通支路的相对角坐标；没有替换中性几何、杆长或装配手性。
- `check_limits=True` 检查 v2 真机械等效约束与该连通差角支路，不读取旧 operating window。`check_limits=False` 仅供显式诊断，连杆不可达仍会报错。
- `set_configuration` 先核验两腿，再更新对应 qpos 并 `mj_forward`，不 `mj_step`、不自动抬 root/落轮、不宣称已消除实体碰撞。传旧 v1 MJCF 时，其范围冲突仍会报出，不静默跳过。

### 本次实际求得的差角端点

左右相同（有限浮点精度下）：

| 项目 | rad | 依据 |
|---|---:|---|
| 原 CAD 记录下界 | -1.0863195404360622 | source mechanical_stop |
| v2 约束交集有效下界 | -1.0863191309262838 | 原 rocker 单侧值及同源骨架的交集 |
| v2 有效上界 | +0.8499999722946541 | gas_slide 恢复上界 0.03520333394408226 m 的求根 |

必须保留这个来源细差：在原 CAD 差角处，同源骨架算得 rocker = -0.7828279184955527/-0.7828279184955522 rad，而规格沿用的止挡元数据是 -0.7828277184955518 rad，差 **2.000000009e-7 rad**。代码既未偷偷改规格，也未用宽容差掩盖，而是在 CAD 附近局部 bracket+bisection 求交集，差角下界因此向内 **4.0950977831e-7 rad**。这不是旧 50e-6 inset。

上界由 `[0.5, 1.0]` bracket、原连续支路及 gas bound 独立算出，代码没有把旧 `.85` 当物理常数。结果恰接近 `.85`，**不**增加硬件实测证据：恢复的上游 slider bound 本身仍是既有资产声明，最大硬件行程待标定。端点判定使用 1e-12 SI 数值容差；API 范围校验默认 1e-9 SI 容差，不是机械软余量。

## 2. 正确的离线接入顺序

以下片段是集成模板，不会由导入自动执行，也没有在目标 Isaac/PhysX 中运行：

```python
# Start a NEW process. Do this before importing its source MOD4 task module.
from package.runtime_adapter_v2 import prepare_environment, apply_runtime_cfg
receipt = prepare_environment(opt_in=True)

import selected_mod4_task as task  # deployment chooses its existing task import path
cfg = task.SelectedEnvCfg()       # deployment chooses its existing config class
report = apply_runtime_cfg(cfg, task, prebuild=True)
# Only the deployment owner constructs an environment after inspecting the receipt.
```

1. `prepare_environment(opt_in=True)` 核验新 USD 存在、合同单侧/无界语义及原 gas law，一律把 `RM_MOD4_USD` 指到本包的 `assets/robot.usd`。旧 task 已导入即报错，要求全新 pre-build 进程。
2. 它覆写继承来的 `RM_DIFF_MIN/MAX` 为几何端点；特别防止旧 `.85` 默认或训练 min 从环境变量回流。新动作本身也完全不读取这两个旧变量。
3. `apply_runtime_cfg(cfg, task, prebuild=True)` 要求已准备环境、loaded task 的 USD/contract 与新包一致；不接收具有 live manager/physics handle 的对象，不重用已经适配的 cfg。`prebuild=True` 是调用者对“尚未创建 env”的明确声明，而非检测任意外部 live env 的神谕。
4. 仅复制并修改新 cfg 的资产、clock、solver、原 termination thresholds 与 leg action class；不 monkeypatch 原 task 的全局类、旧配置或任何 live action manager。
5. 实际设置 `sim.dt=.0025`、`decimation=8`，即 50 Hz policy；不是仅设置可能被旧 source 忽略的 `RM_POLICY_HZ`。TGS32/4，closure reset 10 mm、mimic .01 rad。

### 动作 ABI 与多圈目标

[原动作:912–991](<../e3_fudan_recovery_alignment_20261104/original_runtime_refs/mod4_task.py#L912-L991>) 是 ABI 模板，不是目标 v2 的实测凭据。

`make_mechanical_action_class(task_module, soft_delta_window=None)` 创建原 `DelayedJointPositionAction` 的子类，继承原初始化，只在 `process_actions` 显式调用原 `_DelayMixin.process_actions`，跳过旧 Delayed 类的差角投影，再投影到新机械差角范围。原 mixin 的 `super()` 仍进入原 `JointPositionAction`，所以 delay/hold/resample、scale/default offset、reset 与 apply_actions 路径保留。

每腿 policy 顺序仍为 **crank, hip**。先计算原 pair 的 delta 并按机械区间投影，再将 hip 和 crank **共同**加同一个 `2π*k`，其中 k 使 hip 靠近当前 hip；不会独立 wrap 两轴而破坏相对周数。四 leg position + 两 wheel velocity 的 6 维接口不变。

训练软窗口默认关闭。确有独立训练需求时，调用 `apply_runtime_cfg(..., soft_delta_window=(lo, hi))`；它仅取与机械域的交集，不扩大机械域，且不改 USD/MJCF 的物理限制。

## 3. 气弹簧：行程与力曲线分层

只恢复几何 slider 上界，不通过换气弹簧力来伪装修复限位。

- native contract：stiffness = 2000 N/m，damping = 3 N·s/m，左右 target = 0.22063944109012937 / 0.2206394410901294 m。
- target 是原资产的 slide spring target，不将其擅自解释为中性 eye length。400 N 是标称标签，不是每一行程都恒定 400 N。
- 旧本地 MJCF `springref=.2` 与 native target 存在差异；v2 MJCF 需由资产分工修正到 native 值，不能称“保留了旧 MJCF 原力”。
- 旧参数中的 700 N / 3500 N/m 未混入本包。电机参数取当前 2c 原合同，中性骨架取同源传统控制 manifest；骨架 sidecar 不充当质量/惯量的权威。

## 4. 验收分层 / 待运行

- [x] 两份新 Python 源码内存语法编译；无 pyc。
- [x] 同源 neutral skeleton 原值复用；canonical SHA256 `d445410780f83cdd3a4332f5295093b4cbb42674a5aa1bfa96bd4a529b9bd8e9`。
- [x] 原 CAD 微差定位及左右局部机械边界求根；完整数值记录在 [v2 参数](<package/model_parameters.json>)。
- [ ] 父代理统一执行：v2 MuJoCo compile、用户姿态、common-turn、stop/范围、资产不变量与便携性最小回归。本分工未重复运行。
- [ ] 目标 Isaac/PhysX class ABI、closure/mimic behavior、真实 100 Hz feedback binding 验证。此适配保留原反馈调用，但 source action 文件本身没有证明外层 100 Hz hold；不能把配置要求当完成验证。
- [ ] 硬件最大行程、其他实体上止挡、全转路径的实际干涉标定。

旧专家没有自动晋升成 v2 专家；旧策略在改变后的 D0 plant 上的性能仍需另行评价。数学闭链可解与实体无碰撞、实际止挡和整圈轨迹可达分别记账。
