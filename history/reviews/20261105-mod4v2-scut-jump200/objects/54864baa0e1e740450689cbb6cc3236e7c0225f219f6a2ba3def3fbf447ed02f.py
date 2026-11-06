"""CPU reproduction of the current adapter's command-hold omission.

Uses deliberately injected prediction error, not trained weights or new physics.
The masked arm is a proposed correction to compare, not a production repair.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import time

import torch


ROOT = Path(__file__).resolve().parent
CODE = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train/project/isaac/mod4v2_scut')
ADAPTER = CODE / 'supermimic_newton.py'
EXTENSION = Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/source/ctx_reward_learner.py')


def source_ref(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def main():
    spec = importlib.util.spec_from_file_location('mod4_command_hold_cpu_diagnostic', ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Dimension 160 is a synthetic fixture; the command slots come from the
    # actual actor35 + critic78 context layout. No environment is constructed.
    mdp = module.FudanJumpMdp(160)
    initial = torch.zeros(1, 160)
    initial[0, :3] = torch.tensor([.6, 0., 0.])
    initial[0, 35:38] = initial[0, :3]
    command_slots = [0, 1, 2, 35, 36, 37]
    actions = torch.zeros(1, 6)
    records = []
    for horizon in (1, 8, 32):
        arms = {}
        for name, hold in (('current_all_ones_mask', False), ('proposed_mask_only_comparison', True)):
            delta = torch.full_like(initial, 1e-5)
            delta[0, :3] = torch.tensor([.001, .0005, .0002])
            delta[0, 35:38] = delta[0, :3]
            delta.requires_grad_()
            mask = torch.ones(160)
            if hold:
                mask[command_slots] = 0.
            context = initial.clone()
            for index in range(horizon):
                next_context = context + mask * delta
                context = mdp.project_predicted_context(
                    next_context, None, actions, torch.tensor([index + 1]))
            goal = mdp.goal_with_context(torch.tensor([horizon]), 1, context)
            gradient, = torch.autograd.grad(goal[0, 0], delta)
            arms[name] = dict(
                actor_command=context[0, :3].detach().tolist(),
                duplicate_critic_command=context[0, 35:38].detach().tolist(),
                goal=goal[0].detach().tolist(),
                goal_x_gradient_wrt_injected_command_delta=float(gradient[0, 0]),
                commands_held=bool(torch.equal(context[0, command_slots], initial[0, command_slots])))
            arms[name]['_context'] = context.detach()
        other = [index for index in range(160) if index not in command_slots]
        unchanged = bool(torch.equal(arms['current_all_ones_mask']['_context'][:, other],
                                     arms['proposed_mask_only_comparison']['_context'][:, other]))
        for arm in arms.values():
            del arm['_context']
        assert not arms['current_all_ones_mask']['commands_held']
        assert arms['proposed_mask_only_comparison']['commands_held']
        assert unchanged
        records.append(dict(horizon=horizon, arms=arms, other_context_slots_equal=unchanged))
    report = dict(epoch=time.time(),
        finding='Current projector receives an already incremented context and copies its command back to itself. Default context mask is all ones; generated goals therefore follow injected command prediction error.',
        scope='Synthetic CPU fixture with deliberately injected nonzero prediction error. Does not measure actual final5936 command drift, establish the cause of critic failure, or validate a repaired policy.',
        sources=[source_ref(ADAPTER), source_ref(EXTENSION)],
        initial_command=initial[0, :3].tolist(),
        injected_command_delta_per_step=[.001, .0005, .0002],
        command_slots=command_slots, results=records,
        proposed_mask_only_comparison_is_not_production_patch=True,
        production_source_changes=0, production_PT_reads=0,
        environment_constructions=0, physics_steps=0, optimizer_updates=0,
        SSH=0, GPU_allocations=0, training_restarts=0)
    output = ROOT / 'supermimic_final3786_sampling_1h/reports/IMAGINED_COMMAND_HOLD_CPU_REPRO.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(report=str(output), reproduced=True,
        proposed_mask_comparison_passed=True, production_patch=False,
        production_PT_reads=0, physics_steps=0, SSH=0), ensure_ascii=False))


if __name__ == '__main__':
    main()
