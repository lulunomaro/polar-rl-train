# MOD4 Isaac 开链资产修复与狗洞任务交接指令 V2

继续推进，但先不要实现狗洞课程和奖励。当前运行报告暴露了两个模型级问题，必须先修完并重新验收。

## 1. 机械限位处理需要修正

不要在 `thigh↔crank` 之间凭空添加猜测的小方块。STEP 精确 B-Rep 已确认：

- 固定限位块：`part_145`
- 首先接触的运动件：`part_124`（rocker）
- 同时接近接触：`part_134`（shin）
- `source_difference = -0.6363195404360622 rad`
- `packaged input_difference = -1.0863195404360622 rad`

对应被动关节机械边界：

- `rocker_pin_min = -0.7828279184955518 rad`
- `coupler_pin_max = +0.9027785273324023 rad`
- `knee_min = -0.7613787030122099 rad`
- `distal_pin_max = +0.8152830434591931 rad`
- `gas_pin_max = +0.15599963671374795 rad`
- `gas_slide_min = -0.02675468436086534 m`

当前写入的 `rocker_pin_min=-0.812828`、`knee_min=-0.791379`、`gas_slide_min=-0.056755` 已经越过真实限位。尤其 gas slide 多放了约 30 mm，这是把统一的 `0.03` 同时错误用于弧度和米制坐标。

必须改成：

1. `mechanical_stop` 使用上述 B-Rep 数值。
2. 训练软限制位于机械限位内侧：角度保留 `0.002～0.005 rad`，滑动关节保留 `0.0002～0.0005 m`。
3. 对独立 hip/crank 动作执行耦合投影：`crank - hip >= -1.0863195404`。
4. 训练动作下限建议为 `crank - hip >= -1.0843 rad`。
5. RuntimeGuard 直接检查 `input_difference`，不能只检查单个 hip、crank 或 knee。
6. 如果需要真实接触代理，只能依据 `part_145↔part_124/part_134` 的 CAD 表面生成，不能猜测 thigh↔crank 方块。

当前实测 `input_difference=-1.0994 rad`，已越过机械限位约 13 mrad。这一项必须判为 FAIL，不能继续标记为完整运行期通过。

## 2. 345 mm 高度应先按坐标或刚体归属错误排查

不要先删除 `right_side_armor`、`visual_095`，也不要直接判断它们是云台或电池占位。

已验证的正确姿态：

- `hip = +0.450290972128024 rad`
- `crank = -0.6360285683080382 rad`
- `input_difference = -1.0863195404360622 rad`
- `chassis pitch ≈ 0`
- 中央四个导轮接地
- `chassis root_z ≈ 0.178 m`
- 主驱动轮下缘离刚性地面约 `1.80 mm`

该状态下 MuJoCo 全部 277 个视觉网格的包络：

- 实际地面到全模型最高点：`244.934 mm`
- 对 247.2 mm 洞口的名义余量：`2.266 mm`
- 以主轮下切线为 SolidWorks 基准时，腿顶：`223.529 mm`
- SolidWorks 标注：`223.36 mm`
- 差值：约 `0.17 mm`

USD 中出现 `right_side_armor=331 mm`、`visual_095=345 mm`，优先排查：

- free-root 高度或 spawn offset 重复叠加
- MJCF chassis 初始 `pos=0 0 0.337742301121` 被烘焙进 USD 后又被 InitState 叠加
- visual_095 的 local transform 被重复应用
- geom/prim 挂到错误刚体
- 高度审计使用了不同地面零点
- 审计姿态未真正写入主动和被动关节
- USD 舞台单位或上轴转换错误

制作 MJCF↔USD 同姿态包络对比工具：

1. 两边使用相同物理关节值。
2. 中央导轮最低点统一为世界 `z=0`。
3. `root_z≈0.178 m`。
4. 输出全部 277 个 visual 的 part ID、body/prim、local AABB、world AABB、world max_z。
5. 单独输出 visual_095 的 CAD 名称、归属和局部/世界变换。
6. 输出 right_side_armor 碰撞代理中心、尺寸和 world max_z。
7. 检查是否重复应用 0.337742301121 m 初始平移。
8. MJCF 与 USD 对应网格 world AABB 误差必须 `<1 mm`。
9. 包络一致前禁止开始狗洞 PPO。

## 3. 导轮碰撞体保留

34 个碰撞体应包括原 26 个加 8 个导轮解析圆柱。

中央四个导轮：

- `x=±0.048 m`
- `y=±0.1005 m`
- `z=-0.163 m`
- `radius=0.015 m`

前后四个导轮：

- `x=±0.259 m`
- `y=±0.131 m`
- `z=-0.135 m`
- `radius=0.015 m`

要求圆柱轴沿车体 Y，采用较低切向摩擦。水平低姿态下中央导轮接地，前后导轮不得误接触。主轮与中央导轮约 1.8 mm 的高度差属于 CAD 关系，不要强行改成严格共地。

## 4. 重新验收

依次执行：

1. 静态导入审计。
2. 单环境 6000 步硬限位保持测试。
3. 1024 环境至少 1000 步并行 smoke test。
4. 输出 input_difference 最大越界量、最大闭链残差、mimic 最大误差、NaN/solver warning 数量、导轮接触次数、MJCF/USD 包络差、吞吐和显存占用。

验收阈值：

- `input_difference >= -1.0863195404 rad`
- 训练控制目标 `>= -1.0843 rad`
- 最大闭链残差 `<5e-4 m`
- mimic error `<1e-2 rad`
- MJCF/USD 包络差 `<1 mm`
- 低姿态 full height 约 `244.934 mm`
- 无 NaN、无零件散架、无 solver warning

## 5. 通过后继续狗洞任务

通过上述验收后直接实现：狗洞低姿态参考、五阶段 curriculum、顶部净空与非白名单碰撞奖励、左右对称、动作平滑、关节速度/加速度、力矩/功率/温升约束，以及质量、质心、摩擦、轮径、洞高和控制延迟随机化。必须输出最差样本最小净空与通过率，不能只报告平均 reward。

修改继续放在 `incoming/mod4_fixed_20260912/chassis_mod4/`。保持原始交付包、STEP 和 SolidWorks 文件只读。

## 6. 本地可信基准

本包中的本地 MuJoCo 3 秒测试结果：

- 最终 hip：约 `+0.45079 rad`
- 最终 input_difference：约 `-1.08611 rad`
- base pitch：约 `-2.45e-7 rad`
- 最大闭链残差：`8.64e-7 m`
- 最大腿电机力矩：`12.33 N·m`
- 无 warning、NaN 或零件散架

请先完成模型级修复和 1024 环境验收，再开始正式狗洞训练。
