# Portable Box-QP v2 Fast — 可选free shortcut，受限路径仍诚实回退

**仅数值内核，未部署机器人/MPC/BSP，也不决定最终控制架构。** 原C1与真实H V1不足报告保持封存；本版只优化free问题，未宣称完成真正受限QP优化。

## 变更与接口

- [boxqp_fast.c](<boxqp_fast.c>)从封存C1源精确派生，原件SHA `53ad5bf9f447ea7a7a500a809f0fcdcca8973ffeb8afc4a16a2574ed05c2cdff` 不变；派生记录与工具见[DERIVATION.json](<DERIVATION.json>)、[derive_fast_source.py](<derive_fast_source.py>)。
- [boxqp_fast.h](<boxqp_fast.h>)复用原problem/options/workspace/result **ABI，不增改旧结构字段**。原 `bqp_solve` 仍CCD-only；新 `bqp_solve_fast(...,enable_free,optional_info)` 显式选择新路径，enabled只接受0/1。
- 编译 **boxqp_fast.c替代boxqp.c，勿同时链接两份kernel**；新文件同时提供兼容的dense/base入口与新fast入口。旧公共头是只读依赖。
- workspace仍 **2448 host bytes**，复用gradient/z作三角解scratch；无heap、VLA、共享缓存或跳过验证。info必须和输入/workspace/result分开。

流程：完整输入/对称/SPD验证并取得L → `L*y=-f`、`L' z=y` → **不clip free解** → 逐项原box检查 → 直接用原H/f重算cost与投影KKT → 只有可行且KKT≤原tol才选择free初始候选。否则恢复原clipped warm并走原CCD；可选free中间溢出也只表示优化失败，不额外破坏原来可解的固定box问题。

`free_selected`只是候选来源，不等于按时收敛或允许执行；最终result/status仍是唯一权威。没有改变boxQP约束范围，仍不含状态/接触/耦合功率/电热约束。

## 时钟与失败契约

- absolute uint64 clock在shortcut之前、之后、每sweep检查点和callback之后检查；包含已发生的输入/SPD/shortcut工作与callback耗时。它是checkpoint，不是可抢占硬中断或WCET证书。
- shortcut刚满足KKT但deadline已到，返回DEADLINE、converged=0；clock倒退丢弃候选/输出零。progress只能记录，不直接驱动。
- max_sweeps只数CCD扫描；enable=1时max_sweeps=0仍可能做有限三角解，并在0-CCD-sweep成功。0sweep不是零计算时间。
- 不跳过NaN/shape/box/SPD/alias检查，不把不可行free解clip后冒称最优，也没有扩大tol。

## 数学与接口验证

1. **新kernel的base/disabled路径**直接复用旧67个合成fixtures与原自测源，**4166断言/0失败**，stdout指标与C1一致；不是为旧文档命名重跑旧二进制，而是在测新实现。[原日志](<base_selftest_attempt_01.log>)。
2. **enabled自测**同67数学fixture，另测free可行但KKT过紧应回CCD（实际触发3例）、free溢出而固定box仍可解、输入/diag alias、warm=result.z、shortcut前后expired、callback超时和clock倒退：**1110断言/0失败**。[fast_selftest.c](<fast_selftest.c>)、[日志](<fast_selftest_attempt_01.log>)。
3. 新fast extern-C入口由C++11调用，链接单独C99编译的object，通过0-sweep smoke。[CPP源](<fast_cpp_smoke.cpp>)、[原日志](<cpp_smoke_01.log>)。

## 相同真实H18题：只改善free，保留active不足

共享[真实H V1输入/oracle](<../C_MPC8_NUMERIC_V1/actual_model_vectors.json>)，SHA `250aa77201fd616dec68f8ee932f79ac3da6511092d9fae0b868a0bbc4f70a5a`；Hcond2≈2426.7，15标量输入/9维lag预测，参数没有重生成或改变。tol仍.002。warm仍是前一人为fixture oracle平移，不冒充闭环warm收益。

