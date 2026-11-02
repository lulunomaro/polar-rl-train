# Portable MPC Box-QP v1 — 独立数值内核

**这是n≤16的boxQP求解器，不是已部署机器人MPC。** 未来8-state/单个共同轮扭矩/N=15是父任务的候选建模方向，本包没有机器人Hessian、状态估计器、动力学、闭环或最终架构选择。

## 交付与结果

- [boxqp.h](<boxqp.h>) / [boxqp.c](<boxqp.c>)：纯C99 binary32，调用方固定workspace，无heap、VLA、全局可变状态或外部数值包。
- [C自测](<bqp_selftest.c>) **4,166次断言 / 0失败**，246个progress事件；[原始日志](<selftest_attempt_01.log>)。fixture是24个1D解析、36个2D边/角/内部枚举、6个n15和1个n16精确dyadic KKT问题。[独立Python向量](<python_vectors.json>)不导入/执行父代码。
- 最大解误差 **4.08291817e−6**，目标函数与独立oracle最大差 **2.67984504e−7**；float64复算最终KKT最大1.88044707e−4，对应n15/n16的绝对tolerance=2e−4。这不是机器人episode或全条件数资格。
- `sizeof(float)=4`、尾数24位、`FLT_EVAL_METHOD=0`；当前host workspace **2448 bytes**。不是ARM布局/WCET测量。
- [C++11 smoke](<cpp_smoke.cpp>)链接**单独按C99编译**的object后通过：`status=CONVERGED,z=.5`，见[链接日志](<cpp_link_01.log>)和[运行日志](<cpp_smoke_01.log>)，验证该host下的 `extern "C"` 接口。

现有工具完整路径（没有安装或广扫目录）：

```text
C:\MinGW\bin\gcc.exe
C:\MinGW\bin\g++.exe
```

均为MinGW.org GCC-6.3.0-1 / 6.3.0，[工具原文](<cpp_toolchain_probe.log>)。SSE2选项仅用于host的binary32执行模型，不是ARM选项。

## 数学与算法

求解 `min .5*z'H*z + f'z`，约束只含逐分量 `lo<=z<=hi`。

