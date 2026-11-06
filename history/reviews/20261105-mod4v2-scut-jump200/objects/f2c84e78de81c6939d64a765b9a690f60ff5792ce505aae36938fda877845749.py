"""Review fixtures for the frozen MOD4v2 SuperMimic integration.

CPU only. No production checkpoint load, simulator, optimizer update or SSH.
Injected values and toy states are explicitly not observations of the saved run.
"""
from pathlib import Path
from types import SimpleNamespace
from dataclasses import asdict
import argparse
import ast
import hashlib
import importlib.util
import json
import random
import sys
import time
import traceback

import numpy as np
import torch

N = Path(__file__).resolve().parent
G = Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
CODE = G / 'project/isaac/mod4v2_scut'
VENDOR = Path('F:/RMPOLAR-RL/mod4_standing_step200_rlbptt_20261103/source')
OUT = N / 'supermimic_abstraction_audit_cpu'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(VENDOR))
from ctx_reward_learner import ContextRewardLearner
from supermimic_vendor_v2.learner import SuperMimicConfig, SuperMimicLearner
from supermimic_vendor_v2.networks import WorldModel
from supermimic_vendor_v2.geometry import unflatten_state


def load_adapter():
    spec = importlib.util.spec_from_file_location('mod4v2_cpu_review_adapter', CODE / 'supermimic_newton.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ref(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest())


def function(path, name, cls=None):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    parent = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == cls) if cls else tree
    return next(x for x in parent.body if isinstance(x, (ast.FunctionDef, ast.ClassDef)) and x.name == name)


def named_attributes(node):
    return sorted({x.attr for x in ast.walk(node) if isinstance(x, ast.Attribute)})


