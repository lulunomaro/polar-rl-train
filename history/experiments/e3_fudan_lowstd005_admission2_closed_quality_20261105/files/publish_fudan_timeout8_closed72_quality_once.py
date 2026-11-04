"""Publish current actual quality evidence; input is bounded produced JSON metadata only."""
from pathlib import Path
import json,time,math,statistics
D=Path(__file__).resolve().parent
paths=dict(training=D/'reports/FDN_N20000_W6_TIMEOUT8_20261104_231152/CLOSED_RESULT.json',original=D/'FDNTIMEOUT8_FROZEN_ORIGINAL_SCOPE_READER_V2_RESULT.json',reader_erratum=D/'FDNTIMEOUT8_FROZEN_COLLECTOR_KIND_ERRATUM_V1.json',mujoco=D/'FDN_TIMEOUT8_MUJOCO31_LOWRise_RESULT.json',export=D/'FDNTIMEOUT8_PI_ONLY_EXPORT_STARTED_ONCE.json',previous=D/'FDN_N20000_CLOSED69_QUALITY_DECISION_V1.json')
outputs=[D/'FDN_TIMEOUT8_CLOSED72_QUALITY_DECISION_V1.json',D/'FDN_TIMEOUT8_CLOSED72_QUALITY_RESULTS_V1.md',D/'CURRENT_PROGRESS_V13_TIMEOUT8_CLOSED72_QUALITY_NOT_IMPROVED.md']
assert not any(p.exists()for p in outputs)
a,o,err,j,e,old=[json.loads(paths[k].read_bytes())for k in('training','original','reader_erratum','mujoco','export','previous')]
m=a['metadata'];f=m['FDN_FINAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json'];owner=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json']
assert a['closed']is True and f['final']is True and f['complete_save']is True and f['error']is None and f['close_errors']==[]and latest==f['latest_complete_save']
assert owner['errors']==[]and all(owner[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0
assert q['qualified']is True and all(v is True for v in q['checks'].values())and o['execution_qualified']is True and all(o['execution_checks'].values())
assert e['complete']is True and e['source']['sha256']==latest['sha256']==o['source_binding']['sha256']==j['source_export']['sha256']=='3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e'
s=o['original_worker_outcome_verbatim'];rr=s['original_recovery_recipe_rows'];falls=[r for r in rr if r['original_request']];normal=[r for r in rr if not r['original_request']]
assert len(rr)==13 and len(falls)==12 and len(normal)==1 and normal[0]['recipe']==12 and normal[0]['initial_envs']==6
n=sum(r['initial_envs']for r in falls);credit=sum(r['first_episode_original_stable_credit']for r in falls);assert n==74==s['original_recovery_request_denominator']and credit==s['original_first_episode_recovery_credits']
base,window,cum=f['base_counters'],f['window_counters'],f['counters'];native=f['native_counters'];controls=native['actual_native_policy_steps']
assert base['updates']==133 and window['updates']==72 and cum['updates']==205 and all(cum[k]==base[k]+window[k]for k in base)
assert window['policy_optimizer_steps']==window['encoder_optimizer_steps']==72*20 and window['transitions_seen']==72*48*20000
assert native['actual_native_transitions']==20000*controls and native['physical_callbacks']==8*controls and native['feedback_callbacks']==2*controls
partial=controls-window['updates']*48;assert 0<=partial<=48
nominal={}
for role,rows in j['rows'].items():
 assert len(rows)==5 and all(r['controls']==400 and r['finite_execution_error']is None for r in rows)
 nominal[role]=dict(cases=5,complete_finite_cases=5,engineering_credits=sum(bool(r['credited_by_same_engineering_predicate'])for r in rows),credited_and_stable_at_end=sum(bool(r['credited_and_stable_at_end'])for r in rows),mean_final_height_m=statistics.mean(r['final']['height_m']for r in rows),mean_final_tilt_deg=statistics.mean(r['final']['tilt_deg']for r in rows),mean_final_speed_m_s=statistics.mean(r['final']['root_speed_m_s']for r in rows),mean_endpoint_xy_displacement_m=statistics.mean(math.hypot(*r['final']['root_xy_m'])for r in rows),max_closure_error_m=max(r['max_closure_error_m']for r in rows),max_mimic_error_rad=max(r['max_mimic_error_rad']for r in rows))
row=list(m['COHORT_FINAL.json']['rows'].values())[0];go=1793805189.6210587
result=dict(kind='E3_FUDAN_TIMEOUT8_ACTUAL_CLOSED72_QUALITY_NOT_IMPROVED',epoch=time.time(),source=e['source'],candidate_full_save=latest,training=dict(preceding_mixed_N4096_64_plus_N20000_69=base,new_N20000=window,cumulative=cum,current_native=native,full_saved_unoptimized_pending_controls=partial,full_saved_unoptimized_pending_transitions=partial*20000,original_owner_exit=owner,outer_wait=outer,GO_to_worker_terminal_metadata_derived_seconds=row['owner_received_terminal_epoch']-go,GO_to_outer_actual_wait_metadata_derived_seconds=outer['epoch']-go,not_budget_ledger_rewrite=True,training_task_description_not_independent_grade=f.get('task_summary')),original_N80=dict(execution_qualified=True,actual_original_parent_qualified=True,collector_kind_reader_erratum_preserved=err,recovery_first_episode_credits=credit,original_request_denominator=n,normal_envs=6,normal_first_episode_physical_terminated=normal[0]['first_episode_physical_terminated'],requested_first_episode_physical_terminated=sum(r['first_episode_physical_terminated']for r in falls),recipe_rows=rr,seed=20260928,controls=160,no_reset_stitching=True,no_aggregate_original_graduation_rule_in_source=True),nominal_MuJoCo31=dict(comparison=nominal,previous_8af4_published_comparison=old['nominal_MuJoCo31']['comparison'],pose_count=5,duration_per_pose_seconds=8,policy_hz=50,feedback_hz=100,physics_dt=.0025,clean_observations=True,full_DR=False,not_native_or_hardware_acceptance=True,no_whole_leg_same_end_video_claim=True),decision='KEEP_REGISTRY_V12_E3_1CD_NO_3E64_PROMOTION',H1_and_other_experts_unchanged=True,full_candidate_preserved=True,quality_improvement_not_established=True,native_causal_regression_claim=False,goal_complete=False,source_metadata={k:str(p)for k,p in paths.items()},models_or_raw_or_canonical_IO=0)
outputs[0].write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8')
link=lambda p,label:f'[{label}](<{p.as_posix()}>)'
c,b=nominal['candidate'],nominal['frozen_mother'];prior=old['nominal_MuJoCo31']['comparison']['candidate']
report=f'''# E3 Fudan / N20000 / 低趴8秒timeout：实际闭环结果

## 质量结论

**训练、完整保存及真实评测已完成；低趴8秒timeout干预本轮仍未显示起身质量改善，保留冻结1cd母版。**

- 原 N80/160/seed20260928：首episode恢复信用 **{credit}/{n}**。正常6例另列，物理终止 **{normal[0]['first_episode_physical_terminated']}/6**；不是正常技能通过率或整专家毕业率。
- 31体MuJoCo相同五合法低姿×8秒、每条400控制，候选与母版完整finite **5/5**，工程联合信用分别 **{c['engineering_credits']}/5、{b['engineering_credits']}/5**。母版抬高了车身；新候选仍低位后退。
- **Decision：KEEP_REGISTRY_V12_E3_1CD_NO_3E64_PROMOTION**。保留3e64完整候选和失败证据，H1/其它专家/Registryv12不变。总质量目标未完成。

## 真实训练量

| 阶段 | PPO | 策略Adam | encoder Adam | 已优化转移 |
|---|---:|---:|---:|---:|
| 已关闭前序：4096×64＋20000×69 | {base['updates']} | {base['policy_optimizer_steps']} | {base['encoder_optimizer_steps']} | {base['transitions_seen']:,} |
| 本窗新增：20000/T48 | **{window['updates']}** | **{window['policy_optimizer_steps']}** | **{window['encoder_optimizer_steps']}** | **{window['transitions_seen']:,}** |
| 完整learner累计（混合环境数） | {cum['updates']} | {cum['policy_optimizer_steps']} | {cum['encoder_optimizer_steps']} | {cum['transitions_seen']:,} |

本窗native控制 {controls}、physical callbacks {native['physical_callbacks']}、feedback {native['feedback_callbacks']}、真实转移 {native['actual_native_transitions']:,}。完整保存的 **{partial}个控制/{partial*20000:,}转移未优化**，不是第73次PPO。累计205步不是205步N20000。

从1.2GB完整8af4源实际续接模型、critic、STD、LR、两套Adam和私有generator，读/hash/CPU decode各一次；当前母版/4096祖先读0。新N20000环境/DR/history/global环境RNG fresh reset，source48 pending未应用，不是PhysX位级resume。

本轮唯一任务干预是低趴recipe>=13专用400个已完成控制步的time_out=True；实际全局episode回读20.0s，其余fall/normal、PPO、奖励、物理与fullDR保持。它是经过实际运行的配置，不是已证明的历史根因修复。

原inner/outer actual wait、成本结清及释放均完成，errors=[]。GO到outer actual wait派生时长约 {outer['epoch']-go:.3f}秒；只是metadata解释，不新建或重写canonical。

## 名义MuJoCo末态五姿均值

| 指标 | 本次3e64 | 上次8af4（已发布） | 冻结1cd |
|---|---:|---:|---:|
| 高度 m | {c['mean_final_height_m']:.6f} | {prior['mean_final_height_m']:.6f} | {b['mean_final_height_m']:.6f} |
| 倾斜 deg | {c['mean_final_tilt_deg']:.3f} | {prior['mean_final_tilt_deg']:.3f} | {b['mean_final_tilt_deg']:.3f} |
| 根速度 m/s | {c['mean_final_speed_m_s']:.6f} | {prior['mean_final_speed_m_s']:.6f} | {b['mean_final_speed_m_s']:.6f} |
| 起终点平面位移 m | {c['mean_endpoint_xy_displacement_m']:.6f} | {prior['mean_endpoint_xy_displacement_m']:.6f} | {b['mean_endpoint_xy_displacement_m']:.6f} |
| 工程联合信用 | {c['engineering_credits']}/5 | {prior['engineering_credits']}/5 | {b['engineering_credits']}/5 |

原工程条件含高度≥.23m、姿态/速度/角速度、双轮接触与车身脱地连续.5s。母版速度约.038m/s仍高于.03门，0/5不等于没有抬起。新候选名义高度未提升且后退/速度更大；不据此声称native因果退化或timeout本身单独导致该差异。

这是相同31体/30坐标名义MuJoCo、clean raw35、50Hz策略/100Hz反馈/.0025物理；不是native fullDR或硬件验收，也未覆盖视频整腿同端姿态。没有额外抬升/yaw/动画。旧比较只读取已发布紧凑JSON，没有重开模型或旧raw。

## 评测reader误报已原样保留、仅metadata纠正

原父实际wait后的V3_TIMEOUT8 qualification为true，全部检查通过。collector仍比较V2_N20000 kind，独立一个reader条件误报false；其他11项execution检查为true。{link(paths['reader_erratum'],'专门erratum')}与旧false输出并存。新reader只读取已闭环JSON，将kind识别对齐实际V3，不重跑父qualification、collector、SDK、模型或物理；原0/74/recipe rows丝毫未改。

## 完整证据

- 完整候选 {latest['bytes']:,} bytes，SHA256 `{latest['sha256']}`，留于原production。
- 派生pi-only {e['artifact']['bytes']:,} bytes、14张量/82505标量，明确不是训练resume；只下载小artifact，完整源不为状态或Git重开。
- {link(paths['training'],'真实训练闭环')}
- {link(paths['original'],'原N80 outcome、原父资格与reader修正')}
- {link(paths['mujoco'],'MuJoCo十条实际案例')}
- {link(outputs[0],'完整紧凑结果与保留决定')}

## 下一步

停止按205这个累计数字盲续低位漂移候选。先用本次实际失败反馈选一个训练干预，优先审视从保留1cd重建fresh Fudan learner而非继承坏候选；新谱系不能拼接本谱系Adam、计数或声称full resume。该方向尚未执行，原74分母/判据、physics/DR及完整记录要求继续不变。
'''
outputs[1].write_text(report,encoding='utf8')
handoff=f'''# V13 — timeout8真实closed72；原范围0/74；仍保留1cd

- 当前goal goal-c490e4cc-b28b-440e-bde6-30ee956813f0 rev3 active/armed/max14；目标是质量，不标complete/pause/blocked。
- {link(outputs[1],'完整实测报告')}与{link(outputs[0],'紧凑选择')}已发布。本窗72真实PPO/两Adam各1440/69,120,000优化转移；累计205/4100/147,942,912，原始4096×64不能冒充N20000。完整保存48个未优化控制。
- 完整新候选SHA {latest['sha256']}，{latest['bytes']}B；母版1cd、4096祖先47937、上窗8af4与pi-only93753各自独立。完整learner续接实际CPU一次，环境/DR/history流切断fresh。所有原训练wait/cost/release闭环/errors空，无本任务native训练剩余。
- 原N80实际父1623792/worker1623801/controller1623785，单N80/160/seed20260928/fullDR/原74首episode+6normal。父actual qualification原本为true；collector忘改kind导致仅reader误报false，旧文件保留，新metadata-only reprocess已纠正，不重跑SDK/模型/父资格。结果0/74，normal物理终止{normal[0]['first_episode_physical_terminated']}/6。
- MuJoCo相同5姿每条400control/8s全finite。新候选均值高度{c['mean_final_height_m']:.6f}、速度{c['mean_final_speed_m_s']:.6f}、位移{c['mean_endpoint_xy_displacement_m']:.6f}；母版{b['mean_final_height_m']:.6f}/{b['mean_final_speed_m_s']:.6f}/{b['mean_endpoint_xy_displacement_m']:.6f}；严格信用双方0/5，但母版确实抬高了身。不能称全DR/硬件/视频同端姿态成绩或native因果退化。
- Decision KEEP_REGISTRY_V12_E3_1CD_NO_3E64_PROMOTION，所有候选保留，H1/其它专家不动。下一步单一质量干预源分析尚未形成部署，不按205步数盲续。
- 原训练observer009、原N80observer895均completed0并已收输出；CPUexport和MuJoCo命令均完成0。旧once/roots不可重放，不为状态/Git开模型或raw。
- 最近已验证archive cce218551eba7d527e4b611a41bc6536c1f75039 / trial-20261104-e3-fudan-n20000-timeout8-real-fullresume-native，tagobj ede4f6dd6cd2a8aea2e087c04a2904f562662733。原record WinError206已在同一record短pathspec续完并归档，不重放record。本次72闭环、reader false+纠正、MuJoCo与质量决定等待下一有意义合并阶段archive；新archive务必使用短directory pathspec适配原record，避免Windows argv过长。feature-only/main只读。
'''
outputs[2].write_text(handoff,encoding='utf8')
print(json.dumps(dict(outputs=[str(p)for p in outputs],new_updates=window['updates'],original_recovery=f'{credit}/{n}',nominal_comparison=nominal,decision=result['decision'],goal_complete=False,model_raw_or_canonical_IO=0),indent=2))
