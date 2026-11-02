# ACTIVE_BOX_QP_V3 — feasible primal active-set boxQP

**真实active-bound路径已改善，数学/host阶段；不是完整robotMPC或3ms资格。** 新独立[API](<active_box_qp.h>)/[全f32核心](<active_box_qp.c>)不改原QP1/2 ABI与封存包。无physics、Git、agent、BSP/CAN、ARM运行/WCET。postR16/PH3 pending，不扩PH2结论。

## 问题与输入冻结

解`min .5*z'H*z + f'z, lo<=z<=hi`，n≤16，有限、精确对称的SPD float32 H。输入H不静默平均、不加对角正则；坏shape/box/asym/nonfinite、float Cholesky非正pivot均明确fault。

[来源冻结](<SOURCE_FREEZE.json>)收录530旧文件与实际[H15/f3218cases](<../C_MPC8_NUMERIC_V1/actual_model_vectors.json>)的SHA；H32当double评估cond≈2426.697956。没有import父controller/physics或从随机episode改H。原模型局部zero-yaw/fixed-leg，输入是每轮common torque，不是高速spin资格。

[预算](<NUMERICAL_BUDGET.json>)在新solver结果前写定并保持hash不变：实际主预算64pivots、绝对projectedKKT .002、相对tol0、可行性越界0；诊断预算0/1/4/16/32/64/256。不能把AS pivot数等同CCD sweep数或相同计算时间。

## 算法不是free-only shortcut

1. `z=clip(warm)`；无warm用0再clip。l=u单列固定，不参与release。
2. 完整H Cholesky验证SPD，即使全变量fixed也验证。free-face解`H_FF p_F=-grad_F`。
3. 沿可行方向行进到首个bound，加入blocking constraint；不是把不可行free解直接clip后当最优。
4. free-face满足既定KKT精度时检查active梯度符号，释放最违约非fixed index。
5. 同一全局pivot counter计所有step/release，不做restart、不在phase间清预算，无隐形CCD fallback。
6. fixed32-state exact history检测循环；MAX/CYCLE/NO_PROGRESS/ROUNDOFF等不冒作成功。

[Python proof](<PYTHON_PROOF.json>)93问题×cold/warm共186次全收敛，最坏54pivots。18原问题用封存quantized double oracle；独立75问题包括72固定seed SPD/random与3个active/fixed stress，n=1/2/4/8/15/16、condition classes至1e5。小维oracle穷举active faces，较大用独立SciPy L-BFGS-B +face线性/符号polish，全部重新验double KKT。随机H在结果前定义，不按oracle调整。

## f32 KKT证据，不放宽.002

梯度用32-slot balanced pairwise sum，至多5层加法。每row舍入界预先定义为

```text
B_i = 4*FLT_EPSILON*pairwise_sum(abs(f_i),abs(fl(H_ij*z_j))) + 32*FLT_MIN
free:  abs(g_i)+B_i
lower: max(0,-g_i+B_i)
upper: max(0, g_i+B_i)
fixed: 0
```

只有最大upper≤实际f32 `.002`才CONVERGED/valid1。不是把tol扩成`.002+B`；normal IEEE binary32、round-to-nearest/no-fast-math模型下的保守界。所有valid点又独立double重算精确C输入的KKT。ARM运行时FENV/FPSCR/FTZ未测，不能从对象编译推定。

## 真实active-bound结果（最终attempt02）

| H15组 | cold64 | shifted-warm64 | 最坏pivots cold/warm |
|---|---:|---:|---:|
| free10 | 10/10 | 10/10 | 1 / 1 |
| active或fixed8 | **8/8** | **8/8** | **25 / 54** |
| 合计18 | **18/18** | **18/18** | 25 / 54 |

active cold最多5次release/19次bound hit；warm最多24次release/17次hit，说明确实经过活动面求解与约束释放。75独立stress在64 cold/warm分别75/75。原CCD64 cold仅2/18、256 cold7/18的旧失败证据保持原封存；这里没有据pivot比值宣称速度倍数。

[全部第二轮C输出](<C_RUNS_02.jsonl>)1302配置：910CONVERGED、392诚实非收敛（保留不足预算）。[逐run比较](<RUN_COMPARISON.csv>)/[汇总](<COMPARISON.json>)：0可行性/证书/实际H15预定精度失败。真实active成功点最大z∞误差6.41587e−5、objective gap3.30670e−9、double KKT5.67313e−5，均对精确量化oracle；不把输入量化误差混成迭代误差。

