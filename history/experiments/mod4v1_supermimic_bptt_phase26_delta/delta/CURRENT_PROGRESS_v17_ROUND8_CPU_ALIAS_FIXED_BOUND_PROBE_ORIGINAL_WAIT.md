# 当前交接 v17：CPU恢复别名修复已实测；零更新bound探针已stage/Popen、原准入等待

记录时间2026-11-03 12:47 +08:00。Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 最新revision13/activearmed/round8/max48。用户质量优先，不为3000凑数；H1/所有母本/Registryv12保持。原80/90独立原技能目标未达，E0/S50二元authority仍null。

## 1. 已有合格质量结论不变

[原教师/候选实测](<QUALIFIED_QUALITY_COMPARISON_E3_W35_V1.md>)：E3均0/74，正常6首episode物理终止教师0/6对候选6/6（不混入74）；W35 moving19/63对10/69，standing26/26对16/17，所有partial/终止/timeout单列。独立natural cohort/单seed，relative/causal/matched UID/pose仍null，保留母本，不选当前legacy盲目续量。历史A0与A1计数分开，各自真实完整保存/关闭/结算，不把新CPU测试计专家训练。

新增 [八专家质量路由](<EIGHT_EXPERT_QUALITY_ROUTING_V1.md>) 只用已发布元数据：C878/S135已有好scope则先保留并多seed验证；C113针对上行；E0/E2/S50测量缺口先补；E3/W35单因子。不是已生效的新队列或全任务90%证书。

## 2. 恢复alias：新CPU对照及修复确实执行

[汇总](<RESUME_ALIAS_CPU_CONTROL_AND_FIX_V1.md>) 与 [机器对照](<reports/RESUME_ALIAS_CONTROL_FIX_ACTUAL_CPU_COMPARISON_V1.json>)：

- NEW CPU V2 `pwsh-469a00e997ff4c56` RC1/已收取。修正ordering夹具后，14项负例完整通过、实际same-view全恢复并续3→5；原811 decoded源optimizer值/版本仍改变，所以严格失败保留，无unhandled_error。
- NEW CPU V3 `pwsh-b3e1e66cc4f84caf` RC0/已收取。同样3→5和14负例，whole retained root值及tensor版本均不变、raw不变、一次PT open/hash/decode、后续重读0。
- 新core36941B/SHA20fd4945a0f2345c17505316560ae6d358fcce147c6988f62a08d867e084e749，只加import copy和loader入口whole deepcopy，父已实核移除两处后全模块AST等同原811。原13/811/旧失败全部不改。
- **这是CPU软件问题修复，不是native GPU全恢复/PhysX接触续接或技能收益。新core尚未安装到native训练树，旧质量欠佳legacy未被选择续训。** 原模型PT/SDK/GPU/C/锁操作0，只本用途自己的synthetic完整checkpoint。

## 3. bound-only新用途：完整源已核验，真实stage/parent Popen不等于技能实测

前子82/405于03:34宿主故障终止，稳定源码已在磁盘；父没有重放旧用途。新独立子bac87dff做只读恢复审计：[review](<source_bound_only_native_integration_v1/PARENT_RECOVERY_SOURCE_REVIEW_V1.md>)，17/17源码273460B、index6085/d0519c7a…、stager34960/74f52b47…和全部依赖/原11行实核一致。已有22/22 stdlib/fake/real-import receipt与其早期fixture查错名字失败均保留；本次不冒充新动态重跑。

新17映射保留canonical base37927/7a092独立，new runtime→new route→base无环；AppV6→contracts_v3闭包齐全。原ctor清零在strictload之前、freshcache只build一次，原noisy/delayed35/history/TTr/严格whole CPU/pi/teacher/RMS/source guard保持。新forward只有teacher+.05*tanh(delta)后clip6，**零优化更新**，截断效果不称训练收益，optional stats默认False。