def put(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def run():
    mod = load_adapter()
    mdp = mod.FudanJumpMdp(139)
    source_paths = [CODE / name for name in ('supermimic_newton.py', 'supermimic_train.py',
                    'supermimic_evaluate.py', 'newton_env.py', 'newton_checkpoint.py')]
    source_paths += [VENDOR / 'ctx_reward_learner.py', VENDOR / 'supermimic_vendor_v2/learner.py',
                     VENDOR / 'supermimic_vendor_v2/networks.py']
    findings = {}

    context = torch.zeros(2, 139)
    context[:, 0] = .6
    context[:, 9] = -1.
    context[:, 35:38] = context[:, :3]
    context[:, 57:63] = -1.
    context[:, 106] = 1.
    context[:, 107:113] = .9
    context[:, 123] = 2.
    action = torch.tensor([[.1, .2, .3, .4, .5, .6]]).repeat(2, 1)
    predicted = context + .01
    projected = mdp.project_predicted_context(predicted, None, action, torch.zeros(2, dtype=torch.long))
    findings['context_projection'] = dict(
        scope='Deliberately injected +.01 context error, not final5936 measurements.',
        actor_action_history_matches_action=bool(torch.equal(projected[:, 22:28], action)),
        duplicate_critic_action_history_matches_action=bool(torch.equal(projected[:, 57:63], action)),
        duplicate_critic_wheel_position_placeholders=projected[0, 49:51].tolist(),
        actor_wheel_position_placeholders=projected[0, 14:16].tolist(),
        before_mass_scale=float(context[0, 106]), after_mass_scale=float(projected[0, 106]),
        before_material=float(context[0, 107]), after_material=float(projected[0, 107]),
        before_action_lag=float(context[0, 123]), after_action_lag=float(projected[0, 123]),
        finding='Known duplicated fields are inconsistent; per-episode physical parameters are allowed to drift.')
    assert findings['context_projection']['actor_action_history_matches_action']
    assert not findings['context_projection']['duplicate_critic_action_history_matches_action']

    flat = torch.zeros(2, 73)
    flat[:, 2] = .3
    flat[:, 3] = 1.
    state = unflatten_state(flat)
    shifted = flat.clone()
    shifted[:, 0] += .8
    shifted_state = unflatten_state(shifted)
    wm = WorldModel(hidden=(8,), num_joints=30, action_dim=6, context_dim=139)
    a = wm.inputs(state, action, context)
    b = wm.inputs(shifted_state, action, context)
    features_a = mdp.critic_features(state, torch.zeros(2, dtype=torch.long), context)
    features_b = mdp.critic_features(shifted_state, torch.zeros(2, dtype=torch.long), context)
    findings['terrain_translation_alias'] = dict(
        translation_x_m=.8, WM_input_max_difference=float((a-b).abs().max()),
        critic_input_max_difference=float((features_a-features_b).abs().max()),
        source_terrain_edge_x_m=.8,
        scope='Input-identifiability counterexample. No contact simulation or claim that these paired states occurred in production.',
        finding='At equal context, translation towards the finite step is invisible to WM and critic.')
    assert torch.equal(a, b) and torch.equal(features_a, features_b)

    changed = list(state)
    changed[4] = state[4].clone().requires_grad_()
    different = list(state)
    different[4] = state[4] + .5
    previous = torch.zeros(2, 6)
    ctx = context.clone().requires_grad_()
    obs1 = mdp.obs(tuple(changed), previous, ctx, torch.zeros(2, dtype=torch.long))
    obs2 = mdp.obs(tuple(different), previous, ctx, torch.zeros(2, dtype=torch.long))
    joint_grad, = torch.autograd.grad(obs1.sum(), changed[4], allow_unused=True)
    findings['observation_state_decoupling'] = dict(
        physical_joint_change_rad=.5, observation_max_difference=float((obs1-obs2).abs().max()),
        observation_gradient_to_physical_joint_is_None=joint_grad is None,
        imagination_noise_is_identity=bool(torch.equal(mdp.add_noise(obs1), obs1)),
        finding='Actor observation is independently predicted context[:35], not reconstructed from predicted physical state. Other WM/reward gradient paths still exist.')
    assert torch.equal(obs1, obs2) and joint_grad is None

    calls = []
    class RecordingWM:
        def step(self, current, action, context):
            calls.append(context[:, 0].tolist())
            return current
    contexts = torch.zeros(2, 3, 139)
    contexts[:, :, 0] = torch.tensor([0., 1., 2.])
    owner = SimpleNamespace(cfg=SimpleNamespace(wm_window=3), wm=RecordingWM(), mdp=mdp)
    SuperMimicLearner._wm_rollout(owner, flat[:, None].repeat(1, 3, 1),
                                action[:, None].repeat(1, 3, 1), contexts)
    aux_node = function(VENDOR / 'ctx_reward_learner.py', 'aux_update', 'ContextRewardLearner')
    findings['training_imagination_context_mismatch'] = dict(
        actual_WM_rollout_context_calls=calls,
        auxiliary_samples_individual_transitions='sample_transitions' in named_attributes(aux_node),
        auxiliary_recurrent_training_loop=any(isinstance(x, (ast.For, ast.While)) for x in ast.walk(aux_node)),
        finding='WM gets true context at every training step; aux is one-step real-endpoint supervised. H32 policy uses recurrent predicted state AND predicted context.')
    assert calls == [[0., 0.], [1., 1.], [2., 2.]]

    frames = torch.arange(399)
    valid = mdp.valid_imagination_start_with_context(frames, 32, context[:1].expand(399, -1))
    ends = frames[valid, None] + torch.arange(1, 33)[None]
    timeout = mdp.imagination_timeout(ends, None)
    findings['finite_episode_timeout_exclusion'] = dict(
        last_valid_start_frame=int(frames[valid].max()), latest_end_frame=int(ends.max()),
        actual_timeout_at_frame=399, any_valid_rollout_reaches_timeout=bool(timeout.any()),
        excluded_start_frames=frames[~valid].tolist(),
        finding='All exact time-limit endings are excluded by motion-style start filtering. This removes a known zero-terminal boundary; not proof of the sole critic failure cause.')
    assert not timeout.any()

    class ConstantTeacher(torch.nn.Module):
        def forward(self, obs, stochastic_output=False):
            out = torch.zeros(*obs['policy'].shape[:-1], 6)
            out[..., 0] = 7.
            return out
    class Residual(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.dec = torch.nn.Sequential(torch.nn.Linear(1, 6))
        def forward(self, history, goal):
            return self.dec(torch.ones(*history.shape[:-2], 1))
    residual = Residual()
    policy = mod.FudanPPOResidualPolicy(residual, ConstantTeacher(), residual_scale=.25)
    predicted_action = policy(torch.zeros(2, 2, 35), torch.zeros(2, 3))
    grad, = torch.autograd.grad(predicted_action.mean(0).sum(), residual.dec[-1].bias)
    findings['residual_saturation_condition'] = dict(
        scope='Synthetic teacher output7 in first channel; production saturation fraction unknown.',
        teacher_raw_first=7., residual_range=[-.25, .25],
        executed_first=float(predicted_action[0, 0]), residual_bias_gradients=grad.tolist(),
        finding='If teacher exceeds clip6 by more than residual scale, that channel cannot escape saturation and its direct residual gradient is zero.')
    assert float(grad[0]) == 0 and bool((grad[1:] > 0).all())

    findings['partial_round_save'] = partial_round_fixture(mdp)

    upstream = N / 'supermimic_audit_sources/uni_ac19_src_unisupermimic_rl_algos_supermimic_learner.py'
    if upstream.exists():
        ctor = function(upstream, '__init__', 'SuperMimicLearner')
        ckpt = function(upstream, '_checkpoint', 'SuperMimicLearner')
        loader = function(upstream, 'load', 'SuperMimicLearner')
        stats = ['_v_mean', '_v_std', '_v_init']
        missing = [key for key in stats if key not in named_attributes(ckpt) and key not in named_attributes(loader)]
        findings['public_ac19_value_stats_resume'] = dict(
            fixed_commit='ac19b73a4f919fb2ea37dbad860b012315497139',
            constructor_has_statistics=all(k in named_attributes(ctor) for k in stats),
            statistics_missing_in_save_and_load=missing,
            illustrative_network_output=3., illustrative_before_mean=-10., illustrative_before_std=2.,
            illustrative_before_return=-4., illustrative_after_default_return=3.,
            scope='Source omission plus scalar illustration. Does not say latest upstream is unchanged or local final5936 contains such stats.',
            finding='This fixed public implementation also has a value-normalization resume omission. Local implementation lacks this normalization entirely.')
        assert missing == stats

    findings['boundary_and_model_limits'] = dict(
        production_checkpoint_reads=0, simulator_constructions=0, real_physics_steps=0,
        optimizer_updates=0, network_download_code_executed=False,
        current_final_checkpoint_reused_only_via_existing_JSON_diagnosis=True,
        conclusions_not_proven_by_fixtures=['actual production command drift size',
            'actual teacher saturation fraction', 'unique cause of critic failure',
            'new policy benefit or jump skill', 'hardware jump infeasibility'])
    report = dict(epoch=time.time(), mode='Review only; production source untouched',
                  sources=[ref(p) for p in source_paths], findings=findings)
    target = OUT / 'ABSTRACTION_CPU_REPROS.json'
    put(target, report)
    print(json.dumps(dict(report=str(target), reproduced=list(findings),
        production_PT_reads=0, real_physics_steps=0, optimizer_updates=0,
        training_restarts=0, production_source_changes=0), ensure_ascii=False))


def partial_round_fixture(mdp):
    """Run the actual finite worker main with an injected completed-WM failure.

    Only a counter represents a completed update; no optimizer is stepped.
    Actual ContextRewardLearner._checkpoint decides boundary safety.
    """
    flat = torch.zeros(2, 73); flat[:, 3] = 1.
    env = SimpleNamespace(device='cpu', num_envs=2, supermimic_mdp=mdp,
        state=SimpleNamespace(info={'supermimic_state':dict(s=flat,
            xi=torch.zeros(2, 139), a_prev=torch.zeros(2, 6),
            f=torch.zeros(2, dtype=torch.long), ep_step=torch.zeros(2, dtype=torch.long))}),
        plant=SimpleNamespace(receipt={'CPU_fixture': True}),
        numerical_reset_counts=torch.zeros(2, dtype=torch.long),
        constraint_reset_counts=torch.zeros(2, dtype=torch.long), closed=False)
    env.export_supermimic_resume = lambda: dict(exact=False, streams={})
    env.close = lambda: setattr(env, 'closed', True)
    cfg = SuperMimicConfig(buffer_steps=4, hist=2, warmup_steps=2, wm_window=2,
        wm_hidden=(8,), policy_hidden=(8,), critic_hidden=(8,),
        pi_batch=2, wm_batch=2, wm_batches=4, goal_frames=1,
        compile=False, amp='none')
    learner = ContextRewardLearner(env, cfg, OUT / 'learner_fixture', aux_hidden=(8,))
    learner.pi.residual_scale = .25  # The task worker's metadata, absent in bare Policy.
    learner.buffer.size = 2
    learner.buffer.ptr = 2
    bridge = SimpleNamespace(controls=0, close=lambda: None)
    def collect(steps):
        learner.sim_steps += steps * env.num_envs
        bridge.controls += steps
    learner.collect = collect
    def failed_wm():
        learner.counts.wm_optimizer_steps += 1
        raise RuntimeError('INJECTED_AFTER_ONE_SIMULATED_WM_UPDATE_NO_ACTUAL_OPTIMIZER')
    learner.wm_update = failed_wm
    saved = []
    def save(owner, path, source):
        value = owner._checkpoint(True)
        ext = value['context_reward_extension']
        item = dict(path=str(path), iteration=value['iteration'],
            simulated_WM_count=ext['counts']['wm_optimizer_steps'],
            pending_iteration=ext['pending_iteration'],
            collect_fraction=ext['collect_fraction'],
            update_boundary_safe=ext['update_boundary_safe'])
        saved.append(item)
        return item
    fmt = 'MOD4V2_FUDAN_NEWTON_SUPERMIMIC_FULL_V1'
    source = dict(format=fmt, iteration=0, source_PPO={'CPU_fixture':True},
        context_reward_extension={'counts':asdict(learner.counts)})
    job = OUT / 'failed_worker_main02'
    if job.exists():
        raise RuntimeError('Fixture already exists; do not overwrite prior evidence')
    # The metadata stand-in is not a PT file and is never torch.load-ed.
    standin = OUT / 'source_metadata_standin.json'; put(standin, {'fixture':True})
    cuda = SimpleNamespace(manual_seed_all=lambda x:None, synchronize=lambda x:None,
        memory_allocated=lambda:0, memory_reserved=lambda:0,
        mem_get_info=lambda:(0, 0))
    namespace = dict(Path=Path, argparse=argparse, time=time, random=random, np=np,
        torch=SimpleNamespace(cuda=cuda, manual_seed=lambda x:None), asdict=asdict,
        signal=SimpleNamespace(SIGTERM=15, signal=lambda *args:None),
        put=put, traceback=traceback, FORMAT=fmt, decode=lambda *args:source,
        NewtonEnv=lambda *args:env, build=lambda *args:(learner,bridge), save=save)
    node = function(CODE / 'supermimic_train.py', 'main')
    unit = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(unit, str(CODE / 'supermimic_train.py'), 'exec'), namespace)
    old = sys.argv
    try:
        sys.argv = ['CPU_review', '--package','fixture','--components','fixture',
            '--reset-bank','fixture','--binding','fixture','--job-root',str(job),
            '--resume',str(standin),'--resume-SHA','fixture','--num-envs','2',
            '--save-deadline',str(time.time()+120)]
        try:
            namespace['main']()
        except RuntimeError as exc:
            assert str(exc).startswith('INJECTED_AFTER_ONE_SIMULATED_WM_UPDATE')
        else:
            raise AssertionError('Expected injected failure')
    finally:
        sys.argv = old
    assert len(saved) == 1 and saved[0]['update_boundary_safe'] is True
    assert saved[0]['iteration'] == 0 and saved[0]['simulated_WM_count'] == 1
    assert saved[0]['pending_iteration'] is None and env.closed
    return dict(saved_metadata=saved, configured_WM_updates_per_round=4,
        collected_controls=bridge.controls, env_closed=env.closed,
        finding='Finite main bypasses the learner transaction tracker. Its interrupted save is labelled safe after only part of a round; strict restore cannot identify which phases remain.',
        scope='Injected worker exception, simulated WM count only. No optimizer step, PT write/read or simulator; normal final5936 save is not declared corrupt.')


if __name__ == '__main__':
    run()
