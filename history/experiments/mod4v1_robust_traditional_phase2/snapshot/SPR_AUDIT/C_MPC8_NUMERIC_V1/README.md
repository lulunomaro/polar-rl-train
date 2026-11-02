# C MPC8 actual-H numerical qualification v1

**真实父模型Hessian，仍只是纯数值对照，不是机器人MPC/HIL或ARM实时验证。** 没有import父controller/physics模块，也未创建MjData、执行step或修改已封存boxQP。

## 来源与构造

- 读取[scalar_ground_mpc_v1.py:10–35](<../../scalar_ground_mpc_v1.py#L10-L35>)，source SHA `5fd9b90367f190b7805d36a3cecd62406328168b5d565c8eb290a457cb779337`。
- 参数取[MPC8模型JSON](<../../MPC8_V1/MODEL_AND_QP_CHECKS.json>)，SHA `adfacebc1004dc67c1c3675877bfb30b04f6e350e4c2d5ac62c76a5ef7080cfb`；源SHA与JSON声明吻合。
- state8为distance/pitch/hip_avg/**crank_minus_hip_avg**/forward_v/pitchdot/hipdot_avg/delta_dot_avg，另加last common input成为9维lag状态。没有混入被动膝角或yaw状态。
- 单输入是**每轮共同扭矩Nm**，作用矩阵为两轮B列之和，并非“总扭矩再除二”。模型是局部zero-yaw/fixed-leg，不外推成高速自转资格。
- [独立构造](<build_condensed.py>)：N=15，F=(135×9)，G=(135×15)，Qbar=diag(Q×14,P)，`H=2*(G'QbarG+R*I)`，`f=2*G'Qbar*(F*x9−reference_sequence)`。参考位置按k*.01*vref前移，与父公式对应。
- 原double H最大非对称5.68434e−14；明确取对称部分后再量化并强制float对称，无隐藏对角正则化。H64条件数 **2426.684456**；H32当double评估 **2426.697956**，eig范围[.4161575324,1009.8886334]，f32 Cholesky最小pivot约.96545535。max H元素量化差7.24083e−6。[基线原文](<HESSIAN_BASELINE.json>)。

## Oracle与fixture

[make_fixtures.py](<make_fixtures.py>)构造18个小姿态/速度/位置误差、lag input及active box问题，其中10个原问题free解可行，8个有活动/固定bound。包含非均匀/固定首输入的额外数值box，不声称父当前已用这些时变边界。

- 运行用户提供的**已有**Python314：3.14.3 / NumPy2.4.5 / SciPy1.17.1，`-B`、OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=1；没有安装包。
- SciPy L-BFGS-B，解析gradient=Hz+f，gtol=1e−10、ftol=1e−15、maxiter=20000、maxls=50、maxcor=20。原success/status/message/nit/x/KKT全部保留。
- 原SciPy均success，但有function-tolerance退出，raw quantized-problem KKT最大1.786e−6；并未把success当作1e−10 KKT证明。另做**独立active-face线性求解+活动约束梯度符号释放**polish，绝对KKT检查1e−8；最终quantized oracle maxKKT **1.13687e−13**。
- 分开保存原H64/f64 oracle与**精确C输入H32/f32/bounds32转double**的oracle；仅输入量化造成的max解∞差 **3.30649e−5**，不混作C迭代误差。
- DARE矩阵残差∞约1.29802e−10；free首控制与DARE的对照也留在[完整vector JSON](<actual_model_vectors.json>)。

## C1预算结果：不足就是不足

[driver](<actual_hessian_driver.c>)只链接[已封存boxqp.c](<../portable_mpc_qp_v1/boxqp.c>)，tol采用父原值 **.002（gradient绝对单位）**。所有point可行，但只有CONVERGED才数作数值成功。warm为**前一个人为fixture的quantized oracle解平移一格**后clip，不是已记录闭环warm，甚至可能更差；cold是主要公平基线。

| budget | cold收敛/18 | cold MAX | shifted warm收敛/18 | warm MAX | cold最坏首输入误差(Nm) |
|---:|---:|---:|---:|---:|---:|
|64|2|16|2|16|.1217900|
|256|7|11|6|12|.0142059|
|4096|18|0|18|0|.00118794|
|20000|18|0|18|0|.00118794|

- 4096/20000仅是扩展收敛诊断，实际最坏cold **539** / warm **551** sweeps，不把扩预算称为deadline内成功。
- 64 cold最大z∞误差.142480；256 cold .0206844；充分预算cold .00186868、warm .00264576。这些迭代误差明显高于纯输入量化误差，并与.002梯度tol有关。
- 144 runs共**89 CONVERGED / 55诚实MAX_SWEEPS**；driver的**541,983次契约检查0失败**只表明状态/可行性等逻辑符合契约，绝不等于144问题均在原预算内收敛。
- 64预算的10个free case仅equilibrium零点成功；256 cold同样只有1/10 free成功，而活动case为6/8。父Python有`unconstrained_exact`直接free shortcut，本封存C1没有，两者算法路径不同，不能直接把原Python漂亮nominal表现套给CCD。
- [BUDGET_SUMMARY.csv](<BUDGET_SUMMARY.csv>)、[144次逐run对照](<RUN_COMPARISON.csv>)、[C原输出](<C_RUNS_01.jsonl>)与[抽样sweep检查点](<sweep_checkpoints_01.csv>)均留存；每次callback均检查，日志只保留起始/幂次/每256/终态，未声称写出所有callback行。

## f32 KKT阈值边界

有**1个unique warm case**在4096与20000配置下各出现一次：C报告KKT≤.002，但对精确quantized问题用double复算为 **.00200053929764**，高约5.39e−7。保留原C status及所有数值，标记为同tol复核边界，而非静默改报告或放宽阈值；不是2个独立case。

[COMPARISON.json](<COMPARISON.json>)还记录reported-vs-double残差差、保守float梯度舍入量级、对原box的微量量化越界。C32 box与原double box不同，尤其.15这样的边界；主KKT比较针对实际传给C的量化问题，未暗中把C输出投到原box后冒充原解。

## 约束与后续

- 本次没有时钟deadline性能测量、ARM WCET、物理/HIL/板/BSP/CAN/SSH/Git或新agent；未重跑父闭环。18个代数输入不构成真实DR资格。
- 只实现box，不含状态/接触/耦合电功率约束。所有MAX_SWEEPS都应按上层策略回LQR/失能，不能因为首输入“看着接近”就宣称收敛。
- 可在**新版本**利用已验证Cholesky求free解，只有box可行且重新计算真实KKT达标才成功，否则回CCD。那只能解决free路径，不自动解决受限case；当前C1失败/预算不足报告保持封存不回写。

## 操作与错误保留

[ERROR_REPORT.md](<ERROR_REPORT.md>)保留：未建cwd的host拦截、bundled环境缺SciPy、报告NumPy float32字段JSON序列化异常及修正前源。后者仅改报告转换类型，未重跑C或改算法。C构建/driver首次均成功。

[INDEX.json](<INDEX.json>)记录父模型、封存kernel与所有新源码/结果SHA；[VALIDATION.json](<VALIDATION.json>)复核旧包与ODOM均未变，[MANIFEST.json](<MANIFEST.json>)给主交付哈希。复现只用已有工具：

```powershell
$env:OPENBLAS_NUM_THREADS='1'; $env:OMP_NUM_THREADS='1'
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B .\build_condensed.py
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B .\make_fixtures.py
& 'C:\MinGW\bin\gcc.exe' -std=c99 -O2 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse ..\portable_mpc_qp_v1\boxqp.c actual_hessian_driver.c -lm -o actual_hessian_host.exe
# driver保护既存日志；复现必须选新输出名，勿覆盖原输出。
.\actual_hessian_host.exe NEW_RUNS.jsonl NEW_CHECKPOINTS.csv
```
