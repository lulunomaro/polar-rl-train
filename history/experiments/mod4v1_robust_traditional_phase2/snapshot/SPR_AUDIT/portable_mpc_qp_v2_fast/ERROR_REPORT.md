# V2 fast — 全部构建/测试/预算记录

- [source_derivation_01.log](<source_derivation_01.log>)、[harness_derivation_01.log](<harness_derivation_01.log>)：从已封存C1文本/相同真实H harness生成新目录源码，原件不改；所有exact-replacement与SHA检查成功。
- [base_build_attempt_01.log](<base_build_attempt_01.log>) / [base_selftest_attempt_01.log](<base_selftest_attempt_01.log>)：新kernel的CCD-only入口复用原67 fixtures，自测4166/0，exit0。
- [fast_build_attempt_01.log](<fast_build_attempt_01.log>) / [fast_selftest_attempt_01.log](<fast_selftest_attempt_01.log>)：enabled自测1110/0，包含3个free可行但过紧KKT而回CCD、deadline/callback/rollback/alias/数值回退边界，exit0。
- [actual_build_attempt_01.log](<actual_build_attempt_01.log>) / [actual_selftest_attempt_01.log](<actual_selftest_attempt_01.log>)：真实H driver196951契约检查/0失败，144run中123收敛、**21为诚实MAX_SWEEPS**；后者绝不是已解决的受限题。
- [comparison_attempt_01.log](<comparison_attempt_01.log>)：与同一个double oracle对照成功，不复写或调整C1历史数值。
- [cross_version_attempt_01.log](<cross_version_attempt_01.log>)：80个free组合0sweep成功；64个active组合的点/迭代/目标/KKT/status与C1 bit一致，34个状态改善全来自free路径。
- [benchmark_build_01.log](<benchmark_build_01.log>) / [host_timing_attempt_01.log](<host_timing_attempt_01.log>) / [host_summary_01.log](<host_summary_01.log>)：host-only QPC表成功，72row/2880call。计时程序的Windows头不进入portable kernel，数字不代表ARM WCET。
- [cpp_c_object_build_01.log](<cpp_c_object_build_01.log>) / [cpp_link_01.log](<cpp_link_01.log>) / [cpp_smoke_01.log](<cpp_smoke_01.log>)：C++新fast extern-C接口与单独C99 object链接/运行成功。

本子任务没有构建/自测非零退出或隐藏修复前失败源；C1实际H阶段的cwd/缺包/报告序列化原错误仍留在旧包，没有在这里重写。所有新增物限定本目录，没有parent/旧包修改、父模块import、物理/MjData/step/板/CAN/SSH/Git、新包或agent。

[INDEX.json](<INDEX.json>)记录全部source/日志/共享fixture来源与SHA；[VALIDATION.json](<VALIDATION.json>)复核封存物未变，包含仍需受限solver/提前回退的预算不足。