1. 检查n/stride/声明长度、指针、全部有限值、box顺序与选项。H要求**float值精确对称**，不在内部悄悄取平均。界限为有限数，可有lo==hi固定坐标。
2. 对完整H做f32 Cholesky正pivot校验，无自动正则化、对角修补或“近似成功”。这是数值SPD检查；病态问题可能在f32下被判非SPD或出现数值错误，应由上层报告/缩放/重建，不能把失败隐藏成收敛。
3. 冷启动为clip(0)，warmstart先复制再clip；每个单坐标使用当前其他坐标计算精确一维minimizer，再clip。每次写入的候选坐标都可行。每sweep重新计算梯度/目标，避免跨sweep累积梯度漂移。[Cholesky/metrics/sweep:34–94](<boxqp.c#L34-L94>)。
4. 浮点中间乘积/累加/除法/目标越界或非有限时，明确返回numeric error并清零输出，不把有限box当成允许Inf内部计算的理由。

投影KKT残差是**tangent-projected gradient的∞范数**，单位与gradient一致，不是代价差，也不是经过任意单位步长缩放的z差：

```text
g = H*z + f
r_i = 0                 if lo_i == hi_i
      max(-g_i,0)       if z_i == lo_i
      max( g_i,0)       if z_i == hi_i
      abs(g_i)          otherwise
projected_kkt_inf = max_i r_i
```

`tolerance`为这个量的绝对阈值，必须为有限正数。真实MPC若改变H/f量纲或缩放，应重新解释容差；合成fixture的2e−4不是机器人验收门槛。

## C接口、workspace与别名

[bqp_problem/options/result声明](<boxqp.h#L18-L69>)提供H/f/lo/hi、可选warmstart、max_sweeps/tolerance、clock/deadline与progress callback。`bqp_dense`用于连续H；显式stride和长度支持带padding的H，padding不属于数学问题，不参与有限值检查。

- result包含z、sweeps、cost、projected_kkt_inf、feasible/has_candidate/converged、status和最后clock_us。sweeps仅统计**完整完成**的循环坐标扫描，0表示初始化点。
- workspace由调用方独占，不能和输入数组、problem/options/result对象重叠；problem/options对象也应与result分开。
- **warm_start=result.z受支持**；所有输入数据先复制到workspace才清空result。测试也覆盖f=result.z这种数据别名。[复制与别名检查:101–134](<boxqp.c#L101-L134>)。
- 不同调用可使用各自workspace并发；同一workspace并发、或callback修改workspace/result/输入对象，均不属于接口契约。
- 外部指针实际分配长度仍是C调用方责任；声明长度校验不能替代语言层对象边界。

## 状态与截止时间：不得把候选当收敛

| 返回状态 | has_candidate | converged | 语义 |
|---|---:|---:|---|
| CONVERGED | 1 | 1 | 当前检查点KKT≤tol且最终时间检查未超限 |
| MAX_SWEEPS | 1 | 0 | 有可行候选，迭代预算耗尽；不伪称达到tol |
| DEADLINE | 1 | 0 | 输入/SPD/初始点有效，但截止时间到；即使KKT已足够也不称按时收敛 |
| 输入/形状/NaN/非对称/非SPD/box/选项/alias错误 | 0 | 0 | z全部零、feasible=0 |
| NUMERIC_ERROR / CLOCK_ERROR | 0 | 0 | 数值有效性或单调时钟失效，输出零 |

- `max_sweeps=0`合法：初始点已满足KKT可返回0-sweep收敛，否则返回MAX_SWEEPS及初始可行候选。
- deadline=0表示不设deadline；>0需要uint64单调clock。先做输入/SPD与初始指标计算，然后在每个sweep检查点、progress callback之后采样时钟。**不是可抢占计时器**，也不保证初始化/Cholesky过程中能硬中断。
- 初始事件sweeps=0，随后每完整sweep给progress事件。progress的status是其检查点时刻的状态；callback自身耗时可能跨deadline，**最终返回status才是权威**，因此progress只能记录，不能直接驱动执行器。
- 最终clock检查若发现deadline已到，覆盖刚刚满足KKT的“准收敛”为DEADLINE；clock倒退则CLOCK_ERROR并丢弃候选。已用mock覆盖这两种边界。[终止与callback:135–159](<boxqp.c#L135-L159>)、[budget/clock测试:96–115](<bqp_selftest.c#L96-L115>)。
- 上层应只把最终CONVERGED+has_candidate+feasible+converged视作数值成功；其他状态按其控制策略回LQR/失能，并在实际发送前再次核对年龄/截止时间。本内核不实现这个控制层。

## 自测覆盖与限制

[独立stdlib生成器](<generate_vectors.py>)用固定种子构造问题：

- 1D解析clip(−f/H)；2D枚举所有边的精确一维极小值以及可行内部点，覆盖角点/固定边。C端另有double枚举交叉检查。
- n15/n16采用整数SPD H、dyadic z与梯度构造精确KKT，存在下界/上界/内部/固定坐标混合；精确解warmstart应0sweep、KKT=0。
- 冷启动、warm alias、输出数据alias、workspace冲突、padded stride、n0/n17/长度错误、NaN/Inf、非对称、非SPD/半正定、invalid box、数值溢出、max0/max1、即时/晚到deadline、callback耗时与clock倒退，错误输出归零。
- progress事件逐次检查候选box可行、目标与double计算一致、代价不升（容许float舍入级差），最终点与oracle比较。[自测:29–153](<bqp_selftest.c#L29-L153>)。

**未实现：** 状态约束、一般线性不等式、耦合功率约束、电/热模型、MPC预测矩阵生成、软约束/slack、活动集优化、机器人状态/接触/观测器、闭环验证或ARM实时资格。SPD循环坐标下降可能在相关/病态H上收敛慢；当前合成集的通过不代表未来N15真Hessian可在给定时限内收敛。

## 复现与封存

```powershell
# 在本目录；仅host数学测试。
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' .\generate_vectors.py
& 'C:\MinGW\bin\gcc.exe' -std=c99 -O2 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse boxqp.c bqp_selftest.c -lm -o bqp_selftest_host.exe
.\bqp_selftest_host.exe
```

[错误/构建记录](<ERROR_REPORT.md>)、[来源与源码索引](<INDEX.json>)、[复核](<VALIDATION.json>)、[主交付哈希](<MANIFEST.json>)单列。所有新增物只在本子目录，不改旧SPR/C1/C2或父文件，不运行仿真、板卡、CAN、SSH、训练或Git。也没有为文档纠错重跑旧unit；旧state14语义以父的[append-only勘误](<../../reports/STATE14_SCHEMA_ERRATUM.md>)为准，本solver的z不涉及那些列名称。没有把C1观测实现冒称当前R03/R04动态版本。
