# v23：E3/W35实际保存模型只读CPU诊断完成；原母本不变

2026-11-03 14:43 +08:00。Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 最近revision13/activearmed/round8/max48。用户优先原技能/鲁棒性/保持，updates仅过程。H1/Registryv12/全部母本不变，80/90独立multi-seed未达，E0/S50原binary authority仍null。原2c/bae/400-k2000-d3/50-100Hz/.0025/TGS32,4/.01闭链/.01mimic/fullD0D7/原速度/原接受/Csinglewriter/reserve/authority/privateEX/trainSH-evalEX/3900-3600-300/1800不变。当前无自己的GPU训练/评测/资源observer。

## 新的实际只读CPU证据（不是技能分数或归因）

前序三组原口径实际qualified结果和Phase28核验见[v22](<CURRENT_PROGRESS_v22_PHASE28_VERIFIED_BOUND_NOT_PROMOTED_THREE_SOURCE_TASKS_ACTIVE.md>)。E3教师/unbounded/bound均0/74；normal6首次物理term0/6、6/6、0/6单列。W35moving19/63、10/69、14/60；standing26/26、16/17、13/22；single-seed/自然cohort不同/保留partial/relative与causal null，KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION。零更新bound不是训练收益，原90目标仍未达。

NEW保存回放诊断实际完成：
- [E3 actual CPU](<reports/ACTUAL_SAVED_REPLAY_CONSISTENCY_E3_V1.json>) job `pwsh-d8f0bfbfc03a4507` RC0/已收；[W35 actual CPU](<reports/ACTUAL_SAVED_REPLAY_CONSISTENCY_W35_V1.json>) job `pwsh-57dee4fc1fd940d1` RC0/已收。
- 每角色只物理打开本人已关闭A1 complete一次、SHA一次、weights_only CPU decode一次；E3 a4c56390…/236664417B、W35 b2f2878f…/233435425B，完整root留CPU，model/aux/pi严格复制加载，不恢复optimizer/RNG/env/history，不打开mother；0SDK/0GPU/0BPTT/0canonical。whole-root/live identity/version/value与全局Torch/Python/NumPy RNG实际前后守恒。
- 原 FINAL/TASK四JSON exact bytes/SHA与predecode六字段实际核对通过：[pins](<reports/REPLAY_DIAGNOSTIC_ACTUAL_FINAL_TASK_PINS_V1.json>)；E3 FINAL7039/72758fe2…、TASK2139/bffd72c3…；W35 FINAL7151/0bfb564e…、TASK2173/cbe4f381…，不是汇总重序列化pin。job `pwsh-d9a01c6bb4ae441d` RC0/已收。
- 先有NEW真实Torch CPU synthetic smoke：[receipt](<reports/REPLAY_CONSISTENCY_TORCH_SMOKE_V1.json>) job `pwsh-3e7ba0b4766d44ab` RC0/已收，T48N2ptr17、真实WM/aux/MLP teacher、两档matched H16、history10、值/版本/RNG正负对照通过，真实checkpoint0。另 [exact source_runtime import-only predecode](<reports/REPLAY_DIAGNOSTIC_IMPORT_PREDECODE_V1.json>) job `pwsh-fbfc8ce2fa7e4ad4` RC0/已收，PyRandom跨import相同/无CUDA/无模型实例或PT/JSON，补足toy snapshot覆盖差异。
- 独立[源码审阅](<source_replay_diagnostic_parent_review_v1/REPLAY_DIAGNOSTIC_PARENT_SOURCE_REVIEW_V1.md>) 7514B/b0a9b87c…与JSON9323B/745a932d…由a194封件；22stdlib/AST/17sourcehash，NO_CONFIRMED_SOURCE_BLOCKER，不称运行保证。父已全读738行并review其早失败try/finally覆盖限制；本次actual两例所有guard均完成，但不删除源风险记录。源码诊断a372478e…/42537B及原8文件无编辑。

[人读诊断](<ACTUAL_REPLAY_CONSISTENCY_FINDINGS_V1.md>) / [压缩机器事实](<reports/ACTUAL_REPLAY_CONSISTENCY_COMPACT_FACTS_V1.json>) 只从两份已出版诊断提取，不重开PT/raw或重新评分。人读表格作一次排版修正，不重跑实验/summary once。两角色各一阶64、actor64、matchedH16 windows32：

|事实|E3|W35|
|---|---:|---:|
|一阶位置MAE m|.000464182|.000249724|
|一阶旋转MAE rad|.00211593|.00146179|
|一阶关节q MAE rad|.0447666|.00638273|
|真s1奖励头MAE / 原reward样本std|.0061548 / .136134|.0028826 / .00969654|
|H16 conditional位置/旋转/q MAE|.00377271 / .00824619 / .134548|.00198309 / .00517479 / .0685096|
|H16 FULL位置/旋转/q MAE|.00559255 / .0262374 / .167317|.00381902 / .0238579 / .0838976|
|H16 conditional→FULL sensor16 MAE|.0325883→.066328|.0312125→.0561137|
|H16累计原reward MAE conditional→FULL|.049552→.0807109|.0309945→.0393607|

