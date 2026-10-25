"""SCUT-inspired curriculum: slip is diagnostic, not an uncalibrated veto.

This is NOT an exact SCUT task port or a real-hardware safety certification.
Reuse every non-slip constraint and data-quality check of the prior version.
Preserve both prior slip verdicts and all measurements, without rewriting them.
"""
from contact_gate import assess as prior_assess
VERSION='scut_style_nonslip_gate_v1'
REMOVED=tuple(f'wheel{w}_{reason}' for w in (0,1) for reason in (
    'loaded_time_mean_tangent_speed','loaded_impulse_weighted_tangent_speed',
    'sustained_loaded_excess'))

def assess(report):
    prior=prior_assess(report)
    if 'individual' not in prior:
        return dict(version=VERSION,pass_=False,reasons=prior.get('reasons',[]),
                    prior_loaded015_assessment=prior)
    individual=[]
    for row in prior['individual']:
        removed=[reason for reason in row['reasons'] if reason in REMOVED]
        retained=[reason for reason in row['reasons'] if reason not in REMOVED]
        individual.append(dict(row,pass_=not retained,reasons=retained,
                               slip_diagnostic_reasons=removed))
    groups=[]
    for g in prior['groups']:
        rows=[r for r in individual if r['group_id']==g['group_id']]
        passing=sum(r['pass_'] for r in rows)
        groups.append(dict(g,passing=passing,fraction=passing/len(rows)))
    severe=[r for r in prior['severe_individual_veto'] if r['reason']!='sustained_loaded_excess']
    passed=(prior['complete_evidence'] and prior['actual_parameters_pass'] and
            not severe and all(g['fraction']>=.8 for g in groups))
    return dict(version=VERSION,pass_=bool(passed),groups=groups,individual=individual,
                severe_individual_veto=severe,complete_evidence=prior['complete_evidence'],
                actual_parameters_pass=prior['actual_parameters_pass'],
                prior_loaded015_assessment=prior,
                original_spin_skill_pass=report['spin_skill_pass'],
                legacy_spin_skill_pass=report.get('spin_skill_pass_legacy_reference'),
                removed_only_slip_numeric_veto=True,retained_group_minimum_fraction=.8,
                slip_numeric_safety_limit=None,
                scope='SCUT-inspired qualification by tracking, stability, support and old-skill regression; slip fully retained as diagnostic. Not an exact SCUT port or real-robot certification.')
