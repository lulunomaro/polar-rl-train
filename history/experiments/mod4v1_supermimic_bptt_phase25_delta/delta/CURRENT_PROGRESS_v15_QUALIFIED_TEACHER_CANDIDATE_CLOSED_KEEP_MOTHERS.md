# 当前交接 v15：原教师与候选均已合格闭环，保持母本；不继续堆当前方案

时间：2026-11-03 02:45 +08:00。此文件及相关晚到源码、超时/释放、新闭环和真实评分待Phase25。旧 [v14](<CURRENT_PROGRESS_v14_PHASE24_VERIFIED_V2_ZERO_ADMISSION_CLOSED_RELEASE_WATCH.md>) 的资源等待是历史快照。

## 主质量结果

[合格对照报告](<QUALIFIED_QUALITY_COMPARISON_E3_W35_V1.md>)、[机器筛选](<reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json>) 已完成：

| 原条件 | 原教师参考 | A1后训练候选 |
|---|---:|---:|
| E3 recipe0..11、first-episode stable credit | 0/74 | 0/74 |
| W35 moving，原natural-complete/nonterminal条件 | 19/63（30.16%），190partial | 10/69（14.49%），143partial |
| W35 standing，同条件 | 26/26（100%），37partial | 16/17（94.12%），33partial |

E3另外6个normal recipe12环境首episode physicalterminated为教师0/6、候选6/6；不混入74恢复分母，不把它改写为新的接受口径。未知组均0，原重置/timeout/physicaltermination/partial保留。两边真实N80、seed20260928、E3160/W351600controls、原physics/DR/命令/接受循环及冻结guard、close语义、实际wait、EX释放均合格。**执行资格通过不是技能90%。** natural-complete cohort分母不同，matched pose/UID/relative/causal仍null；不是统计退化根因证明。

**决策：KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION。** 母本/H1/所有旧候选未变。当前候选recovery/moving没有取得80/90目标证据；未为凑3000再排相同baseline训练。历史A0 E02520/E22392单列；A1 E32182/W351973与其他6零更新baseline捕获均完整保存，原训练已正常合作收拢，不拼fresh计数/Adam。

Goal最近读取 `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` revision12、active/armed、round7/max48。人类23:39纠正继续有效：量服务质量，逐专家技能/鲁棒性/保持优先。原每条90及独立多seed证据尚未达成，E0/S50原二元接受缺口仍null。目标不完成/不因当前无提升就blocked。

## 一、V2原超时已关闭，实际资源释放证据已到

V2 parent1496791 原1800秒等待在1793642078.162321自然结束，两个NOT_ADMITTED、无SDK/model/GO/FINAL；旧root/once未重放，原错误保留。外部standing任务1496051曾持GPU0privateEX/finiteSH/双authority，未被干扰。

新 [只读release witness](<reports/FROZEN_V2_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json>) 已观察到actualclear=true，epoch1793643078.2000458（02:11:18），old_closed_metadata_SHA `8fdf76f57d7f3cb73417504d9c5a0123632656af2c9a5e8cf16bfb6d076df3f6`，witness1998B/SHA `7c1eeb6b09dd5ab1902dfab1a5b5a7efd08ba4081aea98b085ac69419373286b`。hostjob `pwsh-9a7165a619cc4f50` 已RC0/收取。它只是历史观察，不承诺资源持有；下述两个新用途均重新走原parent私EX/有限EX/C-readonly门，并在EX下串行执行。

## 二、真实原教师参考新用途：全部合格已关闭

```text
root=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_EMBEDDED_TEACHER_E3_W35_REF_V1_20261103_021449_1793643289716490000
source16 index=5685B/cfedd40d5c70d61a5a32e10861c3af3b6da16cab86c23306053eeccb650c5205
flat16 source=266847B; sourcepreflight/stage actualfiles=3602
stage receipt SHA=4f2eeb4a10d1574608ff76991a0087df8fa4e523bc840f7f44fe482fc7079378
original reference parent=1498906 ticks138518162
external actual-wait controller=1498899 ticks138518138
Popen epoch=1793643797.5832572 (~02:23:17)
reference parent source=9356B/4d77e137e96c34561976815fc6438c8cef109a42c860ff1c40efff9f3d06f0cd
controller source=3451B/276bb2f54b521ffa294a3756724a45b9875607919ef8f058e723c8d14eb9e274
sole observer=pwsh-0582b94c86434c4a [completedRC0,collected]
```

[实际reference闭环](<reports/ACTUAL_EMBEDDED_TEACHER_E3_W35_V1_20261103_022504/CLOSED_RESULT.json>)：qualified_reference_execution=true、external实际p.wait绑定/rc0/errors[]、Python PARENT_STARTED pid与launcher receipt同一1498906、closed source grade通过、原parent全部子wait/释放。controller仅记录原parent真实Popen.wait，无SDK/model/C/lease/signal；旧sealed parent main/close完全不改。仅pid消失不作为wait证明。早期review中run-python是否exec的源未知在本次由真实PythonPID相等给出运行态证据，不凭评论宣称。

