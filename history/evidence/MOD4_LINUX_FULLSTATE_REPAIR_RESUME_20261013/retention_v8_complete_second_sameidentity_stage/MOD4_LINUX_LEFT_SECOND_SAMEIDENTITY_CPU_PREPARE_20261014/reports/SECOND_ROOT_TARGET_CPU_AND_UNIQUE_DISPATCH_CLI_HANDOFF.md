# 第二且最后 sameidentity 3600s：独立目标 CPU 组装与派发准备

本机真实 CPU fixture 已完成，目标机尚未连接、未创建 root、未执行目标 CPU 或 GPU/PPO。唯一源是原完整 20k own2b（`2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971`）。不会采用 center/near 候选，也不会重新初始化原 left mean/std/Adam。

现行 CPU 回执：`SECOND_TARGET_MATERIALIZER_DISPATCHER_LOCAL_CPU_FIXTURE_ACTUAL.json`，107 finite / 99 perenv / 195 tensor，全树 CPU 磁盘往返与所有 tensor storage 独立；25 decision 拒绝和 11 身份拒绝；源 SHA/tree/CPU 与 NumPy RNG 未改、CUDA 未初始化。

原 `second_target_CPU_pure_guard.py` 把实际 `legacy_false_preserved` 字典当成布尔，独立 CPU 检查已严格拒绝，并保留 `SECOND_ORIGINAL_V1_LEGACY_FLAGS_DICT_SCHEMA_REJECTION_ACTUAL.json`。新采用 `payload_v1/second_target_CPU_pure_guard_v2.py` 精确核实际 baseline/candidate 原 flags 字典，与 root decision 内原 flags 一致；不把 strict false / spin 回退改为通过。

根代理是唯一远端 transport owner。确认没有其他 transport owner 后，以以下两步顺序执行。第二步必须等第一步实际 CPU 完整回执，不能将本机 prepared fixture 当目标机通过。

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' 'C:/Users/lulu/Desktop/claude/mjcf/MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/materialize_second_sameidentity_target_CPU_once_v1.py' --decision 'C:/Users/lulu/Desktop/claude/mjcf/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/reports/BEST2B_COMPLETE_FOURCASE_SECOND_SAMEIDENTITY_SCOPE_DECISION_ACTUAL.json' --execute-target-materialization
```

该步先本机 SHA 核验真实 decision 的 7 个证据文件、Wave 完整评测和三项继承 skill 的实际完整 pair；再唯一 SSH 上传新 stage，复核原 first 自然退出/两锁/idle solecanonical、1188000 与 7 个 applied 扩展及最后 ID、原资源上限，完整 sourcefreeze522 byteexact 复制。仅目标实际 whole2b CPU 107/99/195、磁盘往返、独立 storage、负例、无 RNG/CUDA、canonical bytes 未改通过后，才生成新 actual admission manifest `approved_GPU=true`。既有 CPU template 保留 false，不做权威来源。新根拟为 `/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_second_formal_sameidentity_v1`；目前未创建。具体 sourcefreeze 实际数量由目标回执给出，不预报近似数量。

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' 'C:/Users/lulu/Desktop/claude/mjcf/MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/dispatch_second_sameidentity_formal_from_actual_CPU_once_v1.py' --target-cpu-receipt 'C:/Users/lulu/Desktop/claude/mjcf/MOD4_LINUX_LEFT_SECOND_SAMEIDENTITY_CPU_PREPARE_20261014/reports/SECOND_ROOT_TARGET_CPU_MATERIALIZATION_COMPLETE.json' --execute-unique-formal-dispatch
```

派发重新读取 actual manifest/evidence/sourcefreeze/SHA、原 first 退出与 solecanonical/resource/全 source；只启动新独立 parent 一次。dispatcher 本身不写预算，原 canonical 的唯一父进程记录完整 load/learn/save/exit。CPU 磁盘副本只是证据，正式 source 始终原 F 下 whole2b own model32635。两把原 fcntl 锁、20k、seed20260928、24 control/update、save25、15s guardian、3600s 和原环境参数不变。SDK/native/discard/fresh/clock 全部原 SHA reuse，不重跑。

两个根驱动和目标 dispatcher 都先落 fsync intent。任何网络未知 outcome、stage/root 已存在或 intent 已消费，都严格拒绝盲重发；应独立读取 actual 文件、PID 创建标识、argv/cwd、锁与 canonical 后判断续未执行步骤。错误原件保留，不删除 stage/root、不补造 PASSED、不重预算事务。

派发只证明新 parent 已请求启动；13 个 CPUCUDA/disk/episode+1 receipt、actual positive own fullsave 与 actor/Adam 变化随后仍必须实际核验。第二段自己的完整 final/cost/natural exit/locks idle 后全 trace 和四项冻结评测，包括 direct2b prefix，再决定下一轴。此为第二且最后同轴窗口，不第三盲 duration、不晋级 50/70、不覆盖其他专家或 gate。

所有上述本机准备、原 schema 拒绝和新 CPU 回执由 root 普通 supplement 入 Git；未执行目标机或 GPU，不作为新真实学习阶段。
