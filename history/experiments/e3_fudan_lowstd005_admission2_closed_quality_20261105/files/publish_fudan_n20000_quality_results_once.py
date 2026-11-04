"""Publish measured metadata only; never open models, trajectories or a budget ledger."""
from pathlib import Path
import json,math,statistics,time
D=Path(__file__).resolve().parent
paths=dict(training=D/'reports/FDN_N20000_W5_20261104_205335/CLOSED_RESULT.json',original=D/'FDNN20000_FROZEN_ORIGINAL_SCOPE_RESULT.json',mujoco=D/'FDN_N20000_MUJOCO31_LOWRise_RESULT.json',export=D/'FDNN20000_PI_ONLY_EXPORT_STARTED_ONCE.json')
outputs=[D/'FDN_N20000_CLOSED69_QUALITY_DECISION_V1.json',D/'FDN_N20000_QUALITY_RESULTS_V1.md',D/'CURRENT_PROGRESS_V11_N20000_CLOSED69_QUALITY_NOT_IMPROVED.md']
assert not any(p.exists()for p in outputs)
a,o,j,e=[json.loads(paths[k].read_bytes())for k in('training','original','mujoco','export')]
m=a['metadata'];f=m['FDN_FINAL.json'];q=m['FDN_PARENT_WAIT_QUALIFICATION.json'];owner=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json']
assert a['closed']is True and f['final']is True and f['complete_save']is True and f['error']is None and f['close_errors']==[]
assert owner['errors']==[] and all(owner[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))
assert outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0 and q['qualified']is True and all(v is True for v in q['checks'].values())
assert latest==f['latest_complete_save'] and e['complete']is True and e['source']['sha256']==latest['sha256']==o['source_binding']['sha256']==j['source_export']['sha256']
assert o['execution_qualified']is True and all(o['execution_checks'].values())
s=o['original_worker_outcome_verbatim'];rr=s['original_recovery_recipe_rows'];falls=[r for r in rr if r['original_request']];normal=[r for r in rr if not r['original_request']]
assert len(rr)==13 and len(falls)==12 and len(normal)==1 and normal[0]['recipe']==12
n=sum(r['initial_envs']for r in falls);credit=sum(r['first_episode_original_stable_credit']for r in falls)
assert n==74==s['original_recovery_request_denominator'] and credit==s['original_first_episode_recovery_credits']
assert normal[0]['initial_envs']==6
base,window,cum=f['base_counters'],f['window_counters'],f['counters'];native=f['native_counters'];controls=native['actual_native_policy_steps']
assert base['updates']==64 and window['updates']==69 and cum['updates']==133
assert window['policy_optimizer_steps']==window['encoder_optimizer_steps']==69*20 and window['transitions_seen']==69*48*20000
assert all(cum[k]==base[k]+window[k]for k in base)
assert native['actual_native_transitions']==20000*controls and native['physical_callbacks']==8*controls and native['feedback_callbacks']==2*controls
partial=controls-window['updates']*48;assert 0<=partial<=48
nominal={}
for role,rows in j['rows'].items():
    assert len(rows)==5 and all(r['controls']==400 and r['finite_execution_error']is None for r in rows)
    nominal[role]=dict(cases=5,complete_finite_cases=5,engineering_credits=sum(bool(r['credited_by_same_engineering_predicate'])for r in rows),credited_and_stable_at_end=sum(bool(r['credited_and_stable_at_end'])for r in rows),mean_final_height_m=statistics.mean(r['final']['height_m']for r in rows),mean_final_tilt_deg=statistics.mean(r['final']['tilt_deg']for r in rows),mean_final_speed_m_s=statistics.mean(r['final']['root_speed_m_s']for r in rows),mean_endpoint_xy_displacement_m=statistics.mean(math.hypot(*r['final']['root_xy_m'])for r in rows),max_closure_error_m=max(r['max_closure_error_m']for r in rows),max_mimic_error_rad=max(r['max_mimic_error_rad']for r in rows))
