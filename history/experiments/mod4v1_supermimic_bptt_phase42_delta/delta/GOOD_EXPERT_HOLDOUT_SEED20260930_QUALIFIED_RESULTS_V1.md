# C878 / S135：独立seed20260930原条件口径合格复测

| 专家 | 上行完成且接触确认 | 下行完成且接触确认 | 站立无失败 |
|---|---:|---:|---:|
| C878 | 27/27（100%） | 27/27（100%） | 26/26（100%） |
| S135 | 27/27（100%） | 27/27（100%） | 26/26（100%） |

两者各N80、750控制、6000物理callback、1500反馈、750actor调用；新策略BPTT=0。使用原fullDR、原独立seed/方向和站立predicate，未降低速度、物理或接受条件。SOURCE grade、两worker actual wait、外层original parent actual Popen.wait、两项EX释放与完整原字节metadata均通过，errors=[]。这是既有好专家策略的独立保持性结果，不是SuperMimic训练收益；母本/Registryv12/H1未变。

## 范围与保留

这是单个新holdout seed的原方向/站立条件分母。whole_skill_rate / full_expert_graduation仍null；不把站立混入crossing分母，也不合成整个专家≥90%、八专家平均或RM70实场证明。独立多seed保持评测尚未全部完成；历史seed29旧D6运行因为关闭证据链限长失败，保持失败、无补intent或升级资格。新D7仅专用case-FINAL有限2MiB及独立reader selector修复，完整内容/原close顺序/原门保留。

[原合格CLOSED](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_D7_SEED20260930_ACTUAL_CLOSED_20261104_074235/CLOSED_RESULT.json>) · [完整小摘要](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_D7_SEED20260930_QUALIFIED_SUMMARY_V1.json>)

当前模型接口重建仍Stage1/Gate1 UNKNOWN/Stage2=false。本报告只重用已发布本地CLOSED metadata；没有重读原case/模型/trajectory或重跑SDK以制表。
