# E3复旦PPO：64轮已闭环，20000版本已部署并进入原准入

## 当前目标与事实边界
Goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision **3** active/armed，max14。按用户19:13:50要求，后续训练为 **N20000/T48**，只推进E3起身质量；H1/其它专家/Registryv12/1cd母版冻结。20k新窗尚无已观测GO或新增学习，不把派发、源码AST、继承计数当成功。

## 完整保留4096窗与64轮learner
[原闭环](reports/FDN_W3_20261104_185442/CLOSED_RESULT.json) 和 [迁移资格摘要](FDN_W3_4096_CLOSED_FOR_N20000_SOURCE.json)：64真实PPO、两套Adam各1280、12582912已优化转移；3110原生controls/24880 physics/6220 feedback；38 controls/155648转移是未优化pending。complete save、原父资格、inner+outer actual wait、原结清和释放均通过且errors=[]。原GO至父terminal派生1363.4290580749512 expert-seconds，不另写账、不退款。
- 完整保存202962459 B，SHA `47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d`，真实remote路径在迁移摘要；不为本交接或Git重开模型。
- 训练低趴credit仍0，独立原74恢复+6normal及新低趴8秒评测尚未执行，未晋升任何候选。

## N20000已完成源与实际stage/dispatch
[worker](source_fudan_native_worker_v3_20k/worker_fudan_sequence_ppo_native_v1.py)：675行/42683B/SHA `aa9a702303fd285d98f1c6a75f38066efd23365a6102c713a30c9bde983cb432`。
[一次源cache](source_fudan_native_worker_v3_20k/retained_learner_source_v1.py)：221行/13588B/SHA `3f29dac73a85025241044ec4a827bc0aa93b17f526b3121ef9d2948b5fa7618e`。
子agent已停止，不再改两源。父已窄审admit/真实CLI20000、source config/load、fullsave/clock/window/close与generic CPU guard。
- 原PPO核心保持，按源learner config构造并原 `load_state_dict` 完整承接actor/encoder/critic/STD/LR/两Adam/64累计计数/私有generator。fork_rng隔离初始化与载入，环境仍TASK.seed fresh流。母1cd实际读取0。
- 新20000环境/DR/history/queues经原sole reset产生；源整根CPU/raw/unknown字段及38步pending仅保留和强guard，未apply、未切片投影。不是全环境/PhysX位级resume。
- 每新update=960000已优化转移、两Adam各20；累计64+u，累计transitions12582912+960000u。root/UPDATE/FINAL/receipt/intent分别记录base、window与continuation；新窗0学习不会靠旧64变qualified。
- [nonPT stage结果](FDN_N20000_W4_STAGE_RESULT.json)：451完整依赖文件，原owner source-only preflight RC0，模型/SDK/GO/C操作0。旧源一条invalid escape SyntaxWarning保留，不是stage失败。
- [原父派发](FDN_N20000_W4_ORIGINAL_OWNER_DISPATCH_RESULT.json)：19:54:53，outer actual-wait controller **1614620**。源stage/dispatch已消费，不重跑。
```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W4_20261104_195410_1793793250201118300
```

## 原资源等待，唯一observer
唯一活动collector **pwsh-b67b922602404065**，运行 [metadata脚本](collect_fudan_n20000_w4_window_once.py)，6000秒界/15秒，只取own metadata，不读模型/轨迹/预算，不改运行任务。已加真实 `FDN_FULL_LEARNER_CONTINUATION_INITIALIZED.json` 观测，base/window分列，后续从本collector拿actual GO、初始化与真实新增。
- 初始snapshot epoch1793793351.891811：worker identity None、更新None、原PREGO Errno11，不是训练或技能失败。
- [唯一只读等待原因](FDN_N20000_W4_ORIGINAL_RESOURCE_WAIT_CONTEXT.json)：19:57:52原canonical active_segment为 `MOD4_STANDING200_SCUT_RECIPE_V30_FLAT_1793786097220799900`，started_epoch1793793095.372965；remaining234314.1776611805是该时刻视图，不作后续写账依据。未查GPU、未读模型、未动锁或信号。
- 原父自行1800秒准入等待；若后来timeout，先收inner+outer实际wait/结清释放，保留0GO事实，再等真实资源释放后新unused purpose；不重放本根或另开竞争父。
- 只读诊断job `pwsh-65e51291f6e644a2`已完成0并收取；旧4k observer `pwsh-d1904ce6e51c48fb`也已完成0并收取。

## 保持的约束与下一步
原唯一canonical/charge_values、authority双EX/private GPU EX/finite训练SH-评测EX、reserve86412.86069250107、3900/3600/300窗、1800preGO，以及原2c/bae/400-k2000-d3/2.5ms×8/100Hz×2/TGS32,4/fullD0D7/10mm闭链单env重置全部保持；原gpu/account/environment和准入等待段字节同源。
后续：等原父真正GO与20000初始化/新增；正常保存收口后独立原74+6与合法低趴质量评估。旧N80 mean/core CPU测试均不重跑，N80源/stdlib parent qualifier未部署未执行、旧4k provenance待最小适配，不当作已评测。

## 需要一起保留的失败与Git
W1 zero-update Mapping失败和费用、W2 zero-GO timeout、W3真实64闭环均保留。N20000本地生成器曾在空新目录内遇缩进敏感source anchor断言、当时未写生成source文件，随后仅修生成器成功。子agent另有3个纯源工具失败：空Unix here-doc导致PowerShell ParserError(Python未启动)、strict fragment未匹配(未写目标)、动态shell source编辑被工具拦截(未执行)；随后直接FS edit完成，最后一次两文件AST/compile PASS。这些不是native/fixture失败；无新增CPU测试、真实PT读取、GPU或旧物理重跑用于源验证。
最新先前已核验commit `9e11cc7039bbc4a027f022193d09e02dad825dd3`。本阶段把W2 final/release、W3学习与64闭环、N80源、20000用户修正/完整续learner新源/451 stage/实际原准入等待合并一次唯一annotated trial；后续动态进度按时点保留，未完成项不写pass。feature-only，main只读。归档后的正式回执仍需后续有意义阶段补入，或用工具输出核验避免回执无限链。


## Archive scope
This snapshot preserves all earlier failures, W2 zero-GO timeout and original resource release, Admission3 real 64 PPO updates with both Adam states and the entire saved 4096 cohort, the user request for N20000, and the new isolated N20000 admission with full learner continuation plus fresh environment/DR/history stream cut. Source W3 has 3110 actual controls versus 3072 optimized controls; 38 pending controls remain source-only and are not invented updates. Cumulative and newly added window counters are separate. N20000 runtime status is only true at each captured timestamp; admission, initialized environments, CPU checks and update counts are not independent recovery success. N80 source implementations including the unused parent qualifier are not executed tests. The reference video whole-leg-same-end target remains uncovered by the constrained low-rise subtask. Source parity is not backend/hardware proof. Earlier models, all original 74-case grading, physics/DR/limits, H1 and Registryv12 remain preserved. Physical traces, weights and original media are path references, not reopened or copied for this archive. Later actual reports require a later meaningful stage, not replay of this archive.
