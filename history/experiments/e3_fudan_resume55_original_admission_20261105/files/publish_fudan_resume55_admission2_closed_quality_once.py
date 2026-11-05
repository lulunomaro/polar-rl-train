"""Produced JSON only. No model/raw/canonical/SDK operations or preset score."""
from pathlib import Path
import json,time,math,statistics
D=Path(__file__).resolve().parent
ref=json.loads((D/'FDN_N20000_W14_RESUME55_ADMISSION2_COLLECTOR_ONCE.json').read_bytes());out=Path(ref['output']);files=dict(training=out/'CLOSED_RESULT.json',admission=out/'FIRST_ACTUAL_ADMISSION.json',original=D/'FDNRESUME55_FROZEN_ORIGINAL_SCOPE_RESULT.json',nominal=D/'FDN_RESUME55_MUJOCO31_LOWRise_RESULT.json',export=D/'FDNRESUME55_PI_ONLY_EXPORT_STARTED_ONCE.json',baseline=D/'FDN_LRSCHEDULE001_CLOSED_QUALITY_DECISION_V1.json')
a,ad,o,j,e,b=[json.loads(files[k].read_bytes())for k in('training','admission','original','nominal','export','baseline')];m=a['metadata'];f=m['FDN_FINAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json'];owner=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json'];base=dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)
assert a['closed']is True and owner['errors']==[]and all(owner[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['actual_wait_returncode']==0 and outer['original_owner_reaped']is True and q['qualified']is True and all(q['checks'].values())and f['version']==8 and f['complete_save']is f['final']is True and f['error']is None and f['close_errors']==[] and latest==f['latest_complete_save']
assert f['base_counters']==base and f['full_learner_resume']is True and f['inherited_old_iterations']==f['bad_candidate_reads']==0 and f['source_checkpoint']['source_sha256']=='55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7'
window=f['window_counters'];cum=f['counters'];u=window['updates'];n=f['native_counters'];controls=n['actual_native_policy_steps'];partial=controls-48*u
assert 0<u<=25 and window['policy_optimizer_steps']==window['encoder_optimizer_steps']==20*u and window['transitions_seen']==960000*u and all(cum[k]==base[k]+window[k]for k in base)and n['actual_native_transitions']==20000*controls and n['physical_callbacks']==8*controls and n['feedback_callbacks']==2*controls and n['termination_computations']==controls and 0<=partial<=48
assert o['execution_qualified']is True and all(o['execution_checks'].values())and o['actual_parent_wait_qualification']['qualified']is True and o['actual_parent_wait_qualification']['kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V8_RESUME55'
assert e['complete']is True and latest['sha256']==e['source']['sha256']==j['source_export']['sha256']==o['source_binding']['sha256']
s=o['original_worker_outcome_verbatim'];rr=s['original_recovery_recipe_rows'];falls=[r for r in rr if r['original_request']];normal=[r for r in rr if not r['original_request']];den=sum(r['initial_envs']for r in falls);credit=sum(r['first_episode_original_stable_credit']for r in falls);assert den==74 and len(normal)==1 and normal[0]['initial_envs']==6 and credit==s['original_first_episode_recovery_credits']
nominal={}
for role,rows in j['rows'].items():
 assert len(rows)==5 and all(r['controls']==400 and r['finite_execution_error']is None for r in rows)
 nominal[role]=dict(cases=5,complete_finite_cases=5,engineering_credits=sum(bool(r['credited_by_same_engineering_predicate'])for r in rows),credited_and_stable_at_end=sum(bool(r['credited_and_stable_at_end'])for r in rows),mean_final_height_m=statistics.mean(r['final']['height_m']for r in rows),mean_final_tilt_deg=statistics.mean(r['final']['tilt_deg']for r in rows),mean_final_speed_m_s=statistics.mean(r['final']['root_speed_m_s']for r in rows),mean_endpoint_xy_displacement_m=statistics.mean(math.hypot(*r['final']['root_xy_m'])for r in rows))
c=nominal['candidate'];mother=nominal['frozen_mother'];prior=b['nominal_MuJoCo31']['comparison']['candidate'];normal_bad=normal[0]['first_episode_physical_terminated']>b['original_N80']['normal_first_episode_physical_terminated'];positive=credit>0 or c['engineering_credits']>0
choice='PRESERVE_CONTINUED_CANDIDATE_PENDING_HOLDOUT_KEEP_REGISTRY_V12_UNCHANGED' if positive and not normal_bad else 'KEEP_REGISTRY_V12_AND_RETAIN55AFA_NO_CONTINUED_CANDIDATE_PROMOTION'
go=ad['actual_GO']['learning_started_epoch'];r=dict(kind='E3_COMPLETE55AFA_LEARNER_FINITE_CONTINUATION_QUALITY',epoch=time.time(),source=e['source'],candidate_full_save=latest,training=dict(base_counters=base,new_N20000=window,cumulative_counters=cum,current_native=n,full_saved_unoptimized_pending_controls=partial,full_learner_resume=True,source_checkpoint=f['source_checkpoint'],learner_continuation=f['learner_continuation'],actual_initialization=m['FDN_FULL_LEARNER_CONTINUATION_INITIALIZED.json'],last_update_optimizer_diagnostics=m['FDN_NATIVE_UPDATE.json']['learner_functional_metrics'],task_description_not_independent_grade=f['task_summary'],GO_to_outer_actual_wait_metadata_derived_seconds=outer['epoch']-go,not_budget_ledger_rewrite=True,original_owner_exit=owner,outer_wait=outer),original_N80=dict(execution_qualified=True,actual_original_parent_qualified=True,recovery_first_episode_credits=credit,original_request_denominator=den,normal_envs=6,normal_first_episode_physical_terminated=normal[0]['first_episode_physical_terminated'],requested_first_episode_physical_terminated=sum(r['first_episode_physical_terminated']for r in falls),recipe_rows=rr,controls=160,seed=20260928,no_reset_stitching=True),nominal_MuJoCo31=dict(comparison=nominal,published_source55_reference=b['nominal_MuJoCo31']['comparison'],not_native_fullDR_or_hardware=True),reserved_holdout_seeds=[20261002,20261003,20261004],new_native_low80_holdout_status='PENDING_NOT_A_ZERO_SCORE',paired_native_difference=None,decision=choice,H1_and_other_experts_unchanged=True,Registry_v12_and_selected_1cd_unchanged=True,all_complete_candidates_preserved=True,goal_complete=False,model_raw_canonical_IO=0)
paths=[D/'FDN_RESUME55_CLOSED_QUALITY_DECISION_V1.json',D/'FDN_RESUME55_CLOSED_QUALITY_RESULTS_V1.md',D/'CURRENT_PROGRESS_V28_RESUME55_CLOSED_QUALITY_RESULT.md'];assert not any(p.exists()for p in paths)
paths[0].write_text(json.dumps(r,indent=2,allow_nan=False),encoding='utf8');link=lambda p,label:f'[{label}](<{p.as_posix()}>)'
paths[1].write_text(f'''# E3完整55afa learner有限续接：实际质量

实际新增{u} PPO、两Adam各{window['policy_optimizer_steps']}、{window['transitions_seen']:,}优化转移；继承base25/500/24m，累计{cum['updates']}/{cum['policy_optimizer_steps']}/{cum['transitions_seen']:,}。新N20000/T48窗{controls}控制、{n['physical_callbacks']}physics、{n['feedback_callbacks']}feedback；未优化pending{partial}控制。完整候选{latest['bytes']:,}B，SHA `{latest['sha256']}`。原父actual inner/outer wait、成本结清/释放/errors=[]，GO到outer {outer['epoch']-go:.3f}s只是metadata解释，不改账。

**{choice}**。原E3严格firstepisode信用 **{credit}/74**，6normal物理终止{normal[0]['first_episode_physical_terminated']}/6不是normal接受率；原分母、3秒request、连续25控制与门限未改、不拼reset。全部旧候选/H1/其它专家/Registryv12/1cd保持，目标未完成。

| 名义31体五姿指标 | 本续接候选 | 已发布源55afa | 本次实跑母版1cd |
|---|---:|---:|---:|
| 曾连续.5秒联合达标 | {c['engineering_credits']}/5 | {prior['engineering_credits']}/5 | {mother['engineering_credits']}/5 |
| 结束时仍连续达标 | {c['credited_and_stable_at_end']}/5 | {prior['credited_and_stable_at_end']}/5 | {mother['credited_and_stable_at_end']}/5 |
| 末态高度 m | {c['mean_final_height_m']:.6f} | {prior['mean_final_height_m']:.6f} | {mother['mean_final_height_m']:.6f} |
| 末态根速 m/s | {c['mean_final_speed_m_s']:.6f} | {prior['mean_final_speed_m_s']:.6f} | {mother['mean_final_speed_m_s']:.6f} |
| 端点XY位移 m | {c['mean_endpoint_xy_displacement_m']:.6f} | {prior['mean_endpoint_xy_displacement_m']:.6f} | {mother['mean_endpoint_xy_displacement_m']:.6f} |

十条均8秒/400控制/finite；31机器人body/原限位/名义400N-k2000-d3/50策略100PD/.0025物理、无外力/yaw/动画、clean raw35/history5。与native fullDR、硬件、视频整腿同端分列；不把nominal5/5推广为原74或多seed通过。母版抬身与完整联合判据分开。

唯一学习动作是完整55afa再继续≤25：actor/critic/encoder/logSTD/mutable LR/两Adam/privategenerator原样恢复，不重新warm1cd、不重置学习率、不改STD/原奖励/26recipe/8秒timeout/物理/DR。sourceRoot7完整CPU一次read/hash/decode与unknown强immutable；源环境、history/queues/globalenvRNG/pending不应用，新sole reset/noisy35重复5，明确stream cut而非PhysX位级resume。实际fullresume和mutable状态见完整初始化/决定。

新seed20261002/03/04 holdout尚待独立原生确认，状态PENDING、非0分；旧55afa诊断集21/240与7个ever+末帧good不拿来配对因果；无matched native参考，paired差值null。后续需要实际终点当前streak≥25，旧未记录者保持null。

证据：{link(files['training'],'训练完整闭环')} / {link(files['original'],'原74与actual父资格')} / {link(files['nominal'],'新名义五姿实测')} / {link(files['export'],'一次pi派生收据')} / {link(paths[0],'完整质量决定')}。全部源码/真实成功失败/报告归下一meaningful feature-only annotated trial，main只读；不为Git打开模型/raw或重放旧once。
''',encoding='utf8')
paths[2].write_text(f'''# V28 — Root7完整继续的新窗实际收口

- Goal c490 rev3 active/armed/round6/14，H1/其它专家/Registryv12/1cd不变；{link(paths[1],'本窗实测报告')}。
- Source55afa完整learner一次输入，新Root8/base25/current新{u}与累计{cum['updates']}分列；完整{latest['bytes']}B/SHA{latest['sha256']}，actual inner/outer wait/cost/release/errors[]全资格。
- 原E3 {credit}/74；名义曾达标{c['engineering_credits']}/5、末端连续{c['credited_and_stable_at_end']}/5。决定{choice}，不自动晋升、不以CPU/更新数当技能。
- 新holdout seeds20261002/03/04 pending未运行，不当0分；下一独立确认仍待实际。当前阶段text/source/error/report需meaningful feature-only归档，禁止主分支push/reset/旧once或模型重开。
''',encoding='utf8');print(json.dumps(dict(outputs=[str(p)for p in paths],actual_window=u,cumulative=cum,original_score=[credit,den],nominal=nominal,decision=choice,goal_complete=False),indent=2))
