"""New recovery native336 and finite independent PPO, preserving full states and prefixes."""
from pathlib import Path
import argparse, os, sys, time, json, hashlib, traceback, runpy, shutil
B = Path(__file__).resolve().parent
J = B / 'job0'
OUT = None

def H(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(p, v):
    p = Path(p)
    q = p.with_suffix(p.suffix + '.partial')
    q.write_text(json.dumps(v, indent=2))
    q.replace(p)

def main():
    global OUT
    p = argparse.ArgumentParser()
    p.add_argument('--job', type=int, default=0)
    p.add_argument('--phase', choices=['native', 'production'], required=True)
    a = p.parse_args()
    native = a.phase == 'native'
    OUT = J / ('clock_native50' if native else a.phase)
    OUT.mkdir()
    task = json.loads((J / 'TASK.json').read_bytes())
    src = J / 'source/RECOVERY_auto_source.pt'
    assert H(src) == task['source_SHA']
    assert task['policy_clock_migration_authorized'] is True and task['source_policy_hz'] in (50, 100)
    os.environ['MOD4_RESUME_QUEUE_CONTROL_US'] = str(1000000 // task['source_policy_hz'])
    for k in list(os.environ):
        if k.startswith('RM_') or k in ('RANK', 'WORLD_SIZE', 'LOCAL_RANK', 'MASTER_ADDR', 'MASTER_PORT'):
            del os.environ[k]
    old = json.loads((J / 'original_run_manifest.json').read_bytes())['env']
    os.environ.update({k: str(v) for k, v in old.items() if k not in ('RM_RESCUE_DEADLINE', 'RM_RESCUE_STOP_FILE', 'RM_SLOPE_INITIAL_ADMISSION')})
    os.environ.update(RM_MOD4_USD=str(J / 'assets/robot.usd'), RM_MOD4_TERRAIN='flat', RM_MOD4_MAP='', RM_JUMP_SCRIPT_PROB='0', RM_RESCUE_STOP_FILE=str(OUT / 'STOP_AFTER_SAVE.json'), OWN_E2_H1_KIND='E3_PUBLIC_RECOVERY')
    assert int(old.get('RM_SPAWN_GRACE_STEPS', '10')) == 10
    os.environ['RM_SPAWN_GRACE_STEPS'] = '5'
    sys.path[:0] = [str(B / 'lib'), str(J / 'runtime/isaac/mod4')]
    entry = J / 'runtime/isaac/mod4/train_E3_fullstate_v1.py'
    sys.argv = [str(entry), '--headless', '--device', 'cuda:0', '--num_envs', '20000', '--seed', '20260928', '--steps_per_env', '24', '--learning_rate', '.0001', '--save_interval', '25', '--init_checkpoint', str(src), '--log_root', str(OUT / 'logs'), '--run_name', 'E3_' + a.phase, '--additional_iterations', '100000']
    ns = runpy.run_path(str(entry), run_name='owned_E3_config')
    import torch, numpy as np, rescue_training
    from spring_pressure_checkpoint import exact

    class SavedStop(Exception):
        pass

    def work(runner, n, log_dir):
        from mixed_precision_step_benchmark_runtime_v7 import run as run_precision_benchmark
        run_precision_benchmark(runner, src, task, json.loads((B / 'GO_PRODUCTION.json').read_bytes()) if 'recovery' == 'h1' else json.loads((J / 'GO_PRODUCTION.json').read_bytes()), OUT, 'recovery')
        receipt = json.loads((OUT / 'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json').read_bytes())
        assert receipt['suite_execution_complete'] and receipt['not_a_qualified_continuation_source']
        put(OUT / 'FINAL.json', dict(epoch=time.time(), passed=True, benchmark_execution_receipt_only=True, benchmark_result_path=str(OUT / 'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json'), final=None, not_a_training_FINAL_model=True, not_a_qualified_continuation_source=True, not_270mm_or_recovery_skill_pass=True))
    rescue_training.learn = work
    try:
        ns['main']()
    except BaseException:
        put(OUT / 'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json', dict(epoch=time.time(), error=traceback.format_exc()))
        raise
    finally:
        put(OUT / 'APP_CLOSING.json', dict(epoch=time.time()))
        ns['app'].close()
if __name__ == '__main__':
    try:
        main()
    except BaseException:
        if OUT and OUT.exists():
            put(OUT / 'WORKER_ORIGINAL_ERROR.json', dict(epoch=time.time(), error=traceback.format_exc(), no_automatic_retry=True))
        raise
