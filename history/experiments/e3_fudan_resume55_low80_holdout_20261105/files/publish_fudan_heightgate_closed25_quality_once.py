"""Publish actual gated-pilot results from produced JSON only, never preset an outcome."""
from pathlib import Path
import json,time,math,statistics
D=Path(__file__).resolve().parent
paths=dict(training=D/'reports/FDN_N20000_W9_LOWHEIGHTGATE_20261105_024651/CLOSED_RESULT.json',admission=D/'reports/FDN_N20000_W9_LOWHEIGHTGATE_20261105_024651/FIRST_ACTUAL_ADMISSION.json',original=D/'FDNHEIGHTGATE_FROZEN_ORIGINAL_SCOPE_RESULT.json',mujoco=D/'FDN_HEIGHTGATE_MUJOCO31_LOWRise_RESULT.json',export=D/'FDNHEIGHTGATE_PI_ONLY_EXPORT_STARTED_ONCE.json',previous=D/'FDN_FRESH1CD_CLOSED25_QUALITY_DECISION_V1.json')
outputs=[D/'FDN_HEIGHTGATE_CLOSED25_QUALITY_DECISION_V1.json',D/'FDN_HEIGHTGATE_CLOSED25_QUALITY_RESULTS_V1.md',D/'CURRENT_PROGRESS_V19_HEIGHTGATE_CLOSED25_QUALITY_RESULT.md'];assert not any(p.exists()for p in outputs)
a,ad,o,j,e,old=[json.loads(paths[k].read_bytes())for k in('training','admission','original','mujoco','export','previous')];m=a['metadata'];f=m['FDN_FINAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json'];owner=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json'];zero=dict(updates=0,policy_optimizer_steps=0,encoder_optimizer_steps=0,transitions_seen=0)
assert a['closed']is True and f['final']is True and f['complete_save']is True and f['error']is None and f['close_errors']==[]and latest==f['latest_complete_save']
assert owner['errors']==[]and all(owner[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
assert q['qualified']is True and all(v is True for v in q['checks'].values())and o['execution_qualified']is True and all(o['execution_checks'].values())and o['actual_parent_wait_qualification']['qualified']is True and o['actual_parent_wait_qualification']['kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V5_HEIGHTGATE'
sha=latest['sha256'];assert e['complete']is True and e['source']['sha256']==o['source_binding']['sha256']==j['source_export']['sha256']==sha and sha=='bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2'
assert f['version']==5 and f['branch_kind']=='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_HEIGHTGATE'and f['base_counters']==zero and f['window_counters']==f['counters']and f['inherited_old_iterations']==f['bad_candidate_reads']==0 and f['full_learner_resume']is False
s=o['original_worker_outcome_verbatim'];rr=s['original_recovery_recipe_rows'];falls=[r for r in rr if r['original_request']];normal=[r for r in rr if not r['original_request']];assert len(rr)==13 and len(falls)==12 and len(normal)==1 and normal[0]['recipe']==12 and normal[0]['initial_envs']==6
n=sum(r['initial_envs']for r in falls);credit=sum(r['first_episode_original_stable_credit']for r in falls);assert n==74==s['original_recovery_request_denominator']and credit==s['original_first_episode_recovery_credits']and 0<=credit<=n
window=f['window_counters'];native=f['native_counters'];controls=native['actual_native_policy_steps'];assert window==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)
assert native['actual_native_transitions']==20000*controls and native['physical_callbacks']==8*controls and native['feedback_callbacks']==2*controls and native['termination_computations']==controls
partial=controls-window['updates']*48;assert 0<=partial<=48
t=f['task_summary'];gate=t['lowheight_tracking_gate'];passive=t['low_rollout_summary'];assert passive['samples']==t['low_envs']*controls and passive['descriptive_only_not_acceptance']is True and all(v['weight']>0 and v['height_gate_installed']is True for v in gate['terms'].values())
nominal={}
for role,rows in j['rows'].items():
 assert len(rows)==5 and all(r['controls']==400 and r['finite_execution_error']is None for r in rows)
 nominal[role]=dict(cases=5,complete_finite_cases=5,engineering_credits=sum(bool(r['credited_by_same_engineering_predicate'])for r in rows),credited_and_stable_at_end=sum(bool(r['credited_and_stable_at_end'])for r in rows),mean_final_height_m=statistics.mean(r['final']['height_m']for r in rows),mean_final_tilt_deg=statistics.mean(r['final']['tilt_deg']for r in rows),mean_final_speed_m_s=statistics.mean(r['final']['root_speed_m_s']for r in rows),mean_endpoint_xy_displacement_m=statistics.mean(math.hypot(*r['final']['root_xy_m'])for r in rows),max_closure_error_m=max(r['max_closure_error_m']for r in rows),max_mimic_error_rad=max(r['max_mimic_error_rad']for r in rows))
c,b=nominal['candidate'],nominal['frozen_mother'];prior=old['nominal_MuJoCo31']['comparison']['candidate'];previous_credit=old['original_N80']['recovery_first_episode_credits'];normal_regressed=normal[0]['first_episode_physical_terminated']>old['original_N80']['normal_first_episode_physical_terminated']
improved_original=credit>previous_credit;improved_nominal=c['engineering_credits']>prior['engineering_credits'];positive_joint_credit=improved_original or improved_nominal
if positive_joint_credit:decision='RETAIN_HEIGHTGATE_CANDIDATE_FOR_CONFIRMATORY_SCOPED_TEST_KEEP_REGISTRY_V12_UNCHANGED'
else:decision='KEEP_REGISTRY_V12_E3_1CD_NO_HEIGHTGATE_PROMOTION'
go=ad['actual_GO']['learning_started_epoch'];row=list(m['COHORT_FINAL.json']['rows'].values())[0]
result=dict(kind='E3_FUDAN_LOWHEIGHTGATE_CLOSED25_ACTUAL_QUALITY',epoch=time.time(),source=e['source'],candidate_full_save=latest,training=dict(base_counters=zero,new_N20000=window,current_branch_counters=f['counters'],inherited_old_iterations=0,bad_candidate_reads=0,full_learner_resume=False,current_native=native,full_saved_unoptimized_pending_controls=partial,full_saved_unoptimized_pending_transitions=partial*20000,original_owner_exit=owner,outer_wait=outer,GO_to_worker_terminal_metadata_derived_seconds=row['owner_received_terminal_epoch']-go,GO_to_outer_actual_wait_metadata_derived_seconds=outer['epoch']-go,not_budget_ledger_rewrite=True,training_warm_source_receipt=f['source_checkpoint'],training_task_description_not_independent_grade=t,actual_constructed_tracking_gate=gate,pre_reset_height_descriptive_only=passive),original_N80=dict(execution_qualified=True,actual_original_parent_qualified=True,actual_parent_kind=o['actual_parent_wait_qualification']['kind'],collector_kind_erratum_needed=False,recovery_first_episode_credits=credit,original_request_denominator=n,normal_envs=6,normal_first_episode_physical_terminated=normal[0]['first_episode_physical_terminated'],requested_first_episode_physical_terminated=sum(r['first_episode_physical_terminated']for r in falls),recipe_rows=rr,seed=20260928,controls=160,no_reset_stitching=True,no_aggregate_original_graduation_rule_in_source=True,previous_published_credit=previous_credit,normal_physical_termination_increase=normal_regressed),nominal_MuJoCo31=dict(comparison=nominal,previous_246ac_published_comparison=old['nominal_MuJoCo31']['comparison'],pose_count=5,duration_per_pose_seconds=8,policy_hz=50,feedback_hz=100,physics_dt=.0025,clean_observations=True,full_DR=False,not_native_or_hardware_acceptance=True,no_whole_leg_same_end_video_claim=True),strict_joint_credit_above_previous_candidate=positive_joint_credit,independent_multiseed_or_matched_native_causality_established=False,decision=decision,H1_and_other_experts_unchanged=True,Registry_v12_and_mother_unchanged=True,full_candidate_preserved=True,native_causal_regression_claim=False,goal_complete=False,source_metadata={k:str(p)for k,p in paths.items()},models_or_raw_or_canonical_IO=0)
outputs[0].write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8');link=lambda p,label:f'[{label}](<{p.as_posix()}>)'
report=f'''# E3低位正tracking高度门控 / N20000×25：真实质量结果

## 结论

**25次真实PPO完整保存并收口；原N80执行资格通过，原首episode信用{credit}/{n}。**

**{decision}**。原1cd/Registryv12保持，完整bf824候选保留；H1/其它专家不动，总质量目标未完成。是否优于前一候选的严格联合信用按实测计算：{positive_joint_credit}，normal物理终止增加：{normal_regressed}。这是一次单seed/单五姿诊断，不自动建立多seed毕业或matched native因果。

原74请求与6normal分列：normal首episode物理终止{normal[0]['first_episode_physical_terminated']}/6，不是normal接受率；请求组物理终止{result['original_N80']['requested_first_episode_physical_terminated']}/74。原稳定50 public ticks=0.5s=25控制，request300=3s，不拼后续reset。

## 真实训练和唯一干预

| PPO | 策略Adam | encoder Adam | 已优化转移 | 继承 |
|---:|---:|---:|---:|---:|
| 25 | 500 | 500 | 24,000,000 | 0 |

只对recipe>=13的3正tracking项乘clip((height-.1781)/(.23-.1781),0,1)。实际constructed weights：linear {gate['terms']['track_lin_vel']['weight']}、tight {gate['terms']['track_lin_vel_tight']['weight']}、yaw {gate['terms']['track_ang_vel']['weight']}；原std/params保持，三个wrapper标记true。旧fall/normal、负error/height/potential/命令/五姿/8s/400timeout、Fudan核心和物理/fullDR均保持。

重新1cd actor8+critic8 MLP warm、随机fresh encoder/latent列0/STD.5/两Adam-LR-private generator-计数fresh，与旧25pilot同seed和设置，不续坏246ac/205。原1cd14715029B一次physical/hash/CPUdecode，source_optimizer/DR/history/旧迭代不应用；source_iter43090不累计到新25。新N20000/一fresh reset/raw35×5，非PhysX位级resume。

Native {controls}控制/{native['physical_callbacks']}physics/{native['feedback_callbacks']}feedback/{native['actual_native_transitions']:,}真实转移；未优化pending{partial}控制/{partial*20000:,}转移。全候选{latest['bytes']:,}B/SHA `{sha}`。inner+outer实际wait、成本结清/释放/errors=[]，GO至outer约{outer['epoch']-go:.3f}s为metadata解释，不改原账本。

## 被动pre-reset描述，不是起身接受率

采样{passive['samples']:,.0f}低组状态，平均高度{passive['sample_height_mean_m']:.6f}m，≥.23比例{passive['sample_ge023_fraction']:.6f}；已结束{passive['endedLowEpisodes']:,.0f}低episode，峰值均值{passive['ended_low_peak_height_mean_m']:.6f}m，峰值≥.23比例{passive['ended_low_peak_ge023_fraction']:.6f}。这是复用原phase.update的固定内存累计测量，无额外physics/传感/RNG，不把高度峰值当作姿态/静止/接触联合信用。训练信用{t['credited_training_low_episodes']}/{t['completed_training_low_episodes']}单独保留，不是独立测试。旧run没有同一buffer，不用旧postreset .1781与此峰值推因果。

## 同五姿名义MuJoCo末态均值

| 指标 | 本候选bf824 | 前候选246ac（已发布） | 冻结1cd（本次实跑） |
|---|---:|---:|---:|
| 高度 m | {c['mean_final_height_m']:.6f} | {prior['mean_final_height_m']:.6f} | {b['mean_final_height_m']:.6f} |
| 倾斜 deg | {c['mean_final_tilt_deg']:.3f} | {prior['mean_final_tilt_deg']:.3f} | {b['mean_final_tilt_deg']:.3f} |
| 根速度 m/s | {c['mean_final_speed_m_s']:.6f} | {prior['mean_final_speed_m_s']:.6f} | {b['mean_final_speed_m_s']:.6f} |
| 起终点平面位移 m | {c['mean_endpoint_xy_displacement_m']:.6f} | {prior['mean_endpoint_xy_displacement_m']:.6f} | {b['mean_endpoint_xy_displacement_m']:.6f} |
| 工程联合信用 | {c['engineering_credits']}/5 | {prior['engineering_credits']}/5 | {b['engineering_credits']}/5 |

双方五条均完整finite、400控制/8秒，同31体/30坐标/原限位、50策略/100PD/.0025物理、PD60,2/wheel.6/scales.5,10、400N-k2000-d3，无外力/yaw/动画。clean raw35/frame-major5，不是native fullDR/硬件/视频整腿同端姿态验收。严格信用还需h≥.23、姿态/速度<.03/角速度/轮接触/机身脱地连续.5s，分项与联合条件分列。

## 执行、保存与IO边界

原唯一canonical/原charge_values/authority2EX/privateGPU_EX/trainSH-evalEX/reserve86412.86069250107/3900-3600-300/1800preGO保持，无外国signal/清锁/改账/扩预算/退款。CPUexport对新bf824仅一次整文件read/hash/CPUdecode、whole CPU根/未知字段保留，仅下载{e['artifact']['bytes']:,}B/14pi/82505派生，不是完整resume；本次正确EXCLUDED实际常量名且未重复旧import失败。原N80对相同新完整来源是另一真实用途的一次CPU缓存读取，不切片20k DR/history给80，不优化/安装训练gate。source-only旧生成器CRLF格式错误在输出mkdir前，旧源/错误及新V2 byte保持纠正已保留，未改原Appclose/actualwait。

## 完整证据与下一步

- {link(paths['training'],'训练完整终态')} / {link(paths['admission'],'实际原门控GO')}。
- {link(paths['original'],'原74 recipe与实际父资格')} / {link(paths['mujoco'],'同五姿十条完整物理案例')}。
- {link(paths['export'],'一次CPU派生收据')} / {link(outputs[0],'紧凑完整质量决定')}。

不按25/205计数自动长跑或晋升。不把0信用等同零reward，不把瞬时高或100%峰值当起身成功。下一步依据真实联合失败分项和保持表现选择一项干预或确认性测试，原判据/分母/physics/DR保持；本报告及全部新成功失败下一有意义feature-only annotated trial归档，main只读。
'''
outputs[1].write_text(report,encoding='utf8')
outputs[2].write_text(f'''# V19 — heightgate closed25质量实测

- goal-c490e4cc-b28b-440e-bde6-30ee956813f0 rev3 active/armed/round2/14，未完成，H1/其它专家/Registryv12/1cd保持。{link(outputs[1],'实测报告')} / {link(outputs[0],'完整决定')}。
- W9 root {a['root']}，controller1629746/parent1629753/worker1630734，GO1793819803.834791；实际25/两Adam500/24m，零继承，{controls}controls/{native['physical_callbacks']}physics/{native['feedback_callbacks']}feedback，pending{partial}，完整{latest['bytes']}B/{sha}，全部inner+outer wait/cost/release/error[]闭环。训练observer4bc已completed0/output collected。
- 原N80 source bf824，V5_HEIGHTGATE实际parent qualified+collector全部true，原{credit}/74/normal物理{normal[0]['first_episode_physical_terminated']}/6，非graduation。名义MuJoCo十条completefinite，候选{c['engineering_credits']}/5、母版{b['engineering_credits']}/5；候选h/v/XY {c['mean_final_height_m']:.6f}/{c['mean_final_speed_m_s']:.6f}/{c['mean_endpoint_xy_displacement_m']:.6f}，母版{b['mean_final_height_m']:.6f}/{b['mean_final_speed_m_s']:.6f}/{b['mean_endpoint_xy_displacement_m']:.6f}。三正项实际1/.2/.5及新pre-reset被动测量真实，不是联合接受率。
- CPUexport正确一次整bf824 CPU read/hash/decode，派生{e['artifact']['bytes']}B/{e['artifact']['sha256']}、本地{e['local_pi_export']}，不是完整resume。原source/bad候选不为状态/Git开启。错误源CRLF格式检查发生于本地输入读取、mkdir前，V2只保留合法原byte且原close/math/resource完全相同，均保留。
- 决策{decision}，full候选保留，原模型不晋升。独立多seed/native因果未建立，goal_completeFalse。当前Native/eval已收口，不重放旧stage/dispatch/collector/export/record。
- 最近源准入阶段已核验565c504fbe62649c31f9962c56d83f71fdac888a/tag trial-20261105-e3-fudan-lowheightgate-original-admission（537源；main只读f9837af03f8e704b05c28c16ca13c21bc3aa958a，未push/reset）。其后实际GO/首11proof/closed25/N80/CPUexport/MuJoCo/本报告需新意义阶段合并归档；原record全部校验+短2pathspec/fullstagedset，模型/raw/JSONL/geometry先跳再stat/read/hash，不为Git重跑物理。
''',encoding='utf8')
print(json.dumps(dict(outputs=[str(p)for p in outputs],actual_new_updates=25,original_recovery=f'{credit}/{n}',nominal_comparison=nominal,actual_constructed_gate=gate,pre_reset_height_descriptive_only=passive,decision=decision,goal_complete=False,model_raw_or_canonical_IO=0),indent=2))