复用同一wholeA1缓存的冻结pi.teacher，直接原RSLmean，无残差/history动作；source容器SHA仍a4/b2，bootstrap母本身份另列。actual producer guard从Admission2 TASK→INSTALL_MANIFEST→7c4298/8211小PY bytes/AST+成功FINAL派生，不是新GPU trace或新boolean。source16完整AppV6→Base；包含旧11相同/3route替换+400e helper/producer guard。源18focused/import/stdAST测试passed，CPU参考V2误差0，均未混作native技能。

真正新W35数据仅单遍评分，未下载raw、未复读旧raw补表：
- [reference W35原分组实际评分](<reports/EMBEDDED_TEACHER_E3_W35_V1_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json>)。
- [合格教师技能基线](<reports/QUALIFIED_EMBEDDED_TEACHER_ORIGINAL_SKILL_BASELINE_V1.json>)。
- sourcegrade/observer已结束，不要再开旧purpose或watcher。

## 三、候选V2_ADMISSION2新用途：全部合格已关闭

82新 [source builder](<source_frozen_v2_admission2_callers_v1/build_frozen_v2_admission2_callers_v1.py>)18717B/SHA344fabb8...已由父--emit一次生成R四新caller与独立source receipt；42stdlib/fake/AST通过。闭件精确SHA+release witness在写dispatch marker/connector前校验，原14PIN/index69688/CLI9c788/parent9a943e/actor/ABI不变。新stage首读就是V2 receipt，不使用历史collector erratum。

```text
root=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_FROZEN_E3_W35_BATCH_V2_ADMISSION2_20261103_022047_1793643647081984400
actual sourcepreflight/stage files=3600
stage SHA=ecdd365b8b3f28ccd975f83303a173e93ac73b7de7d1369e88e260045c0d01be
parent=1499174 ticks138520365; Popenepoch1793643819.8880951
parent source=8991B/9a943e730f66bfb1a68af35ddfa8118d6da605dc83f442e3c0b51c9c7ad8da7b
sole observer=pwsh-f87ba29ce3844ea8 [completedRC0,collected]
```

[实际candidate闭环](<reports/ACTUAL_FROZEN_E3_W35_BATCH_V2_ADMISSION2_20261103_022504/CLOSED_RESULT.json>) 原parent无errors，两个terminal实际wait+passed_execution、全部lease释放。新W35一次评分 [结果](<reports/FROZEN_E3_W35_BATCH_V2_ADMISSION2_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json>) qualified=true；数值重现V1先前诊断，但它是新的物理执行与新的数据单遍评分，不是把V1 close失败重新标pass。graderjob `pwsh-755071f0ee9d4d36` 已RC0/收取；reference grader `pwsh-db81bf2b75484825` 已RC0/收取。

当前没有自有native GPU父/子、资源observer或模型评分后台仍运行。未来任务不能据此假定外部资源持续free，仍用原实际门。

## 四、接下来仅SOURCE准备，实际训练仍未启用

- 405正NEW `source_quality_microtrain_executor_v1`：1–2角色显式subset，其余deferred不构造SDK；A1 raw35 LEGACY fresh/fullresume小段≤300 verified增量，加载后原总counter+增量，原whole4model/4opt/replay/RNG/streamcut不切N80。预算/EX/finiteSH/完整save/fastclose语义/actualwait会计原样，原双GPU锁与RESERVE+7800仍保留。旧worker和owner硬3000需在新源显式替换目标schema；不是只改plan。新的payload run/role/九counter须与实际producer相符，不拼谱系；无H32/bound/reward改入该legacy executor，未stage/dispatch。
- 82正NEW `source_bound_only_frozen_probe_v1`：显式**零更新postprocess探针**，同权重只把.05*delta改.05*tanh(delta)，保留原raw35/history/teacher/norm/完整CP/clip6，明确不同effective actor variant；不能声称训练收益。先分开部署截断与后续bounded短训练收益，源任务未完成/未nativeenabled，不改现有seal或过去结果。若记录Δaction只在已有forward中取标量，不新采obs/RNG/physics。
- 之前bound-only训练与E3H32-only均disabled、独立，不叠加；H32/恢复reward/传感WM一致性/残差漂移仍须实证，不能把H16短或g²cost当已证根因。

主下一步是短段单因子、完整保存释放后冻结验收，而非原固定8队列整批跑满或把次数当通过。

## 五、Git与追加

Phase24已remote exact verified：feature commit60a5ee122fc45238d3c636383e0a2d5f71d0343e，annotated trial `trial-20261103-mod4v1-supermimic-first-quality-screen-dependency-complete-eval-phase24` objectbd0139c4ded651a8d797e6d21509bfca562ce406，peeled同commit；main当时仅读d429a5b2b38e6e62829ef2efefd147f1c0af775a，未push/resetmain。

Phase24之后此v15、v14、人类质量报告、资源诊断/V2零准入自然超时/release、16源reference/seals/controller评审/真实stage/Popen/wait/闭环、Admission2四caller与真实stage/闭环、两组新数据单遍评分/合格基线/保母对照，以及晚到microtrain/bound-probe点时源均待Phase25。原模型/raw不为Git重读，使用已有producer引用；旧once/stage/grade/record不重跑。所有真失败与reader错误保留，main仅读，不宣目标完成。
