# Actual-H numerical v1 — 原错误/修正/预算不足记录

1. [host_cwd_denial_01.txt](<host_cwd_denial_01.txt>)：新输出cwd尚未存在，host在命令启动前阻止。按工具给出的路径创建办法写入本目录SCOPE后再执行；无ACL/沙箱变更，无权限升级。
2. [environment_probe_02.log](<environment_probe_02.log>)：bundled Python已有NumPy、无SciPy，ModuleNotFoundError/exit1。未安装；父提供已有Python314完整路径后，[probe03](<environment_probe_03.log>)成功，3.14.3/NumPy2.4.5/SciPy1.17.1，mujoco_loaded=False。
3. [hessian_build_01.log](<hessian_build_01.log>)、[fixture_generation_01.log](<fixture_generation_01.log>)：成功。SciPy原status/KKT与后续active-face证书全留[vector JSON](<actual_model_vectors.json>)，不抹去function-tolerance退出事实。
4. [build_attempt_01.log](<build_attempt_01.log>)：严格C99首次exit0、无警告；封存boxqp源未改。
5. [selftest_attempt_01.log](<selftest_attempt_01.log>)：driver exit0、541983契约检查/0失败；**144run中55次是诚实MAX_SWEEPS**，不是144次全部优化成功。原[C结果](<C_RUNS_01.jsonl>)从未覆盖。
6. [comparison_attempt_01.log](<comparison_attempt_01.log>)与[完整traceback](<comparison_error_01.txt>)：报告字段 `float_gradient_rounding_bound_conservative` 是NumPy float32，json.dumps拒收，exit1。数学比较已计算，写JSON前报错；不是C求解错误。原源保留为 [attempt01源码](<revisions/compare_results_attempt_01.py>)。
7. 只把gamma显式转Python float并将后续错误文件改新编号，[comparison_attempt_02.log](<comparison_attempt_02.log>)成功；没重跑C、没改solver/fixture/父模型或隐藏预算不足。
8. 1个unique warm case的同tol f64 KKT边界不一致在两个扩预算run中保留原状态，详见[README](<README.md>)与[COMPARISON.json](<COMPARISON.json>)，未静默扩大阈值。

没有物理/MjData/step/HIL/板/CAN/SSH/Git、新包或新agent。所有新写入限定本目录；[INDEX.json](<INDEX.json>)与[VALIDATION.json](<VALIDATION.json>)复核旧封存物、父输入与C原输出不变。