row=list(m['COHORT_FINAL.json']['rows'].values())[0]
wall_derived=row['owner_received_terminal_epoch']-1793796864.332392
result=dict(kind='N20000_E3_FUDAN_ACTUAL_QUALITY_AND_SCOPED_KEEP_DECISION',epoch=time.time(),source=e['source'],candidate_full_save=latest,training=dict(base_N4096=base,new_N20000=window,cumulative=cum,current_native=native,full_saved_unoptimized_pending_controls=partial,full_saved_unoptimized_pending_transitions=partial*20000,original_owner_exit=owner,outer_wait=outer,GO_to_terminal_metadata_derived_expert_seconds=wall_derived,not_budget_ledger_rewrite=True,training_task_description_not_independent_grade=f.get('task_summary')),original_N80=dict(execution_qualified=True,recovery_first_episode_credits=credit,original_request_denominator=n,normal_envs=6,normal_first_episode_physical_terminated=normal[0]['first_episode_physical_terminated'],requested_first_episode_physical_terminated=sum(r['first_episode_physical_terminated']for r in falls),recipe_rows=rr,seed=20260928,controls=160,no_reset_stitching=True,no_aggregate_original_graduation_rule_in_source=True),nominal_MuJoCo31=dict(comparison=nominal,pose_count=5,duration_per_pose_seconds=8,policy_hz=50,feedback_hz=100,physics_dt=.0025,clean_observations=True,full_DR=False,not_native_or_hardware_acceptance=True,no_whole_leg_same_end_video_claim=True),decision='KEEP_REGISTRY_V12_E3_1CD_NO_8AF4_PROMOTION',H1_and_other_experts_unchanged=True,full_candidate_preserved=True,quality_improvement_not_established=True,native_causal_regression_claim=False,goal_complete=False,source_metadata={k:str(p)for k,p in paths.items()},models_or_raw_or_canonical_IO=0)
outputs[0].write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8')
link=lambda p,label:f'[{label}](<{p.as_posix()}>)'
c,b=nominal['candidate'],nominal['frozen_mother']
report=f'''# E3 Fudan / N20000 实测结果

## 结论

**N20000 真实训练与独立原范围评测均完成，但尚无起身质量改善证据；本候选不替换冻结母本。**

- 原 E3 首 episode 稳定恢复计分：**{credit}/{n}**。原口径的6个正常案例另列，物理终止 **{normal[0]['first_episode_physical_terminated']}/6**，不并入恢复分母。
- 31体 MuJoCo 的5个固定合法低姿、每姿8秒对照中，候选与母本按完整工程联合条件均 **0/5**。这不是原 E3 整专家毕业判定，也不是 native/fullDR 成绩。
- MuJoCo 母本确实抬高了车身；候选反而维持低位并明显后退。不给“两个都0，所以行为相同”的解释。
- **保留 Registry v12 的 E3 `1cd99995…`；保存 `8af4e04c…` 完整候选与所有失败证据，不推广。H1 和其他专家不变。**

## 实际训练量

| 阶段 | 环境数 | 实际 PPO 更新 | 策略 Adam | 编码器 Adam | 已优化 transitions |
|---|---:|---:|---:|---:|---:|
| 已关闭的前窗 | 4096 | {base['updates']} | {base['policy_optimizer_steps']} | {base['encoder_optimizer_steps']} | {base['transitions_seen']:,} |
| 本窗新增 | **20000** | **{window['updates']}** | **{window['policy_optimizer_steps']}** | **{window['encoder_optimizer_steps']}** | **{window['transitions_seen']:,}** |
| 完整 learner 累计 | 分阶段 | {cum['updates']} | {cum['policy_optimizer_steps']} | {cum['encoder_optimizer_steps']} | {cum['transitions_seen']:,} |

累计133步不是133步 N20000。新窗实际控制 {controls} 次、physical callbacks {native['physical_callbacks']}、feedback callbacks {native['feedback_callbacks']}；完整保存的 **{partial} 个控制/{partial*20000:,} 个 transitions 尚未优化**，不冒充第70次更新。

本窗恢复了模型、critic、STD、LR、两套 Adam 与 learner 私有 generator；N20000 环境/DR/历史为新初始化，没有把旧4096环境状态裁切成20000。原 inner/outer wait、计费结算、租约释放均完成，errors为空。按 GO→原终态元数据算得约 {wall_derived:.3f} expert-seconds；它是派生说明，不是新账本或退款。

## MuJoCo 名义行为：5姿平均8秒末

| 指标 | 新候选 | 冻结母本 |
|---|---:|---:|
| 车身高度 m | {c['mean_final_height_m']:.6f} | {b['mean_final_height_m']:.6f} |
| 倾斜 deg | {c['mean_final_tilt_deg']:.3f} | {b['mean_final_tilt_deg']:.3f} |
| 根速度 m/s | {c['mean_final_speed_m_s']:.6f} | {b['mean_final_speed_m_s']:.6f} |
| 起点至终点平面位移 m | {c['mean_endpoint_xy_displacement_m']:.6f} | {b['mean_endpoint_xy_displacement_m']:.6f} |
| 完整、finite案例 | 5/5 | 5/5 |
| 工程联合条件计分 | 0/5 | 0/5 |

工程条件仍为高度≥0.23m、重力/线速度/角速度、双轮接触及车身脱地连续0.5秒的联合条件。母本末速度约0.038m/s，超过0.03m/s门；不能把母本的0/5解释成没有抬起。候选的名义高度和漂移较差，但这不是跨 backend 的 native 因果退化证明。

这是新31体/30坐标模型的真实 MuJoCo 仿真，50Hz策略/100Hz PD/0.0025s物理；使用名义参数与 clean raw35，非 native 噪声/延迟/完整DR。五个姿势保持既有关节范围，**没有覆盖参考视频中整腿同端的姿态**。没有外部抬升、yaw辅助或姿态动画。

## 完整产物与证据

- 完整候选：{latest['bytes']:,} bytes，SHA256 `{latest['sha256']}`；保留于原远程 production。
- 派生部署文件：338,617 bytes，只含14个 actor+encoder 张量、82,505个标量；**不是完整训练 resume**。原完整输入仅为实际导出目的读取/哈希/CPU解码各一次，未下载1.2GB完整输入。
- {link(paths['training'],'训练原始闭环')}
- {link(paths['original'],'原 E3 N80 outcome 与实际父等待资格')}
- {link(paths['mujoco'],'MuJoCo十条真实案例')}
- {link(outputs[0],'紧凑选择与算术结果')}

## 下一步

先针对奖励/请求窗口/训练数据分配检查提出单一、可测试干预，再决定下一窗；不按133这个数字盲续本候选。原74案例和正常保留口径、物理、DR、H1及冻结母本保持不动。本次总质量目标仍在推进，未标完成。
'''
outputs[1].write_text(report,encoding='utf8')
handoff=f'''# V11 — N20000 closed69；原范围0/74；不推广候选

- 当前 goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision3，active/armed，max14；质量改善未实现，不 complete/pause/blocked。
- 本窗 N20000/T48 新增69真实PPO/双Adam1380/66,240,000已优化transitions；累计133/双2660/78,822,912。native控制3360，完整保存48个未优化控制。
- 完整候选SHA `{latest['sha256']}`，{latest['bytes']} bytes；source/new env/DR/history/RNG语义见 {link(outputs[1],'实测总报告')}。
- 原 native N80/160/seed20260928执行qualified，0/74；normal6的物理终止0；父/子/outer实际等待与资源释放均闭环。原口径未放宽。
- 31体名义MuJoCo5姿×8s各400control均finite。严格计分双方0/5；候选高度约.183m/速度.309，母本高度约.241m/速度.038，不能把两者行为说相同。未证明native因果退化。
- Decision：`KEEP_REGISTRY_V12_E3_1CD_NO_8AF4_PROMOTION`。H1/其他专家/Registryv12不变，所有完整候选保留。
- stage_v1只在本地 pinned-assets 两/三空格锚点失败，marker/connect/模型/SDK/GO前；旧源保留。新stage_v2仅修两处锚点，成功完整nonPT materialization445files。没有物理重跑旧根。
- native训练observer6639、CPUexport66529、真实MuJoCo6d4、原native评测47bb均已completed0并收集，当前无本任务 native/observer。勿复跑已消费 stage/dispatch/collector/export/benchmark。
- 14权重派生artifact见 {link(Path(e['local_pi_export']),'pi-only部署artifact')}；它明确不是完整resume。原1.2GB输入不为状态/Git重开。
- 一个源分析child 3b92c2b6-8850-4ad3-857f-77fc0e518590只查奖励/episode/窗口，禁止模型/SDK/CPUfixture/SSH/Git；待其短结论后选单一质量干预，不盲续数。
- 最新已验证archive仍4fc5baf6c8a1df672bbb3d281475d6b370d70a4b / trial-20261104-e3-fudan-n20000-admission2-native；本次69闭环、实测、失败、选择、晚源等待下一次有意义合并archive。feature-only，main只读；模型/raw/media/geometry在stat/read/hash前跳过。
'''
outputs[2].write_text(handoff,encoding='utf8')
print(json.dumps(dict(outputs=[str(p)for p in outputs],new_N20000_updates=window['updates'],original_recovery=f'{credit}/{n}',nominal_credits={k:v['engineering_credits']for k,v in nominal.items()},decision=result['decision'],goal_complete=False,model_or_raw_IO=0),indent=2))
