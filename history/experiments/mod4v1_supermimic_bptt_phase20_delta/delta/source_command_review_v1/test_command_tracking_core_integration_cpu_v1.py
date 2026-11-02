"""NEW source-only SYNTHETIC CPU integration, not native MOD4 training.

Requires: existing CPU torch; adjacent frozen candidate/core; parent's existing
supermimic_vendor_v2 package; explicit tiny fixture/bridge source paths. No PT,
SDK/App, simulator, worker entrypoint, CUDA execution, C/GO, install or old data.
Only named audited classes are AST-loaded; old fixture bottom is never executed.

python -B test_command_tracking_core_integration_cpu_v1.py \
  --vendor-parent NEW_CPU_INPUT_ROOT \
  --fixture INPUT/synthetic_cpu_contract_check.py \
  --bridge-source INPUT/native_supermimic_bridge.py \
  --output-dir NEW_CPU_INPUT_ROOT/NEW_SYNTHETIC_INTEGRATION_RESULT

The output directory must not already exist. Logs/counts are SYNTHETIC only.
"""
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import argparse
import ast
from dataclasses import dataclass
import hashlib
import importlib
import json
from pathlib import Path
import sys
import traceback
import types

PINNED = {
    'command_tracking_torch_candidate_v1.py': 'bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223',
    'ctx_reward_candidate_v1.py': 'c0cc5d201e98598d32f62572a61be633cb7d8bcdf53e5f33883792df12539454',
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def class_ast_only(path, names, namespace):
    tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    selected = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in names]
    if {n.name for n in selected} != set(names):
        raise AssertionError('fixture class contract mismatch: ' + str(names))
    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(path) + ':SELECTED_CLASSES_ONLY', 'exec'), namespace)
    return {name: namespace[name] for name in names}