warm是原18人工fixture的“前一quantized oracle平移一格”输入，不是记录闭环warm，更不是保证更快的实际warm轨迹。

## 首轮warm失败没有抹去

[第一轮](<C_RUNS_01.jsonl>)cold18/18，但warm64 **14/18**、warm256 **16/18**，有MAX/CYCLE，valid0/zero z。全部402失败诊断、旧source/binary/log在[旧比较](<revisions/run_attempt_01/COMPARISON.json>)、[旧失败](<revisions/run_attempt_01/ALL_NONCONVERGED.json>)及[迭代trace](<WARM01_TRACE.csv>)保留。

[结构修复说明](<ALGORITHM_REVISION_02.md>)有具体证据：free梯度约1e−6时，病态面把噪声放成数ULP Newton方向；单靠p相对ULP阈值使active错误梯度−.38仍不被释放。attempt02改用**同一预先KKT证书**资格判断free-face stationarity，不改H/f/box/warm/tol/预算，不冷restart。所有旧失败点仍交付，不把最终通过回写成首轮成功。

## 真正内部earlyabort

Caller提供nonblocking monotonic clock/context/相对uint64预算。检查点在full/face Cholesky每cell、gradient每row、triangular每row、line/iteration内，并出口再检。时间通过`now-start`比较，不计算可能overflow的`start+budget`。clock rollback/wrap明确CLOCK_ERROR。

[531单测](<unit_run_01.log>)零失败，[逻辑时钟轨迹](<EARLY_ABORT_CASES_01.csv>)证明：

- 完整H15 Cholesky仅执行**1/120cells**即deadline/valid0，不是factor结束才看。
- face factor仅执行1cell即停；gradient/triangular/line/iteration内均能停。
- 已有精确解但出口过期仍zero output；rollback/UINT64 wrap/nearMAX与MAX预算边界均检查。
- bad input、asym、非SPD、bad box、alias、tiny-tol roundoff/no-progress、finite中间overflow也明确fault。

每个非CONVERGED都`valid0,n/z/cost/KKT0`，只保留status/work counters。workspace的私有iterate只作为[失败诊断](<ALL_NONCONVERGED.json>)，不是可接受输出。上层须自行fallback/失能；这个库不发送电机命令。

**时间范围：**相对窗口从START clock采样开始；之前的参数/alias检查与workspace清零属于固定API准备开销，调用者仍需管理完整周期绝对deadline。clock回调必须只读观察、非阻塞、不可actuate。内部检查是cooperative checkpoints，不是preemption，也不证明整机/ARM3ms。未新做host时延基准来包装实时资格。

## 内存、构建与封存

固定caller-owned workspace，核心无heap/VLA/f64/可变全局状态；host ABI下workspace5240bytes、result184bytes，非实测ARM stack。输入数组与workspace/result分离；本独立API不允许warm直接alias result.z，需显式copy。

严格MinGW C99 O2/Wall/Wextra/Werror/pedantic/Wvla/no-fast-math/ffp-contract=off/SSE2通过；第二轮21596契约检查/0失败。[C++ extern-C](<cpp_run_01.log>)真实active2-bound smoke通过。宿主重启后只核对已完成02/531落盘证据，没有为补档重跑它们；新增CPP/ARM是先前未完成的验证。

新[ARM命令receipt](<BUILD_RECEIPT.json>)/[ELF与宏检查](<OBJECT_SUMMARY.json>)：M4/M7 SP-hard **2/2新对象**，14684/13472bytes；armclang6.10.1，binary32/Thumb/v7E-M/VFP args检查通过。仅`-c`，无BSP链接/BIN/板、ARM运行、FPU状态或WCET结论，对象长度不是最终flash/stack。

[ERROR_REPORT](<ERROR_REPORT.md>)、[INDEX](<INDEX.json>)、[VALIDATION](<VALIDATION.json>)、[MANIFEST](<MANIFEST.json>)给全部attempts与主件SHA，并复核旧530文件/实际H15来源不变。此组件不含状态/接触/耦合功率约束，也不等于选定完整MPC架构或机器人控制资格。
