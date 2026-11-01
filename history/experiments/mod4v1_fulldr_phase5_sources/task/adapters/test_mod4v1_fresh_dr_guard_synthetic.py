"""Synthetic NumPy-backed API doubles only: no Torch/SDK/PT/physics/SSH/file writes."""
import argparse
import copy
import json
from types import SimpleNamespace as NS
import numpy as np
from mod4v1_fresh_dr_guard import (
    AssetMigrationError, FreshDRNominalGuard, configure_new_task,
    read_asset_identity, verify_task_module,
)


class T(np.ndarray):
    def __new__(cls, value, dtype=None):
        return np.asarray(value, dtype=dtype).view(cls)

    @property
    def device(self):
        return 'cpu'

    def detach(self):
        return self

    def clone(self):
        return self.copy().view(T)

    def to(self, *args, **kwargs):
        return self


NP_TORCH = NS(as_tensor=lambda x, device=None, dtype=None: T(x, dtype),
              equal=np.array_equal, allclose=np.allclose, isfinite=np.isfinite,
              linalg=NS(eigvalsh=np.linalg.eigvalsh))


class FakeEnv:
    def __init__(self, identity):
        self.num_envs = 2
        self._sim_step_counter = 0
        self.reset_count = 0
        names = list(identity.contract['bodies'])
        bodies = identity.contract['bodies']
        m = T([[bodies[n]['mass_kg'] for n in names]] * 2, np.float32)
        c = T([[bodies[n]['com_m'] for n in names]] * 2, np.float32)
        i = T([[np.diag(bodies[n]['diagonal_inertia_kg_m2']).reshape(9)
                for n in names]] * 2, np.float32)
        pose = T(np.zeros((2, 31, 7)), np.float32)
        pose[..., :3] = c
        pose[..., 6] = 1.
        self._mild_dr = NS(mass=m, inertia=i, com=c, factor=T([1., 1.], np.float32))
        self._mild_dr.audit = lambda: {'actual_parameters_pass': True, 'synthetic_only': True}
        self._chassis_com = NS(original_pose=pose)
        self.live_mass, self.live_inertia = m.clone(), i.clone()
        view = NS(get_masses=lambda: self.live_mass, get_inertias=lambda: self.live_inertia)
        self.scene = {'robot': NS(body_names=names, root_view=view)}
        self.cfg = NS(scene=NS(robot=NS(spawn=NS(usd_path=identity.usd_path))),
                      terminations=NS(closure=NS(params={'threshold': .01}),
                                      mimic=NS(params={'threshold': .01})))
        # Sentinels are never exposed to/modified by the production guard.
        self.actor_STD_optimizer_norm = {'actor': 'unchanged', 'STD': 'unchanged',
                                         'Adam17': 'unchanged', 'norm': 'unchanged'}

    def reset(self):
        self.reset_count += 1
        self._mild_dr.factor = T([.95, 1.05], np.float32)
        self.live_mass = self._mild_dr.mass * self._mild_dr.factor[:, None]
        self.live_inertia = self._mild_dr.inertia * self._mild_dr.factor[:, None, None]
        return {'policy': T(np.zeros((2, 35))), 'critic': T(np.zeros((2, 38)))}, {}


def make(env, identity):
    return FreshDRNominalGuard(env, identity, torch_module=NP_TORCH,
                               tensor_converter=lambda x: x)


def raises(fn, text):
    try:
        fn()
    except AssetMigrationError as error:
        assert text in str(error), (text, str(error))
    else:
        raise AssertionError('Expected guarded rejection: ' + text)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--asset-dir', required=True)
    args = p.parse_args()
    identity = read_asset_identity(args.asset_dir)  # root/JSON hashes only, not stage/model load
    verify_task_module(NS(USD_PATH=identity.usd_path, CONTRACT=identity.contract), identity)
    raises(lambda: verify_task_module(NS(USD_PATH='old_asset.usd', CONTRACT={}), identity),
           'different USD')
    passed = ['pinned_asset_hashes_and_json', 'wrong_imported_asset_detected']

    env = FakeEnv(identity)
    env.cfg.terminations.closure.params['threshold'] = .002
    configure_new_task(env.cfg, identity)
    assert env.cfg.terminations.closure.params['threshold'] == .01
    assert env.cfg.terminations.mimic.params['threshold'] == .01
    before = copy.deepcopy(env.actor_STD_optimizer_norm)
    guard = make(env, identity)
    original_reset = env.reset
    with guard.around_original_fullstate_restore():
        observation, _ = env.reset()
        guard.check_observations(observation)
    assert env.reset == original_reset and env.reset_count == 1
    assert before == env.actor_STD_optimizer_norm
    assert guard.receipt()['physical_parameter_setters_by_hook'] == 0
    passed += ['new_cfg_10mm_mimic_unchanged', 'one_reset_preserved',
               'new_nominal_times_episode_factor', 'interface35_38',
               'core_STD_Adam_norm_sentinels_untouched', 'reset_method_restored']

    for field in ('mass', 'inertia', 'com'):
        env = FakeEnv(identity)
        guard = make(env, identity)
        def corrupt_then_reset(field=field, env=env, guard=guard):
            with guard.around_original_fullstate_restore():
                getattr(env._mild_dr, field).flat[0] += .01
                env.reset()
        raises(corrupt_then_reset, 'overwrote NEW asset nominal cache')
        assert env.reset_count == 0
        passed.append('old_absolute_' + field + '_overwrite_blocked_before_reset')

    env = FakeEnv(identity)
    guard = make(env, identity)
    def corrupt_d7():
        with guard.around_original_fullstate_restore():
            env._chassis_com.original_pose[0, 0, 0] += .01
            env.reset()
    raises(corrupt_d7, 'D7.original_pose')
    assert env.reset_count == 0
    passed.append('old_D7_nominal_COM_overwrite_blocked')

    env = FakeEnv(identity)
    guard = make(env, identity)
    def double_reset():
        with guard.around_original_fullstate_restore():
            env.reset()
            env.reset()
    raises(double_reset, 'more than one')
    assert env.reset_count == 1
    passed.append('second_reset_blocked')
    raises(guard.receipt, 'No completed')
    passed.append('failed_restore_cannot_emit_completed_receipt')

    env = FakeEnv(identity)
    guard = make(env, identity)
    def no_reset():
        with guard.around_original_fullstate_restore():
            pass
    raises(no_reset, 'did not do its ONE')
    passed.append('missing_restore_reset_detected')

    env = FakeEnv(identity)
    env._mild_dr.mass[:, env.scene['robot'].body_names.index('chassis')] -= .132
    raises(lambda: make(env, identity), 'nominal mass does not match')
    passed.append('old_constructor_mass_detected')

    # No invented spectral/FP64 SDK-frame gate: actual v1 inertia birth proof
    # is deliberately reserved for the parent's installed target Native0PT.
    print(json.dumps({'passed': True, 'scope': 'SYNTHETIC_API_DOUBLES_ONLY',
                      'checks': passed, 'check_count': len(passed),
                      'SDK_or_PhysX_executed': False, 'PT_opens': 0,
                      'real_model_or_optimizer_executed': False,
                      'new_artifact_files_written_by_test': 0}, indent=2))


if __name__ == '__main__':
    main()
