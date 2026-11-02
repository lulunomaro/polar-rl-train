# Kinematics v2 — 原样错误、尝试与指标命名记录

| 操作 | 原样记录 | 结果 |
|---|---|---|
| stdlib向量生成01 | [vector_generation_01.log](<vector_generation_01.log>) | 成功；52个kinematics、48个LQR fixture，预选pose均可达，无异常traceback |
| 严格构建01 | [build_attempt_01.log](<build_attempt_01.log>) | exit0，无警告 |
| 代数自测01 | [selftest_attempt_01.log](<selftest_attempt_01.log>) | exit0，2549次断言/0失败；当时源保留为 [历史测试源](<revisions/ctk_selftest_attempt_01.c>) |
| 严格构建02 | [build_attempt_02.log](<build_attempt_02.log>) | exit0，无警告；加入独立刚体旋转恒等式、半径错配反例并拆分单位指标 |
| 代数自测02 | [selftest_attempt_02.log](<selftest_attempt_02.log>) | exit0，2761次断言/0失败；当前主机程序与当前源一致 |

**已修正的指标命名：** 首轮 `max_pose_error` 混合了位置m和膝角rad；`max_forward_error`混合了相对线速度、角速度与最终前向速度。原日志没有修改，最终日志已按 `position_m / angle_rad / relative_m_s / rate_rad_s / forward_m_s / LQR_nm` 分开。首轮数字不应被误当作全部以m/s计量。epsilon扫描本来就单独统计最终前向误差，其原值未变。

- 本子任务没有编译或单测非零退出。旧v1的构建警告属于旧子任务，本轮没有继承或覆盖其日志。
- FK不可达/奇异、NaN/Inf、FD分辨率不足、无效valid/参数等错误码是单测主动输入后的预期结果，输出清零检查同时通过；不是实际设备错误。
- FD stencil跨出可达域的错误路径由代码显式处理；这批固定fixture未声称穷尽所有构型或覆盖所有可能的近奇异边界。
- 数学输入只读JSON/冻结公式，无MuJoCo、真实CAN、板卡、SSH、Git、父任务或训练操作。没有执行原参考源码/脚本，也没有安装工具。
- 仅使用已有 [GCC版本/目标记录](<toolchain_version.log>)；SSE2用于主机binary32测试，不推导ARM实时资格。
- 当前源、fixture、日志、历史测试源与主机测试产物的bytes/SHA/行链接在 [INDEX.json](<INDEX.json>)，复核在 [VALIDATION.json](<VALIDATION.json>)。
