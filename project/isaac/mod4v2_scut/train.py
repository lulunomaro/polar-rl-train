"""Fresh SCUT PPO on released MOD4v2; reuse the complete finite save/eval lifecycle."""
import os
from pathlib import Path
import sys
from .shared import load, export
_source = load('train')
export(_source, globals())


def boot(args, job):
    _source.environment_settings(args)
    runtime = Path(args.runtime).resolve()
    sys.path[:0] = [str(runtime), *args.support, str(runtime.parents[1])]
    storage = job / 'kit_isolation'
    (storage / 'data').mkdir(parents=True)
    (storage / 'DerivedDataCache').mkdir()
    (storage / 'data/user.config.json').write_text('{}')
    os.environ.update(MOD4V1_E0_ASSET_DIR=str(args.assets), MOD4V1_E0_JOB_ROOT=str(job),
                      MOD4V1_E0_KIT_STORAGE_ROOT=str(storage))
    from .hardware import adapter
    preparation = adapter().prepare_environment(opt_in=True)
    guard = _source.load_guard(args.guard)
    identity = guard.bind_before_task_import(args.assets)
    from launcher_mod4v1_e0 import IsolatedAppLauncher208
    launcher = IsolatedAppLauncher208(headless=True, device=args.device,
                                     enable_cameras=False, livestream=0)
    _source.put(job / 'MOD4V2_PREIMPORT_BINDING.json', preparation)
    return dict(app=launcher.app, E0_IDENTITY=identity)


_source.boot = boot


def build_runner(vec, directory):
    runner = _original_build_runner(vec, directory)
    if runner.current_learning_iteration != 0 or runner.alg.optimizer.state:
        raise ValueError('Fresh v2 run unexpectedly contains prior learner state')
    put(Path(directory) / 'FRESH_INITIALIZATION.json', dict(
        initialization='fresh_random_SCUT_actor_critic_STD_and_Adam',
        initial_iteration=0, optimizer_entries=0, checkpoint_reads=0,
        v1_policy_loaded=False, physics_restored=False))
    return runner


_original_build_runner = _source.build_runner
_source.build_runner = build_runner


if __name__ == '__main__':
    _source.main()
