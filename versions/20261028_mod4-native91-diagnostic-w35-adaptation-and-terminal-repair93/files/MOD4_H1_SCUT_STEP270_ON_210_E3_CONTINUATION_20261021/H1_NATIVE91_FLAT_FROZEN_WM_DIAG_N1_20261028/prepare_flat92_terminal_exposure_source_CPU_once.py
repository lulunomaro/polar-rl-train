"""New source-only purpose: expose the unchanged 5s terminal to imagination.

No checkpoint reads, actor/WM forward, physics, remote connection or account IO.
"""
from pathlib import Path
import ast, hashlib, json, time, traceback

S = Path(__file__).resolve().parent
T = S.parent
N = T / 'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027'
F = T / 'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/flat92_terminal_exposure_source_v1'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def main():
    F.mkdir(exist_ok=False)
    original = N / 'payload/source/native_flat_jump_adapter_v1.py'
    before = original.read_bytes()
    old = b'return (frames >= 0) & (delay < 250) & (age + int(horizon) + 10 <= 500)'
    new = b'return (frames >= 0) & (delay < 250) & (age < 500)'
    assert before.count(old) == 1
    after = before.replace(old, new, 1)
    assert after.replace(new, old, 1) == before
    out = F / original.name
    out.write_bytes(after)
    def functions(b):
        return {node.name: ast.dump(node, include_attributes=False)
                for node in ast.walk(ast.parse(b)) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    a, b = functions(before), functions(after)
    changed = [key for key in a if a[key] != b[key]]
    assert changed == ['valid_imagination_start'] and a.keys() == b.keys()
    import torch
    from types import SimpleNamespace
    import sys
    sys.path.insert(0, str(N / 'payload/source'))
    from private_phase_frame_v1 import encode, decode
    def fixture(code):
        tree = ast.parse(code)
        cls = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'OwnFlatJumpMdp')
        method = next(x for x in cls.body if isinstance(x, ast.FunctionDef) and x.name == 'valid_imagination_start')
        mod = ast.Module(body=[method], type_ignores=[])
        ns = {'decode_frame': lambda frames: (decode(frames)['public_age'], decode(frames)['delay_ticks'])}
        exec(compile(ast.fix_missing_locations(mod), str(out), 'exec'), ns)
        return ns['valid_imagination_start']
    old_fn, new_fn = fixture(before), fixture(after)
    age = torch.arange(500).repeat(250)
    delay = torch.arange(250).repeat_interleave(500)
    frames = encode(age, delay)
    original_valid = old_fn(None, frames, 32)
    fixed_valid = new_fn(None, frames, 32)
    assert original_valid.sum().item() == 459 * 250
    assert fixed_valid.all()
    assert (age[original_valid] + 32).max().item() == 490
    assert not ((age[original_valid, None] + torch.arange(1, 33)) >= 500).any()
    crossing = (age[:, None] + torch.arange(1, 33)) >= 500
    assert (fixed_valid & crossing.any(-1)).sum().item() == 32 * 250
    terminal_frames = encode(torch.tensor([500, 501, 999]), torch.tensor([0, 10, 249]))
    assert not new_fn(None, terminal_frames, 32).any()
    assert not new_fn(None, torch.tensor([-1]), 32).any()
    # The original learner TD(lambda) equation must cut arbitrary value tails
    # at the existing timeout. This checks the actual target equation's math,
    # not a saved critic or an extra model forward.
    rewards = torch.full((32,), .06)
    dones = (499 + torch.arange(1, 33) >= 500).float()
    values = torch.full((33,), 1e6)
    target = values[-1]
    targets = []
    for i in range(31, -1, -1):
        target = rewards[i] + .99 * (1-dones[i]) * ((1-.95)*values[i+1] + .95*target)
        targets.append(target)
    assert targets[-1].item() == rewards[0].item()
    assert not torch.cuda.is_initialized()
    result = dict(passed=True, source_only_not_installed=True,
        source_original=dict(path=str(original), SHA=sha(before)),
        source_candidate=dict(path=str(out), SHA=sha(after)),
        changed_AST_functions=changed, exact_reverse_byte_equality=True,
        actual_learner_source_predicate_before_imagination=True,
        original_age_start_max=458, original_imagined_age_max=490,
        original_time_out_500_never_in_sampled_32step_rollout=True,
        new_valid_actual_starts=125000, new_terminal_crossing_starts=8000,
        original_physical_timeout_500_unchanged=True,
        original_soft_termination_action_reward_WM_Pi_Critic_norms_optimizers_unchanged=True,
        arbitrary_critic_tail_cut_by_existing_timeout=True,
        no_model_load_forward_physics_GPU_remote_or_budget_IO=True,
        not_proven_unique_zero_jump_cause_or_learning_gain=True,
        qualification_next='NEW typed91 formal bd36a58c native lineage, new source/SDK/admission and actual resource/account scheduling boundary; never hotpatch91',
        scope='Future analytic goal frames are defined beyond500. Physical reset/age/hard timeout are unchanged. Imagined post-terminal rewards remain excluded by original learner continuation; no reset dynamics are invented.',
        epoch=time.time())
    (F/'SOURCE_CPU_ACTUAL.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf8')
    (F/'HANDOFF.md').write_text('Source-only flat92 terminal exposure repair. Exactly one return expression changed; all other AST and bytes reverse exactly. Original physical timeout500 and success unchanged. Native91 previously excluded all time-limit endings from its32step imagined critic targets; this source change admits actual preterminal starts. It does not establish that this is the sole cause, validate airborne WM dynamics, or authorize reusing old Task/once. Actual typed source/SDK/continuation/resource admission is still required.\n', 'utf8')
    rows = [dict(path=str(p), bytes=p.stat().st_size, SHA=sha(p.read_bytes())) for p in sorted(F.iterdir()) if p.is_file()]
    (F/'FROZEN_SOURCE_INDEX_ACTUAL.json').write_text(json.dumps(dict(frozen=True, files=rows), indent=2), 'utf8')
    print(json.dumps(dict(passed=True, changed=changed, original_critic_max_age=490, new_terminal_crossing_starts=8000)))

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        (S/'reports'/('FLAT92_TERMINAL_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).write_text(json.dumps(dict(traceback=traceback.format_exc()), indent=2), 'utf8')
        raise
