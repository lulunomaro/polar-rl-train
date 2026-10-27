"""UNEXECUTED installed CPU entry point. Loads newly admitted native + bootstrap.

No Isaac scene, environment, actor forward, optimizer step, lock or GO. The saved
85 named-order object is a metadata CPU fixture; fresh86 readback occurs in the
frozen bridge after the original reset and before its first control or Pi.
"""
from pathlib import Path
import ast
from dataclasses import asdict
import importlib.util
import json
import os
import sys
import time
from types import SimpleNamespace

os.environ['CUDA_VISIBLE_DEVICES'] = ''


def main(B):
    B = Path(B).resolve()
    sys.path[:0] = [str(B), str(B / 'source'), str(B / 'source/sm_deps')]
    import torch
    torch.set_num_threads(2)
    from native86_source_guard_v1 import H, read, check_payload, validate_whole_native, NATIVE_SHA, BOOTSTRAP_SHA
    from native_continuation_v1 import read_pinned_metadata_bundle, admit_closed_source, exact, canonical
    from native_finalization_v1 import verify_native
    from h1_step270_fullstate_checkpoint_candidate_uninstalled import validate_new_phase
    checked = check_payload(B)
    m = read(B / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    contract = read(B / 'NATIVE86_SOURCE_CONTRACT_ACTUAL.json')
    binding, metadata = read_pinned_metadata_bundle(B / 'NATIVE_CONTINUATION_BINDING_ACTUAL.json')
    old_runtime = read(B / 'native_source_metadata/NATIVE85M2_RUNTIME_OBJECTIVE_CONTRACT_ACTUAL.json')
    assert H(B / 'native_source_metadata/NATIVE85M2_RUNTIME_OBJECTIVE_CONTRACT_ACTUAL.json') == binding['producer']['runtime_objective_contract_SHA']
    admitted = admit_closed_source(binding, current_runtime_order=metadata['runtime_order'],
        current_runtime_objective=old_runtime, **metadata)
    # This is the only initial source read and only initial bootstrap read in
    # this CPU process. No old experiment weights or NPZ are opened here.
    source = B / 'job0/source' / m['source_filename']
    bootstrap_path = B / 'job0/source' / m['bootstrap_filename']
    assert H(source) == NATIVE_SHA and H(bootstrap_path) == BOOTSTRAP_SHA
    s = torch.load(source, map_location='cpu', weights_only=False)
    bootstrap = torch.load(bootstrap_path, map_location='cpu', weights_only=False)
    whole = validate_whole_native(s, bootstrap, binding, metadata['final'], validate_new_phase, verify_native)
    rsl = Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
    actual = []
    for row in m['expected_actual_RSL_sources']:
        path = rsl / row['relative']
        assert path.stat().st_size == row['bytes'] and H(path) == row['SHA']
        actual.append(dict(path=str(path), SHA=H(path)))
    sdk = Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations))) / 'utils/math.py'
    assert H(sdk) == m['expected_actual_SDK_math_SHA']
    # Exercise the installed RSL loader on the in-memory source; no reread,
    # environment, algorithm step, policy sampling or inference is performed.
    from tensordict import TensorDict
    from rsl_rl.models import MLPModel
    from rsl_rl.algorithms import PPO
    obs = TensorDict(dict(policy=torch.zeros(1, 35), critic=torch.zeros(1, 38)), batch_size=[1])
    groups = dict(actor=['policy'], critic=['critic'])
    cfg_env = read(B / 'job0/original_run_manifest.json')['env']
    hidden = [int(x) for x in cfg_env['RM_HIDDEN_DIMS'].split(',')]
    actor = MLPModel(obs, groups, 'actor', 6, hidden_dims=hidden, activation='elu',
        distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',
                              init_std=float(cfg_env['RM_INIT_STD']), std_type='scalar'))
    critic = MLPModel(obs, groups, 'critic', 1, hidden_dims=hidden, activation='elu')
    optimizer = torch.optim.Adam(list(actor.parameters()) + list(critic.parameters()), lr=.0001)
    holder = SimpleNamespace(actor=actor, critic=critic, optimizer=optimizer, rnd=None)
    assert PPO.load(holder, s, None, True) is True
    for name, obj in (('actor_state_dict', actor), ('critic_state_dict', critic), ('optimizer_state_dict', optimizer)):
        assert exact(obj.state_dict(), s[name]), name
    # Read the exact config expression from the pinned bridge rather than
    # duplicating defaults. Native restore will independently enforce it again.
    from supermimic_vendor_v2.learner import SuperMimicConfig
    tree = ast.parse((B / 'source/h1_supermimic_bridge_v1.py').read_text('utf8'))
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    expr = next(n.value for n in run.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'cfg' for t in n.targets))
    assert isinstance(expr, ast.Call) and expr.func.id == 'SuperMimicConfig' and not expr.args
    expected_cfg = SuperMimicConfig(**{k.arg: ast.literal_eval(k.value) if not isinstance(k.value, ast.BinOp) else
        eval(compile(ast.Expression(k.value), '<pinned_constant_cfg>', 'eval'), {'__builtins__': {}}) for k in expr.keywords})
    assert canonical(s['UniSuperMimic_H1_test']['args']) == canonical(asdict(expected_cfg))
    # Native module/optimizer schemas and literal load roundtrip are checked
    # without constructing its replay, env, learner, logger or any forwards.
    from supermimic_vendor_v2.learner import SuperMimicLearner
    mdp = SimpleNamespace(num_joints=30, action_dim=6, context_dim=49, obs_dim=128, goal_frame_dim=73)
    skeleton = SimpleNamespace(mdp=mdp, cfg=expected_cfg)
    from supermimic_vendor_v2.networks import Critic
    wm = SuperMimicLearner._make_world_model(skeleton)
    pi = SuperMimicLearner._make_policy(skeleton)
    # Pinned H1 critic_features = invariant73 + context49 + frame1;
    # concatenating its one goal73 gives196. Avoid _critic_input_dim(), whose
    # upstream implementation would ask an environment for a state/forward.
    value = Critic(196, hidden=expected_cfg.critic_hidden)
    modules = dict(wm=wm, pi=pi, critic=value)
    opts = dict(opt_wm=torch.optim.Adam(wm.parameters(), lr=expected_cfg.lr),
        opt_pi=torch.optim.Adam(pi.parameters(), lr=expected_cfg.lr, betas=(.9, .95)),
        opt_v=torch.optim.Adam(value.parameters(), lr=expected_cfg.lr))
    for name, obj in {**modules, **opts}.items():
        if name in modules:
            obj.load_state_dict(s['UniSuperMimic_H1_test'][name], strict=True)
        else:
            obj.load_state_dict(s['UniSuperMimic_H1_test'][name])
        assert exact(obj.state_dict(), s['UniSuperMimic_H1_test'][name]), name
    from step270_reward_installed_CPU_v1 import check as reward_check
    from step270_boundary_installed_CPU_v1 import check as boundary_check
    from sampling_acceleration_installed_CPU_v2 import check as sampling_check
    reward = reward_check(B, sdk.parent.parent / 'managers/reward_manager.py', reference_path=B / 'reference_sources/V5_h1_step270_path_reward_v1.py')
    boundary = boundary_check(B)
    sampling = sampling_check(B, 'h1')
    assert not torch.cuda.is_initialized()
    result = dict(epoch=time.time(), passed_CPU_only=True, actual_H1_source_SDK_CPU_passed=True,
        source_SHA=NATIVE_SHA, bootstrap_SHA=BOOTSTRAP_SHA, bootstrap_Adam=829700,
        all17Adam=829700, native85_fullstate_source_CPU_passed=True, whole_native=whole,
        source_original85_cost_allout_passed=admitted['admitted'],
        manifest_SHA=checked['manifest_SHA'], actual_RSL_sources=actual,
        actual_SDK_math=dict(path=str(sdk), SHA=H(sdk)), rsl_load_roundtrip_CPU=True,
        native_modules_three_optimizers_config_roundtrip_CPU=True,
        new_reward_integration_CPU=reward, boundary_repair_integration_CPU=boundary,
        sampling_acceleration_CPU=sampling, native_continuation_restore_required=True,
        saved85_runtime_order_used_only_as_metadata_CPU_fixture=True,
        actual_fresh86_runtime_order_readback=False, CUDA_initialized=False,
        no_environment_actor_forward_optimizer_or_GO=True)
    destination = B / 'TARGET_NATIVE86_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json'
    with destination.open('x', encoding='utf8') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(json.dumps(result))


if __name__ == '__main__':
    main(sys.argv[1])
