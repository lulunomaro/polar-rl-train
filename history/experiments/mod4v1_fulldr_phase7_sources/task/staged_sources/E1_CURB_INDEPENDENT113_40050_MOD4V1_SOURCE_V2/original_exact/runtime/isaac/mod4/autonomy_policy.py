"""Bounded autonomous gates; no simulator imports and no budget authority."""
import math

LEVELS = (3., 4., 5., 6., 8., 10., 4*math.pi)
DR_PROFILES = {
    'white_v1': {'mass': (.95,1.05), 'motor': (.95,1.05), 'friction': (.8,1.)},
    'white_v2': {'mass': (.925,1.075), 'motor': (.925,1.075), 'friction': (.75,1.)},
    'white_v3': {'mass': (.9,1.1), 'motor': (.9,1.1), 'friction': (.7,1.)},
}

def next_action(cap, profile, consecutive, paired, remaining, dr_rejected, rate_rejected=()):
    if cap not in LEVELS or profile not in DR_PROFILES:
        raise ValueError('Unknown curriculum')
    if consecutive < 2 or not paired or remaining < 5400:
        return ('continue', None)
    # Hold yaw fixed during DR changes; never combine the two changes.
    target = 'white_v2' if profile=='white_v1' and cap>=6 else 'white_v3' if profile=='white_v2' and cap>=8 else None
    if target and target not in dr_rejected:
        return ('dr_trial', target)
    index=LEVELS.index(cap)
    if index+1<len(LEVELS) and LEVELS[index+1] in rate_rejected:
        return ('targeted_repair_hold', LEVELS[index+1])
    return ('rate_preflight', LEVELS[index+1]) if index+1<len(LEVELS) else ('continue',None)

def settle_segment(b, pid, ended):
    # Frozen evaluation, reconnect time and a second recovery cannot be charged.
    a=b.get('active_segment')
    if not a or a['pid'] != pid:
        raise ValueError('Missing or different active trainer; reconciliation required')
    if ended < a['accounted_through_epoch']:
        raise ValueError('Invalid training end boundary')
    tail=ended-a['accounted_through_epoch']
    b['charged_training_seconds'] += tail
    a.update(accounted_through_epoch=ended, ended_epoch=ended, end_reason='autonomy_save_boundary_handover')
    b.setdefault('completed_segments',[]).append(a)
    b['active_segment']=None
    b['remaining_training_seconds']=max(0.,b['authorized_training_seconds']-b['charged_training_seconds'])
    return tail

def safety_veto(report):
    """Extra single-sample severe-event guard; retain the original group booleans."""
    per=report.get('per_environment',{})
    peak=per.get('peak_tilt',per.get('max_tilt',[]))
    off=per.get('longest_both_low_s',per.get('longest_both_low_force_s_substep',[]))
    alive=report.get('alive',per.get('alive',[]))
    # Existing flat +/-2 extrapolation remains diagnostic, not a trained group.
    gids=per.get('group_ids')
    if gids and report.get('mode')=='deterministic_policy':
        groups=report['groups']
        ids=[i for i,gid in enumerate(gids) if abs(groups[gid]['command_vx'])<=1.5]
        peak=[peak[i] for i in ids] if peak else []
        off=[off[i] for i in ids] if off else []
        alive=[alive[i] for i in ids] if alive else []
    return (not report.get('nonfinite',False)
            and all(alive)
            and (not peak or max(peak)<=15.)
            and (not off or max(off)<=.02001))
