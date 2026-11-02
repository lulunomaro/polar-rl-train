# Box-QP v1 — 原样构建与测试记录

| 操作 | 原样日志 | 结果 |
|---|---|---|
| 独立stdlib fixture生成 | [vector_generation_01.log](<vector_generation_01.log>) | 成功，67个合成数值QP，无机器人数据/源码执行 |
| 严格C99构建 | [build_attempt_01.log](<build_attempt_01.log>) | exit0，无警告 |
| C代数/边界单测 | [selftest_attempt_01.log](<selftest_attempt_01.log>) | exit0，4166次断言/0失败，246个progress事件 |
| 精确已知路径C++工具探测 | [cpp_toolchain_probe.log](<cpp_toolchain_probe.log>) | 已有MinGW g++ 6.3.0；未安装或广扫个人目录 |
| 单独编译C99 object | [c_object_build_01.log](<c_object_build_01.log>) | exit0，无警告 |
| C++11链接C object | [cpp_link_01.log](<cpp_link_01.log>) | exit0，无警告，验证extern-C链接 |
| C++ smoke | [cpp_smoke_01.log](<cpp_smoke_01.log>) | exit0，status=CONVERGED，z=.5，pass=1 |

- 本轮没有非零构建/测试退出，没有隐藏、覆盖失败或伪造修订版本；当前源首次构建即通过，故没有“修复前源码”副本。
- 非SPD/不对称/NaN/Inf/invalid box/shape/alias/clock rollback/numeric overflow是主动单测输入，返回失败状态及零输出是预期；deadline/maxsweeps则返回诚实可行候选但不声称收敛。
- 时钟使用mock测试预算与时间倒退；没有把主机耗时当ARM WCET，也没有测量/停止父任务。
- 没有为旧state14文档勘误重跑旧unit或修改封存C1/C2。新QP不解释机器人状态列。
- 核心/fixture/日志/host对象和测试程序的bytes/SHA在 [INDEX.json](<INDEX.json>)；父与旧包只做主交付哈希复核，见 [VALIDATION.json](<VALIDATION.json>)。所有新增物在本子目录。
