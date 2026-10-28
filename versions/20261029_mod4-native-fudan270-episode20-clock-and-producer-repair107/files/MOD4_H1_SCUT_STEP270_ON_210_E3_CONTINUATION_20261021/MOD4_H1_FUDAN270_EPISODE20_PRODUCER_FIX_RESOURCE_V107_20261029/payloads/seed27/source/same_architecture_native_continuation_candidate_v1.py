"""Uninstalled first post-R5 native continuation primitive.

Not a source-admission guard. Caller must first pin actual formal R5 FINAL,
wholeCPU/native provenance/original fees/allout. No file/model loading occurs.
Fresh environment/replay/history are retained; all trained modules, normalizer
buffers, three optimizer states and global iteration are restored together.
"""
from dataclasses import asdict
from copy import deepcopy
import math

DIMS=dict(state_joints=30,actions=6,obs_dim=86,goal_dim=146,
          packed_state_dim=127,dynamic_aux_dim=54,static_context_dim=31)

def exact_plain(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,dict):return set(a)==set(b) and all(exact_plain(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return len(a)==len(b) and all(exact_plain(x,y) for x,y in zip(a,b))
    return a==b

def validate_source(full,expected_source_contract,expected_args,expected_progress,expected_reference_SHA):
    if not exact_plain(full['UniSuperMimic_test_contract'],expected_source_contract):
        raise ValueError('qualified source contract differs; legacy native86 is not admitted')
    if any(type(expected_source_contract.get(k)) is not int or expected_source_contract[k]!=v for k,v in DIMS.items()):
        raise ValueError('only native127/86/146x10 architecture accepted')
    native=full['UniSuperMimic_H1_test'];pub=full['UniSuperMimic_publication']
    required=('wm','pi','critic','opt_wm','opt_pi','opt_v','iteration','wall_time','sim_steps','args','saved_at')
    if set(required)-set(native):raise ValueError('full native state/three optimizers required')
    if not exact_plain(native['args'],expected_args):raise ValueError('same native config including seed required')
    if expected_args['hist']!=10 or expected_args['goal_frames']!=10 or expected_args['no_critic']:
        raise ValueError('original history/goal/critic scope differs')
    if native['iteration']!=pub['native_iteration'] or native['iteration']!=expected_progress['updates']:
        raise ValueError('formal source iteration mismatch')
    for k in ('world_updates','policy_updates'):
        if pub[k]!=expected_progress[k] or type(pub[k]) is not int or pub[k]<=0:
            raise ValueError('formal learned global counters required')
    if type(native['iteration']) is not int or native['iteration']<=expected_args['wm_only_iters']:
        raise ValueError('source has not completed original world-only phase')
    if not math.isfinite(native['wall_time']) or native['wall_time']<0 or native['sim_steps']<=0:
        raise ValueError('invalid native source time/transitions')
    if pub['history_shape']!=[4096,10,86] or pub['episode_step_shape']!=[4096]:
        raise ValueError('formal R5 source population/shape differs')
    producer=pub['producer']
    if producer['reference_artifact_SHA']!=expected_reference_SHA or producer['method']!='MOD4_own_Fudan_native_v3':
        raise ValueError('source reference/method differs')
    if producer['native_architecture_fresh'] is not True or producer['bootstrap_Adam']!=832460:
        raise ValueError('candidate is only first same-architecture continuation from formal R5')
    return native,pub

def restore_same_architecture(learner,bridge,full,*,expected_source_contract,
                              expected_args,expected_progress,expected_reference_SHA,
                              expected_num_envs=4096):
    native,pub=validate_source(full,expected_source_contract,expected_args,
                              expected_progress,expected_reference_SHA)
    if not exact_plain(asdict(learner.cfg),expected_args):
        raise ValueError('new learner config differs before state mutation')
    if learner.env.num_envs!=expected_num_envs or learner.buffer.size!=0:
        raise ValueError('fresh target physical population/replay required')
    if learner.iteration!=0 or learner.sim_steps!=0 or bridge.wm_updates!=0 or bridge.pi_updates!=0:
        raise ValueError('do not restore over an already running learner')
    if tuple(learner.obs_hist.shape)!=(expected_num_envs,10,86) or tuple(bridge.ep_step.shape)!=(expected_num_envs,):
        raise ValueError('fresh target history/episode shape differs')
    # Do not copy source physical state, DR/RNG, replay, obs_history or ep_step.
    # load_state_dict includes registered normalization buffers.
    for name in ('wm','pi','critic'):
        getattr(learner,name).load_state_dict(native[name],strict=True)
    for name in ('opt_wm','opt_pi','opt_v'):
        getattr(learner,name).load_state_dict(deepcopy(native[name]))
    learner.iteration=native['iteration']
    learner.wall_time=native['wall_time']
    learner.sim_steps=native['sim_steps']
    bridge.wm_updates=pub['world_updates'];bridge.pi_updates=pub['policy_updates']
    return dict(passed=True,restored_iteration=learner.iteration,
        restored_world_updates=bridge.wm_updates,restored_policy_updates=bridge.pi_updates,
        all_three_modules_and_optimizers_restored=True,normalizers_inside_model_state_restored=True,
        source_observation_history_restored=False,source_environment_or_DR_RNG_or_replay_restored=False,
        fresh_environment_history_preserved=True,no_exact_PhysX_or_replay_resume=True,
        future_publisher_and_source_guard_contract_integration_required=True)

