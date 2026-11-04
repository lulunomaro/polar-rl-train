"""Publish actual cached E3 training/skill/startup results; no PT/trajectory/SDK reopens."""
from pathlib import Path
import json,time,math
D=Path(__file__).resolve().parent;W=D.parent;assert not(D/'E3_CONTINUATION_RESULTS.json').exists();train=json.loads((D/'TRAIN_CLOSED_RESULT.json').read_bytes());ev=json.loads((D/'E3_ORIGINAL_FROZEN_SCOPE_RESULT.json').read_bytes());full_ev=json.loads((D/'EVAL_CLOSED_RESULT.json').read_bytes());mj=json.loads((D/'mujoco_startup/SUMMARY.json').read_bytes());base=json.loads((W/'mod4v1_e3_stowed_startup_20261104/SUMMARY.json').read_bytes());assert train['training_execution_qualified']and full_ev['execution_qualified']and ev['execution_qualified'];f=train['metadata']['roles/E3/production/FINAL.json'];ck=f['final'];assert ck['SHA']==ev['model_SHA']==mj['model_SHA']and f['actual_new_PPO_updates']==20 and f['actual_optimizer_step_calls']==400;new=mj['cases']['E3_recover_then_drive_same_weights'];old=base['E3_at_8s'];a=new['recovery_at_8s'];b=new['end_at_13s'];dx=a['root_xyz'][0]-new['initial']['root_xyz'][0];dy=a['root_xyz'][1]-new['initial']['root_xyz'][1]
assert dx<old['initial_to_8s_world_x_displacement_m']and a['upright_degrees']>old['upright_degrees']and a['linear_speed']>old['linear_speed_m_s']
def charge(v):
 c=v['metadata']['COHORT_FINAL.json'];assert c['original_cost_settled']and c['all_own_children_waited'];keys=list(c['go']);assert len(keys)==1;key=keys[0];return c['rows'][key]['owner_received_terminal_epoch']-c['go'][key]['learning_started_epoch']