E3 sampled scaled residual RMS六项 `[.98719,6.95953,11.48828,1.83750,3.67098,.72069]`，actor−clipped teacher max可达7.38749；W35六项 `[.08309,.17515,.27187,.25012,.14052,.07838]`，差max .71270。说明实际learned .05*unbounded并不是.05硬界；这只是记录history上的mean，不是actor新actions未来标签。teacher本身的clip saturation也须一起看，不能把所有clipping都归于残差。E3 done正例1/64、W35 0/64；W35低Brier不证明终止识别。实际context里哪些recovery字段/offset/mask、frames/ep_step与所有排除数在原完整JSON，不造UID/phase。

**解释边界：POSTHOC_REPLAY_RESUBSTITUTION。** replay可能已用于训练，不是heldout/generalization/原技能/因果。conditional每步true xi/a_prev/f仅state连续；FULL只初始真值、之后WM+aux+savedmask+legacyproject沿记录clip6 raw manager commands，不是延迟后物理torque，也不是actor反事实。H16为完整survivor windows，排除done/cut/xi1_invalid，非原技能完整分母。原frames确实+1/recovery非普遍held；不拿“全held”当已证根因。当前证据优先提示审查残差漂移/长链context误差，而非盲目增加训练量/H32或把新reward权重当已选方案；尚未启用任何新训练。

## E3单因素奖励源码已封，仍disabled

[source reward目录](<source_e3_signed_upright_reward_review_v1/PROTOCOL_DISABLED_V1.md>) V1四件全保持：协议4251/92a23c…；stdlib测试14445/002886…；receipt2845/19a0dc…；manifest16638/8f9b47…，28/28 synthetic PASS，首轮仅1ulp tuple fixture失败后改14位almostEqual，公式未改，历史保留。新候选仅learner dense occupancy κ*.02*request_t*u(pre-reset s1)，κnull/enabledfalse；κ≤1/3只是reviewer禁用数学封套，非用户批准/历史/选定超参。原peak已有signedu，不能称总reward缺signed或已证倒立根因。action前request mask、298→300末步、terminal当步、normal6新项0、原reward分账/PBRS不保证均明确。无执行器。

封件后只加 [A1分层V2](<source_e3_signed_upright_reward_review_v1/A1_BASE_VIEW_LAYERING_APPEND_V2.md>) 2845/96ee6876…与refs3211/9a209ad1…：base bridge.obs有privileged拼接，但active qualified worker7c4298确实用Raw35ActorMDP bb7555覆盖obs=xi[:35]/offset0；reward-only未来baseline保留当前A1 legacy+transition_projector=None，不能退回A0或混actor/projector第二因子。

## 好专家holdout源码已封；materializer新任务进行中

`d66482f4-bbf6-4ad6-a2b4-231a32e6bf8a` 已交 [SOURCE_REVIEW](<source_good_expert_holdout_subset_v1/SOURCE_REVIEW_GOOD_EXPERT_HOLDOUT_V1.md>) 全102行父已读、API、20overlay+24原deps索引、21/21stdlib/fake/fullAST、40原indexed/另42映射pins不变；seal root `032c431b844aedc02bffad76549b9516f92e5cfd06cce6194e47d5f4451c7534`。原V1封件不动。C878/S135用实际0-update own A1 fullcapture内embedded原teacher，不称SM训练；C878 own ae4ac8d3…220144758B/teacher db3d5a6a…17621306，S135 own22d7ea42…220144758/teacher ec5b4956…17620922。母本不再为计数扰动。

明确走真实E1 wrappers→NEW e1worker→task.runtime_root canonical metadata→原route80factory→guard→唯一explicitreset→原step separate term/trunc→canonical OriginalEpisodeBoundary；不拿仅E0/E2/E3/W35的formal worker套角色。原E1 _run_loop、EndpointPredicate、reset/done/parent main资源/close/wait/finally AST保持，只显式seed/成员/metadata接口。seed20260929、20260930各独立purpose/group，N80/750control/27up27down26stand/6000physics1500feedback/D0D7/原predicate不变，单条件Wilson描述非IID/不称whole90。canonical7a092 alias独立/AppV6→fulldc4保留。**当前materialized/staged/dispatched/native_measurement均false**，20overlay不是完整runtime；原V8完整selected-role树/NPZNPYbanks/assets/deps/vendor7/实际producerTASK+MANIFEST+FINAL仍待真实materialize。

父已续派其NEW `source_stage_good_expert_holdout_v1`：只写一个stdlib --preflight-only/--stage CLI源码，不SSH/实际stage/dispatch/PT/SDK/C。需原GROUP_PLAN完整树、20PIN/canonical/App闭包、actual0producer源证据重导、metadata lexical.pt而实际PTstat/open/hash0、原资源无变更、固定STAGE_COMPLETE_GOOD_EXPERT_HOLDOUT_V1.json、两seed各absent root、无自动Popen。该新源码任务仍进行中，父稍后review再新purpose执行；没有声称新holdout已测或90。

## Git和下一步

Phase28 `ba10b8473bf644479028c7cadcdc455feb8dbeca` / annotated `0ddb5ccba6973952618bd2565cfede214dd733ba` 已feature/tag/peeled远端exact核验，main仅仅读；本次source/reviews/真实CPU smoke/import/pins/诊断/分层和好专家SOURCE+此handoff待Phase29归档。所有本轮hostjob上列均completed+收取；只有好专家materializer SOURCE子agent继续工作。下一步优先真实独立好专家保持holdout、根据已测一致性事实选择一个可复现短因素；不继续badlegacy只凑3000，不热换旧core/旧用途，未来GPUfullresume仍需显式new20fd两alias/sourceindex/producer守卫及原完整状态恢复验证。
