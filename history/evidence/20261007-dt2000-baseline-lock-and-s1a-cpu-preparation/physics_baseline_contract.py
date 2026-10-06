"""Fail-closed checks for the human-locked 2ms production baseline."""
from decimal import Decimal

def validate_baseline(env, *, control_period_s=.01, contact_bin_s=.005,
                      num_envs=20000, steps_per_env=24, save_interval=25,
                      learning_rate=.0001, preflight=False):
    # Compare decimal clocks exactly rather than silently rounding a candidate.
    dt=Decimal(str(env['RM_PHYSICS_DT_S']))
    if dt!=Decimal('.002') or Decimal(str(control_period_s))!=Decimal('.01'):
        raise ValueError('Locked physics2ms/control10ms baseline changed')
    if Decimal(str(contact_bin_s))!=Decimal('.005'):
        raise ValueError('Original 5ms contact impulse bins changed')
    if int(env['RM_SOLVER_POS'])!=16 or int(env['RM_SOLVER_VEL'])!=4:
        raise ValueError('Locked solver16/4 changed')
    if any(env.get(k)!='1' for k in ('RM_KEEP_STD','RM_CONTACT_INTEGRATED','RM_CONTACT_EAGER5MS')):
        raise ValueError('STD restoration or original contact path changed')
    if steps_per_env!=24 or save_interval!=25 or learning_rate!=.0001:
        raise ValueError('Locked PPO collection/save/LR baseline changed')
    if num_envs!=20000 and not (preflight and num_envs==128):
        raise ValueError('Production or explicit128env preflight count changed')
    return {'physics_dt_s':.002,'decimation':5,'control_period_s':.01,
            'contact_bin_s':.005,'solver':[16,4],'accepted':True}
