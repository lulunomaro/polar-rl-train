"""Publish the actually closed old-recipe window, not an exact-SCUT or one-hour skill pass."""
from pathlib import Path
import json,time
D=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_bytes())
tp=Path(read(D/'E0_HOUR_WINDOW_CLOSED_RESULT_PATH.json')['path']);ep=Path(read(D/'E0_HOUR_FROZEN_CLOSED_RESULT_PATH.json')['path']);t=read(tp);ev=read(ep);f=t['cases']['E0']['V2_MIGRATION_FINAL.json'];m=t['metadata'];e=m['OWNER_EXIT_ACTUAL.json'];o=m['OUTER_OWNER_WAIT_ACTUAL.json'];cw=t['cases']['E0']['PARENT_WAITED_ACTUAL.json'];go=t['cases']['E0']['GO_PRODUCTION.json'];metrics=ev['normal_metrics']
assert t['closed']is True and e['errors']==[]and all(e[k]is True for k in('all_own_children_waited','original_cost_settled','original_private_finite_authority_leases_released'))and o['original_owner_reaped']is True and o['actual_wait_returncode']==0 and cw['semantic_qualification']['qualified']is True
assert ev['closed']is ev['execution_qualified']is True and ev['skill_grader']is ev['full_skill_graduation']is None and metrics['controls']==1000 and metrics['physics_callbacks']==8000 and metrics['feedback_samples']==2000
u=f['completed_actual_updates'];full=f['fullsave'];latest=f['latest_complete_save'];assert latest==full['latest_complete_save']and f['error']is None and f['source_env_state_applied']is False and u>0
assert latest['sha256']=='f326418aea63a9a73b06fb887de88426b856c904048aa5fcea3d4c3c994b487b'and latest['bytes']==104430359
live=full['live_core'];assert len(live['Adam17_steps'])==17 and set(live['Adam17_steps'])=={641600+20*u}
recipe=read(D/'E0_HOUR_CURRENT_RECIPE_SOURCE_READBACK_V1.json');stop=read(D/'E0_HOUR_SCUT_ALIGNMENT_STOP_REQUEST_V1.json');assert recipe['root']==t['root'] and recipe['root'].endswith('/'+stop['run_id']) and stop['complete_own_save_and_exit_only'] is True
health=metrics['unique_envs_terminated']==0 and metrics['max_current_mimic_rad']<=.01 and metrics['max_current_closure_m']<=.01
result=dict(kind='MOD4V2_E0_D6_OLD_RECIPE_STOPPED_FOR_SCUT_ALIGNMENT_ACTUAL_QUALITY_V1',epoch=time.time(),training_closed_path=str(tp),training_root=t['root'],source=dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700/roles/E0/production/model_final_complete.pt',bytes=14035411,SHA=go['source_SHA'],source_iteration=32004,source_Adam17_step=641600),complete_candidate=latest,actual_new_updates=u,actual_Adam_delta_each=20*u,optimized_transitions=u*24*20000,live_core=live,training_timing=f.get('training_timing'),stop_reason=f.get('stop_reason'),GO_to_outer_wait_metadata_only_seconds=o['epoch']-go['learning_started_epoch'],not_new_budget_or_ledger=True,actual_owner_exit=e,actual_outer_wait=o,actual_child_semantic=cw['semantic_qualification'],eval_closed_path=str(ep),eval_root=ev['root'],execution_qualified=True,normal_metrics=metrics,health_prerequisite_passed=health,full_skill_graduation=None,registered_SCUT_recipe_aligned=False,actual_inherited_recipe_source_receipt='E0_HOUR_CURRENT_RECIPE_SOURCE_READBACK_V1.json',reason='Existing25V3-derived term0/value2 and source formulas/commands differ from registered V14Flat-v0; own complete-boundary STOP_SAVE, no live source patch',not_a_completed_one_hour_effective_training_claim=True,reference_report='SCUT_ORIGINAL_TRAINING_ALIGNMENT_V1.md',reference_actor_critic_action=[35,78,6],MOD4_compatible_actor_critic_action=[35,38,6],interface_difference_not_exact_upstream_observation_claim=True,decision='KEEP_FORMAL_E0_NO_PROMOTION_PRESERVE_OLD_RECIPE_CANDIDATE_ALIGN_NEW_SOURCE_ONLY',other_eight_not_started=True,old_Registry_and_formal_mothers_unchanged=True,no_paired_causal_improvement_claim=True,goal_complete=False,publisher_model_raw_GPU_SDK_C_operations=0)
jp=D/'E0_D6_STOP26_QUALITY_V1.json';mp=D/'E0_D6_STOP26_QUALITY_V1.md';assert not jp.exists()and not mp.exists();jp.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8')
timing=result['training_timing']or{}
text=f'''# E0 D6旧配方 STOP_SAVE闭合与独立评测（非SCUT完全对齐/非毕业）

- 实际N20000/T24，{u}新PPO，17Adam各+{20*u}，{u*480000:,}优化transitions；没有20更新硬停，因核实参考配方不一致按原STOP_SAVE完整边界退出，未热改源/奖励/物理，无退款/新账/扩窗。
- 完整candidate `{latest['path']}`，{latest['bytes']}B/SHA `{latest['sha256']}`；原RSL实记iter{live['iteration']}，Adam17{live['Adam17_steps'][0]}、LR{live['source_LR']}，不是推算label。旧母本与此前candidate均保留。
- 实际SDKclose/child和outer wait/原costsettle/资源释放semantic合格；GO到outer {result['GO_to_outer_wait_metadata_only_seconds']:.3f}s仅解释元数据，不冒称有效PPO/整小时或重写账。
- Timing（Python调用wall不等于GPU纯kernel时间）：startup {timing.get('native_and_load_startup_seconds')}s；rollout step调用{timing.get('rollout_step_call_wall_seconds')}s；PPO update调用{timing.get('PPO_update_call_wall_seconds')}s；完整save{timing.get('own_complete_save_wall_seconds')}s；loop排save {timing.get('observed_loop_wall_seconds_excluding_complete_save')}s。未运行满一小时是明确源配方修正停止，不是假装小时已完成。

## 独立原E0 N80/fullDR/1000ctrl/20s/seed20260928

|项目|实际结果|
|---|---:|
|execution资格|合格；实际wait/FINAL-intent/ERROR/释放已核验|
|发生物理终止的env|{metrics['unique_envs_terminated']}/80|
|mimic终止|{metrics['termination_events_by_reason'].get('mimic')}|
|bad_orientation终止事件|{metrics['termination_events_by_reason'].get('bad_orientation')}|
|timeout事件|{metrics['termination_events_by_reason'].get('time_out')}|
|max当前mimic|{metrics['max_current_mimic_rad']:.9f}rad|
|替代传动保留原mimic健康门|.01rad未改|
|max当前闭环|{metrics['max_current_closure_m']:.9f}m|
|vx/vy/yaw MAE|{metrics['body_velocity_MAE']}|
|max raw/applied action|{metrics['max_raw_action_abs']}/{metrics['max_applied_action_abs']}|
|完整原始二元/profile grader|缺失，null；不编毕业|

D6这一次实际评测未再发生mimic终止，但姿态和跟踪仍不合格；不同候选/不同物理后端单cohort不作配对因果改善。42个独立env物理终止与80次姿态事件不是同一分母。RC0/26更新/mimic0都不等于技能成功。原终止和健康阈值未放宽、无reset拼接。

## 用户原版SCUT要求

已核当前purpose源+选定环境：RM_SCUT_TERM_W0、value_loss2，实际注册V14Flat-v0 termination -200（每control原dt.02后为-4）/value_loss4，另有sigma/deadzone/clamp/命令课程/终止差异；不是改两个数字就称一致。参考链见[完整源报告](<F:/RMPOLAR-RL/mod4v2_expert_normalization_20261105/SCUT_ORIGINAL_TRAINING_ALIGNMENT_V1.md>)。上游critic78，现完整A0 critic38是明确MOD4兼容接口适配，不以shape或名字相同声称原版观测全等；保已学STD/normalizer/Adam/LR，不切片伪exactresume。

新奖励/命令/课程/终止仅允许逐项上游源公式和原权重、机械/量纲/接口必要映射，缺项明确；不自造reward、混Flat1/2/Rough或把landing充起身。新源码尚待交付/原生证据；其他8专家未启动。正式E0 source/旧Registry不改，不晋升f326，goal664仍active。所有真实失败/诊断/D6修复/训练/评测/配方差异与本报告待下一meaningful feature-only唯一annotated归档；不为Git开模型/raw或重放旧once/物理，main只读。

证据：[train close](<{tp.as_posix()}>)/[eval close](<{ep.as_posix()}>)/[quality JSON](<{jp.as_posix()}>)/[actual recipe](<{(D/'E0_HOUR_CURRENT_RECIPE_SOURCE_READBACK_V1.json').as_posix()}>)/[stop receipt](<{(D/'E0_HOUR_SCUT_ALIGNMENT_STOP_REQUEST_V1.json').as_posix()}>).
''';mp.write_text(text,encoding='utf8');print(json.dumps(dict(report=str(mp),new_PPO=u,optimized_transitions=u*480000,health=health,metrics=metrics,training_timing=timing,registered_SCUT_recipe_aligned=False,decision=result['decision'],goal_complete=False),indent=2))
