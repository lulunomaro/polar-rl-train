"""NEW bound-only quality screen from qualified closed JSON/grade receipts.
Metadata only: no selected checkpoints/raw telemetry, remote access, or promotion.
"""
from pathlib import Path
import json,math,hashlib,time
R=Path(__file__).resolve().parent
OUT=R/'reports/BOUND_ONLY_E3_W35_ORIGINAL_QUALITY_SCREEN_V1.json'
DOC=R/'BOUND_ONLY_E3_W35_ORIGINAL_QUALITY_SCREEN_V1.md'
assert not OUT.exists() and not DOC.exists()
evidence=[]
def read_json(p):
 raw=p.read_bytes();evidence.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()));return json.loads(raw)
def wilson(n,N):
 if not N:return None
 z=1.959963984540054;p=n/N;den=1+z*z/N;mid=(p+z*z/(2*N))/den;half=z*math.sqrt(p*(1-p)/N+z*z/(4*N*N))/den
 return [max(0,mid-half),min(1,mid+half)]
def e3(f):
 recipes=f['skill']['original_recovery_recipe_rows'];requested=[x for x in recipes if x['original_request']is True];normal=[x for x in recipes if x['original_request']is False]
 assert sorted(x['recipe']for x in requested)==list(range(12)) and len(normal)==1 and normal[0]['recipe']==12
 n=sum(x['first_episode_original_stable_credit']for x in requested);N=sum(x['initial_envs']for x in requested);assert N==74 and 0<=n<=N and normal[0]['initial_envs']==6
 return dict(n=n,N=N,rate=n/N,wilson95=wilson(n,N),recipe_rows=recipes,normal_recipe_excluded=normal)
prefix='BOUND_ONLY_E3_W35_V1_ADMISSION2'
ptr=read_json(R/(prefix+'_LATEST_CLOSED_RESULT_PATH.json'));closed=read_json(Path(ptr['path']))
assert closed['closed'] and closed['qualified_bound_probe_execution']is True and closed['actual_external_parent_wait_bound'] and closed['actual_Python_parent_PID_matches_launcher'] and not closed['early_controller_dead_without_wait_proof']
top=closed['top'];end=top['PARENT_EXIT_SCOPE.json'];wait=top['BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json'];term=top['TERMINAL_ROWS.json'];sg=top['BOUND_PROBE_GROUP_CLOSED_SOURCE_GRADE_V1.json']
assert end['all_own_children_waited'] and end['original_single_GPU_private_EX_released'] and end['original_global_finite_EX_released'] and not end['errors'] and end['canonical_writes']==0
assert wait['actual_parent_p_wait_returned'] and wait['returncode']==0 and not wait['controller_errors'] and wait['group_id']==closed['group_id']
assert sg['passed_closed_bound_probe_source_grade'] and len(term)==2 and all(x['actual_waited'] and x['passed_execution']for x in term)
finals={x['role']:x['FINAL']for x in closed['rows']};assert set(finals)=={'E3','W35'}
variant='A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_NATIVE_PROBE_V1'
for role,controls in [('E3',160),('W35',1600)]:
 f=finals[role];assert f['role']==role and f['num_envs']==80 and f['controls']==controls and f['policy_variant']==variant and f['optimizer_updates']==0
