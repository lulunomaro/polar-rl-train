# Phase1 outer parent actual-wait recorder — SOURCE

该独立controller只做一次Popen(original finite-validation parent)并真正p.wait，记录controller/parent PID、Linux start ticks、RC与实际wait返回epoch。未运行main，未启动parent/SDK/资源，也不替代原parent内的worker wait/EX释放/预算门。

- 新root prefix：`MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_`。
- 固定stage receipt：`STAGE_COMPLETE_PHASE1_CAPTURE_V1.json`；要求真实文件materialized=true、parent_launches=0、purpose=NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN，并先核receipt bytes SHA；preflight不是materialized。
- 固定parent9336B / d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41。
- `PHASE1_CAPTURE_PARENT_WAITED_ACTUAL_V1.json`只在实际p.wait之后发布。Controller-start、Popen、PID消失、RC0或App fastintent都不单独证明完整闭包；后续collector还要结合原parent的全部worker实际wait/EX释放与NEWcapture Source grade。
- 没有flock/canonical read-write/model/SDK/信号/训练；原parent仍唯一控制全部resources/SDK/deadline/清理。
- 源自已实际运行并闭包的bound controller，identity/atomic put函数AST保持、main Try/Popen/wait/finally AST除metadata strings完全相同。9项stdlib测试只检查元数据/源码，不执行main/Popen。

本SOURCE不是实际准入、执行、parent wait或Gate1通过。CPU/SDK/训练均0。内容seal创建后再运行seal_source.py只读复验，不重写，后续变化NEW lineage。
