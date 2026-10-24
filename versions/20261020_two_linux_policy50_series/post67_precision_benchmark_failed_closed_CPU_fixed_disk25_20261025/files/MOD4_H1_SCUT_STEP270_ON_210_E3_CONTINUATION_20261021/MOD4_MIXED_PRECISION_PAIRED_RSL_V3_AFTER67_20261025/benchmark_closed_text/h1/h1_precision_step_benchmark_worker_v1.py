"""Prepared only: requires a new actual original-owner GO and admitted native source.

Never launches a native case or learns without the exact bounded H1 grant.
"""
from pathlib import Path
import os, sys, argparse, json, time, hashlib, traceback, runpy
B = Path(__file__).resolve().parent
J = B / 'job0'

def H(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(p, v):
    p = Path(p)
    q = p.with_suffix(p.suffix + '.partial')
    q.write_text(json.dumps(v, indent=2))
    q.replace(p)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--phase', choices=('production',), required=True)
    args = p.parse_args()
    phase = args.phase
    task = json.loads((J / 'TASK.json').read_bytes())
    go = json.loads((B / ('GO_' + phase.upper() + '.json')).read_bytes())
    assert go['actual_H1_step270_scope_admitted'] and (not go['actual_H1_prelaunch_v2_scope_admitted']) and (go['max_parent_seconds'] == 3900) and (go['exit_headroom_seconds'] == 300) and (go['save_deadline'] < go['nominal_end_epoch'])
    assert time.time() < go['save_deadline']
    assert go['source_SHA'] == task['source_SHA']
    src = J / 'source' / task['source_filename']
    assert H(src) == go['source_SHA']
    assert not (J / phase).exists()
    out = J / phase
    out.mkdir()
    fresh = phase == 'precheck128'
    N = 128 if fresh else 20000
    for k in list(os.environ):
        if k.startswith('RM_') or k in ('RANK', 'LOCAL_RANK', 'WORLD_SIZE', 'MASTER_ADDR', 'MASTER_PORT'):
            del os.environ[k]
    original = json.loads((J / 'original_run_manifest.json').read_bytes())['env']
    os.environ.update({k: str(v) for k, v in original.items() if k not in ('RM_RESCUE_DEADLINE', 'RM_RESCUE_STOP_FILE', 'RM_SLOPE_INITIAL_ADMISSION')})
    os.environ.update(RM_MOD4_USD=str(J / 'assets/robot.usd'), RM_MOD4_TERRAIN='flat', RM_MOD4_MAP='', RM_JUMP_SCRIPT_PROB='0', RM_KEEP_STD='1', RM_RESCUE_STOP_FILE=str(out / 'STOP_AFTER_SAVE.json'), OWN_E2_H1_KIND=task['kind'])
    sys.path[:0] = [str(B / 'lib'), str(J / 'runtime/isaac/mod4')]
    entry = J / 'runtime/isaac/mod4' / ('train_H1_fresh128_preflight_v1.py' if fresh else 'train_H1_ground_prelaunch_fullstate_v2.py')
    sys.argv = [str(entry), '--headless', '--device', 'cuda:0', '--num_envs', str(N), '--seed', '20260928', '--steps_per_env', '24', '--learning_rate', '.0001', '--save_interval', '25', '--init_checkpoint', str(src), '--log_root', str(out / 'logs'), '--run_name', 'H1_STEP270_SCUT_' + phase, '--additional_iterations', '100000']
    ns = runpy.run_path(str(entry), run_name='owned_H1_learner_config')
    import h1_scut_fudan_jump_reward_v1 as scut
    import h1_step270_sdk_runtime_candidate as terrain
    original_rewards = scut.configure
    scut.configure = lambda cfg: terrain.configure_rewards(cfg, original_rewards)
    factory = ns['build_env']
    original_cfg = ns['Mod4EnvCfg']
    created = [None]

    def step270_cfg():
        c = original_cfg()
        assert c.scene.num_envs == 20000 or N == 20000
        c.scene.num_envs = 20000
        c.seed = 20260928
        c.sim.device = 'cuda:0'
        assert float(c.terminations.closure.params['threshold']) == 0.002 and float(c.terminations.mimic.params['threshold']) >= 0.01
        c.terminations.mimic.params = {**c.terminations.mimic.params, 'threshold': 0.01}
        return c
    factory.__globals__.update(Mod4Env=terrain.H1Step270Env, Mod4EnvCfg=step270_cfg)

    def build_step270():
        env = factory()
        created[0] = env
        env._physics_action_delay.queue.control_us = 10000
        assert env.num_envs == 20000 and env.physics_dt == 0.0025 and (env.step_dt == 0.01) and (env.cfg.decimation == 4)
        return env
    ns['main'].__globals__['build_env'] = build_step270
    import h1_fullstate_checkpoint_v1 as checkpoint_API
    from h1_step270_fullstate_checkpoint_candidate_uninstalled import resume_step270_new_episode, install_step270_save_contract
    checkpoint_API.resume_h1_new_episode = resume_step270_new_episode
    checkpoint_API.install_h1_save_contract = install_step270_save_contract
    import torch, rescue_training
    from spring_pressure_checkpoint import exact
    from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe

    class OwnSavedStop(Exception):
        pass

    def learn(runner, n, log_dir):
        from mixed_precision_step_benchmark_runtime_v7 import run as run_precision_benchmark
        run_precision_benchmark(runner, src, task, json.loads((B / 'GO_PRODUCTION.json').read_bytes()) if 'h1' == 'h1' else json.loads((J / 'GO_PRODUCTION.json').read_bytes()), out, 'h1')
        receipt = json.loads((out / 'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json').read_bytes())
        assert receipt['suite_execution_complete'] and receipt['not_a_qualified_continuation_source']
        put(out / 'FINAL.json', dict(epoch=time.time(), passed=True, benchmark_execution_receipt_only=True, benchmark_result_path=str(out / 'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json'), final=None, not_a_training_FINAL_model=True, not_a_qualified_continuation_source=True, not_270mm_or_recovery_skill_pass=True))
    rescue_training.learn = learn
    try:
        ns['main']()
    except BaseException:
        put(out / 'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json', dict(epoch=time.time(), error=traceback.format_exc(), no_auto_retry=True))
        raise
    finally:
        if created[0] is not None:
            try:
                created[0].close()
            except BaseException:
                put(out / 'ENV_CLOSE_ORIGINAL_ERROR.json', dict(epoch=time.time(), error=traceback.format_exc()))
        put(out / 'APP_CLOSING.json', dict(epoch=time.time()))
        ns['app'].close()
if __name__ == '__main__':
    try:
        main()
    except BaseException:
        try:
            put(B / ('H1_PHASE_ORIGINAL_ERROR_' + str(time.time_ns()) + '.json'), dict(epoch=time.time(), error=traceback.format_exc(), no_retry=True))
        except BaseException:
            pass
        raise
