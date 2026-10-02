"""Summarize existing 9903 paired reports; no SSH or simulator, no gate changes."""
import json
from pathlib import Path
from admission_gate import assess

BASE = Path(__file__).parent
REPORTS = BASE / 'reports_mild_trial'
rows = []
pairs = []
for seed in (20261001, 20260927):
    paired = {}
    for profile in ('nominal', 'mild'):
        path = REPORTS / f'trial_model9903_{profile}_seed{seed}.json'
        report = json.loads(path.read_text())
        paired[profile] = report
        admission = assess(report)
        assert admission['eligible_for_mild_dr_trial'], admission
        per = report['per_environment']
        trained_ids = [i for i, gid in enumerate(per['group_ids'])
                       if abs(report['groups'][gid]['command_vx']) <= 1.5]
        assert len(trained_ids) == 64
        worst = {key: max(per[key][i] for i in trained_ids) for key in (
            'max_tilt', 'height_error', 'delta', 'd2', 'longest_both_low_force_s_substep',
            'left_gap_max_control_m', 'right_gap_max_control_m',
            'left_support_slip_control', 'right_support_slip_control', 'stop_abs_speed')}
        constant = [{key: g[key] for key in (
            'command_vx', 'speed', 'vel_error', 'tilt', 'height_error', 'delta', 'd2',
            'left_mean_fz_substep', 'right_mean_fz_substep', 'strict_pass_window')}
            for g in report['groups'] if abs(g['command_vx']) == 1.5 and g['profile'] == 'constant']
        rows.append({'seed': seed, 'profile': profile, 'file': path.name,
                     'admission': admission, 'constant_1_5_group_means': constant,
                     'worst_environment_trained_groups': worst,
                     'closure_max_mm_all_groups': report['max_closure_after_grace_m']*1000,
                     'mimic_max_rad_all_groups': report['max_mimic_after_grace_rad'],
                     'all_trained_survive_15s': all(per['alive'][i] for i in trained_ids),
                     'legacy_window_graduation': report['strict_pass_window'],
                     'rating_diagnostics_note': 'Old gain-compensated leg fields may mismatch actuator order. Replay-only fix recorded separately; do not infer real saturation from this old field.'})
    pair = {'seed': seed, 'same_checkpoint': paired['nominal']['checkpoint'] == paired['mild']['checkpoint'],
            'exact_initial_root_equal': paired['nominal']['reset_root_before_physics'] == paired['mild']['reset_root_before_physics'],
            'exact_initial_q_equal': paired['nominal']['reset_joint_pos_before_physics'] == paired['mild']['reset_joint_pos_before_physics']}
    assert all(v for k, v in pair.items() if k != 'seed'), pair
    pairs.append(pair)
result = {'checkpoint_iteration': 9903, 'pairs': pairs, 'results': rows,
          'continuation_decision': 'continued_mild', 'legacy_criteria_changed': False,
          'scope': 'Two seeds, nominal and explicit mild whitelist, 15-second deterministic trained ±1.5 m/s groups. Experimental admission, not Rough/full-DR/sim2real certification.',
          'motor_diagnostic_followup_required': True, 'spring_300_700N_validated': False}
(REPORTS/'MILD_TRIAL_9903_REVIEW_20261001.json').write_text(json.dumps(result, indent=2))
print(json.dumps({'paired_initial_states_equal': True, 'all_four_admissions': True,
                  'legacy_graduation': False, 'worst_trained_low_load_s': max(r['worst_environment_trained_groups']['longest_both_low_force_s_substep'] for r in rows),
                  'worst_trained_gap_m': max(max(r['worst_environment_trained_groups'][k] for k in ('left_gap_max_control_m', 'right_gap_max_control_m')) for r in rows)}))
