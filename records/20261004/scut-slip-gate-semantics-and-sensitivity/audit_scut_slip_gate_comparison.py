"""Offline counterfactual only. Never edits a report, gate, trainer or ledger."""
import hashlib
import json
from pathlib import Path

D = Path(__file__).resolve().parent
R = D.parent / 'reference_repos/scut_wheeled_legged_RL'
inputs = [(49, 17351), (51, 17773), (53, 18207), (55, 18643)]
thresholds = [.15, .16, .17, .18, .20, .25]
rows = []
for sequence, model in inputs:
    path = D / f'auto_{sequence:04d}_assessment_cap6_white_v2_rate.json'
    report = json.loads(path.read_text(encoding='utf8'))
    pe = report['per_environment']; by_threshold = {}
    for threshold in thresholds:
        groups = []
        for group in report['groups']:
            ids = [i for i, gid in enumerate(report['group_ids']) if gid == group['group_id']]
            accepted = []
            for i in ids:
                ok = bool(report['alive'][i]) and report['first_failure_step'][i] >= report['steps']
                limits = dict(peak_tilt=12, tilt=8, height_error=.03, left_slip=threshold,
                              right_slip=threshold, delta=.18, d2=.25, maximum_gap_m=.002,
                              longest_both_low_s=.01501, guide_force=1, base_force=1,
                              wheel_rating_clip=.2, leg_rating_clip=.2)
                ok &= all(pe[key][i] <= limit for key, limit in limits.items())
                ok &= pe['left_fz'][i] >= 10 and pe['right_fz'][i] >= 10
                ok &= pe['yaw_error'][i] <= max(.2, .2 * abs(group['wz']))
                ok &= pe['speed_error'][i] <= max(.12, .25 * abs(group['vx']))
                ok &= group['wz'] == 0 or pe['spin_translation_speed'][i] <= .12
                ok &= group['profile'] != 'spin_ramp_stop_reverse' or pe['stop_yaw_abs'][i] <= .2
                accepted.append(bool(ok))
            if threshold == .15:
                assert abs(sum(accepted)/len(accepted) - group['spin_skill_fraction']) < 1e-6
            groups.append(dict(group_id=group['group_id'], passing=sum(accepted), count=len(ids)))
        eligible = all(g['passing']/g['count'] >= .8 for g in groups)
        eligible &= report['seconds'] >= 15 and not report['nonfinite'] and report['max_closure_m'] <= .002 and report['max_mimic_rad'] <= .01
        by_threshold[str(threshold)] = dict(group_rule_pass=eligible, positive_passing=groups[7]['passing'],
                                           negative_passing=groups[8]['passing'], groups=groups)
        if threshold == .15: assert eligible == report['spin_skill_pass']
    rows.append(dict(model=model, input=path.name, input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     checkpoint=report['checkpoint'], seed=report['seed'], profile=report['profile'],
                     thresholds=by_threshold))
source_paths = ['scripts/rsl_rl/play.py',
                'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py',
                'source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py']
out = dict(upstream_commit='b8ff79f3df855faf9dc92f4a282bd80c42649466',
           source_sha256={p: hashlib.sha256((R/p).read_bytes()).hexdigest() for p in source_paths},
           upstream=dict(debug_threshold_m_s=.25, debug_is_a_graduation_gate=False,
                         geometry='world-vertical radius-offset point using body_lin_vel_w; geometric proxy',
                         selection='contact-history force peak >1N, when available',
                         statistic='mean, maximum and fraction above threshold; print-only',
                         wheel_bottom_slip_exp_implemented=True, configured_in_public_V14_spin=False),
           project=dict(threshold_m_s=.15, geometry='lowest input-mesh vertex, link-reference velocity',
                        selection='all live post-warmup control samples, no load mask for slip mean',
                        rule='15-second per-environment mean for each wheel, >=80% per group',
                        new_rolling_reward='separate load-weighted midplane rolling approximation'),
           ideal_edge_yaw_speed=dict(half_width_m=.01, speed_at_6rad_s_m_s=.06,
                                    speed_at_4pi_m_s=.12566370614359174,
                                    scope='ideal horizontal axle edge contribution, not measured contact speed or universal correction'),
           counterfactual_thresholds=rows,
           scope='All four locally available completed rolling6 assessments through auto0055; no new replay, new graduation or safety validation',
           simulation_PPO_production_budget_gate_unchanged=True)
(D/'SCUT_SLIP_GATE_COMPARISON_20261004.json').write_text(json.dumps(out, indent=2), encoding='utf8')
table = [{'model': x['model'], **{k: f"+{v['positive_passing']}/8,-{v['negative_passing']}/8,group_rule={v['group_rule_pass']}" for k,v in x['thresholds'].items()}} for x in rows]
print(json.dumps(table, ensure_ascii=False))
