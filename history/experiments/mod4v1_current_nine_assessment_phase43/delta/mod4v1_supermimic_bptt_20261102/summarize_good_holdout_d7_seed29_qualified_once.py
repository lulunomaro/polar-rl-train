"""Summarize published closed metadata only; no original case/model/trajectory reread."""
from pathlib import Path
import hashlib,json,time
R=Path(__file__).resolve().parent;pointer=json.loads((R/'GOOD_HOLDOUT_D7_SEED20260929_LATEST_CLOSED_RESULT_PATH.json').read_bytes());p=Path(pointer['result']);out=R/'reports/GOOD_HOLDOUT_D7_SEED20260929_QUALIFIED_SUMMARY_V1.json';md=R/'GOOD_EXPERT_HOLDOUT_SEED20260929_QUALIFIED_RESULTS_V1.md';assert not out.exists()and not md.exists();assert pointer['seed']==20260929 and pointer['passed_closed_good_reference_execution']is True and p.is_absolute()and p.resolve().is_relative_to((R/'reports').resolve())and p.name=='CLOSED_RESULT.json'and p.is_file()and not p.is_symlink();raw=p.read_bytes();q=json.loads(raw);stage=json.loads((R/'reports/GOOD_HOLDOUT_D7_SEED20260929_ACTUAL_STAGE_V1.json').read_bytes());assert q['kind']=='GOOD_HOLDOUT_CLOSED_RESULT_V1'and q['root']==pointer['root']==stage['root']and q['group_id']==stage['group_id']and q['seed']==stage['seed']==20260929 and q['requested_roles']==['CURB_PROTECTED878','SLOPE135']and q['status']==pointer['status']=='CLOSED_GOOD_REFERENCE_SOURCE_GRADE_AND_ACTUAL_WAITS';assert q['passed_closed_good_reference_execution']and type(q['gates'])is dict and q['gates']and all(v is True for v in q['gates'].values())and q['errors']==[]and type(q['actual_outer_parent_returncode'])is int and q['actual_outer_parent_returncode']==0 and len(q['own_child_waits'])==2 and {x['role']for x in q['own_child_waits']}=={'CURB_PROTECTED878','SLOPE135'}and all(x['actual_waited']and type(x['returncode'])is int and x['returncode']==0 for x in q['own_child_waits'])
conditions=q['conditional_original_scope_results'];expected=dict(controls=750,physics=6000,feedback=1500,actor_calls=750,source_actual_BPTT_policy_steps=0)
for role in('CURB_PROTECTED878','SLOPE135'):
 assert q['observed_counts'][role]==expected;v=conditions[role];assert all(v[k]is None for k in('whole_skill_rate','new_acceptance_predicate','full_expert_graduation'))
 for direction in('ascending','descending'):
  value=v[direction];assert type(value['denominator'])is int and value['denominator']==27 and all(type(value[key])is int and 0<=value[key]<=value['denominator']for key in('complete','contact_confirmed'));assert all(type(value[key])in(int,float)and 0<=value[key]<=1 for key in('complete_rate','contact_confirmed_rate'))
 value=v['stand'];assert type(value['denominator'])is int and value['denominator']==26 and type(value['no_failure'])is int and 0<=value['no_failure']<=value['denominator']and type(value['no_failure_rate'])in(int,float)and 0<=value['no_failure_rate']<=1
