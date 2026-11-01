"""Read-only admission to a mild-DR experiment, NOT legacy graduation or sim2real."""
import argparse
import json
from pathlib import Path


def assess(report):
    reasons = []
    if report.get('nonfinite', True) or not report.get('physics_pass'):
        reasons.append('physics/nonfinite')
    if report.get('seconds', 0) < 15 or report.get('mode') != 'deterministic_policy':
        reasons.append('requires deterministic fifteen-second report')
    if report.get('max_closure_after_grace_m', 1) > .002 or report.get('max_mimic_after_grace_rad', 1) > .01:
        reasons.append('closure/mimic')
    pe = report.get('per_environment', {})
    groups = report.get('groups', [])
    passed = []
    constants = set()
    for group_id, group in enumerate(groups):
        ids = [i for i, gid in enumerate(pe.get('group_ids', [])) if gid == group_id]
        cmd = float(group['command_vx'])
        # ±2 m/s extrapolation is diagnostic; this admission only covers trained ±1.5.
        if abs(cmd) > 1.5:
            continue
        if group['profile'] == 'constant':
            constants.add(cmd)
        if len(ids) < 8:
            reasons.append(f'group {group_id}: fewer than eight samples')
            continue
        try:
            accepted = []
            for i in ids:
                accepted.append(bool(pe['alive'][i])
                    and pe['vel_error'][i] <= max(.12, .25 * abs(cmd))
                    and pe['tilt'][i] <= 8 and pe['max_tilt'][i] <= 12
                    and pe['height_error'][i] <= .03
                    and pe['delta'][i] <= .18 and pe['d2'][i] <= .25
                    and pe['guide_force'][i] <= 1 and pe['base_force'][i] <= 1
                    and pe['left_mean_fz_substep'][i] >= 10
                    and pe['right_mean_fz_substep'][i] >= 10
                    and pe['longest_both_low_force_s_substep'][i] <= .01501
                    and max(pe['left_gap_max_control_m'][i], pe['right_gap_max_control_m'][i]) <= .002
                    and max(pe['left_support_slip_control'][i], pe['right_support_slip_control'][i]) <= .15
                    and (group['profile'] != 'ramp_brake_reverse' or pe['stop_abs_speed'][i] <= .12))
            fraction = sum(accepted) / len(accepted)
            passed.append(dict(group_id=group_id, command_vx=cmd, profile=group['profile'],
                               count=len(ids), physical_admission_fraction=fraction))
            if fraction < .8:
                reasons.append(f'group {group_id}: physical admission {fraction:.3f} < .8')
        except (KeyError, IndexError, TypeError) as error:
            reasons.append(f'group {group_id}: missing physical evidence {error}')
    if not {0., .3, .6, 1., -1.5, 1.5}.issubset(constants):
        reasons.append('missing required trained constant-speed groups')
    return dict(eligible_for_mild_dr_trial=not reasons, reasons=reasons, groups=passed,
                seed=report.get('seed'), checkpoint=report.get('checkpoint'),
                legacy_strict_pass_window=report.get('strict_pass_window'),
                integrated_mean_pass=report.get('strict_pass_integrated_mean'),
                scope='project-specific admission for an isolated DR experiment; not legacy graduation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reports', nargs='+', type=Path)
    args = parser.parse_args()
    outcomes = [assess(json.loads(path.read_text())) for path in args.reports]
    seed_count = len({result['seed'] for result in outcomes if result['eligible_for_mild_dr_trial']})
    result = dict(results=outcomes, two_recent_windows_pass=len(outcomes) >= 2 and
                  all(r['eligible_for_mild_dr_trial'] for r in outcomes[-2:]),
                  distinct_passing_seeds=seed_count,
                  multi_seed_evidence_present=seed_count >= 2,
                  automatic_graduation=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))