def run(args, out):
    vendor_parent = args.vendor_parent.resolve(strict=True)
    candidate_dir = args.candidate_dir.resolve(strict=True)
    fixture = args.fixture.resolve(strict=True)
    bridge = args.bridge_source.resolve(strict=True)
    for name, expected in PINNED.items():
        actual = sha(candidate_dir / name)
        if actual != expected:
            raise AssertionError('frozen file SHA mismatch: ' + name)
    if not (vendor_parent / 'supermimic_vendor_v2' / 'learner.py').is_file():
        raise AssertionError('--vendor-parent must contain supermimic_vendor_v2/learner.py')
    sys.path.insert(0, str(vendor_parent))
    sys.path.insert(0, str(candidate_dir))
    import torch
    torch.set_num_threads(1)
    torch.manual_seed(37)
    torch.set_default_dtype(torch.float32)
    assert not torch.cuda.is_initialized()
    c = importlib.import_module('command_tracking_torch_candidate_v1')
    core = importlib.import_module('ctx_reward_candidate_v1')
    assert Path(c.__file__).resolve() == candidate_dir / 'command_tracking_torch_candidate_v1.py'
    assert Path(core.__file__).resolve() == candidate_dir / 'ctx_reward_candidate_v1.py'
    from supermimic_vendor_v2.geometry import invariant_features, unflatten_state, so3_exp, so3_log
    from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY, SUPERMIMIC_TRANSITION_KEY
    from supermimic_vendor_v2.learner import SuperMimicConfig

    namespace = types.ModuleType('_source_command_synthetic_ast_v1')
    sys.modules[namespace.__name__] = namespace
    namespace.__dict__.update(torch=torch, dataclass=dataclass,
                              invariant_features=invariant_features, unflatten_state=unflatten_state,
                              SUPERMIMIC_STATE_KEY=SUPERMIMIC_STATE_KEY,
                              SUPERMIMIC_TRANSITION_KEY=SUPERMIMIC_TRANSITION_KEY)
    class_ast_only(bridge, ('BridgeState', 'OriginalTaskMdp'), namespace.__dict__)
    selected = class_ast_only(fixture, ('FakeTeacher', 'Synthetic'), namespace.__dict__)
    OriginalTaskMdp = namespace.OriginalTaskMdp
    Synthetic = selected['Synthetic']
    FakeTeacher = selected['FakeTeacher']

    class SyntheticSampleOracle:
        """SYNTHETIC declared substep oracle, not an Isaac/WM reconstruction.

        2 sample ticks/control; geodesic midpoint R + linear midpoint values; an
        exogenous uniform tape at original raw bounds; per-episode leg bias and
        0/1 sample lag. Both samples retain their own BODY frame. Using known
        synthetic substeps does NOT fill the missing real 100Hz state receipts.
        """
        def __init__(self):
            generator = torch.Generator(device='cpu').manual_seed(7337)
            self.bounds = {'base_ang_vel': .125, 'projected_gravity': .025,
                           'leg_pos': .005, 'leg_vel': .25, 'wheel_vel': .5}
            widths = {'base_ang_vel': 3, 'projected_gravity': 3,
                      'leg_pos': 4, 'leg_vel': 4, 'wheel_vel': 2}
            self.noise = {k: (2 * torch.rand(1024, width, generator=generator) - 1) * self.bounds[k]
                          for k, width in widths.items()}
            self.bias = (2 * torch.rand(4, generator=generator) - 1) * .0075
            self.calls = 0
            self.sample_evaluations = 0
            self.min_tick = None
            self.max_tick = None

        def sensors(self, state, state1, frames, lag):
            midpoint = tuple(.5 * (a + b) for a, b in zip(state, state1))
            rm = state[1] @ so3_exp(.5 * so3_log(state[1].transpose(-1, -2) @ state1[1]))
            midpoint = (midpoint[0], rm, *midpoint[2:])
            zeros = state1[4].new_zeros(state1[4].shape)
            results = []
            for sample_index, sample_state in enumerate((midpoint, state1), start=1):
                tick = (2 * frames + sample_index).long()
                if int(tick.max()) >= 1024 or int(tick.min()) < 0:
                    raise AssertionError('synthetic tape clock exceeded')
                clean = c.sampled_state_sensor_inputs(sample_state, (0, 1, 2, 3), (4, 5), zeros, zeros)
                noisy = {k: value + self.noise[k][tick] for k, value in clean.items()}
                noisy['leg_pos'] = noisy['leg_pos'] + self.bias
                results.append(noisy)
                self.sample_evaluations += frames.numel()
                lo, hi = int(tick.min()), int(tick.max())
                self.min_tick = lo if self.min_tick is None else min(self.min_tick, lo)
                self.max_tick = hi if self.max_tick is None else max(self.max_tick, hi)
            self.calls += 1
            return {k: torch.where(lag[:, None], results[0][k], results[1][k]) for k in results[0]}

        def __call__(self, context, state, state1, action, frames, next_frames):
            # MODEL SIDE ONLY suffix: role, axis, rate, moving, transition,
            # standing, initial_phase, absolute synthetic timer, lag Boolean.
            role_w35 = context[..., 35] > .5
            axis, rate = context[..., 36], context[..., 37]
            moving, transition, standing = (context[..., i] > .5 for i in (38, 39, 40))
            phase = context[..., 41] + frames * .02
            known = (context[..., 42] - next_frames * .02 > 0) & (next_frames == frames + 1)
            command_e2 = c.e2_command(context[..., :3], torch.atan2(state1[1][..., 1, 0], state1[1][..., 0, 0]),
                world_direction=axis, signed_yaw=rate, moving=moving, transition=transition,
                standing=standing, next_write_elapsed=phase, progress_goal=.5, body_limit=1.5)
            command_w35 = c.w35_all_rough_command(context[..., :3], standing)
            command = torch.where(role_w35[:, None], command_w35, command_e2)
            sensors = self.sensors(state, state1, frames, context[..., 43] > .5)
            return c.ProjectedTransition(command, sensors, True, bool(known.all()), True,
                                         'SYNTHETIC_2x100HZ_NOISY_LAG_ORACLE_NOT_RUNTIME')

    oracle = SyntheticSampleOracle()

    class SyntheticOracleEnv(Synthetic):
        def __init__(self):
            super().__init__()
            self.xi = torch.zeros(self.num_envs, 44)
            self.xi[:, 3] = 1.25  # .25m * original height scale5
            self.xi[:, 35] = torch.tensor([0, 0, 0, 0, 1, 1, 1, 1])
            self.xi[:, 36] = torch.arange(8) * .1
            self.xi[:, 37] = torch.tensor([4., -4., 4., -4., 0., 0., 0., 0.])
            self.xi[:2, 38] = 1
            self.xi[3, 39] = 1
            self.xi[[2, 7], 40] = 1
            self.xi[:, 42] = 20.  # toy horizon stays below synthetic resampling
            self.xi[:, 43] = torch.tensor([0, 1, 0, 1, 0, 1, 0, 1])
            self.xi[:, 2] = self.xi[:, 37]
            self.xi[4:7, 0] = torch.tensor([-.2, .15, .3])
            s = unflatten_state(self.s)
            initial = oracle(self.xi, s, s, self.a, self.f, self.f + 1)
            self.xi[:, :35] = c.compose_raw35(initial.command, self.xi[:, 3:4] / 5.,
                                             initial.sensor_values, self.a, self.xi[:, 28:35])
            self.mdp = c.Raw35ActorMDP(OriginalTaskMdp(44, self.s), oracle,
                                      require_sampled_sensor_projection=True, tracking_component=None)

        @torch.no_grad()
        def step(self, action):
            result = super().step(action)  # original tiny fixture's physical/reward toy
            t = result.info[SUPERMIMIC_TRANSITION_KEY]
            p = oracle(t['xi'], unflatten_state(t['s']), unflatten_state(t['s1']), t['a'], t['f'], t['f'] + 1)
            raw = c.compose_raw35(p.command, t['xi'][:, 3:4] / 5., p.sensor_values, t['a'], t['xi'][:, 28:35])
            next_context = torch.cat((raw, t['xi'][:, 35:]), -1)
            t['xi1'] = next_context.clone()
            result.info[SUPERMIMIC_STATE_KEY]['xi'] = next_context.clone()
            return result

    env = SyntheticOracleEnv()
    env.init_state()
    teacher = FakeTeacher().eval().requires_grad_(False)
    teacher_snapshot = {k: v.detach().clone() for k, v in teacher.state_dict().items()}

    def teacher_forward(model, raw):
        assert raw.shape[-1] == 35
        return model({'policy': raw}, stochastic_output=False)

    class Learner(core.ContextRewardLearner):
        def _make_policy(self):
            return c.ScaledTeacherResidualPolicy35(super()._make_policy(), teacher, teacher_forward,
                                                   radius=.05, anchor_coefficient=0.)

    config = SuperMimicConfig(iterations=100, buffer_steps=16, utd=1., horizon=16,
        goal_frames=1, hist=10, z_dim=4, wm_hidden=(16,), policy_hidden=(16,), critic_hidden=(16,),
        wm_window=2, wm_batches=1, wm_batch=8, pi_batch=8, lr=.001, warmup_steps=8,
        wm_only_iters=2, critic_epochs=1, critic_minibatches=1, ckpt_every=10000,
        log_every=10000, log_backend='none', amp='none', compile=False, seed=37)
    learner = Learner(env, config, out / 'SYNTHETIC_LOGS', device='cpu', aux_hidden=(16,),
                      aux_batch=8, predict_context_mask=torch.zeros(44))
    assert learner.mdp.obs_dim == learner.obs_hist.shape[-1] == 35
    assert learner.pi.obs_norm.mean.numel() == 35
    assert learner.pi.anchor_coefficient == 0 and learner.mdp.tracking_component is None
    teacher_ids = {id(p) for p in teacher.parameters()}
    assert not teacher_ids.intersection(id(p) for group in learner.opt_pi.param_groups for p in group['params'])
    learner.collect(8)
    assert learner.counts.pi_optimizer_steps == learner.counts.pi_bptt_optimizer_steps == 0
    for _ in range(20):
        learner.wm_update()  # includes the actual auxiliary supervised optimizer
    receipts = []
    for _ in range(3):
        learner.policy_update()  # actual frozen candidate core + actual critic optimizer
        r = dict(learner.last_bptt_receipt)
        assert r['verified_bptt_optimizer_step'], r
        assert r['cross_time_finite'] and r['cross_time_grad_norm'] > 0, r
        assert r['wm_path_finite'] and r['wm_path_grad_norm'] > 0, r
        assert r['parameter_grad_norm'] > 0 and r['probe_parameter_delta_l2'] > 0, r
        receipts.append(r)
    assert learner.counts.pi_optimizer_steps == learner.counts.pi_bptt_optimizer_steps == 3
    assert learner.counts.pi_unverified_steps == 0
    assert learner.counts.wm_optimizer_steps == learner.counts.aux_optimizer_steps == 20
    assert learner.counts.critic_optimizer_steps == 3
    assert all(torch.equal(teacher_snapshot[k], value) for k, value in teacher.state_dict().items())
    assert all(not p.requires_grad and p.grad is None for p in teacher.parameters())
    assert oracle.sample_evaluations == oracle.calls * 2 * 8
    assert learner.mdp.last_projection_status == 'SYNTHETIC_2x100HZ_NOISY_LAG_ORACLE_NOT_RUNTIME'
    assert not torch.cuda.is_initialized()
    assert all(p.device.type == 'cpu' for m in (learner.wm, learner.pi, learner.critic, learner.aux) for p in m.parameters())
    assert not any(name == 'isaaclab' or name.startswith(('isaaclab.', 'omni.')) for name in sys.modules)
    return {'kind': 'SYNTHETIC_CPU_ACTUAL_CANDIDATE_CORE_INTEGRATION_NOT_NATIVE_TRAINING',
            'passed': True, 'torch_version': torch.__version__, 'CUDA_initialized': False,
            'native_expert_BPTT_updates_counted': 0, 'PT_SDK_App_GPU_C_GO_operations': 0,
            'fixture_bottom_executed': False, 'fixture_AST_classes': ['FakeTeacher', 'Synthetic'],
            'bridge_AST_classes': ['BridgeState', 'OriginalTaskMdp'],
            'actual_core_import': str(Path(core.__file__).resolve()),
            'actual_vendor_learner': str(Path(sys.modules['supermimic_vendor_v2.learner'].__file__).resolve()),
            'frozen_source_SHA256': PINNED, 'fixture_SHA256': sha(fixture), 'bridge_SHA256': sha(bridge),
            'this_test_SHA256': sha(__file__), 'synthetic_counts': vars(learner.counts),
            'all_three_optimizer_gradient_receipts': receipts, 'actor_obs_dim': 35, 'model_context_dim': 44,
            'teacher_frozen_unchanged': True, 'bounded_residual_enabled': False, 'anchor_coefficient': 0.,
            'reward_decomposition_enabled': False, 'uncertainty_enabled': False,
            'synthetic_sensor_oracle': {'calls': oracle.calls, 'sample_evaluations': oracle.sample_evaluations,
                'samples_per_control': 2, 'tick_min': oracle.min_tick, 'tick_max': oracle.max_tick,
                'noise_and_bias': 'exogenous original raw-bound toy uniform tape, not actual runtime RNG',
                'substep_states': 'declared synthetic geodesic midpoint/end, not recovered real 100Hz state'},
            'runtime_bindings_verified': False, 'native_pass_rate': None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor-parent', type=Path, required=True)
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--bridge-source', type=Path, required=True)
    parser.add_argument('--candidate-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir.resolve()
    if out.exists():
        raise FileExistsError('use a NEW synthetic result directory: ' + str(out))
    out.mkdir(parents=True, exist_ok=False)
    try:
        result = run(args, out)
    except Exception as error:
        result = {'kind': 'SYNTHETIC_CPU_INTEGRATION_SOFTWARE_FAILURE_NOT_NATIVE', 'passed': False,
                  'error_type': type(error).__name__, 'error': str(error), 'traceback': traceback.format_exc(),
                  'this_test_SHA256': sha(__file__), 'native_expert_BPTT_updates_counted': 0}
        (out / 'CORE_INTEGRATION_RECEIPT_V1.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
        raise
    (out / 'CORE_INTEGRATION_RECEIPT_V1.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
