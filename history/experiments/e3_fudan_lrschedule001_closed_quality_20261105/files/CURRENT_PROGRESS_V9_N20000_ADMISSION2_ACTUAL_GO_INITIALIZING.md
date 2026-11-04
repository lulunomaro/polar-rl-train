# N20000 Admission2真实GO，正在初始化；尚无新更新证据

## 当前目标
Goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` rev3 active/armed，max14，roundsStarted1。只做E3复旦五帧监督编码器+PPO质量/起身；用户明确N20000/T48。H1/其它专家/Registryv12/1cd母版不变。4096窗真实64PPO/两Adam各1280/12582912优化转移已完整保存收口，不能与新20k计数混为一窗。

## 已结束的W4与释放观察
W4原1800秒preGO窗20:24:54超时，0GO/0SDK/0model/0新更新；errors保留，inner+outer wait/settle/releases真。旧根与once不重放。[W4 CLOSED](reports/FDN_N20000_W4_20261104_195548/CLOSED_RESULT.json)。
只读观察job **pwsh-3af039d76e89496d**已完成0且输出收取：[观察结果](FDN_AFTER_N20000_W4_ORIGINAL_AUTHORITY_WATCH_RESULT.json) 在epoch1793796703.1734571观察原canonical owner None，remaining231080.1015341282，reader_gaps0；未GPU/锁/SDK/model/C写。None不是eligibility替代；后续确由原父重核全部门槛。

## W5新根与真实准入
20:42:18仅nonPT stage451/preflightRC0，原训练v3双源/owner/stager/core/actual4k64来源全不改。20:53:23派发新原父，controller **1616377**，原父 **1616384**。不与旧W4并发、不重放旧根。
```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LEARNER_CONTINUE64_W5_ADMISSION2_20261104_204218_1793796138143516800
```
[First actual admission](reports/FDN_N20000_W5_20261104_205335/FIRST_ACTUAL_ADMISSION.json)：
- GO **1793796864.332392 = 20:54:24**；worker **1616433**（同PID由bash exec为glibc loader/Python，不是第二worker）。
- 原authority双EX/private GPU0_EX/finite_SH全部真，inherited FDs3,4,5,6；唯一canonical writer original parent1616384。
- fresh GPU UUID `GPU-16828f91-2b45-b646-8dc0-9481138e2842`，RTX4090/free24203MiB/util0/compute-empty；RAM532250439680B/disk254332534784B。均原父实际门槛，不是额外probe。
- original save_deadline1793800464.332392/nominal_end1793800764.332392/headroom300/max3900。它们是已绑定窗口参数，不是完成时间承诺。
- 第一snapshot Native initialization/update/error/FINAL均null，terminal/pending空，owner training_num_envs20000。尚未证明N20k环境初始化完成或新PPO，不能拿已继承64当新更新。
- snapshot仍留旧PREGO_RESOURCE_WAIT Errno11文件，但它的epoch1793796833早于GO，**不是当前仍等待**；已有真实GO/ROOT/PID证明状态已转变。

唯一活动本地observer **pwsh-6639fa6ff84148d3**，运行[W5 collector](collect_fudan_n20000_w5_admission2_window_once.py)，6000s/15s只读ownmetadata，不读model/raw/canonical。输出目录[W5 reports](reports/FDN_N20000_W5_20261104_205335)；实际close后才生成CLOSED与LATEST_CLOSED指针。勿重复启动collector/worker/parent。

## learner续接边界
实际input是W3完整64保存202962459B/SHA `47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d`，不是重开1cd；GO.teacher_sha仍1cd是祖先元数据。保留完整模型/STD/LR/两Adam/私有generator/计数，source一次物理read/hash/CPUdecode缓存；新env/DR/history/queues/globalRNG fresh sole reset，源4096及38未优化pending不apply。非PhysX整环境位级resume。每新更新20k×48=960000转移、两Adam各20，累计base64与newwindow分开。source CPU未知字段保留，完整newenv与pending仍全保存。

## 评测与source-only工作
[source_fudan_frozen_native_eval_v2_n20000](source_fudan_frozen_native_eval_v2_n20000)七py和[source_fudan_frozen_parent_v2_n20000](source_fudan_frozen_parent_v2_n20000)三py已定稿/AST；数学/14pi/history/clip6保持，provenance改真实4k source+base+正window+20k。parent原resource与finally cleanup/wait/release代码块相同，只改one-E3/Task与actual p.wait后AND资格。均未执行native评测，无新Torch/CPUfixture；老唯一core与N80×9合成测试不重跑。
同一子agent `3b92c2b6-8850-4ad3-857f-77fc0e518590`仅写 `stage_fudan_n20000_frozen_original_once.py` 单源：使用原完整nonPT materializer/zip/runtime/lib/assets/static NPZ，实际正N20k CLOSED门槛与10py overlay；不stage/SSH/模型/SDK/GPU/Git。已说明真实FINAL无顶层num_envs，要用continuation+INIT.fresh_envs+UPDATE.rollout_N/T/native计数证明，不虚构字段。交付后父审，实际train完整收口后才执行。
独立原评测固定N80/160/seed20260928/74firstepisode+6normal/fullDR/one reset/无lowrise26patch；独立合法低趴8秒及31体MuJoCo质量仍未执行。训练计数、PID、RC0、AST都不是技能通过。

## Git与下一步
最新feature-only已核验 `ebf1ecf8370e7ce2541b9b2747a6fb5f07af32f1`，tag `trial-20261104-e3-fudan-64closed-n20000-native-admission` / obj `e7ac4e07f7b3ce8ea2e1f42c926259f1bd47149a`，231 entries，main仅只读。已消耗归档脚本不重放。
之后W4 timeout/释放、V2七源/三parent、W5三助手CRLF静态失败及补collector AST、451 stage/真实GO、新handoff与后续native证据合并下一有意义trial。跳过模型/raw/大二进制在stat/read/hash之前；不为Git重跑物理。
下一步优先观察sole collector的N20k初始化与正window实际梯度更新；完整原关SDK/实际inner+outerwait/原账结清/释放后再做独立质量评测。不改原2c/bae模型、PD/气弹簧/关节限位/fullDR，不清外国锁/信号/改账/退款/扩窗或扩预算。
