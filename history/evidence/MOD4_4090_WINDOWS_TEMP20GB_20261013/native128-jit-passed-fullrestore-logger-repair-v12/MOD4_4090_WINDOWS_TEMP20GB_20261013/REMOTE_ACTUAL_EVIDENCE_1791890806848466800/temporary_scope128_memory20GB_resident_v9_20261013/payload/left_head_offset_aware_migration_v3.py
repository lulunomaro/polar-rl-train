"""One-time independent left-head initializer with actual API offsets explicit.

Pure CPU tree migration. Runtime must first finish the original12 restore markers,
then verify every actual offset against actual default_q and this admitted fixture.
Older v1/v2 offset-omitting proofs remain historical and are not consumed here.
"""
import copy, hashlib
from pathlib import Path
import torch
from temporary_state_binding import same, floating_count, validate, DONOR_SHA
PROFILE = 'windows4090_full20k_left_effective_exploration_offset_aware_v3'
LOWER = -1.0843
UPPER = 0.85
SCALE = 0.5

def offsets_validate(offsets, n):
    assert torch.is_tensor(offsets) and offsets.shape == (n, 4) and (offsets.dtype == torch.float32) and torch.isfinite(offsets).all(), 'actual offset schema'
    assert torch.equal(offsets, offsets[:1].expand(n, 4)), 'nonuniform offsets need separately reviewed initializer'
    return offsets[:1].detach().cpu().clone()

def guarded_targets(action, offsets, lower=LOWER, upper=UPPER, scale=SCALE):
    assert action.shape[-1] == 6 and offsets.shape[-1] == 4
    p = action[..., :4].clamp(-6.0, 6.0) * scale + offsets
    out = p.clone()
    for crank, hip in ((0, 1), (2, 3)):
        out[..., crank] = torch.maximum(p[..., crank], p[..., hip] + lower)
        out[..., crank] = torch.minimum(out[..., crank], p[..., hip] + upper)
    return out

def migrate_tree(source, *, source_sha, actual_offsets, expected_num_envs=128):
    assert expected_num_envs == 128 and source_sha == DONOR_SHA, 'new20k donor must be complete d05c; no91d splice'
    validate(source, source_sha)
    assert 'WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL' not in source and 'WINDOWS4090_LEFT_HEAD_OFFSET_AWARE_CPU_CANDIDATE' not in source, 'initializer cannot repeat'
    off = offsets_validate(actual_offsets, expected_num_envs)
    new = copy.deepcopy(source)
    a = new['actor_state_dict']
    o = new['optimizer_state_dict']
    delta = (LOWER + float(off[0, 1]) - float(off[0, 0])) / SCALE
    a['mlp.6.weight'][0].copy_(a['mlp.6.weight'][1])
    a['mlp.6.bias'][0] = a['mlp.6.bias'][1] + delta
    a['distribution.std_param'][0] = a['distribution.std_param'][2]
    assert (a['distribution.std_param'] > 0).all()
    for pid in (0, 7, 8):
        for field in ('exp_avg', 'exp_avg_sq'):
            o['state'][pid][field][0].zero_()
        assert same(o['state'][pid]['step'], source['optimizer_state_dict']['state'][pid]['step'])
    for key in source:
        if key not in ('actor_state_dict', 'optimizer_state_dict'):
            assert same(source[key], new[key]), key
    for key, v in a.items():
        if key in ('mlp.6.weight', 'mlp.6.bias', 'distribution.std_param'):
            assert same(v[1:], source['actor_state_dict'][key][1:])
        else:
            assert same(v, source['actor_state_dict'][key])
    for pid, v in o['state'].items():
        if pid in (0, 7, 8):
            for field in ('exp_avg', 'exp_avg_sq'):
                assert same(v[field][1:], source['optimizer_state_dict']['state'][pid][field][1:])
        else:
            assert same(v, source['optimizer_state_dict']['state'][pid])
    assert same(o['param_groups'], source['optimizer_state_dict']['param_groups'])
    new['WINDOWS4090_LEFT_HEAD_OFFSET_AWARE_CPU_CANDIDATE'] = dict(profile=PROFILE, source_sha256=source_sha, num_envs=expected_num_envs, offsets_leg_order=off[0].tolist(), offsets_float32_bytes_SHA=hashlib.sha256(off.numpy().tobytes()).hexdigest(), left_bias_delta_action_units=delta, scale=SCALE, diff_min_rad=LOWER, diff_max_rad=UPPER, CPU_prepared_only=True, original_complete_source_restore_before_initialization_required=True, all_other5_actor_rows_std_and_hidden_critic_DR_RNG_exact=True, Adam_moment_row0_only_cleared_parameter_ids=[0, 7, 8], original_Adam_steps_retained=True, actual_runtime_API_offsets_full20k_and_default_q_must_match=True, deterministic_target_domain_must_be_verified_on_actual_initial_observations=True, same_repaired_resume_must_not_repeat=True, no_live_action_coupling_teacher_privileged_input_or_qualification=True)
    assert floating_count(new) == 107
    return new
