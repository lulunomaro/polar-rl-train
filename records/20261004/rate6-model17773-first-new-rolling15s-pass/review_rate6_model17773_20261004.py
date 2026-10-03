"""Review the existing second6 assessment, without running or changing training."""
import json
from datetime import datetime,timezone,timedelta
from pathlib import Path
D=Path(__file__).resolve().parent
read=lambda n:json.loads((D/n).read_text(encoding='utf8'))
r=read('auto_0051_assessment_cap6_white_v2_rate.json');old=read('auto_0049_assessment_cap6_white_v2_rate.json')
decision=read('auto_0051_assessment_cap6_white_v2_decision.json')
actual=read('RATE6_MODEL17773_ACTUAL_VERIFIED.json');runtime=read('RUNTIME_ACTUAL.json')
assert r['physical_smoke_pass'] and r['spin_skill_pass'] and r['spin_skill_pass_legacy_reference']
assert len(r['alive'])==88 and all(r['alive']) and not r['nonfinite']
assert all(g['spin_skill_fraction']==g['spin_skill_fraction_legacy_reference']==1 for g in r['groups'])
assert r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass']
assert decision['current_rate_skill_pass'] and decision['original_flat_admission']['eligible_for_mild_dr_trial']
assert all(g['physical_admission_fraction']==1 for g in decision['original_flat_admission']['groups'])
assert all(r[k]==old[k] for k in ['reset_root_before_physics','reset_joint_pos_before_physics','group_ids','probe_sha256','seed','profile'])
assert actual['resume_source']['sha256']==decision['checkpoint']['sha256']
p=r['per_environment'];pureids=[i for i,g in enumerate(r['group_ids']) if g in [7,8]]
rows=[]
for gid in [7,8]:
 ids=[i for i,g in enumerate(r['group_ids']) if g==gid]
 rows.append(dict(group_id=gid,environment_ids=ids,skill_count=8,per_environment={k:[p[k][i] for i in ids] for k in p}))
metrics=dict(max_mean_mesh_slip_m_s=max(p[k][i] for k in ['left_slip','right_slip'] for i in pureids),
 positive_yaw_mean=sum(p['yaw_rate'][i] for i,g in enumerate(r['group_ids']) if g==7)/8,
 negative_yaw_mean=sum(p['yaw_rate'][i] for i,g in enumerate(r['group_ids']) if g==8)/8,
 pure_peak_tilt_deg=max(p['peak_tilt'][i] for i in pureids),pure_gap_max_m=max(p['maximum_gap_m'][i] for i in pureids),
 pure_both_low_max_s=max(p['longest_both_low_s'][i] for i in pureids),
 pure_mean_xy_speed_max_m_s=max(p['spin_translation_speed'][i] for i in pureids),
 closure_max_m=r['max_closure_m'],mimic_max_rad=r['max_mimic_rad'])
state=runtime['state'];assert state['consecutive']==1 and state['failed_blocks']==0
deadline=runtime['status']['trainer_deadline_epoch']
review=dict(checkpoint=decision['checkpoint'],original_skill_pass=True,legacy_skill_pass=True,physical_pass=True,survived=88,
 groups_all_8_of_8=True,flat_trained64_all_original_admission=True,strict_window_retained=False,
 initial_final_parameter_readbacks_pass=True,comparison17351_same_probe_seed_profile_root_q=True,
 metrics=metrics,pure_groups=rows,consecutive=1,failed_blocks=0,
 first_new_rolling_rate6_single_seed_pass_not_mature=True,real_robot_certified=False,
 old16475_single_pass_and_historical_failures_retained=True,actual_current_runtime=actual,
 next_deadline_epoch=deadline,no_new_probe_PPO_config_budget_or_restart=True)
(D/'RATE6_MODEL17773_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
time_text=datetime.fromtimestamp(deadline,timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
note=f'''# 滚动专项6档首份完整单种子原验收通过：17773

auto0051对正式17773执行原定80env平地与88env自转15秒冻结回放。17351之后两小时6档学习已在17773完整保存，SHA{decision['checkpoint']['sha256']}，CPU完整actor/critic/optimizer/std/iter共68浮点有限。原corrected与legacy spin_skill均true、physicaltrue，88/88存活；11组各8/8技能通过，包括纯左右±6、低速、站跑及启停反向。实际参数初末读回通过。独立flat的64个已训练环境各组原准入100%，旧strict_window=false保留。

交错group_ids逐环境核查，纯+6实测平均{metrics['positive_yaw_mean']:.6f}rad/s，纯-6为{metrics['negative_yaw_mean']:.6f}。纯±6所有轮每环境平均网格滑移代理最坏{metrics['max_mean_mesh_slip_m_s']:.6f}m/s<原.15；纯+6左轮.099739–.139733/右轮.101298–.140747，纯-6左轮.127529–.140284/右轮.062994–.070134。四侧全部报告，不只挑此前失败的右轮。纯±6最坏peaktilt{metrics['pure_peak_tilt_deg']:.6f}deg、gap{metrics['pure_gap_max_m']*1000:.6f}mm、双轮低载{metrics['pure_both_low_max_s']*1000:.3f}ms；闭链{metrics['closure_max_m']*1000:.6f}mm、mimic{metrics['mimic_max_rad']:.6f}rad。纯自转平均XY速度最坏{metrics['pure_mean_xy_speed_max_m_s']:.6f}m/s<原.12，余量仍有限。

与先前17351同seed20261002、white_v2、probe源SHA和完整初始root/q精确相同。权重和训练经历不同，这属于训练进展证据，不能当隔离奖励因果、PhysX材料点滑移认证或实车性能。100Hz代理/扭矩/网格非子步峰，低力非腾空。历史17351和旧6全部失败报告不改，旧16475早先单次通过也不是此次新专项多seed毕业。

专项consecutive=1、failed_blocks=0。这是新滚动专项首份完整策略单seed6通过，仍需要另一份不同正式策略通过及同候选两个seed nominal/white_v2 flat/spin严格初态配对通过，才称6成熟并升8。当前已自动开始后续最长2小时6档段，parent3238128/start20735397、guardian3238171/start20735462正常；单一trainer3579975/start22325334、run logs/2026-10-04_06-57-24_auto_0052_rolling_rate_trial_or_continued_cap6_white_v2，从17773完整恢复。实际run_manifest核实start17773/KEEP_STD1/cap6/white_v2/rolling v1，当前新trainer自身完整receipt在核验时尚待首次保存，不能把17773称作此新PID训练后的新策略。旧root.status某些latest字段是前一段已保存策略；使用PID绑定receipt，不用全目录最高iter。

当前段截止约北京时间{time_text}，已有监督器随后顺序flat/rate及符合门控才执行配对；本轮不额外发probe。3连续新档技能失败或旧能力/物理退化回实际paired17196/5并hold。当前不升8、不加强DR、不改奖励硬件或.15门槛。104原源与123候选实际哈希一致，GPU90%/12728MiB/50C是初始化快照。

唯一252000秒70h、三条已应用扩展不变；核验时余{actual['remaining_effective_s']:.2f}秒约17小时38分为快照，实时扣活跃PPO。当前只采集既有报告、CPU和来源核验/同步归档，没有新的PPO/探针、暂停重启、重复记账或新增预算。原地spin优先，移动/FPS/地形延期，目标4π=2转每秒=120rpm仍未达到。
'''
(D/'RATE6_MODEL17773_REPORT.md').write_text(note,encoding='utf8')
print(json.dumps(metrics))