w1=json.loads((W/'mod4v1_e3_continue_20261104/TRAIN_CLOSED_RESULT.json').read_bytes());costs={'W1_failed_startup_actual_expert_seconds':charge(w1),'W2_success_actual_expert_seconds':charge(train),'derivation':'Published own original GO through actual parent terminal; original canonical remains sole ledger; no refund or new ledger'}
comparison=dict(baseline_selected_mother_SHA=base['model_SHA'],candidate_SHA=ck['SHA'],baseline_at8s=old,candidate_at8s=a,candidate_initial_to_8s_world_xy_m=[dx,dy],baseline_drive_world_xy_m=base['same_E3_drive_8_to_13s']['world_xy_displacement_m'],candidate_drive_world_xy_m=new['drive_displacement_world_xy_m'],baseline_end_tilt_deg=base['same_E3_drive_8_to_13s']['end_upright_degrees'],candidate_end_tilt_deg=b['upright_degrees'],same_declared_pose_clock_plant_adapter_command_protocol=True,single_local_nominal_pose_not_native_fullDR_or_hardware=True,matched_local_input67ee_baseline_missing=True,causal_effect_of_only_this20_updates=None)
result=dict(kind='E3_ONE_BOUNDED_CONTINUATION_QUALITY_RESULT',epoch=time.time(),training_execution_qualified=True,actual_current_window_PPO_updates=20,actual_optimizer_step_calls=400,transitions=9600000,source_input_SHA=ck['source_SHA'],source_input_iteration=43110,source_input_Adam=866460,final_complete=ck,native_original_scope=ev,local_startup_comparison=comparison,actual_original_training_costs=costs,decision='KEEP_SELECTED_1CD_NO_A3CE_PROMOTION',decision_reason='Original recovery credit not improved and nominal rear-stowed startup much worse relative to existing selected1cd; candidate retained, no blind additional window',selected_mother_registry_H1_and_visible_replay_unchanged=True,all_new_native_train_and_eval_children_waited_and_leases_released=True,full_expert_graduation=False)
(D/'E3_CONTINUATION_RESULTS.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf8')
md=f'''# E3 单独续训与质量复测结果

## 结论
**本轮有效完成20次真实PPO更新并完整保存；新候选表现退化，保留原选中版本1cd，不替换演示、不晋升新候选a3ce，也未追加下一训练窗。**

本轮从上一轮完整PPO候选67ee（iter43110/Adam866460）接续，而非重放母版1cd已跑的20步，亦非旧SuperMimic分支。新候选a3ce相对母版1cd累计多40次PPO，其中本次20次。未对输入67ee做同样MuJoCo本地对照，因此差异不全部归因于本次20步。

## 实际训练
- 单4090，20,000环境，原PPO/fullD0–D7、原奖励/命令/接受判据，MOD4v1 400N/k2000/d3、50Hz/100Hz、.0025s/TGS32/4、closure/mimic .01均未改。
- 实际20 PPO updates、400 optimizer.step、480控制步、9,600,000 transitions；无未完成rollout。
- 完整保存iter **{ck['saved_iteration']}**、17 Adam一致step **{ck['saved_17Adam'][0]}**、实际LR **{ck['actual_saved_LR']}**，actor/critic/STD/optimizer/DR/历史/队列/RNG及未知字段完整验证保留。
- 新检查点SHA：`{ck['SHA']}`；{ck['bytes']} bytes。训练执行成功、实际内外wait/费用结清/释放完整；技能判定另列。
- 首次W1在初始完整保存的旧“只接受母版”元数据检查处中断，尚未调用PPO；原producer更新计数缺失，未把它伪造为计数0或技能0%。W2仅为当前run_id使用独立保存元数据命名空间，旧元数据完整保留。两次实际成本均保留：W1 **{costs['W1_failed_startup_actual_expert_seconds']:.3f}**、W2 **{costs['W2_success_actual_expert_seconds']:.3f}** expert-seconds（按原GO到实际parent terminal推导，非新账本）。

## 原Isaac恢复科目
N80、seed20260928、原13种recipe，160控制步/3.2s，原连续.5s稳定判据和第一episode范围不变。

| 子项 | 原选中1cd | 新a3ce |
|---|---:|---:|
| 请求恢复首episode稳定credit | 0/74 | {ev['recovery_n']}/74 |
| 正常recipe首episode物理终止 | 0/6 | {ev['normal_first_episode_physical_terminated']}/6 |

新评测实际执行合格、1280物理/320反馈、0学习更新、完整关闭/wait/EX释放。终止事件：`{json.dumps(ev['termination_events_by_reason'],ensure_ascii=False)}`；事件可重叠，不加总成独立失败人数。该3.2秒原科目统计不是“任何场景都起不来”的结论，也不是实机毕业。

## 同一个后收平放上电场景：本地MuJoCo
与原基线采用同一个22关节后收闭链姿态、初始高度.18495m/平放/零速度、同一场景与动作映射，0–8s mode3/vx0，8–13s mode0/vx.2；全程同一个E3，不换E0。只运行新候选一次，旧zero-torque未重跑。

| 指标 | 原选中1cd | 新a3ce |
|---|---:|---:|
| 8s机身高度 | {old['root_xyz'][2]*100:.2f}cm | {a['root_xyz'][2]*100:.2f}cm |
| 8s倾角 | {old['upright_degrees']:.2f}° | {a['upright_degrees']:.2f}° |
| 恢复阶段世界X位移 | {old['initial_to_8s_world_x_displacement_m']:+.3f}m | {dx:+.3f}m |
| 恢复阶段世界Y位移 | {old['root_xyz'][1]:+.3f}m | {dy:+.3f}m |
| 8s线速度（指令为0） | {old['linear_speed_m_s']:.3f}m/s | {a['linear_speed']:.3f}m/s |
| 8–13s世界X位移 | {base['same_E3_drive_8_to_13s']['world_xy_displacement_m'][0]:+.3f}m | {new['drive_displacement_world_xy_m'][0]:+.3f}m |
| 13s倾角 | {base['same_E3_drive_8_to_13s']['end_upright_degrees']:.2f}° | {b['upright_degrees']:.2f}° |

新候选在零速度恢复指令下发生较大前后/侧向漂移，平衡与停稳明显差于当前使用版本。两者都在.36s一度达到参考高度/角度，**该穿越时刻不代表稳定起身成功**。世界位移与机身局部速度分开报告；不把旧CAD局部坐标vx直接当作世界前向跟踪指标。此处仅一个名义MuJoCo姿态诊断，不替代Isaac/fullDR/实机资格，也未建立本轮20步的严格因果归因。

## 保留策略与证据
原母版、67ee输入及新a3ce完整候选均保留，Registryv12/H1/当前可视回放未修改。原恢复credit无提升且本地上电保持更差，因此不采用新候选、不盲目再加一窗。

- [训练完整闭环](<mod4v1_e3_continue_v2_20261104/TRAIN_CLOSED_RESULT.json>)
- [原N80逐recipe评测](<mod4v1_e3_continue_v2_20261104/E3_ORIGINAL_FROZEN_SCOPE_RESULT.json>)
- [新候选本地紧凑结果](<mod4v1_e3_continue_v2_20261104/mujoco_startup/SUMMARY.json>)
- [旧选中版本上电基线](<mod4v1_e3_stowed_startup_20261104/SUMMARY.json>)
- [W1实际失败及最小保存修复](<mod4v1_e3_continue_v2_20261104/W1_FAILURE_AND_V2_METADATA_FIX.json>)
- [本地评测源AST读者错误及修复](<mod4v1_e3_continue_v2_20261104/EVAL_LOCAL_AST_READER_FAILURE_AND_V2_FIX.json>)，发生在SSH/新root/SDK之前，未重跑旧评测。

本报告及本轮源码、实际失败/结果将合并一次feature-only annotated trial归档，最终远端核验以工具返回为准；不为Git重开权重或原始轨迹。
'''
(D/'E3_CONTINUATION_RESULTS.md').write_text(md,encoding='utf8');print(json.dumps(dict(actual_PPO_updates=20,final_SHA=ck['SHA'],original_recovery=[ev['recovery_n'],74],candidate_8s_world_xy=[dx,dy],candidate_8s_tilt=a['upright_degrees'],decision=result['decision'],actual_original_costs=costs),indent=2))
