"""Depth-conditioned SuperMimic interfaces and differentiable H32 core; not a launched learner."""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Protocol:
    physics_us:int=2500
    physics_callbacks:int=8
    feedback_samples:int=2
    policy_us:int=20000
    horizon:int=32
    original_state_dim:int=127
    original_static_dim:int=31
    depth_dim:int=9
    action_dim:int=6
    closure_reset_m:float=.01
    mimic_rad:float=.01

def policy_observation(proprio,depth_features):
    a=np.asarray(proprio);d=np.asarray(depth_features)
    if a.shape[-1]not in(35,38)or d.shape[-1]!=9 or a.shape[:-1]!=d.shape[:-1]:raise ValueError('Typed35/38 plus normalized9 depth features required')
    if not np.isfinite(a).all()or not np.isfinite(d).all():raise ValueError('Nonfinite observation')
    return np.concatenate((a,d),axis=-1)

def validate_transition(row,previous_control=None,*,synthetic_interface_test=False):
    """Validate clock/identity before a native WM replay/norm write. No pose-only NPZ input."""
    kind='SYNTHETIC_INTERFACE_ONLY'if synthetic_interface_test else'ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER'
    if row['producer_kind']!=kind or row['plant']!='own_MOD4_live_USD':raise ValueError('Own admitted plant source required')
    if (row['physics_us'],row['physics_callbacks'],row['feedback_samples'],row['policy_us'])!=(2500,8,2,20000):raise ValueError('Not the actual50Hz boundary')
    if previous_control is not None and row['control_index']!=previous_control+1:raise ValueError('Skipped/duplicate control')
    if not(row['run_id']and row['generation']and row['source_admission_SHA']):raise ValueError('Missing producer identity')
    if row['depth_control_time']>row['control_time']:raise ValueError('Future-depth truth')
    if row['depth_control_time']<row['control_time']-.20:raise ValueError('Stale-depth truth')
    for k,n in [('s',127),('s1',127),('xi',31),('depth',9),('a',6)]:
        x=np.asarray(row[k])
        if x.shape[-1]!=n or not np.isfinite(x).all():raise ValueError('Incomplete fullstate '+k)
    return True

def imagine32(initial_state,depth_anchor,*,actor,world_step,context,policy_obs,literal_reward_step,terminal_value,reward_memory,gamma=.9801):
    """Torch-compatible native callbacks. Reward callback must return original reward already weighted/clipped/dt-scaled once.

    context uses only the captured depth anchor and predicted pose, never future camera/physics truth.
    Actual127-state WM, ownFK/Fudan memory adapter and actor/critic admission are required outside this kernel.
    """
    state=initial_state;discount=1.;direct=0.;memory=reward_memory
    for _ in range(32):
        known=context(state,depth_anchor)
        action=actor(policy_obs(state,known)).clamp(-6.,6.)
        following=world_step(state,action,known)
        reward,memory=literal_reward_step(state,action,following,memory)
        direct=direct+discount*reward;discount=discount*gamma;state=following
    bootstrap=discount*terminal_value(state,context(state,depth_anchor))
    return dict(objective=direct+bootstrap,direct_reward=direct,terminal_value=bootstrap,state=state,reward_memory=memory)
