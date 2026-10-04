"""Independently review existing auto0055 arrays. No simulation or gate changes."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

D = Path(__file__).resolve().parent
read = lambda n: json.loads((D / n).read_text(encoding='utf8'))
r = read('auto_0055_assessment_cap6_white_v2_rate.json')
dec = read('auto_0055_assessment_cap6_white_v2_decision.json')
previous = read('auto_0053_assessment_cap6_white_v2_rate.json')
health = read('HEALTH_20261004_1300.json')
cpu = read('RATE6_MODEL18643_CPU_VERIFIED.json')
runtime = read('RUNTIME_ACTUAL.json')
assert r['physical_smoke_pass'] and not r['spin_skill_pass'] and not r['spin_skill_pass_legacy_reference']
assert all(r['alive']) and len(r['alive']) == 88 and not r['nonfinite']
assert dec['original_flat_admission']['eligible_for_mild_dr_trial']
assert all(g['physical_admission_fraction'] == 1 for g in dec['original_flat_admission']['groups'])
assert all(r[k] == previous[k] for k in ['reset_root_before_physics', 'reset_joint_pos_before_physics', 'group_ids', 'probe_sha256', 'seed', 'profile'])
assert r['initial_parameter_audit']['actual_parameters_pass'] and r['final_parameter_audit']['actual_parameters_pass']
assert cpu == dec['checkpoint'] and cpu['finite_tensors'] == 68
assert health['consecutive'] == 0 and health['failed_blocks'] == 2
p = r['per_environment']; failed = []; rows = []
for g in r['groups']:
    ids = [i for i, group in enumerate(r['group_ids']) if group == g['group_id']]
    count = 0
    for i in ids:
        bad = []
        limits = {'peak_tilt': 12, 'tilt': 8, 'height_error': .03, 'left_slip': .15,
                  'right_slip': .15, 'delta': .18, 'd2': .25, 'maximum_gap_m': .002,
                  'longest_both_low_s': .01501, 'guide_force': 1, 'base_force': 1,
                  'wheel_rating_clip': .2, 'leg_rating_clip': .2}
        for key, limit in limits.items():
            if p[key][i] > limit: bad.append(key)
        for key in ['left_fz', 'right_fz']:
            if p[key][i] < 10: bad.append(key)
        if not r['alive'][i]: bad.append('survival')
        if p['yaw_error'][i] > max(.2, .2 * abs(g['wz'])): bad.append('yaw_error')
        if p['speed_error'][i] > max(.12, .25 * abs(g['vx'])): bad.append('speed_error')
        if g['wz'] != 0 and p['spin_translation_speed'][i] > .12: bad.append('spin_translation_speed')
        if g['profile'] == 'spin_ramp_stop_reverse' and p['stop_yaw_abs'][i] > .2: bad.append('stop_yaw_abs')
        if bad:
            failed.append(dict(environment=i, group_id=g['group_id'], reasons=bad,
                               values={k: p[k][i] for k in bad if k in p}))
        else:
            count += 1
    assert abs(count / len(ids) - g['spin_skill_fraction']) < 1e-6
    rows.append(dict(group_id=g['group_id'], profile=g['profile'], yaw_command=g['wz'],
                     count=len(ids), skill_count=count, legacy_fraction=g['spin_skill_fraction_legacy_reference']))
assert len(failed) == 6 and all(f['group_id'] == 7 and f['reasons'] == ['right_slip'] for f in failed)
pure = [i for i, group in enumerate(r['group_ids']) if group in [7, 8]]
pos = [i for i, group in enumerate(r['group_ids']) if group == 7]
neg = [i for i, group in enumerate(r['group_ids']) if group == 8]
metrics = dict(positive_yaw_mean=r['groups'][7]['means']['yaw_rate'], negative_yaw_mean=r['groups'][8]['means']['yaw_rate'],
               positive_right_slip_range=[min(p['right_slip'][i] for i in pos), max(p['right_slip'][i] for i in pos)],
               negative_left_slip_range=[min(p['left_slip'][i] for i in neg), max(p['left_slip'][i] for i in neg)],
               pure_peak_tilt_deg=max(p['peak_tilt'][i] for i in pure), pure_gap_m=max(p['maximum_gap_m'][i] for i in pure),
               pure_both_low_s=max(p['longest_both_low_s'][i] for i in pure), pure_mean_xy_speed_max=max(p['spin_translation_speed'][i] for i in pure),
               closure_m=r['max_closure_m'], mimic_rad=r['max_mimic_rad'])
review = dict(checkpoint=cpu, physical_pass=True, original_skill_pass=False, legacy_skill_pass=False, survived=88,
              flat_trained64_all_original_admission=True, strict_window_retained=False, initial_final_parameter_readbacks=True,
              same18207_seed_profile_probe_initial_root_q=True, rows=rows, failed_environments=failed, metrics=metrics,
              consecutive=0, failed_blocks=2, current_health=health,
              no_new_probe_PPO_budget_config_restart_or_gate_change=True)
(D / 'RATE6_MODEL18643_REVIEW.json').write_text(json.dumps(review, indent=2), encoding='utf8')
deadline = datetime.fromtimestamp(runtime['status']['trainer_deadline_epoch'], timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
failtext = '、'.join(f"env{f['environment']}={f['values']['right_slip']:.6f}" for f in failed)
note = f'''# 6档18643：同一滑移门控仍未过，第二个连续失败块

auto0055原定平地80env与自转88env各15秒已完成。正式源18643 SHA{cpu['sha256']}已按精确评测路径独立CPU读取actor/critic/optimizer/std/iter，68浮点完整有限。flat64已训练环境全部原准入通过，旧strict_window=false保留；rate88/88存活、physical=true、初末实际参数读回通过，corrected与legacy_reference spin_skill均false。

交错group_ids逐环境重算与原报告分数相同。纯+6正确参考点技能2/8=25%，旧参考点5/8=62.5%，两者均低于原80%；6个失败仅为右轮平均网格滑移代理>.15m/s：{failtext}。正转8个样本右轮范围{metrics['positive_right_slip_range'][0]:.6f}–{metrics['positive_right_slip_range'][1]:.6f}；纯-6与其余9组均8/8，反转左轮范围{metrics['negative_left_slip_range'][0]:.6f}–{metrics['negative_left_slip_range'][1]:.6f}。不通过组均值、切换参考点或降低阈值毕业；没有死亡、NaN、物理或旧站跑退化。

纯±6实际yaw均{metrics['positive_yaw_mean']:.6f}/{metrics['negative_yaw_mean']:.6f}rad/s，逐环境最坏peaktilt{metrics['pure_peak_tilt_deg']:.6f}deg、控制gap{metrics['pure_gap_m']*1000:.6f}mm、双轮低载{metrics['pure_both_low_s']*1000:.3f}ms、平均XY速度{metrics['pure_mean_xy_speed_max']:.6f}m/s，closure{metrics['closure_m']*1000:.6f}mm/mimic{metrics['mimic_rad']:.6f}rad。与18207同seed20261002、white_v2、probe源码及完整初始root/q严格相同，权重不同。17773首次通过及18207反转失败均保留；失败轮侧随策略变化，不能宣称持久修好、奖励单独因果或PhysX材料点/实车滑移。

REPAIR_STATE consecutive=0/failed_blocks=2，原监督器继续已经安排的第三个有界6学习块，未升8；只有第三个连续技能失败或物理/旧能力退化才按既定规则保留权重、回实际paired成熟17196/5并hold，不抢先热改活跃trainer。本轮与已通知的滑移门控是同一未解条件，没有新严重故障，不重复通知。

核验时单一正式trainer3905371/start23845428从18643完整恢复、KEEP_STD1，run logs/2026-10-04_11-10-45_auto_0056_rolling_rate_trial_or_continued_cap6_white_v2；parent3238128/start20735397与guardian3238171/start20735462独立会话正常，cap6/white_v2/rolling v1固定。PID绑定19025 SHA{health['checkpoint']['sha256']}已CPU读回68浮点有限，104原源/123候选源一致；19025尚无15秒回放，不借训练success/reward宣布毕业。约29.7k环境策略步/s、GPU77%/14562MiB/47C是快照，近期无NaN/Traceback/OOM。下一段deadline约北京时间{deadline}，随后已有自动保存及顺序flat/rate，不发重复probe。

唯一252000有效PPO秒与三授权扩展不变，核验剩{health['remaining_effective_s']:.2f}秒约11小时49分为快照，后续扣活跃尾段。本轮只读已有报告、CPU/来源/进程/GPU与Git归档及交接更新，无额外probe/PPO、暂停重启、奖励/物理/DR/硬件/门槛或预算改变。原地小陀螺优先，移动/FPS/地形延期，120rpm未达到。
'''
(D / 'RATE6_MODEL18643_REPORT.md').write_text(note, encoding='utf8')
print(json.dumps(dict(rows=rows, failed=failed, metrics=metrics, next_deadline=deadline), ensure_ascii=False))
