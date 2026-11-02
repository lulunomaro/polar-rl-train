# Portable Core v1 — 原样错误与测试尝试记录

本报告不替换原始日志。所有本轮新增物仅在本子目录；旧SPR审计没有修订。

| 尝试 | 原样日志 | 结果/修正 |
|---|---|---|
| 向量生成01 | [vector_generation_01.log](<vector_generation_01.log>) | 成功，stdlib独立参考；未执行冻结源 |
| 构建01 | [build_attempt_01.log](<build_attempt_01.log>) | exit1；9处紧凑if语句触发 `-Werror=misleading-indentation`；原源文件保留在 [ct_core_attempt_01.c](<revisions/ct_core_attempt_01.c>) |
| 构建02 | [build_attempt_02.log](<build_attempt_02.log>) | exit0；加花括号/分行后严格构建通过；当时源见 [ct_core_attempt_02.c](<revisions/ct_core_attempt_02.c>) |
| 自测01 | [selftest_attempt_01.log](<selftest_attempt_01.log>) | exit0，18101次检查/0失败；当时测试源见 [ct_selftest_attempt_01.c](<revisions/ct_selftest_attempt_01.c>) |
| 构建03 | [build_attempt_03.log](<build_attempt_03.log>) | exit0；明确SSE2/binary32并补齐空输出擦除、缺失回调gate、六轴回归；源见 [ct_core_attempt_03.c](<revisions/ct_core_attempt_03.c>) 与 [旧头](<revisions/ct_core_attempt_03.h>) |
| 自测02 | [selftest_attempt_02.log](<selftest_attempt_02.log>) | exit0，18151次检查/0失败，FLT_EVAL_METHOD=0；测试源见 [ct_selftest_attempt_02.c](<revisions/ct_selftest_attempt_02.c>) |
| 构建04 | [build_attempt_04.log](<build_attempt_04.log>) | exit0；当前源，增加int64圈数/残差的连续yaw表达，无警告 |
| 自测03 | [selftest_attempt_03.log](<selftest_attempt_03.log>) | exit0，当前18152次检查/0失败；最大逐标量绝对差7.62939453e−6；sizeof(float)=4、FLT_MANT_DIG=24、FLT_EVAL_METHOD=0 |

- 没有隐藏或覆盖构建01错误；重试前修改了对应源码，而非重复相同失败操作。
- 改动边界检查带来的拒入/锁存是自测预期条件，不是未记录的异常或实际设备错误。
- 编译器只使用已有 [MinGW版本/目标记录](<toolchain_target.log>)；没有安装、广扫个人目录或探测真实设备。
- 所有通过结果均为host algebra，不等于ARM/BSP构建、固件执行、台架/HIL、实时尾延迟或实物性能。
- 当前源/所有尝试日志与历史源码SHA见 [INDEX.json](<INDEX.json>)。当前主机测试程序已重建为构建04版本，旧主机EXE没有被当作硬件固件留档；旧源码和原始日志仍保留。
