"""Data-driven lowSTD finite-pilot publication. Only produced JSON, no model/raw/C IO."""
from pathlib import Path
import json,time,math,statistics
D=Path(__file__).resolve().parent
ref=json.loads((D/'FDN_N20000_W11_LOWSTD005_ADMISSION2_COLLECTOR_ONCE.json').read_bytes());out=Path(ref['output'])
paths=dict(training=out/'CLOSED_RESULT.json',admission=out/'FIRST_ACTUAL_ADMISSION.json',original=D/'FDNLOWSTD005_FROZEN_ORIGINAL_SCOPE_RESULT.json',mujoco=D/'FDN_LOWSTD005_MUJOCO31_LOWRise_RESULT.json',export=D/'FDNLOWSTD005_PI_ONLY_EXPORT_STARTED_ONCE.json',baseline=D/'FDN_FRESH1CD_CLOSED25_QUALITY_DECISION_V1.json',heightgate=D/'FDN_HEIGHTGATE_CLOSED25_QUALITY_DECISION_V1.json')
outputs=[D/'FDN_LOWSTD005_ADMISSION2_CLOSED_QUALITY_DECISION_V1.json',D/'FDN_LOWSTD005_ADMISSION2_CLOSED_QUALITY_RESULTS_V1.md',D/'CURRENT_PROGRESS_V22_LOWSTD005_ADMISSION2_CLOSED_QUALITY_RESULT.md'];assert not any(p.exists()for p in outputs)
a,ad,o,j,e,old,hg=[json.loads(paths[k].read_bytes())for k in('training','admission','original','mujoco','export','baseline','heightgate')];m=a['metadata'];f=m['FDN_FINAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json'];owner=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json'];zero=dict(updates=0,policy_optimizer_steps=0,encoder_optimizer_steps=0,transitions_seen=0)
assert a['closed']is True and f['final']is True and f['complete_save']is True and f['error']is None and f['close_errors']==[]and latest==f['latest_complete_save']
assert owner['errors']==[]and all(owner[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
assert q['qualified']is True and all(v is True for v in q['checks'].values())and o['execution_qualified']is True and all(o['execution_checks'].values())and o['actual_parent_wait_qualification']['qualified']is True and o['actual_parent_wait_qualification']['kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V6_LOWSTD005'
sha=latest['sha256'];assert e['complete']is True and e['source']['sha256']==o['source_binding']['sha256']==j['source_export']['sha256']==sha and sha not in {'1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8','47937b27407d6994b08f206c386d54eba220fe637a1082a32d9e7d127e5bbe4d','8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78','3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e','246ac694c655dc6c43f8d6f72474234ed8f69898cba8b5bcf297762cea46c2e2','bf824b1eae9eef1fd1a9041d124be298d0e98898b7372cb0b86ec4822277f2b2'}
init=m['FDN_SINGLE_SOURCE_NEW_BRANCH_WARM_START.json'];assert init['learner_config']['initial_std']==.05
assert f['version']==6 and f['branch_kind']=='FRESH_FUDAN_MLP_WARM_FROM1CD_N20000_TIMEOUT8_LOWSTD005'and f['base_counters']==zero and f['window_counters']==f['counters']and f['inherited_old_iterations']==f['bad_candidate_reads']==0 and f['full_learner_resume']is False
s=o['original_worker_outcome_verbatim'];rr=s['original_recovery_recipe_rows'];falls=[r for r in rr if r['original_request']];normal=[r for r in rr if not r['original_request']];assert len(rr)==13 and len(falls)==12 and len(normal)==1 and normal[0]['recipe']==12 and normal[0]['initial_envs']==6
n=sum(r['initial_envs']for r in falls);credit=sum(r['first_episode_original_stable_credit']for r in falls);assert n==74==s['original_recovery_request_denominator']and credit==s['original_first_episode_recovery_credits']and 0<=credit<=n
window=f['window_counters'];u=window['updates'];native=f['native_counters'];controls=native['actual_native_policy_steps'];assert 0<u<=25 and window['policy_optimizer_steps']==window['encoder_optimizer_steps']==20*u and window['transitions_seen']==960000*u
assert native['actual_native_transitions']==20000*controls and native['physical_callbacks']==8*controls and native['feedback_callbacks']==2*controls and native['termination_computations']==controls
partial=controls-u*48;assert 0<=partial<=48
t=f['task_summary'];tracking=t['tracking_reward_config'];passive=t['low_rollout_summary'];criteria=t['low_criterion_summary'];names=('height_ok','upright_ok','speed_ok','angular_ok','wheels_ok','chassis_ok','joint_good')
assert tracking['height_gate_enabled']is False and all(v['height_gate_installed']is False for v in tracking['terms'].values())and passive['samples']==criteria['samples']==t['low_envs']*controls and passive['descriptive_only_not_acceptance']is criteria['descriptive_only_not_acceptance']is True and set(criteria['counts'])==set(names)and all(0<=v<=criteria['samples']for v in criteria['counts'].values())
nominal={}
for role,rows in j['rows'].items():
 assert len(rows)==5 and all(r['controls']==400 and r['finite_execution_error']is None for r in rows)
 failures={name:0 for name in names[:-1]}
 for row in rows:
  z=row['final'];ok=dict(height_ok=z['height_m']>=.23,upright_ok=z['tilt_deg']<10.,speed_ok=z['root_speed_m_s']<.03,angular_ok=z['angular_speed_rad_s']<.2,wheels_ok=all(v>1. for v in z['wheel_net_contact_force_N']),chassis_ok=z['chassis_net_contact_force_N']<1.)
  for name,good in ok.items():failures[name]+=not good
 nominal[role]=dict(cases=5,complete_finite_cases=5,engineering_credits=sum(bool(r['credited_by_same_engineering_predicate'])for r in rows),credited_and_stable_at_end=sum(bool(r['credited_and_stable_at_end'])for r in rows),mean_final_height_m=statistics.mean(r['final']['height_m']for r in rows),mean_final_tilt_deg=statistics.mean(r['final']['tilt_deg']for r in rows),mean_final_speed_m_s=statistics.mean(r['final']['root_speed_m_s']for r in rows),mean_endpoint_xy_displacement_m=statistics.mean(math.hypot(*r['final']['root_xy_m'])for r in rows),max_closure_error_m=max(r['max_closure_error_m']for r in rows),max_mimic_error_rad=max(r['max_mimic_error_rad']for r in rows),final_only_joint_component_failures=failures)
c,b=nominal['candidate'],nominal['frozen_mother'];prior=old['nominal_MuJoCo31']['comparison']['candidate'];previous_credit=old['original_N80']['recovery_first_episode_credits'];normal_regressed=normal[0]['first_episode_physical_terminated']>old['original_N80']['normal_first_episode_physical_terminated']
positive=credit>previous_credit or c['engineering_credits']>prior['engineering_credits'];decision='RETAIN_LOWSTD005_CANDIDATE_FOR_CONFIRMATORY_SCOPED_TEST_KEEP_REGISTRY_V12_UNCHANGED'if positive and not normal_regressed else 'KEEP_REGISTRY_V12_E3_1CD_NO_LOWSTD005_PROMOTION'
go=ad['actual_GO']['learning_started_epoch'];row=list(m['COHORT_FINAL.json']['rows'].values())[0]
training=dict(base_counters=zero,new_N20000=window,current_branch_counters=f['counters'],inherited_old_iterations=0,bad_candidate_reads=0,full_learner_resume=False,initial_policy_gaussian_std=.05,actual_fresh_learner_config=init['learner_config'],current_native=native,full_saved_unoptimized_pending_controls=partial,full_saved_unoptimized_pending_transitions=partial*20000,original_owner_exit=owner,outer_wait=outer,GO_to_worker_terminal_metadata_derived_seconds=row['owner_received_terminal_epoch']-go,GO_to_outer_actual_wait_metadata_derived_seconds=outer['epoch']-go,not_budget_ledger_rewrite=True,training_warm_source_receipt=f['source_checkpoint'],training_task_description_not_independent_grade=t,actual_original_tracking_configuration=tracking,pre_reset_height_descriptive_only=passive,pre_reset_joint_criteria_descriptive_only=criteria)
original=dict(execution_qualified=True,actual_original_parent_qualified=True,actual_parent_kind=o['actual_parent_wait_qualification']['kind'],collector_kind_erratum_needed=False,recovery_first_episode_credits=credit,original_request_denominator=n,normal_envs=6,normal_first_episode_physical_terminated=normal[0]['first_episode_physical_terminated'],requested_first_episode_physical_terminated=sum(r['first_episode_physical_terminated']for r in falls),recipe_rows=rr,seed=20260928,controls=160,no_reset_stitching=True,no_aggregate_original_graduation_rule_in_source=True,previous_published_credit=previous_credit,normal_physical_termination_increase=normal_regressed)
result=dict(kind='E3_FUDAN_LOWSTD005_FINITE25_ACTUAL_QUALITY',epoch=time.time(),source=e['source'],candidate_full_save=latest,training=training,original_N80=original,nominal_MuJoCo31=dict(comparison=nominal,published_W8_initial_std0p5_no_heightgate_reference=old['nominal_MuJoCo31']['comparison'],failed_heightgate_noncontrolled_previous_comparison=hg['nominal_MuJoCo31']['comparison'],pose_count=5,duration_per_pose_seconds=8,policy_hz=50,feedback_hz=100,physics_dt=.0025,clean_observations=True,full_DR=False,not_native_or_hardware_acceptance=True,no_whole_leg_same_end_video_claim=True),strict_joint_credit_above_W8_candidate=positive,independent_multiseed_or_matched_native_causality_established=False,decision=decision,H1_and_other_experts_unchanged=True,Registry_v12_and_selected_1cd_unchanged=True,all_complete_candidates_preserved=True,goal_complete=False,model_raw_or_canonical_IO=0)
outputs[0].write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8');link=lambda p,label:f'[{label}](<{p.as_posix()}>)'
criterion_table='\n'.join(f"| {name} | {criteria['counts'][name]:,.0f} | {criteria['fractions'][name]:.6f} |"for name in names)
report=f'''# E3 初始策略STD0.05 / N20000有限25：真实质量结果

## 结论

**实际{u}次PPO/两Adam各{window['policy_optimizer_steps']}次/{window['transitions_seen']:,}已优化转移，完整收口。原N80执行资格通过，首episode恢复信用{credit}/{n}。**

**{decision}**。原1cd/Registryv12保持，全部完整候选保留；H1/其它专家不动，总质量目标未完成。相对W8严格联合信用增加：{positive}，normal物理终止增加：{normal_regressed}。单seed/五姿态筛查不建立多seed毕业或matched native因果；诊断量变化不自动晋升。

原74请求与6normal分列：normal首episode物理终止{normal[0]['first_episode_physical_terminated']}/6不是normal接受率；请求组物理终止{original['requested_first_episode_physical_terminated']}/74。原stable50 public100Hz=0.5s=25控制，request300=3s，不拼reset。

## 唯一行为参数与固定边界

相对已经真实运行的W8无heightgate/STD0.5 baseline，仅将新policy Gaussian初始STD降为0.05。恢复W8原tracking函数/权重，不把失败heightgate继续叠加。实际constructed linear/tight/yaw weights分别{tracking['terms']['track_lin_vel']['weight']}/{tracking['terms']['track_lin_vel_tight']['weight']}/{tracking['terms']['track_ang_vel']['weight']}，所有heightgate marker为false。原低8s/400timeout、26 recipes、commands/height/negative奖励、动作scale、PPO核心与entropy/KL/两Adam自适应LR、2c/bae物理/fullD0D7保持。降低policy探索不是关闭D0D7噪声或延迟。

原1cd actor8+critic8 MLP warm；encoder随机fresh、新latent列0、STD/LR/两Adam/private generator/计数fresh，零继承，不续246ac/bf824/205。source_iter43090仅来源，实际1cd14715029B一次physical/hash/CPUdecode；原优化器/DR/history/旧迭代不应用。N20000/sole fresh reset/raw35×5，不声称PhysX位级resume。

Native {controls}控制/{native['physical_callbacks']}physics/{native['feedback_callbacks']}feedback/{native['actual_native_transitions']:,}真实转移；未优化pending{partial}控制/{partial*20000:,}转移。完整候选{latest['bytes']:,}B/SHA `{sha}`。inner+outer actual wait、成本结清/释放/errors=[]；GO至outer约{outer['epoch']-go:.3f}s是metadata解释，不改账。

## 原位pre-reset被动统计，不是联合技能接受率

低组样本{passive['samples']:,.0f}，均高{passive['sample_height_mean_m']:.6f}m，≥.23样本比例{passive['sample_ge023_fraction']:.6f}；已结束低episode{passive['endedLowEpisodes']:,.0f}，峰值均高{passive['ended_low_peak_height_mean_m']:.6f}m，峰值≥.23比例{passive['ended_low_peak_ge023_fraction']:.6f}。训练信用{t['credited_training_low_episodes']}/{t['completed_training_low_episodes']}分列，不当独立分数。

| 原条件 | 通过样本数 | 比例 |
|---|---:|---:|
{criterion_table}

七项复用原update已有height/gravity/root_speed/angular/contact，不增加getter/physics/sensor/RNG，typed float64[7]累计，不参与reward/credit。joint_good含原request条件；单项样本通过或高度峰值不等于连续0.5秒联合成立。旧W8缺同一被动计量，不能凭此建立配对因果。

## 同五姿名义31体MuJoCo末态均值

| 指标 | 本候选{sha[:8]} | W8 STD0.5/no-gate（已发布） | 冻结1cd（本次实跑） |
|---|---:|---:|---:|
| 高度 m | {c['mean_final_height_m']:.6f} | {prior['mean_final_height_m']:.6f} | {b['mean_final_height_m']:.6f} |
| 倾斜 deg | {c['mean_final_tilt_deg']:.3f} | {prior['mean_final_tilt_deg']:.3f} | {b['mean_final_tilt_deg']:.3f} |
| 根速度 m/s | {c['mean_final_speed_m_s']:.6f} | {prior['mean_final_speed_m_s']:.6f} | {b['mean_final_speed_m_s']:.6f} |
| 起终点平面位移 m | {c['mean_endpoint_xy_displacement_m']:.6f} | {prior['mean_endpoint_xy_displacement_m']:.6f} | {b['mean_endpoint_xy_displacement_m']:.6f} |
| 工程联合信用 | {c['engineering_credits']}/5 | {prior['engineering_credits']}/5 | {b['engineering_credits']}/5 |

双方五条均400控制/8秒、finite完整，同31机器人body/30坐标/原限位、50策略/100PD/.0025物理、PD60,2/wheel.6/scales.5,10、400N-k2000-d3，无外力/yaw/动画。clean raw35/frame-major5，不是native fullDR/硬件/视频整腿同端验收。严格工程条件：h≥.23、gz<−.984807753、v<.03、omega<.2、两wheel>1N/chassis<1N连续.5s。母版抬身能力与strict0/5分开陈述；实际末态分项见完整决定，不把0联合信用解读为全无能力。

## 保存、IO与证据

原唯一canonical/charge_values/authority2EX/privateGPU_EX/trainSH-evalEX/reserve86412.86069250107/3900-3600-300/1800preGO保持，无外国signal/清锁/改账/扩预算/退款。新完整来源每实际用途一次whole CPU read/hash/decode；原N80不投影20k DR/history、不装训练overlay、不优化。CPUexport仅下载{e['artifact']['bytes']:,}B/14pi/82505派生，非完整resume；没有为状态/Git开原PT或旧raw。

- {link(paths['training'],'训练完整终态')} / {link(paths['admission'],'实际原门控GO')}。
- {link(paths['original'],'原74 recipe及实际父资格')} / {link(paths['mujoco'],'同五姿十条完整物理案例')}。
- {link(paths['export'],'一次CPU派生收据')} / {link(outputs[0],'完整质量决定')}。

不按更新数或单项高度自动长跑/晋升。所有新成功失败/源码/本报告在下一有意义feature-only唯一annotated trial合并记录，main只读，不为Git重跑物理或消费旧once。质量goal保持active。
'''
outputs[1].write_text(report,encoding='utf8')
outputs[2].write_text(f'''# V22 — lowSTD005 Admission2有限25真实质量结果

- goal-c490e4cc-b28b-440e-bde6-30ee956813f0 rev3 active/armed/round3/14，质量未完成；H1/其它专家/Registryv12/1cd不变。{link(outputs[1],'实测报告')} / {link(outputs[0],'完整决定')}。
- W11 Admission2 root {a['root']}，GO{go}；实际{u}PPO/两Adam各{window['policy_optimizer_steps']}/{window['transitions_seen']:,}已优化转移，base0/无旧计数拼接；{controls}native controls/physics{native['physical_callbacks']}/feedback{native['feedback_callbacks']}/pending{partial}，完整{latest['bytes']}B/{sha}，inner+outer wait/cost/release/error[]全闭环。
- 原N80 V6_LOWSTD005真实父及collector全qualified；原{credit}/74，normal物理{normal[0]['first_episode_physical_terminated']}/6。名义MuJoCo十条completefinite，新候选{c['engineering_credits']}/5与母版{b['engineering_credits']}/5；候选h/v/XY {c['mean_final_height_m']:.6f}/{c['mean_final_speed_m_s']:.6f}/{c['mean_endpoint_xy_displacement_m']:.6f}，母版{b['mean_final_height_m']:.6f}/{b['mean_final_speed_m_s']:.6f}/{b['mean_endpoint_xy_displacement_m']:.6f}；非硬件/fullDR/video验收。
- 实际init STD0.05、tracking无heightgate；passive七项保留原阈值/联合good，不当独立信用。完整候选保留，决策{decision}，goal_completeFalse；原source/current坏候选不为状态/Git开启，旧once不重放。
- 上一准入阶段已核验feature14d2f3cca33913933f16d8baa6188d6d02567399/tag trial-20261105-e3-fudan-lowstd005-original-admission，616源，main只读c43b88f8d2f054dde60ffe546855a5817bef8651。其后真实GO/首positive/完整收口/N80/export/MuJoCo/本报告待新意义quality归档；原记录全校验+2短pathspec/fullstagedset，模型/raw/JSONL/geometry先跳再stat/read/hash，不为Git重跑物理、不造无限验证链。
''',encoding='utf8')
print(json.dumps(dict(outputs=[str(p)for p in outputs],actual_new_updates=u,original_recovery=f'{credit}/{n}',nominal_comparison=nominal,passive_criteria=criteria,decision=decision,goal_complete=False,model_raw_or_canonical_IO=0),indent=2))
