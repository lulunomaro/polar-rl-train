"""Synthetic CPU tensor tests only: no SDK/old model/input NPZ/raw/GPU query."""
import importlib.util
import json
from pathlib import Path
import time
import traceback
import torch

D = Path(__file__).resolve().parent


def main():
    torch.set_num_threads(1)
    spec = importlib.util.spec_from_file_location('w35_source_panel_CPU_fixture', D / 'w35_profile_env_domain_panel_v1.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    b = module.ProfileBook(torch, 3, 'cpu', ('base_contact', 'rough_route_boundary'))
    key = torch.tensor([8, 11, 12], dtype=torch.long, device='cpu')
    uid = torch.zeros(3, dtype=torch.long, device='cpu')
    zero = torch.zeros(3, device='cpu')
    false = torch.zeros(3, dtype=torch.bool, device='cpu')
    errors = [torch.tensor([0., .2, .4], device='cpu') for _ in range(4)]
    yaw = torch.tensor([0., -1.2, 1.2], device='cpu')
    b.observe(0, key, uid, errors, zero, yaw, false, false, [false, false])
    delta = torch.tensor([0., -6.4, 6.4], device='cpu')
    b.observe(1, key, uid, errors, delta, yaw, false, false, [false, false])
    # Same environment can complete another cycle; events must not become unique envs.
    b.observe(1, key, uid, errors, delta, yaw, false, false, [false, false])
    failed = torch.tensor([False, True, False], device='cpu')
    timeout = torch.tensor([False, False, True], device='cpu')
    b.observe(1, key, uid, errors, zero, yaw, failed, timeout, [failed, timeout])
    b.observe(1, key, uid, errors, zero, yaw, failed, timeout, [failed, timeout])
    profiles = b.summary()
    cond = b.condition_summary()
    row = lambda p: next(x for x in profiles if x['phase']=='steady' and x['profile']==p)
    negative = row(11)
    positive = row(12)
    moving = next(x for x in cond if x['phase']=='steady' and x['condition']=='moving_world_yaw')
    standing = next(x for x in cond if x['phase']=='steady' and x['condition']=='standing')
    checks = dict(
        actual_moving_denominator8=moving['population_control_denominator']==8,
        actual_standing_denominator4=standing['population_control_denominator']==4,
        unique_moving_env2=moving['unique_exposed_env_denominator']==2,
        weighted_moving_error_separate=abs(moving['means']['moving_world_progress_abs_error']-.3)<1e-7,
        standing_world_progress_not_applicable=standing['means']['moving_world_progress_abs_error'] is None,
        repeated_failure_events2_unique_env1=negative['terminated_mask_events']==2 and negative['unique_env_with_terminated_mask']==1,
        repeated_timeout_events2_unique_env1=positive['truncated_mask_events']==2 and positive['unique_env_with_truncated_mask']==1,
        cycle_events4_unique_env2=moving['complete_signed_cycle_events']==4 and moving['unique_env_with_complete_signed_cycle']==2,
        each_signed_profile_cycle_events2_unique1=negative['complete_signed_cycle_events']==2 and negative['unique_env_with_complete_signed_cycle']==1,
        phase_boundary_does_not_import_warmup_duration=abs(negative['maximum_live_continuous_seconds']-.04)<1e-7,
    )
    # New episode and changed profile must break continuity and accumulated turn.
    before = b.cycles.clone()
    uid += 1
    new_key = torch.tensor([8, 12, 11], dtype=torch.long, device='cpu')
    new_yaw = torch.tensor([0., 1.2, -1.2], device='cpu')
    tiny = torch.tensor([0., .1, -.1], device='cpu')
    b.observe(1, new_key, uid, errors, tiny, new_yaw, false, false, [false, false])
    checks['episode_and_profile_boundaries_no_cross_credit'] = bool(torch.equal(before,b.cycles)) and bool(torch.allclose(b.age, torch.full_like(b.age,.02)))
    # Even within one profile a unique environment cannot be counted twice across phases.
    whole = next(x for x in b.condition_summary() if x['phase']=='whole' and x['condition']=='moving_world_yaw')
    checks['whole_unique_environment_OR_not_phase_sum'] = whole['unique_exposed_env_denominator']==2
    assert all(checks.values()), checks
    result = dict(epoch=time.time(), passed=True, kind='synthetic_CPU_statistics_only', checks=checks,
                  device='cpu', no_old_models_NPZ_raw_or_SDK_import=True,
                  no_GPU_query_or_model_forward=True, actual_target_hooks_and_runtime_pending=True)
    with (D/'CPU_SYNTHETIC_PROFILE_ENV_DENOMINATOR_ACTUAL.json').open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2)
    print(json.dumps(result))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        with (D/('ORIGINAL_CPU_SYNTHETIC_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf-8') as f:
            json.dump(dict(passed=False,traceback=traceback.format_exc()),f,indent=2)
        raise
