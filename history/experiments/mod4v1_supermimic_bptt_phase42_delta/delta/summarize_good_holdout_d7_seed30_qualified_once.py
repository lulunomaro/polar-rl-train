"""Summarize published closed metadata only; no original case/model/trajectory reread."""
from pathlib import Path
import hashlib,json,time
R=Path(__file__).resolve().parent;p=R/'reports/GOOD_HOLDOUT_D7_SEED20260930_ACTUAL_CLOSED_20261104_074235/CLOSED_RESULT.json';out=R/'reports/GOOD_HOLDOUT_D7_SEED20260930_QUALIFIED_SUMMARY_V1.json';md=R/'GOOD_EXPERT_HOLDOUT_SEED20260930_QUALIFIED_RESULTS_V1.md';assert not out.exists()and not md.exists();raw=p.read_bytes();q=json.loads(raw);assert q['passed_closed_good_reference_execution']and all(q['gates'].values())and q['errors']==[]and q['actual_outer_parent_returncode']==0 and len(q['own_child_waits'])==2 and all(x['actual_waited']and x['returncode']==0 for x in q['own_child_waits']);assert q['seed']==20260930
conditions=q['conditional_original_scope_results'];expected=dict(controls=750,physics=6000,feedback=1500,actor_calls=750,source_actual_BPTT_policy_steps=0)
for role in('CURB_PROTECTED878','SLOPE135'):
 assert q['observed_counts'][role]==expected;v=conditions[role];assert all(v[k]is None for k in('whole_skill_rate','new_acceptance_predicate','full_expert_graduation'));assert all(v[d]['denominator']==v[d]['complete']==v[d]['contact_confirmed']==27 for d in('ascending','descending'))and v['stand']['denominator']==v['stand']['no_failure']==26
v=dict(kind='QUALIFIED_GOOD_ORIGINAL_CONDITIONAL_HOLDOUT_SINGLE_SEED_METADATA_SUMMARY_V1',epoch=time.time(),root=q['root'],seed=q['seed'],closed_metadata=dict(path=str(p),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest()),passed_closed_execution=True,gates=q['gates'],observed_counts=q['observed_counts'],own_child_waits=q['own_child_waits'],actual_outer_parent_returncode=q['actual_outer_parent_returncode'],conditional_original_scope_results=conditions,errors=[],producer_grade_rewritten=False,prior_seed29_failed_run_promoted=False,mother_registry_H1_or_policy_changed=False,relative_improvement=None,matched_UID_pose_cohort=None,multiseed_holdout_completed=False,full_expert_graduation=None,Gate1='UNKNOWN',stage2_GO=False,original_case_model_raw_SDK_C_or_resource_opens=0)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
text='''# C878 / S135：独立seed20260930原条件口径合格复测

| 专家 | 上行完成且接触确认 | 下行完成且接触确认 | 站立无失败 |
|---|---:|---:|---:|
| C878 | 27/27（100%） | 27/27（100%） | 26/26（100%） |
| S135 | 27/27（100%） | 27/27（100%） | 26/26（100%） |

两者各N80、750控制、6000物理callback、1500反馈、750actor调用；新策略BPTT=0。使用原fullDR、原独立seed/方向和站立predicate，未降低速度、物理或接受条件。SOURCE grade、两worker actual wait、外层original parent actual Popen.wait、两项EX释放与完整原字节metadata均通过，errors=[]。这是既有好专家策略的独立保持性结果，不是SuperMimic训练收益；母本/Registryv12/H1未变。

## 范围与保留

这是单个新holdout seed的原方向/站立条件分母。whole_skill_rate / full_expert_graduation仍null；不把站立混入crossing分母，也不合成整个专家≥90%、八专家平均或RM70实场证明。独立多seed保持评测尚未全部完成；历史seed29旧D6运行因为关闭证据链限长失败，保持失败、无补intent或升级资格。新D7仅专用case-FINAL有限2MiB及独立reader selector修复，完整内容/原close顺序/原门保留。

[原合格CLOSED](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_D7_SEED20260930_ACTUAL_CLOSED_20261104_074235/CLOSED_RESULT.json>) · [完整小摘要](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_D7_SEED20260930_QUALIFIED_SUMMARY_V1.json>)

当前模型接口重建仍Stage1/Gate1 UNKNOWN/Stage2=false。本报告只重用已发布本地CLOSED metadata；没有重读原case/模型/trajectory或重跑SDK以制表。
'''
with md.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps(dict(summary=str(out),report=str(md),qualified=True,conditions=conditions,stage2_GO=False),indent=2))
