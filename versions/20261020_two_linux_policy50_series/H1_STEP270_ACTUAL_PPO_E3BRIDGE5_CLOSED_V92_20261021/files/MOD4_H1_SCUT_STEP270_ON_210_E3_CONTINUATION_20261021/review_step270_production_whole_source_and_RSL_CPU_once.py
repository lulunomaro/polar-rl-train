"""Review the new production wiring, reusing completed scene evidence. CPU fixture only."""
from pathlib import Path
import ast, copy, hashlib, importlib.metadata, io, json, sys, time, traceback
import torch

T = Path(__file__).resolve().parent
W = T.parent
R = T / 'reports'
D = T / 'production_candidate_V1_UNINSTALLED'
OLD = W / 'MOD4_SCUT_FUDAN_SIXTEENTH_HOUR_20261019/payload/h1'
RT = OLD / 'job0/runtime/isaac/mod4'
H = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(name, value):
    with (R / name).open('x', encoding='utf8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def fn(source, name):
    return next(x for x in ast.walk(ast.parse(source)) if isinstance(x, ast.FunctionDef) and x.name == name)

def main():
    assert not (R / 'STEP270_PRODUCTION_WHOLE_SOURCE_AND_RSL_CPU_ACTUAL.json').exists()
    put('STEP270_PRODUCTION_WHOLE_SOURCE_AND_RSL_CPU_STARTED_ACTUAL.json',
        dict(epoch=time.time(), no_remote_transport_GPU_or_environment_rollout=True))
    torch.set_num_threads(2)
    initial_rng = torch.get_rng_state().clone()
    prepared = json.loads((R / 'STEP270_PRODUCTION_V1_UNINSTALLED_SOURCE_AST_AND_STORAGE_CPU_ACTUAL.json').read_bytes())
    for row in prepared['files']:
        assert Path(row['path']).stat().st_size == row['bytes'] and H(row['path']) == row['SHA']
    old_manifest = json.loads((OLD / 'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
    native_manifest = json.loads((T / 'full20k_native180_V3_actual/SOURCE_MANIFEST.json').read_bytes())
    before = {x['relative']: x for x in old_manifest['files']}
    runtime_match = []
    for row in native_manifest['files']:
        if row['relative'].startswith(('job0/runtime/', 'job0/assets/', 'lib/')):
            assert before[row['relative']]['SHA'] == row['SHA']
            assert before[row['relative']]['bytes'] == row['bytes']
            runtime_match.append(row['relative'])
    assert len(runtime_match) == 433
    proof_names = [
        'STEP270_FULL20K_NATIVE180_V3_CORE_CLOCK_GUARD_WITNESS_CPU_ACTUAL.json',
        'STEP270_FULL20K_NATIVE180_V3_ORIGINAL_ACTOR_MEAN_CPU_ACTUAL.json',
        'STEP270_FULL20K_NATIVE180_V3_EVENTS_SCUT_REFERENCE_CPU_ACTUAL.json',
        'STEP270_FULL20K_V9_ALL160K_COOKED_METRIC_GEOMETRY_CPU_V2_ACTUAL.json',
    ]
    core, mean, events, query = [json.loads((R / x).read_bytes()) for x in proof_names]
    assert core['passed_core_clock_action_guards_and_witness_CPU']
    assert core['source_actor9_critic8_sixSTD_all17Adam_literal_exact']
    assert core['actual_D0_D7_original_CUDA_resume_and_new_phase_roundtrip_verified']
    assert core['controls'] == 180 and core['callbacks'] == 720 and core['num_envs'] == 20000
    assert mean['passed_original_FP32_raw_mean_absolute_1e4']
    assert mean['actual_executed6_is_literal_clip_of_recorded_GPUraw']
    assert events['passed_saved_event_and_ballistic_reference_CPU']
    assert events['all_goal_thresholds_270mm_and_stable200_callbacks_unchanged']
    assert query['passed_independent_all160k_metric_geometry_CPU']
    assert query['actual_SDK_three_new_rate_math_passed']
    assert query['actual_GPU_complete_all_ownout_and_private_lease_released']
    for name in ('h1_step270_sdk_runtime_candidate.py', 'step270_goal_and_scut_rates_candidate.py',
                 'step270_triangle_geometry_cpu.py', 'scut_ballistic_reference_uninstalled.py'):
        assert H(D / name) == H(T / 'H1_step270_native32_V4_payload' / name)
    assert H(D / 'h1_step270_fullstate_checkpoint_candidate_uninstalled.py') == H(T / 'H1_step270_full20k_native180_V3_delta/h1_step270_fullstate_checkpoint_candidate_uninstalled.py')
    worker = (D / 'h1_step270_production_worker_v1.py').read_text('utf8')
    for path in D.glob('*.py'):
        compile(path.read_text('utf8'), str(path), 'exec')
    # Verify the existing entry resolves the actual patched factory and checkpoint API.
    entry = (RT / 'train_H1_ground_prelaunch_fullstate_v2.py').read_text('utf8')
    entry_main = ast.unparse(fn(entry, 'main'))
    assert "env = build_env()" in entry_main
    assert 'from h1_fullstate_checkpoint_v1 import resume_h1_new_episode' in entry_main
    assert 'from h1_fullstate_checkpoint_v1 import install_h1_save_contract' in entry_main
    assert 'from rescue_training import learn as bounded_learn' in entry_main
    factory = ast.unparse(fn(entry, 'build_env'))
    assert 'configure_h1_rewards(cfg)' in factory and 'Mod4Env(cfg=cfg)' in factory
    assert "ns['main'].__globals__['build_env'] = build_step270" in ast.unparse(ast.parse(worker))
    assert 'checkpoint_API.resume_h1_new_episode = resume_step270_new_episode' in ast.unparse(ast.parse(worker))
    assert 'checkpoint_API.install_h1_save_contract = install_step270_save_contract' in ast.unparse(ast.parse(worker))
    old_worker = (OLD / 'h1_prelaunch_v2_production_worker_v1.py').read_text('utf8')
    # Protected update/save/log loop is unchanged except the source Adam comes from the task.
    old_learn = ast.unparse(fn(old_worker, 'learn'))
    new_learn = ast.unparse(fn(worker, 'learn'))
    old_learn = old_learn.replace('673900', "task['source_Adamstep']").replace('all17Adam673900=True', 'all17Adam_source_literal_inherited=True')
    assert ast.dump(ast.parse(old_learn)) == ast.dump(ast.parse(new_learn))
    assert ast.dump(fn(old_worker, 'H')) == ast.dump(fn(worker, 'H'))
    assert 'actual_H1_step270_scope_admitted' in worker and "not go['actual_H1_prelaunch_v2_scope_admitted']" in worker
    assert "RM_KEEP_STD='1'" in worker and "RM_JUMP_SCRIPT_PROB='0'" in worker
    assert "runner.alg.__class__.__module__=='owned_h1_public4_mean_overflow_ppo_v2'" in worker
    assert 'env.physics_dt==.0025' in worker and 'env.step_dt==.01' in worker
    controllers = T / 'controllers_candidate_v2_uninstalled'
    current = T / 'E3_bridge_continuation_V5/two_policy50_original_account_controllers'
    for name in ('three_slot_common_v1.py', 'three_slot_finite_owner_v1.py', 'three_slot_finite_node_v1.py',
                 'three_real_gpu_resource_v1.py'):
        ast.parse((controllers / name).read_text('utf8'))
    a = (controllers / 'three_slot_common_v1.py').read_text('utf8')
    b = (current / 'three_slot_common_v1.py').read_text('utf8')
    for name in ('charge_values', 'authenticated_row', 'terminal', 'validate_payload', 'environment', 'spawn'):
        assert ast.dump(fn(a, name)) == ast.dump(fn(b, name)), name
    owner = (controllers / 'three_slot_finite_owner_v1.py').read_text('utf8')
    old_owner = (current / 'three_slot_finite_owner_v1.py').read_text('utf8')
    assert ast.dump(fn(owner, 'account')) == ast.dump(fn(old_owner, 'account'))
    assert "sum(b.CAPS[k] for k in specs)+9400.860692501068+512+64800" in owner
    assert "c['authorized_training_seconds']==1548000" in owner and "len(c['budget_extensions'])==8" in owner
    assert "set(specs)=={'h1','recovery'}" in owner and "cfg['deferred_experts']==['e2']" in owner
    # Exercise the same original RSL/PPO import and full 17-state optimizer on a disposable CPU copy.
    # Synthetic observations/rewards test API wiring, not task performance or trained source.
    sys.path.insert(0, str(RT))
    from tensordict import TensorDict
    from rsl_rl.models import MLPModel
    from rsl_rl.storage import RolloutStorage
    from owned_h1_public4_mean_overflow_ppo_v2 import PPO
    source_info = json.loads((R / 'STEP270_20K_EXPLICIT_FULLSTATE_MIGRATION_CPU_REFERENCE_ACTUAL.json').read_bytes())['source']
    source = Path(source_info['path'])
    assert source.is_file() and source.stat().st_size == source_info['bytes']
    ck = torch.load(source, map_location='cpu', weights_only=False)
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(20260928)
        policy = torch.zeros(128, 35)
        policy[:, 28] = 1.
        policy[64:, 28] = 0.
        policy[64:, 32] = 1.
        obs = TensorDict(dict(policy=policy, critic=torch.zeros(128, 38)), batch_size=[128])
        groups = dict(actor=['policy'], critic=['critic'])
        actor = MLPModel(obs, groups, 'actor', 6, [256, 128, 64], 'elu',
                         distribution_cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',
                                               init_std=.3, std_type='scalar'))
        critic = MLPModel(obs, groups, 'critic', 1, [256, 128, 64], 'elu')
        storage = RolloutStorage('rl', 128, 24, obs, [6], device='cpu')
        alg = PPO(actor, critic, storage, num_learning_epochs=5, num_mini_batches=4,
                  learning_rate=.0001, schedule='adaptive', desired_kl=.01,
                  value_loss_coef=2., entropy_coef=.005, gamma=.99, lam=.95, device='cpu')
        actor.load_state_dict(ck['actor_state_dict'])
        critic.load_state_dict(ck['critic_state_dict'])
        alg.optimizer.load_state_dict(copy.deepcopy(ck['optimizer_state_dict']))
        assert torch.equal(actor.distribution.std_param, ck['actor_state_dict']['distribution.std_param'])
        assert len(alg.optimizer.state) == 17
        assert {int(x['step']) for x in alg.optimizer.state.values()} == {674740}
        saved_lr = alg.optimizer.param_groups[0]['lr']
        for i in range(24):
            with torch.no_grad():
                actions = alg.act(obs)
                reward = torch.linspace(-.02, .02, 128) + .001 * i
                alg.process_env_step(obs, reward, torch.zeros(128, dtype=torch.long), {})
        with torch.no_grad():
            alg.compute_returns(obs)
        loss = alg.update()
        assert {int(x['step']) for x in alg.optimizer.state.values()} == {674760}
        assert len(actor.state_dict()) == 9 and len(critic.state_dict()) == 8
        assert all(torch.isfinite(x).all() for x in (*actor.state_dict().values(), *critic.state_dict().values()))
        assert all(torch.isfinite(torch.tensor(x)) for x in loss.values())
        fixture = dict(RSL_version=importlib.metadata.version('rsl-rl-lib'), torch_version=torch.__version__,
                       num_envs=128, controls=24, synthetic_CPU_updates=1, Adam_before=674740, Adam_after=674760,
                       actual_17_optimizer_states=True, six_source_STD_loaded_literal_exact=True,
                       source_optimizer_saved_LR=saved_lr, configured_initial_LR=.0001,
                       losses={k:float(v) for k,v in loss.items()},
                       not_scene_rollout_not_skill_not_production_source=True)
        del actor, critic, alg, storage
    assert torch.equal(torch.get_rng_state(), initial_rng) and not torch.cuda.is_initialized()
    report = dict(epoch=time.time(), passed_independent_whole_production_source_and_RSL_CPU=True,
                  passed_existing_actual_SDK_math_scene_and_fullstate_proofs_reused=True,
                  source_SHA=core['source_SHA'], source_Adam=674740,
                  actual_native_controls=180, callbacks=720, num_envs=20000,
                  matched_native_runtime_asset_files=len(runtime_match),
                  original_RSL_PPO_CPU_fixture=fixture,
                  protected_original_learn_log_save_stop_AST_exact_with_dynamic_Adam=True,
                  controller_charge_account_auth_and_resource_AST_exact=True,
                  selected_h1_recovery_reserve_seconds=7800,
                  original_1548000_8extensions_safety_and_legacy_retained=True,
                  candidate_sources=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(D.glob('*.py'))],
                  reused_proofs=[dict(path=str(R/n),bytes=(R/n).stat().st_size,SHA=H(R/n)) for n in proof_names],
                  no_new_GPU_native_or_query_or_PPO_environment=False,
                  synthetic_CPU_update_only_not_H1_actual_GO=True,
                  no_H1_production_installed_or_admitted_by_this_report_alone=True,
                  remaining='Bind complete source manifest and existing native/query admission loader, validate installed source SDK/RSL/math CPU and fresh resource/canonical/all-out at a new unused root.')
    report['no_new_GPU_native_or_query_or_PPO_environment'] = True
    put('STEP270_PRODUCTION_WHOLE_SOURCE_AND_RSL_CPU_ACTUAL.json', report)
    print(json.dumps(dict(passed=True, RSL_CPU_API_Adam674740_to674760_disposable_only=True,
                          actual_H1_GO=False, actual_native_and_query_reused=True)))

if __name__ == '__main__':
    try:
        main()
    except BaseException:
        put('STEP270_PRODUCTION_WHOLE_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',
            dict(epoch=time.time(), error=traceback.format_exc(), no_GPU_replay_or_actual_H1_GO=True))
        raise
