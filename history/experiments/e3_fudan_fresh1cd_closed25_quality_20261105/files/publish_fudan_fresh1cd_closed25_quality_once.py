"""Publish one completed fresh1cd pilot from produced metadata only; no model/raw replay."""
from pathlib import Path
import json,time,math,statistics
D=Path(__file__).resolve().parent
paths=dict(training=D/'reports/FDN_N20000_W8_FRESH1CD_ADMISSION2_20261105_014143/CLOSED_RESULT.json',admission=D/'reports/FDN_N20000_W8_FRESH1CD_ADMISSION2_20261105_014143/FIRST_ACTUAL_ADMISSION.json',original=D/'FDNFRESH1CD_FROZEN_ORIGINAL_SCOPE_RESULT.json',mujoco=D/'FDN_FRESH1CD_MUJOCO31_LOWRise_RESULT.json',export=D/'FDNFRESH1CD_PI_ONLY_EXPORT_V2_STARTED_ONCE.json',export_zero_input_error=D/'FDN_FRESH1CD_EXPORT_V1_ZERO_INPUT_IMPORT_ERRATUM.json',previous=D/'FDN_TIMEOUT8_CLOSED72_QUALITY_DECISION_V1.json')
outputs=[D/'FDN_FRESH1CD_CLOSED25_QUALITY_DECISION_V1.json',D/'FDN_FRESH1CD_CLOSED25_QUALITY_RESULTS_V1.md',D/'CURRENT_PROGRESS_V17_FRESH1CD_CLOSED25_ORIGINAL_NOT_IMPROVED.md'];assert not any(p.exists()for p in outputs)
a,ad,o,j,e,err,old=[json.loads(paths[k].read_bytes())for k in('training','admission','original','mujoco','export','export_zero_input_error','previous')];m=a['metadata'];f=m['FDN_FINAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json'];owner=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json'];zero=dict(updates=0,policy_optimizer_steps=0,encoder_optimizer_steps=0,transitions_seen=0)
assert a['closed']is True and f['final']is True and f['complete_save']is True and f['error']is None and f['close_errors']==[]and latest==f['latest_complete_save']
assert owner['errors']==[]and all(owner[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
assert q['qualified']is True and all(v is True for v in q['checks'].values())and o['execution_qualified']is True and all(o['execution_checks'].values())and o['actual_parent_wait_qualification']['qualified']is True and o['actual_parent_wait_qualification']['kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V4_FRESH1CD'
sha='246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2';assert e['complete']is True and e['source']['sha256']==latest['sha256']==o['source_binding']['sha256']==j['source_export']['sha256']==sha
assert f['version']==4 and f['branch_kind']=='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8'and f['base_counters']==zero and f['window_counters']==f['counters']and f['inherited_old_iterations']==f['bad_candidate_reads']==0 and f['full_learner_resume']is False
s=o['original_worker_outcome_verbatim'];rr=s['original_recovery_recipe_rows'];falls=[r for r in rr if r['original_request']];normal=[r for r in rr if not r['original_request']];assert len(rr)==13 and len(falls)==12 and len(normal)==1 and normal[0]['recipe']==12 and normal[0]['initial_envs']==6
n=sum(r['initial_envs']for r in falls);credit=sum(r['first_episode_original_stable_credit']for r in falls);assert n==74==s['original_recovery_request_denominator']and credit==s['original_first_episode_recovery_credits']==0
window=f['window_counters'];native=f['native_counters'];controls=native['actual_native_policy_steps'];assert window==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)
assert native['actual_native_transitions']==20000*controls and native['physical_callbacks']==8*controls and native['feedback_callbacks']==2*controls and native['termination_computations']==controls
partial=controls-window['updates']*48;assert 0<=partial<=48
nominal={}
for role,rows in j['rows'].items():
 assert len(rows)==5 and all(r['controls']==400 and r['finite_execution_error']is None for r in rows)
 nominal[role]=dict(cases=5,complete_finite_cases=5,engineering_credits=sum(bool(r['credited_by_same_engineering_predicate'])for r in rows),credited_and_stable_at_end=sum(bool(r['credited_and_stable_at_end'])for r in rows),mean_final_height_m=statistics.mean(r['final']['height_m']for r in rows),mean_final_tilt_deg=statistics.mean(r['final']['tilt_deg']for r in rows),mean_final_speed_m_s=statistics.mean(r['final']['root_speed_m_s']for r in rows),mean_endpoint_xy_displacement_m=statistics.mean(math.hypot(*r['final']['root_xy_m'])for r in rows),max_closure_error_m=max(r['max_closure_error_m']for r in rows),max_mimic_error_rad=max(r['max_mimic_error_rad']for r in rows))
assert all(v['engineering_credits']==0 for v in nominal.values())
go=ad['actual_GO']['learning_started_epoch'];row=list(m['COHORT_FINAL.json']['rows'].values())[0];decision='KEEP_REGISTRY_V12_E3_1CD_NO_246AC_PROMOTION'
result=dict(kind='E3_FUDAN_FRESH1CD_CLOSED25_ORIGINAL_RECOVERY_NOT_IMPROVED',epoch=time.time(),source=e['source'],candidate_full_save=latest,training=dict(base_counters=zero,new_N20000=window,current_branch_counters=f['counters'],inherited_old_iterations=0,bad_candidate_reads=0,full_learner_resume=False,current_native=native,full_saved_unoptimized_pending_controls=partial,full_saved_unoptimized_pending_transitions=partial*20000,original_owner_exit=owner,outer_wait=outer,GO_to_worker_terminal_metadata_derived_seconds=row['owner_received_terminal_epoch']-go,GO_to_outer_actual_wait_metadata_derived_seconds=outer['epoch']-go,not_budget_ledger_rewrite=True,training_warm_source_receipt=f['source_checkpoint'],training_task_description_not_independent_grade=f.get('task_summary')),original_N80=dict(execution_qualified=True,actual_original_parent_qualified=True,actual_parent_kind=o['actual_parent_wait_qualification']['kind'],collector_kind_erratum_needed=False,recovery_first_episode_credits=credit,original_request_denominator=n,normal_envs=6,normal_first_episode_physical_terminated=normal[0]['first_episode_physical_terminated'],requested_first_episode_physical_terminated=sum(r['first_episode_physical_terminated']for r in falls),recipe_rows=rr,seed=20260928,controls=160,no_reset_stitching=True,no_aggregate_original_graduation_rule_in_source=True),nominal_MuJoCo31=dict(comparison=nominal,previous_3e64_published_comparison=old['nominal_MuJoCo31']['comparison'],pose_count=5,duration_per_pose_seconds=8,policy_hz=50,feedback_hz=100,physics_dt=.0025,clean_observations=True,full_DR=False,not_native_or_hardware_acceptance=True,no_whole_leg_same_end_video_claim=True),export_zero_input_import_failure_preserved=err,decision=decision,H1_and_other_experts_unchanged=True,full_candidate_preserved=True,original_recovery_improvement_not_established=True,native_causal_regression_claim=False,goal_complete=False,source_metadata={k:str(p)for k,p in paths.items()},models_or_raw_or_canonical_IO=0)
outputs[0].write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8')
link=lambda p,label:f'[{label}](<{p.as_posix()}>)';c,b=nominal['candidate'],nominal['frozen_mother'];prior=old['nominal_MuJoCo31']['comparison']['candidate']
report=f'''# E3 fresh1cd Fudan / N20000×25：真实闭环质量结果

## 结论

**25次真实PPO已完整收口，独立原N80执行合格但起身信用仍为{credit}/{n}；暂保留1cd，不晋升246ac候选。**

- 原74首episode请求与6个normal分开；normal物理终止{normal[0]['first_episode_physical_terminated']}/6，不是normal技能通过率。请求组物理终止{result['original_N80']['requested_first_episode_physical_terminated']}/74是描述，不据不同run推因果。
- 名义31体MuJoCo，同五合法低姿×8秒，每条400控制：两策略均完整finite5/5，严格工程联合信用均0/5。分项实测见下，0/5不等于车身没有抬起。
- **{decision}**。全候选保留，H1/其它专家/Registryv12与母版不变；总质量目标未完成。

## 真实训练与保存

| 分支 | PPO | 策略Adam | encoder Adam | 优化转移 |
|---|---:|---:|---:|---:|
| 新fresh1cd分支（N20000/T48） | **25** | **500** | **500** | **24,000,000** |
| 继承旧分支/旧迭代 | **0** | **0** | **0** | **0** |

仅1cd actor8＋critic8 MLP warm，encoder随机fresh、新latent列0、STD.5/两Adam/LR/private generator/计数fresh。真实母版14715029B读/hash/CPU decode各1，未套旧Adam/环境DR/history；43090只是source_iter，不累计旧205。新环境N20000/一fresh reset/noisy35×5；同一低8s/400time_out、PPO/core/physics/fullDR，不是PhysX位级resume。

Native {controls}控制、{native['physical_callbacks']}physics、{native['feedback_callbacks']}feedback、{native['actual_native_transitions']:,}真实转移；完整保存的未优化pending为{partial}控制/{partial*20000:,}转移。完整候选{latest['bytes']:,}B/SHA `{sha}`。原inner/outer实际wait、结清/释放/errors=[]，GO至outer actual wait约{outer['epoch']-go:.3f}秒，只是metadata解释，不另建/改写账本。

## 名义五姿末态均值

| 指标 | fresh246ac | 旧3e64（已发布） | 冻结1cd（本次实跑） |
|---|---:|---:|---:|
| 高度 m | {c['mean_final_height_m']:.6f} | {prior['mean_final_height_m']:.6f} | {b['mean_final_height_m']:.6f} |
| 倾斜 deg | {c['mean_final_tilt_deg']:.3f} | {prior['mean_final_tilt_deg']:.3f} | {b['mean_final_tilt_deg']:.3f} |
| 根速度 m/s | {c['mean_final_speed_m_s']:.6f} | {prior['mean_final_speed_m_s']:.6f} | {b['mean_final_speed_m_s']:.6f} |
| 起终点平面位移 m | {c['mean_endpoint_xy_displacement_m']:.6f} | {prior['mean_endpoint_xy_displacement_m']:.6f} | {b['mean_endpoint_xy_displacement_m']:.6f} |
| 工程联合信用 | {c['engineering_credits']}/5 | {prior['engineering_credits']}/5 | {b['engineering_credits']}/5 |

工程条件含h≥.23、姿态/速度/角速度/双轮接触/车身脱地连续.5s；母版确实升高车身，但约.038m/s仍超过.03速度门。实测分项和严格信用分列，不把执行合格或0/5当作同样行为。相同31体/30坐标/原限位，50Hz策略/100Hz反馈/.0025物理、400N-k2000-d3、clean raw35/frame-major5，无外力/yaw/动画；不是native fullDR/硬件或视频整腿同端姿态验收。

## 错误与IO边界

W7原1800s preGO自然超时，0GO/SDK/PT/PPO，全部实际wait/结清/释放后新W8 admission才真正开训；不是重放旧失败root，也不将它记为技能失败。

本次原N80实际V4_FRESH1CD父资格与collector完整kind一致，全部execution检查true；无旧V3那种reader纠正。第一次CPU pi export仍导入已删除的LEARNER_SOURCE_PATH，ImportError发生在输入stat/read/hash/decode和ownsave前，全部IO0。旧源、marker、error保留；新V2仅改为实际EXCLUDED常量及读取前规范字符串路径/SHA排除，outer/remote AST＋静态import-name合同通过，未改14pi数学或重开旧输入。V2第一次真正导出时输入完整候选读/hash/CPU decode各1，仅下载{e['artifact']['bytes']:,}B派生14pi/82505标量，不是完整训练resume。

## 完整证据与下一步

- {link(paths['training'],'训练完整终态')} / {link(paths['admission'],'真实原门控GO')}。
- {link(paths['original'],'原N80原始recipe与父资格')} / {link(paths['mujoco'],'同五姿十条真实MuJoCo案例')}。
- {link(paths['export_zero_input_error'],'零输入import错误与新V2纠正')} / {link(outputs[0],'紧凑完整质量与保留决定')}。

先用本次实际task_summary与独立结果限定下一项干预，不按25/205数字盲续，不更改原分母、判据、物理或DR。训练描述不是独立接受率，缺失的effective reward分解不当作已证明根因；下一实训需要独立有限目的和原资源门控。
'''
outputs[1].write_text(report,encoding='utf8')
handoff=f'''# V17 — fresh1cd实际closed25，原0/74，保留母版

- 当前E3 goal-c490e4cc-b28b-440e-bde6-30ee956813f0 revision3 active/armed/max14，未完成，不pause/blocked/complete。H1/其它专家/Registryv12不变。{link(outputs[1],'实测报告')}与{link(outputs[0],'紧凑结果')}已发布。
- W7零GO的原1800s超时及W8新namespace450stage/真实释放watch均保留；W8 root为{a['root']}，controller1626919/parent1626926/worker1627057，GO1793814178.5811079。实际fresh25/两Adam500/24m优化转移，零继承，不拼旧205。1200native控制/9600physics/2400feedback，未优化pending{partial}。
- 全候选{latest['bytes']}B/SHA{sha}，完整learner/两Adam/RNG/typed环境保存；warm1cd一实际读取，原learner/DR/history不应用，full_learner_resumeFalse描述起点而非不完整保存。所有inner/outer wait/cost/release/errors[]闭环，observer91f已completed0/output collected。
- 原N80 parent1627966/controller1627959，单80/160/seed20260928/原74+6/fullDR/一reset/0优化。实际父kindV4_FRESH1CD合格、collector全部execution检查true，无reader重跑；原0/74、normal物理0/6、请求物理{result['original_N80']['requested_first_episode_physical_terminated']}/74。observer705已completed0/output collected。
- CPUexportV1错误为删除的LEARNER_SOURCE_PATH名称，全部源IO0/ownsave0，旧源与error保留。新V2同closed前门+实际EXCLUDED前读排除，输入246ac第一次实际CPU一次解码；14pi派生{e['artifact']['bytes']}B/SHA{e['artifact']['sha256']}，本地{e['local_pi_export']}，NOTfullresume。MuJoCo十条completefinite已完成0；双方0/5，但分项fresh高度{c['mean_final_height_m']:.6f}/速度{c['mean_final_speed_m_s']:.6f}/XY{c['mean_endpoint_xy_displacement_m']:.6f}，母版{b['mean_final_height_m']:.6f}/{b['mean_final_speed_m_s']:.6f}/{b['mean_endpoint_xy_displacement_m']:.6f}。没有native因果退化/全DR/硬件/视频同端姿态声明。
- 决策{decision}，完整候选与母版保留。当前无本任务native/observer/background工作剩余，下一干预未部署；不得重跑旧一次入口/模型/raw为状态/Git。
- 最近核验Git7ee034128525a83dc3a33284bfe219eece934e26/trial-20261105-e3-fudan-fresh1cd25-original-admission（7ee为W7提交点时，不包含后续真实闭环）。本W7超时/释放/W8闭环/首次10proof/原N80/零IO错误+V2导出/MuJoCo/本报告等待一次有意义合并archive。原record_experiment全部校验＋短2pathspec/full staged-set核对；feature+唯一annotated tag，main只读，模型/raw/JSONL/geometry先跳再stat/read/hash。
'''
outputs[2].write_text(handoff,encoding='utf8')
print(json.dumps(dict(outputs=[str(p)for p in outputs],actual_new_updates=25,original_recovery=f'{credit}/{n}',nominal_comparison=nominal,training_task_description_not_independent_grade=f.get('task_summary'),decision=decision,goal_complete=False,model_raw_or_canonical_IO=0),indent=2))