| budget | C1 cold收敛/18 | V2 cold/18 | C1 synthetic warm/18 | V2 warm/18 | V2 active cold收敛/8 |
|---:|---:|---:|---:|---:|---:|
|64|2|11|2|11|1|
|256|7|16|6|13|6|
|4096|18|18|18|18|8|
|20000|18|18|18|18|8|

- 10个free case ×2起点×4预算，**全部80组合free selected且0 CCD sweep收敛**。free类double复算最大KKT约2.3587e−5，首输入对quantized oracle最坏差5.79225e−6Nm。
- **全部64个active组合的z/sweeps/cost/KKT/status与C1逐项bit相同**：[CROSS_VERSION.json](<CROSS_VERSION.json>)。这是明确的“受限路径没变”证据，不是拿漂亮nominal掩盖失败。
- 144run中 **123 CONVERGED / 21诚实MAX_SWEEPS**；196951契约检查0失败只证明接口/可行性逻辑，未把21个MAX改成成功。[原C输出](<C_RUNS_01.jsonl>)、[对照表](<BUDGET_SUMMARY.csv>)。
- 剩余active扩预算最坏cold439/warm471 sweeps。扩预算不是原deadline内成功。256 cold仍有2/8 active不足，warm5/8不足，受限solver/提前回退仍是下一独立工作。
- 总z∞误差在64 cold可达.124381、256 cold .0117101，来自尚未收敛的后续horizon坐标；此组active首输入恰好已在正确bound附近，**首输入看似准确也不等于整个QP达KKT**。
- V1的2个扩预算f64 KKT同tol边界记录来自1个free warm题，shortcut后不再出现；当前144run没有C-converged但double同tol不满足的记录。未改V1历史状态。[COMPARISON.json](<COMPARISON.json>)保留全量误差。

## Host耗时单列，绝不是ARM WCET

[host_benchmark.c](<host_benchmark.c>)为**host-only**，Windows QueryPerformanceCounter不进入portable kernel。冷数值启动、每call完整验证/Cholesky，不缓存；每题40次、72行、2880call，progress/clock callback与日志关掉，info=NULL。共享host且重复硬件cache已热，不含caller模型构造/通信/ISR；观测max也不是WCET。

下表是**各case均值的中位数**，不是最坏时延：

| budget | free CCD-base → fast (µs) | active CCD-base → fast (µs) |
|---:|---:|---:|
|64|85.99 → 4.39|86.66 → 87.18|
|256|341.32 → 4.39|292.11 → 301.76|

free确实省掉CCD；active多一次三角尝试，未变快。完整mean/min/max（含调度噪声）与各组接受计数见[HOST_TIMING_01.csv](<HOST_TIMING_01.csv>)、[HOST_TIMING_SUMMARY.json](<HOST_TIMING_SUMMARY.json>)；不能用它替代ARM、完整控制链deadline或PHY闭环验证。

## 封存与构建

所有新增物只在本新目录；没有parent import/物理/MjData/step/板/CAN/SSH/Git/新包或agent。真实H来自指定V1局部模型，不把父后续R09等新控制器的运行结果归给本C内核。源码/原日志/比较/失败及旧物不变证据见[ERROR_REPORT.md](<ERROR_REPORT.md>)、[INDEX.json](<INDEX.json>)、[VALIDATION.json](<VALIDATION.json>)、[MANIFEST.json](<MANIFEST.json>)。

```powershell
# 仅host strict C99；firmware库不编入host_benchmark.c/Windows头。
& 'C:\MinGW\bin\gcc.exe' -std=c99 -O2 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse boxqp_fast.c fast_selftest.c -lm -o fast_selftest_host.exe
.\fast_selftest_host.exe
```

GCC/g++为已有MinGW6.3.0；SSE2只用于host binary32验证。Python数值对照复用已有Python314 NumPy2.4.5，不import父控制模块。后续真正受限算法、缓存或ARM移植应另版本与新证据，不回写本包或C1。