base=read_json(R/'reports/QUALIFIED_EMBEDDED_TEACHER_ORIGINAL_SKILL_BASELINE_V1.json')
old=read_json(R/'reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json')
assert base['qualified_reference_execution'] and old['qualified_reference_execution'] and old['qualified_candidate_execution'] and old['decision']=='KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION'
assert all(finals[r]['source_cache']['source_SHA']==base['actor_container_and_teacher'][r]['container_checkpoint_SHA']for r in finals)
gr=read_json(R/'reports'/(prefix+'_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json'))
assert gr['qualified_execution'] and gr['root']==closed['root'] and gr['case_root']==closed['root']+'/cases/W35' and gr['policy_variant']==variant and gr['probe_training_updates']==0 and gr['returncode']in(0,2)
g=gr['grade'];assert g['group_id']==closed['group_id'] and g['source_SHA']==finals['W35']['source_cache']['source_SHA'] and g['role']=='W35'
integrity=bool(gr['returncode']==0 and g['grading_integrity_verified'] and g['all_original_complete_population_coverage_verified'] and not g['integrity_errors'])
old_conditions={x['condition']:x for x in old['conditions']}
old3=old_conditions['ORIGINAL_REQUESTED_RECIPE0_TO11_FIRST_EPISODE_STABLE_CREDIT'];oldmoving=old_conditions['ORIGINAL_MOVING_VALID_SAME_UID_NATURAL_COMPLETE_NONTERMINAL'];oldstanding=old_conditions['ORIGINAL_STANDING_VALID_SAME_UID_NATURAL_COMPLETE_NONTERMINAL']
probe3=e3(finals['E3'])
conditions=[dict(role='E3',condition='original_requested_first_episode_credit',reference=base['E3']['original_requested_first_episode_credit'],unbounded_candidate=old3['candidate'],bound_probe={k:v for k,v in probe3.items()if k not in('recipe_rows','normal_recipe_excluded')}),dict(role='W35',condition='original_moving_natural_complete_nonterminal',reference=base['W35']['moving'],unbounded_candidate=oldmoving['candidate'],bound_probe=g['groups']['moving']),dict(role='W35',condition='original_standing_natural_complete_nonterminal',reference=base['W35']['standing'],unbounded_candidate=oldstanding['candidate'],bound_probe=g['groups']['standing'])]
normal=dict(reference=base['E3']['normal_recipe_excluded'],unbounded_candidate=old3['normal_candidate_excluded'],bound_probe=probe3['normal_recipe_excluded'],excluded_from_recovery_denominator=True)
point_screen80=bool(integrity and all(x['bound_probe'].get('rate')is not None and x['bound_probe']['rate']>=.8 for x in conditions))
v=dict(kind='QUALIFIED_ZERO_UPDATE_BOUND_ONLY_ORIGINAL_SKILL_SCREEN_V1',epoch=time.time(),qualified_bound_probe_execution=True,W35_grade_population_integrity_verified=integrity,reference_root=base['root'],unbounded_candidate_root=old['candidate_root'],bound_probe_root=closed['root'],policy_variant=variant,bound_probe_optimizer_updates=0,source_checkpoint_producer_training_counts_are_historical_not_probe_updates=True,original_scope=dict(num_envs=80,seed_from_fixed_original_source_contract=20260928,E3controls=160,W35controls=1600,original_physics_DR_speed_predicate_changed=False),conditions=conditions,E3_recipe_rows=probe3['recipe_rows'],normal_E3_recipe12_retention_diagnostic=normal,W35_all_original_groups=g['groups'],W35_grade_integrity_evidence={k:g.get(k)for k in('grading_integrity_verified','all_original_complete_population_coverage_verified','binding_evidence_gaps','metadata_evidence_gaps','integrity_errors','unknown_reason_counts')},actual_external_parent_wait=wait,actual_original_parent_exit_scope=end,matched_UID_pose_cohort=None,relative_improvement=None,causal_or_statistical_improvement_claim=None,independent_multiseed_final_acceptance=False,full_expert_pass_rate=None,bound_point_estimates_all_reach80pct_necessary_not_sufficient=point_screen80,decision='KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION',mother_checkpoint_registry_or_H1_mutated=False,new_training_scheduled=False,further_same_legacy_baseline_volume_scheduled_to_reach3000=False,next_actions=['Keep all mothers/candidates/failures and all original partial/reset/terminal exposures','Treat any difference as a zero-update deployment-constraint observation, not training benefit','Inspect per-condition pass/retention and integrity before selecting any single-factor short training segment','Require original complete acceptance and independent multiseed before promotion; E0/S50 missing binary authority stays null'],metadata_evidence=evidence,selected_model_raw_remote_SDK_C_or_promotion_operations=0)
OUT.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8',newline='\n')
def rate(x):
 n=x.get('n');N=x.get('N');p=x.get('rate');return f'{n}/{N}'+(f'（{100*p:.2f}%）'if p is not None else'（rate null）')
lines=['# 零更新 bound：原技能质量筛选 V1','','新探针已完成实际控制、原关闭与等待、原资源释放和源码/冻结检查。动作只把同权重残差映射由 `.05*delta` 换为 `.05*tanh(delta)` 后总clip6，优化器更新为0，观察差异不归作训练收益。','','| 原条件 | 原教师 | 原unbounded候选 | 本次bound探针 |','|---|---:|---:|---:|']
for x in conditions:lines.append('| '+x['role']+' '+x['condition']+' | '+rate(x['reference'])+' | '+rate(x['unbounded_candidate'])+' | '+rate(x['bound_probe'])+' |')
lines+=['','## 完整分母与保持诊断','']
for k in('moving','standing'):
 a=base['W35'][k];b=oldmoving['candidate']if k=='moving'else oldstanding['candidate'];c=g['groups'][k]
 lines.append(f'- W35 {k} partial（原教师 / unbounded / bound）={a["partial"]} / {b["partial"]} / {c["partial"]}；bound unknown={c["unknown"]}，original reset={c["end_reasons"].get("original_reset",0)}，物理term={c["terminated_before_reset_true"]}，trunc={c["truncated_before_reset_true"]}，Wilson95={c["wilson95"]}。partial不混入原conditional完整区间成功率，也不消失。')
for label in('reference','unbounded_candidate','bound_probe'):
 q=normal[label];lines.append(f'- E3正常recipe12（{label}）首次物理term={sum(x["first_episode_physical_terminated"]for x in q)}/{sum(x["initial_envs"]for x in q)}，独立于requested recipe0–11的74个恢复分母。')
lines+=['',f'W35原分组数据完整性已验证：`{integrity}`。同一seed但自然区间/episode并非已匹配cohort；matched UID/pose、relative、因果及统计提升均保留null，不把点估计差当因果。','','## 选择','','保持Registryv12 scoped best与所有母本/H1，暂不晋级候选；没有调度新训练，不为3000继续旧质量欠佳方案。80/90目标需要原接受与独立multi-seed，不由这一次点估计完成。','','[机器证据与所有分组](<reports/BOUND_ONLY_E3_W35_ORIGINAL_QUALITY_SCREEN_V1.json>)；[原教师/旧候选合格对照](<QUALIFIED_QUALITY_COMPARISON_E3_W35_V1.md>)。']
DOC.write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(report=str(OUT),human=str(DOC),qualified_bound_probe=True,W35_integrity_verified=integrity,probe_optimizer_updates=0,conditions=conditions,normal_retention=normal,decision=v['decision']),indent=2,ensure_ascii=False))
