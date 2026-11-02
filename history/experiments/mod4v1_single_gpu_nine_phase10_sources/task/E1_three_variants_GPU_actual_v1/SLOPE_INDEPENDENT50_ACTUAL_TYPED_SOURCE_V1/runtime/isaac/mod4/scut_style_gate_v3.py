"""SCUT-inspired spin qualification: mean XY speed is a diagnostic.

Preserve all v2 verdicts and finite-data, tracking and physical checks.
No reward, dynamics, command or hardware changes.
"""
import math
from scut_style_gate_v2 import assess as v2_spin, assess_flat as v2_flat

VERSION='scut_style_nonslip_xymean_diagnostic_v3'

def assess(report):
    try:
        prior=v2_spin(report)
    except (KeyError,IndexError,TypeError,ValueError) as error:
        return dict(version=VERSION,pass_=False,reasons=['Missing or invalid inherited evidence: '+str(error)])
    if 'individual' not in prior:
        return dict(version=VERSION,pass_=False,prior_v2_assessment=prior,
                    reasons=prior.get('reasons',['Incomplete contact evidence']))
    rows=[];invalid=[]
    for row in prior['individual']:
        i=row['env']
        try:
            value=report['per_environment']['spin_translation_speed'][i]
            valid=math.isfinite(value)
        except (KeyError,IndexError,TypeError,ValueError):
            value=None;valid=False
        retained=[reason for reason in row['reasons'] if reason!='spin_translation_speed']
        if not valid:
            retained.append('spin_translation_speed_missing_or_nonfinite')
            invalid.append(dict(env=i,reason='spin_translation_speed_missing_or_nonfinite'))
        rows.append(dict(row,pass_=not retained,reasons=retained,
                         translation_diagnostic=dict(mean_xy_speed_m_s=value,
                            prior_numeric_limit_m_s=.12,
                            prior_numeric_veto='spin_translation_speed' in row['reasons'])))
    groups=[]
    for group in prior['groups']:
        members=[r for r in rows if r['group_id']==group['group_id']]
        passing=sum(r['pass_'] for r in members)
        groups.append(dict(group,passing=passing,fraction=passing/len(members) if members else 0.))
    severe=list(prior['severe_individual_veto'])+invalid
    passed=bool(prior['complete_evidence'] and prior['actual_parameters_pass'] and
                not severe and groups and all(g['fraction']>=.8 for g in groups))
    return dict(prior,version=VERSION,pass_=passed,groups=groups,individual=rows,
                severe_individual_veto=severe,prior_v2_assessment=prior,
                mean_xy_speed_numeric_veto=None,
                removed_only_finite_spin_mean_xy_numeric_veto=True,
                scope='Finite spin mean horizontal speed is diagnostic. v2 flat, tracking, posture, support, stop, closure, actuation and complete contact evidence remain. SCUT-inspired project qualification, not an exact task port.')

def assess_flat(report):
    prior=v2_flat(report)
    return dict(prior,version=VERSION,prior_v2_flat_assessment=prior,
                flat_rule_unchanged=True,mean_xy_speed_numeric_veto=None)
