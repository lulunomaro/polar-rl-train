# MINIHOP_AUDIT_V2 — 全接触合力的只读 grading

**本交付只有新审计代码、synthetic tests 与真实 fullmodel 的 0-step boot 准入；episode/积分步为 0。** 旧 R39、v1 分数、controller 与所有旧 sealed/blocked 组件保持原字节。当前 PH4 cutoff 排除本 v2；PH5/后续以及父负责的 DR4221..4224 均 pending。

## 1. 改动与合同

- [初始合同](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/GRADING_CONTRACT.json>)的阈值全程未变：`total = math.fsum(max(0,fn) for every world↔robot contact)`，**先全量合计** main/guide/hard，再用 `total <= 1 N` 连续 40×0.0005 s 定义 operational air。没有逐点 1 N 过滤；三点各 0.4 N 的 1.2 N 支持不会算 air。
- environment 定义为 `geom_bodyid==0`，不依赖 collision mask；仅一个端点是 environment 时计入 robot 外部接触。self/world-world 的 net external contribution 为零，但它们的 force6/frame/position 仍须 finite。
- 首次 air 同时报 interval start 和确认 post-time；首次 landing 取其后第一条 total>1 N 的行，并保存**所有正力接触点**及完整 environment 列表，包括每点低于 1 N 的接触、身份、坐标与力。负法向原值保留，normal aggregation 按合同取 max(0,fn)。
- [schema](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/schema_v2.py>)和[grader](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/contact_grade_v2.py>)对 nonfinite/shape/stage/aggregate overflow 明确 instrumentation fault 并锁存。错误不是零力样本；仅在 finite schema 与 stream append 都成功后提交 air/landing 状态。恢复需新实例。

## 2. 同一 physics stage，而非混合 post root

[flat/rm 桥证明](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/BRIDGE_AST.json>)证明两个新完整 `apply_torque_request` AST 与旧 mini-hop v1 相同；移除原来的两个 observer hook 后分别与旧 V3/rm_buffer 完整 AST 相同。hook 参数未增加，也没有 raw-servo hook。

1. `_capture_drivepoint(actual_dq,bounded)` 位于原 `d.ctrl`/`mj_step` 之前，复制同一时刻 dq6、bounded tau6 和 pre root qpos，不改输入/model/data/DR/IMU。
2. `_grade_minihop_sample()` 在原 `mj_step`、tick 与 IMU accumulation 后读取 contact force/geometry、精确 mesh、xmat/subtree_com 的已刷新 dynamics cache。对于冻结的 implicitfast 模型，这些是本次 **pre-integration evaluation**；它们的 stage time 与捕获 drivepoint 一致。
3. `d.qpos[:3]`/`d.time` 是单列的 root-post；不会拿 post root 去宣称 pre contact/mesh。跨 hook stage interval 与连续 tick 均检查。

初轮曾把私有 R/COM cache 读在 capture，人工复查发现它会早一个 dynamics cache；已移到 post-grade 读取，并新增模拟 cache refresh 测试。初轮源/回执完整留存，见[修订记录](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/ERROR_REPORT.md>)。这个 staging 约定绑定当前冻结模型/桥，未扩成任意 integrator 的通用断言。

## 3. 私有 force/mass 诊断

`private_contact_diagnostic` **仅在 physics rows 内**：

- `F_on_geom2_world = ct.frame.reshape(3,3).T @ local_force[:3]`；robot 为 geom1 则取反。包括 normal 与两轴 friction，按 world↔robot 全量相加；self/world-world 不加入净外力。
- `actual_model_body_mass_sum_kg` 读取 DR 后当前 `m.body_mass.sum()`，不用缓存 `self.mass`。
- 可用时读取同 pre-cache 的 root rotation 与 chassis subtree COM；缺失为显式 `None`，不是零阵/零向量。

它只叫 **contact-only external force/mass diagnostic**。其他外力、阻尼等尚未核实，未命名完整 trueCOMproper；normal-only air 也不是可信 airborne sensor。未进入 public SensorPacket、controller、FSM、MPC 或任何 cue/confidence cap。

## 4. 已发生的资格事实

| 新证据 | 结果 | 明确边界 |
|---|---:|---|
| [unit01](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/UNIT_RESULT_01.json>) | 917 checks / 0 failure | 当时测试未检测旧 cache 读取位置；保留，不冒充最终源 |
| [当前 unit02](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/UNIT_RESULT_02.json>) | **936 / 0**，7组 | mock contactForce 284 次；mj_step=0，mj_forward=0，无 fullmodel 构造 |
| [真实 boot01](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/BOOT_ADMISSION_01.json>) | **39 / 0**，flat+rm | 六种 integration entry points=0；初始化 mj_forward=60；两模型 tick/time/physics grade rows=0 |
| [runner AST](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/RUNNER_AST.json>) | 完整 control loop AST 相等 | sensor/timer/controller/processed-target/driver 链未换；不宣称 walltime 相等 |

Unit 覆盖小点合计、guide 支持、精确 20ms/1N 边界、首次 landing 身份、friction/geom 反序符号、actual mass≠cached mass、cache refresh、各 stage clock/NaN/Inf/shape/overflow/schema、只读输入/plant 与 streamed prefix。保存的[synthetic ERROR](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/unit_attempt_02/synthetic_ERROR.json>)明确不是 episode 结果。

Boot 使用独立 seed314159、nominal=False；flat/rm 均 nq37/nv36/nbody32/nmesh279，ngeom 分别312/326。两次实际 mass=14.670646607738608 kg，本次恰好与 legacy cached mass 相等；不夸称真实 boot 出现二者差异。差异读取另由 unit 的 actual20/cached999 合成验证。只生成默认 disabled 的一次 0时刻 command，未调用 apply、未给 ctrl 赋值或制造 post-time，未产生 trajectory/grade。

## 5. 源闭包、prefix 与未来使用

- [冻结清单](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/SOURCE_FREEZE.json>)：1078 旧文件 +26 源引用 +279 个实际 XML mesh asset；最终[验证](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/VALIDATION.json>)核对字节。旧 R39 只 hash，未 parse/regrade，旧 preflight 未重跑。active ROOT world_leg 未改/未导入。
- [源闭包](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/SOURCE_CLOSURE.json>)和两个 boot SOURCE_PREEXEC 记录新 observer/runner 与原模型/old libraries。实际 XML 有279 meshes；不是拿旧277条统计替代当前依赖。
- [runner](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/run_minihop_case_v2.py>)继续用原 StreamedRows：控制与 physics 文件逐行单 producer、原 bytes/SHA；[provenance](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/provenance_v2.py>)在错误时另 hash **实际留下的 raw prefix**，不重建、不删截。若 I/O 中断留下额外 raw suffix，receipt 的 actual/producer 比对会暴露它，不把它伪装成成功行。
- [默认 disabled prototype](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/PROTO_DISABLED.json>)及[使用边界](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/BUILD.txt>)供父随后冻结新配置；此委托没有运行 runner/DR4221..4224，没有更新任何旧分数。
- [源码 overlay ZIP](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/minihop_audit_v2_source.zip>)依赖原冻结 workspace/资产，并非独立模型包。完整文件/哈希见[INDEX](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/INDEX.json>)与[MANIFEST](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/MANIFEST.json>)。

**Operator 默认 disabled；contact/FSM/MPC 许可与置信上限不变；0 新 episode/GPU/Git/agent/blocked-IO/goal 修改。** 后续 physics、成绩与 cutoff 由父处理，本次不扩张现有阶段结论。