v=dict(kind='QUALIFIED_GOOD_ORIGINAL_CONDITIONAL_HOLDOUT_SINGLE_SEED_METADATA_SUMMARY_V1',epoch=time.time(),root=q['root'],seed=q['seed'],closed_metadata=dict(path=str(p),bytes=len(raw),SHA256=hashlib.sha256(raw).hexdigest()),passed_closed_execution=True,gates=q['gates'],observed_counts=q['observed_counts'],own_child_waits=q['own_child_waits'],actual_outer_parent_returncode=q['actual_outer_parent_returncode'],conditional_original_scope_results=conditions,errors=[],producer_grade_rewritten=False,prior_seed29_failed_run_promoted=False,mother_registry_H1_or_policy_changed=False,relative_improvement=None,matched_UID_pose_cohort=None,multiseed_holdout_completed=False,full_expert_graduation=None,Gate1='UNKNOWN',stage2_GO=False,original_case_model_raw_SDK_C_or_resource_opens=0)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
ROW_TEMPLATE='| {label} | {ascending_complete}/{ascending_denominator}（{ascending_complete_rate:.2%}） | {ascending_contact}/{ascending_denominator}（{ascending_contact_rate:.2%}） | {descending_complete}/{descending_denominator}（{descending_complete_rate:.2%}） | {descending_contact}/{descending_denominator}（{descending_contact_rate:.2%}） | {stand_no_failure}/{stand_denominator}（{stand_no_failure_rate:.2%}） |'
table_rows=[]
for role,label in(('CURB_PROTECTED878','C878'),('SLOPE135','S135')):
 value=conditions[role];table_rows.append(ROW_TEMPLATE.format(label=label,ascending_complete=value['ascending']['complete'],ascending_denominator=value['ascending']['denominator'],ascending_complete_rate=value['ascending']['complete_rate'],ascending_contact=value['ascending']['contact_confirmed'],ascending_contact_rate=value['ascending']['contact_confirmed_rate'],descending_complete=value['descending']['complete'],descending_denominator=value['descending']['denominator'],descending_complete_rate=value['descending']['complete_rate'],descending_contact=value['descending']['contact_confirmed'],descending_contact_rate=value['descending']['contact_confirmed_rate'],stand_no_failure=value['stand']['no_failure'],stand_denominator=value['stand']['denominator'],stand_no_failure_rate=value['stand']['no_failure_rate']))
text='''# C878 / S135：独立seed20260929原条件口径合格闭合执行的实际条件结果

| 专家 | 上行完成 | 上行接触确认 | 下行完成 | 下行接触确认 | 站立无失败 |
|---|---:|---:|---:|---:|---:|
PUBLISHED_CONDITIONAL_TABLE_ROWS

表中n/N来自原published完整conditions，百分比仅格式化其各自原rate；完整JSON原值保留。合格闭合执行由原sourcegrade/等待/EX/无错误判定，不等于质量100%。完成和接触确认分列，站立不混入crossing分母。

两者各N80、750控制、6000物理callback、1500反馈、750actor调用；新策略BPTT=0。使用原fullDR、原独立seed/方向和站立predicate，未降低速度、物理或接受条件。SOURCE grade、两worker actual wait、外层original parent actual Popen.wait、两项EX释放与完整原字节metadata均通过，errors=[]。这是既有好专家策略的独立保持性结果，不是SuperMimic训练收益；母本/Registryv12/H1未变。

## 范围与保留

这是单个新holdout seed的原方向/站立条件分母。whole_skill_rate / full_expert_graduation仍null；不把站立混入crossing分母，也不合成整个专家≥90%、八专家平均或RM70实场证明。本单seed摘要不合并另一seed；跨seed保持汇总由父沿原独立双seed接口处理，本摘要不声明multiseed_holdout_completed。历史seed29旧D6运行因为关闭证据链限长失败，保持失败、无补intent或升级资格。新D7仅专用case-FINAL有限2MiB及独立reader selector修复，完整内容/原close顺序/原门保留。

[原合格CLOSED](<PUBLISHED_CLOSED_METADATA_PATH>) · [完整小摘要](<PUBLISHED_SINGLE_SEED_SUMMARY_PATH>)

当前模型接口重建仍Stage1/Gate1 UNKNOWN/Stage2=false。本报告只重用已发布本地CLOSED metadata；没有重读原case/模型/trajectory或重跑SDK以制表。
'''
text=text.replace('PUBLISHED_CONDITIONAL_TABLE_ROWS','\n'.join(table_rows)).replace('PUBLISHED_CLOSED_METADATA_PATH',p.as_posix()).replace('PUBLISHED_SINGLE_SEED_SUMMARY_PATH',out.as_posix())
with md.open('x',encoding='utf8')as f:f.write(text)
print(json.dumps(dict(summary=str(out),report=str(md),qualified=True,conditions=conditions,stage2_GO=False),indent=2))
