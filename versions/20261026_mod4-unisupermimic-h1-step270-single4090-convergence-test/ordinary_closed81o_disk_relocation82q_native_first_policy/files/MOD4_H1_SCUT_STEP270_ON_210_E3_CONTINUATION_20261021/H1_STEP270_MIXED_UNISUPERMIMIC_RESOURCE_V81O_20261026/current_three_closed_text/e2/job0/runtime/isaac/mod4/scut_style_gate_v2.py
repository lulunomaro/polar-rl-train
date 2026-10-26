"""Slip-diagnostic qualification for BOTH flat and spin; old verdicts retained."""
import math
from admission_gate import assess as original_flat_assess
from scut_style_gate import assess as prior_spin_assess

VERSION='scut_style_nonslip_gate_v2_flat_and_spin'

def assess(report):
    result=dict(prior_spin_assess(report))
    result.update(version=VERSION,prior_spin_acceptance_version='scut_style_nonslip_gate_v1',
                  scope='Slip is diagnostic for both flat and spin. All non-slip constraints and data-quality checks remain. Not real-robot certification.')
    return result

def assess_flat(report):
    prior=original_flat_assess(report)
    reasons=[];groups=[];individual=[];constants=set()
    if report.get('nonfinite',True) or not report.get('physics_pass'):reasons.append('physics/nonfinite')
    if report.get('seconds',0)<15 or report.get('mode')!='deterministic_policy':reasons.append('requires deterministic fifteen-second report')
    for key,maximum in (('max_closure_after_grace_m',.002),('max_mimic_after_grace_rad',.01)):
        value=report.get(key,float('nan'))
        if not math.isfinite(value) or value>maximum:reasons.append(key)
    pe=report.get('per_environment',{})
    for gid,g in enumerate(report.get('groups',[])):
        cmd=float(g['command_vx'])
        if abs(cmd)>1.5:continue # Existing extrapolation remains diagnostic.
        if g['profile']=='constant':constants.add(cmd)
        ids=[i for i,v in enumerate(pe.get('group_ids',[])) if v==gid]
        if len(ids)<8:reasons.append(f'group {gid}: fewer than eight samples');continue
        passed=[]
        for i in ids:
            fail=[];slip=[]
            limits={'vel_error':max(.12,.25*abs(cmd)),'tilt':8,'max_tilt':12,'height_error':.03,
                    'delta':.18,'d2':.25,'guide_force':1,'base_force':1,
                    'longest_both_low_force_s_substep':.01501,
                    'left_gap_max_control_m':.002,'right_gap_max_control_m':.002}
            if g['profile']=='ramp_brake_reverse':limits['stop_abs_speed']=.12
            try:
                if not pe['alive'][i]:fail.append('survival')
                for key,limit in limits.items():
                    value=pe[key][i]
                    if not math.isfinite(value) or value>limit:fail.append(key)
                for key in ('left_mean_fz_substep','right_mean_fz_substep'):
                    value=pe[key][i]
                    if not math.isfinite(value) or value<10:fail.append(key)
                for key in ('left_support_slip_control','right_support_slip_control'):
                    value=pe[key][i]
                    if not math.isfinite(value):fail.append(key+'_nonfinite')
                    elif value>.15:slip.append(dict(metric=key,value=value,prior_limit=.15))
            except (KeyError,IndexError,TypeError) as error:fail.append('missing physical evidence: '+str(error))
            passed.append(not fail)
            individual.append(dict(env=i,group_id=gid,pass_=not fail,reasons=fail,slip_diagnostics=slip))
        fraction=sum(passed)/len(passed)
        groups.append(dict(group_id=gid,command_vx=cmd,profile=g['profile'],count=len(ids),physical_admission_fraction=fraction))
        if fraction<.8:reasons.append(f'group {gid}: physical admission {fraction:.3f} < .8')
    if not {0.,.3,.6,1.,-1.5,1.5}.issubset(constants):reasons.append('missing required trained constant-speed groups')
    return dict(version=VERSION,eligible_for_mild_dr_trial=not reasons,pass_=not reasons,reasons=reasons,
                groups=groups,individual=individual,seed=report.get('seed'),checkpoint=report.get('checkpoint'),
                legacy_strict_pass_window=report.get('strict_pass_window'),integrated_mean_pass=report.get('strict_pass_integrated_mean'),
                prior_original_flat_admission=prior,slip_numeric_safety_limit=None,
                scope='Original flat admission with ONLY the two finite slip-proxy numeric vetoes removed. Survival, tracking, posture, loading, unload duration, gap, stop and finite evidence retained.')
