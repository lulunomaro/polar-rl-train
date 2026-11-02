# 当前交接 v13：先看原技能质量，保持母本；V2 闭环复测等待原资源

记录时间：2026-11-03 01:44 +08:00。此文件在 Phase23 之后生成，**待 Phase24 归档**，不声称已推送。

## 1. 人类目标与完成条件

人类于 2026-11-02 23:39 明确：增加训练量是为了提高通过率，别本末倒置。当前 goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb`，最近读取 revision12、active/armed、round7/max48。主线是“原口径基线 → 针对失败训练 → 独立冻结复测 → 保留有证据收益的候选”，不是凑够 BPTT 次数。中间80%/最终逐专家90%的真实原技能证据尚未达成；原接受口径缺件保留 null，不以 MAE、nofall、站立混入或平均值代替。H1 冻结。

## 2. 已完成的阶段质量诊断：不提升为正式验收

| 原技能条件 | 当前候选观测事实 | 分母/缺口 | 当前处理 |
|---|---:|---|---|
| E3 原 requested recipe0..11，first-episode credited | **0/74** | normal recipe12 的6环境单列，不混入 | 保留 Registry_v12 母本，不提升候选 |
| W35 原 moving，自然完整且非终止条件 | **10/69（14.49%）** | 另有143 partial；不是全部任务成功率 | 保母，不因更新量而继续同方案 |
| W35 原 standing，同条件 | **16/17（94.12%）** | 另有33 partial；不混作 moving 通过率 | 仅描述本条件；不据此称 W35 达标 |

上述 V1 两个实际 N80 控制循环已完整运行（E3 160、W35 1600 controls），冻结 pi/norm 与实际 RSL 源绑定检查通过；但结束阶段导入 App close helper 时缺少 `resume_runtime_contracts_v3`，因此 **执行收尾不合格、不是合格最终验收**。保留全部输出与错误，不将 RC0 当成功。无实际 matched teacher/reference、跨组 UID/pose/cohort 配对证据，相对增益、统计退化与根因仍为 null。

主要证据：
- [V1 诊断与收尾错误](<reports/FROZEN_E3_W35_BATCH_V1_QUALITY_FACTS_WITH_CLOSE_ERROR.json>)
- [W35 原始行首次实际分组评分](<reports/FROZEN_W35_BATCH_V1_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json>)
- [首次质量筛选决定](<reports/FIRST_A1_ORIGINAL_QUALITY_SCREEN_SELECTION_V1.json>)

W35 分组消费者只对这次新产生的数据做过一次真正评分读取，438行、drop0、schema5；moving/standing 由原布尔字段分组，不通过 vx/MAE 推断。不重开旧 raw 来补表格或改标签。

## 3. 原训练已合作收拢，非信号中断

Admission2 原父进程1490574、ticks137458072，原8专家队列通过各自原 `STOP_AFTER_SAVE` 接口收拢；没有 SIGSTOP/INT/CONT/KILL、源码热改、锁/账本/超参变更。实际全8完整保存、原 semantic 检查、实际 wait、费用结算与 lease 释放通过。E3实际2182 BPTT、W35实际1973；其他6是0更新 fresh baseline capture（真实 SDK/reset/teacher/learner 初始化发生），不是训练或技能通过。历史 A0 E02520/E22392 单独保留，不与 A1 相加。

- [Admission2 合作边界实际闭环](<reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json>)
- [原 STOP 请求](<reports/QUALITY_BOUNDARY_ORIGINAL_COOPERATIVE_STOP_REQUEST_V1.json>)

实际 GO→wait 成本6903.554010629654 expert-seconds，原账计费，无退款/新账本。两新完整 checkpoint 的生产者引用如下（不要为状态、Git 或格式化再次读取其权重）：

```text
native_root=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000
E3: roles/E3/production/checkpoints/model_BPTT002182_I002282_S0005_complete.pt
bytes=236664417 SHA=a4c56390b4c549ba8bfb808a63206c0816ad50e8c9659dc053f98cc66b3c8127
W35: roles/W35/production/checkpoints/model_BPTT001973_I002073_S0005_complete.pt
bytes=233435425 SHA=b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff
```

## 4. V2 依赖修复与实际当前等待

V2 仅补齐原 AppV6 helper 的 stdlib 项目依赖；原13项源码、actor、原接受循环、物理、DR、parent资源门都保持原字节。新增14项完整 closure，并做真实 App+base 导入检查。14源码220240B；index `69688e86528e400f188de3f147614cde5c66f86985adaceed805af800819dc50`。

真实远端 stage 已一次成功 rc0；本地第一次 collector 在此之后误读 V1 receipt 文件名而退出1。保留原错误，新增只读收据修正，**未重复 stage**。实际 receipt SHA `993bf46284d208c5bf63d5bc55f8a121180b50ac96205373a68fada5d0e80941`。只修改了尚未执行的本地 V2 dispatcher/observer 的收据文件名，未改运行中的原评测源码。

```text
V2 root=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_20261103_011752_1793639872103756500
parent=1496791 linux_start_ticks=138166132
actual Popen epoch=1793640277.5620935
source parent SHA=9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b
sole observer host job=pwsh-f7d351747ab14e5b
```

最近已读发布快照 epoch1793641105.7204876 仍为原资源 wait（Errno11、partial held0、未 SDK/selected-model、C写0），不是开始评测。不要把之后的 historical WAIT 文件当现场状态；以实际 admission/barrier/FINAL/exit 为准。原1800秒等待仍生效，未延长或清外部锁。唯一 observer 正运行；不要重开 watcher、旧 stage 或 dispatcher。

- [V2 原 stage 输出（保留 collector 错误背景）](<reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_SOURCE_STAGE_V1.json>)
- [只读收据修正](<reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_SOURCE_STAGE_RECEIPT_CORRECTED_V2.json>)
- [实际一次 parent dispatch](<reports/FROZEN_E3_W35_BATCH_V2_ACTUAL_PARENT_DISPATCH_V1.json>)
- [最新 observer 指针](<FROZEN_E3_W35_BATCH_V2_LATEST_METADATA_WATCH.json>)

## 5. 嵌入原教师参考：CPU 软件验证通过，真实参考未运行

参考 adapter400e... 不变；V1 CPU fixture 在4×N80正向比较后，误假设原 RSL teacher 一定有 norm buffer。实际合法 schema 为 std_param+8项MLP权重/偏置，没有 teacher norm/buffer。原 V1 失败保存，未篡改算法。

NEW fixture V2 `246f8a305d0fed032da964c92b899d731bc81cab61804d901558d1be01dd8a2c` 在新 CPU 用途中实际 Torch rc0：4×N80 对原 RSL mean 误差0；候选残差与教师数值差0.1559954136610031（不是技能收益）；STD full-value 独立变异与 whole-mean guard/sticky 检测；独立自有 synthetic 残差 obs_norm.mean 变异检测；teacher buffer 明确 N/A；全局 RNG 不变。无旧模型读取、SDK、GPU、原资源/账本、native 更新。它证明软件参考路径，不证明真实母本表现或配对效果。

- [V1 软件 fixture 失败](<reports/EMBEDDED_TEACHER_REFERENCE_CPU_V1.json>)
- [V2 实际 CPU 软件结果](<reports/EMBEDDED_TEACHER_REFERENCE_CPU_V2.json>)
- [原参考 adapter](<source_frozen_embedded_teacher_reference_v1/embedded_teacher_reference_v1.py>)

405已提交新 source-only 两角色原教师参考入口/完整依赖 stage 任务；未声明完成或真实运行。82只封存 fixture 与独立 review；不重造算法。真实参考必须区分 A1 container checkpoint SHA 和嵌入母本 actor 身份，核对原设备冻结证据，保留原 N80/seed/control/DR/接受分母及实际 close/wait。配置同 seed 不自动成为 matched pose/UID/cohort 证据。

## 6. 下一轮改进仍 disabled

[一页失败假设](<source_first_quality_failure_plan_v1/FIRST_QUALITY_FAILURE_PLAN_V1.md>)、[机器 disabled 计划](<source_first_quality_failure_plan_v1/FIRST_QUALITY_FAILURE_PLAN_DISABLED_V1.json>) 已冻结。四项未证实假设：unbounded residual/模型利用；raw35 sensor 与 WM-state 不一致；恢复时序支持；原 orientation 成本路径竞争。亲查 recovery counters 走 aux learned delta，并非 held；frames每步+1。H16=.32s、原 stable=.5s/request=3s，有 critic bootstrap，短H本身不证明失败。仅预登记两个单因子未来对照：bound-only、E3 H32-only；不叠加、不改原 reward/physics/DR/命令/验收。implemented/enabled均false。先合格复测和真实教师参考，再决定训练。

## 7. Git 与后续顺序

Phase23 已 remote exact verified：feature `mod4v1-experts-fulldr-rm70`，commit `01232718ef0ae41207dc50315d1bdbdeaa1c60d9`，annotated trial `trial-20261103-mod4v1-supermimic-quality-first-native-closed-eval-source-phase23`，tag object `8d2f1f1509087009d3f85d417e4f2aa84175934e`。main仅读、独立推进。此文件及 V1实际评测/错误/评分/保母决定、V2修复/receipt erratum/dispatch/等待、CPU参考V1失败和V2通过、一页disabled计划，均待 Phase24 追加。

后续：收集唯一V2 observer实际闭环；如等待零GO自然超时，保留原边界，不重放原purpose。核对新参考源码完整依赖、再以新unused用途在实际资源释放后执行。所有母本/候选/失败留存；质量结果主汇报，训练次数辅助。各原技能真实>=90及独立鲁棒性证据前，goal保持active。
