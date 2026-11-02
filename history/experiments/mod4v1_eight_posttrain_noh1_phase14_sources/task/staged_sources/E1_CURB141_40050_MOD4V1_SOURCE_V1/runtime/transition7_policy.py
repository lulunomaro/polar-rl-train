"""Small, explicit yaw step after measured6 and rejected untrained8."""
import math
VERSION='rate7_transition_scut_v2'
GATE_VERSION='scut_style_nonslip_gate_v2_flat_and_spin'
SOURCE_SHA='64a9dd769108e448d0816ce9b3f670fcc6d915ddc91ce1c7be9acf6c0511bca5'
LEVELS=(3.,4.,5.,6.,7.,8.,10.,4*math.pi)

def validate_limit(value):
    if not math.isfinite(value) or not any(abs(value-x)<1e-8 for x in LEVELS):
        raise ValueError('Unregistered rate transition')
    return value

def next_limit(value):
    validate_limit(value)
    index=next(i for i,x in enumerate(LEVELS) if abs(value-x)<1e-8)
    return LEVELS[index+1] if index+1<len(LEVELS) else None

def progress(skilled,different,consecutive,failures):
    if skilled:return consecutive+int(different),0
    return 0,failures+1

def validate_context(e):
    assert e['phase']=='repair_hold' and e['current_cap']==6.
    assert not e['active_training'] and not e['active_segment'] and not e['live_children']
    source=e['checkpoint'];m=e['mature'];accepted=e['accepted6']
    assert source['sha256']==SOURCE_SHA and source['iteration_stored']==19975 and source['finite_tensors']==68
    assert m==dict(checkpoint=source['path'],cap=6.,profile='white_v2')
    assert e['chosen_checkpoint']==source['path']
    assert accepted['checkpoint']==source and accepted['acceptance_version']==GATE_VERSION and accepted['cap']==6.
    assert accepted['fresh_latest_policy_flat_spin_and_two_seed_nominal_DR_pair']
    b=e['budget'];assert b['authorized']==252000 and b['remaining']>3600 and 0<=b['charged']<b['authorized']
    assert abs(b['authorized']-b['charged']-b['remaining'])<.001
    assert e['old8_rejected']['source']==source['path'] and e['old8_rejected']['cap']==8. and not e['old8_rejected']['physical_smoke_pass'] and not e['old8_rejected']['ppo_performed']
    assert e['source_hashes_match'] and e['acceptance_routes_verified'] and e['only_rate_changes']
    return True