父新 [本地payload](<reports/BOUND_ONLY_NATIVE17_LOCAL_SOURCE_PAYLOAD_V1.json>) / [caller源](<reports/BOUND_ONLY_NATIVE_PARENT_CALLERS_SOURCE_V1.json>)：17源码273460B，全部实际PINS；新外层controller独立Popen.wait，原sealed parent仍管SDK/worker wait/EX/Creadonly/期限。之前成功reference-controller只作模板，bound字段/根/parentPIN明确替换；controller/observer不冒用子17审计签收，父已逐行审阅。

```text
root = /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_20261103_123731_1793680651375185300
source-input = root + _SOURCE_INPUT
source preflight = RC0 / files3603 / source-only / no SDK, selectedPT, C or lock ops
actual stage = RC0 / files3603
stage complete SHA = 1a40a9f2c84eeac6bd84ce90a3121ebc904017e401837ea0046e11d689eecd72
controller pid = 1524129 / startticks142230893
original parent pid = 1524136 / startticks142230922
parent actual Popen epoch = 1793680925.1494608 (12:42:05)
source parent = 9348B / 63eaa4b04ee085a1efbbbc72a4d0756036faa7928af01e19713e6871925d0e80
controller = 3456B / 818e434162c6f4ae91ae50dfcd059ad2b53755accc7b074bf63e75b12c47f6e6
```

preflight `pwsh-8053ef93dafa4218`、stage `pwsh-d33217b8cc864806`、dispatch `pwsh-f0feac5ad0c245ae` 均RC0/已收取。**唯一活跃相关job** `pwsh-4eeba5d08a6e4e0c` 跑 [bound observer](<collect_bound_only_e3_w35_metadata_once.py>)；不要重启/另起父。pointer [BOUND_ONLY_E3_W35_V1_LATEST_METADATA_WATCH.json](<BOUND_ONLY_E3_W35_V1_LATEST_METADATA_WATCH.json>)，自身20s published metadata、无模型/raw/SDK/C操作，7200cap。实际wait/close/sourcegrade齐备才qualified，不把Popen当准入。

## 4. 当前实际资源等待，不是已开始GPU评分

[一次只读诊断](<reports/BOUND_ONLY_E3_W35_V1_ACTUAL_ORIGINAL_RESOURCE_WAIT_DIAGNOSIS_V1.json>)，`pwsh-c88fb1d22fd4495b` RC0/已收取，epoch1793681145.9725697(12:45:45)：自身parent exact PID/ticks活着，ACTUAL_GROUP_ADMISSION未发布；canonical别的原LQR owner `Linux_LQR_MPC_DEPTH_STUDENT389_1793680800878775786` PID1523782持原两authority EX，GPU1私EX1523792/compute1523806约4486MiB/util38；GPU0 free24203MiB/util0、finiteEX空闲也不绕过原ownerNone门。原remaining300795.843419075/reserve86412.86069250107，readonly snapshot不是可回写账本。自身原1800preGOwait，未延长、未抢锁/foreign signal/预算写。

[评分源](<grade_bound_only_closed_w35_original_rows_once.py>) 已写**尚未执行**：只在新的bound qualified闭环后一次远端stream这个NEW W35 artifact、原standingBoolean/fullUID/完整分母+partial绑定、无旧raw或模型重读；输出BOUND_ONLY_E3_W35_V1_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1。若本用途原1800超时0GO，则保留失败，不重放旧root/dispatch；以后只能新用途并核实实际资源释放。

## 5. Git

Phase25已remote exact verified HEAD8d2c00278fa7734144362074f990ab87d7061b5a、annotated对象e5ffe4cb06eda1c846494830e93262b05c4c1173（见v16）；main独立推进只读。**此v17、v16后late source、CPU V2/V3、独立readiness、八专家路由、本次source-only preflight/stage/parent/资源诊断及后续probe实际metadata待Phase26。** 归档仅固定文本点时刻，模型在stat前排除、raw/large仅producer引用，不因Git重跑任何实际once。Goal仍active，保留所有失败与源，不称80/90或RM70实物已验证。
