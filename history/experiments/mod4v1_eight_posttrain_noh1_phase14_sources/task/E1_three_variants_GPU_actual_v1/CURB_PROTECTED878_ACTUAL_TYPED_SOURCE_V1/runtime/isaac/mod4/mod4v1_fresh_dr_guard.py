"""Sidecar guard for a NEW mod4v1 task, never an old-task/checkpoint patch.

No checkpoint/PT I/O, optimizer calls, random draws, physics steps or physical setters.
Torch and the ORIGINAL mild_dr.tensor converter are injected at runtime.
The old D0-D7 restore path remains authoritative and must reset exactly once.
"""
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import sys

USD_SHA256 = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
CONTRACT_SHA256 = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'


class AssetMigrationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise AssetMigrationError(message)


@dataclass(frozen=True)
class AssetIdentity:
    usd_path: str
    contract_path: str
    usd_sha256: str
    contract_sha256: str
    contract: dict


def read_asset_identity(asset_dir):
    """Hash only the declared new USD root and JSON contract, not any PT."""
    folder = Path(asset_dir).resolve()
    usd, contract_file = folder / 'robot.usd', folder / 'import_contract.json'
    raw_usd, raw_contract = usd.read_bytes(), contract_file.read_bytes()
    uh, ch = hashlib.sha256(raw_usd).hexdigest(), hashlib.sha256(raw_contract).hexdigest()
    require(uh == USD_SHA256, 'New-task USD root SHA mismatch')
    require(ch == CONTRACT_SHA256, 'New-task import contract SHA mismatch')
    contract = json.loads(raw_contract)
    require(len(contract['bodies']) == 31, 'Expected unchanged 31-body structure')
    require(contract['leg_motor']['mass_each_kg'] == .963, 'Wrong leg motor mass metadata')
    require(contract['wheel_motor']['bare_motor_mass_assumption_kg'] == .131,
            'Wrong user-weighed retained bare motor metadata')
    for gas in contract['gas_springs'].values():
        require(gas['stiffness_n_m'] == 2000. and gas['damping_n_s_m'] == 3.,
                '400N/k2000/damping3 nominal contract must remain unchanged')
    return AssetIdentity(str(usd), str(contract_file), uh, ch, contract)


def bind_before_task_import(asset_dir):
    """Call AFTER the new worker clears/restores RM_* and BEFORE task imports."""
    identity = read_asset_identity(asset_dir)
    existing = sys.modules.get('mod4_task')
    if existing is not None:
        verify_task_module(existing, identity)
    os.environ['RM_MOD4_USD'] = identity.usd_path
    return identity


def verify_task_module(task_module, identity):
    """Do not silently reload a task module already bound to the old contract."""
    require(Path(task_module.USD_PATH).resolve() == Path(identity.usd_path),
            'mod4_task was imported with a different USD; use a fresh task process')
    require(task_module.CONTRACT == identity.contract,
            'Imported mod4_task.CONTRACT differs from the pinned new JSON')


def configure_new_task(cfg, identity):
    """Only new cfg: point to v1 and use 10mm episode closure, keep mimic .01rad."""
    require(cfg.terminations.mimic.params['threshold'] == .01,
            'Original mimic threshold must already be .01rad')
    cfg.scene.robot.spawn.usd_path = identity.usd_path
    cfg.terminations.closure.params['threshold'] = .01
    return cfg


class FreshDRNominalGuard:
    """Capture NEW constructor nominals before runner.load / fullstate restore.

    Existing source captures D0 absolute references in MildDR.__init__, not in PT.
    D7 load_state_dict restores delta/RNG against its constructor original_pose.
    A stale baseline overwrite is therefore an ERROR, not a reason to guess
    fields, edit the selected checkpoint, or write inferred physical parameters.
    """
    def __init__(self, env, identity, *, torch_module, tensor_converter):
        self.env, self.identity = env, identity
        self.torch, self.tensor = torch_module, tensor_converter
        self.robot = env.scene['robot']
        self.dr, self.com = env._mild_dr, env._chassis_com
        self.n = env.num_envs
        self.names = tuple(self.robot.body_names)
        require(len(self.names) == 31 and len(set(self.names)) == 31,
                'Expected 31 unique bodies in actual runtime order')
        require(set(self.names) == set(identity.contract['bodies']), 'Body-name/schema mismatch')
        require(int(env._sim_step_counter) == 0, 'Attach before the first physics step')
        require(Path(env.cfg.scene.robot.spawn.usd_path).resolve() == Path(identity.usd_path),
                'Actual constructed cfg is not bound to the new USD root')
        require(env.cfg.terminations.closure.params['threshold'] == .01,
                'NEW task must use 10mm per-episode closure reset')
        require(env.cfg.terminations.mimic.params['threshold'] == .01,
                'Mimic must remain .01rad')
        self.saved = {key: self._clone(value) for key, value in self._baselines().items()}
        shapes = {'D0.mass': (self.n, 31), 'D0.inertia': (self.n, 31, 9),
                  'D0.com': (self.n, 31, 3), 'D7.original_pose': (self.n, 31, 7)}
        for key, value in self.saved.items():
            require(tuple(value.shape) == shapes[key], 'Unsupported runtime shape: ' + key)
            require(bool(self.torch.isfinite(value).all()), 'Nonfinite new nominal: ' + key)
        self._verify_constructor_contract()
        self.reset_calls = 0
        self.parameter_readback = None
        self.observation_shapes_checked = False
        self.restore_completed = False
        self._inside = False

    def _clone(self, value):
        return self.tensor(value).detach().clone()

    def _baselines(self):
        # EXACT names from pinned MildDR / ChassisCOMSDK. No invented defaults.
        return {'D0.mass': self.dr.mass, 'D0.inertia': self.dr.inertia,
                'D0.com': self.dr.com, 'D7.original_pose': self.com.original_pose}

    def _like(self, data, reference):
        return self.torch.as_tensor(data, device=reference.device, dtype=reference.dtype)

    def _verify_constructor_contract(self):
        bodies = self.identity.contract['bodies']
        mass, com = self.saved['D0.mass'], self.saved['D0.com']
        expected_mass = self._like([bodies[n]['mass_kg'] for n in self.names], mass)
        expected_com = self._like([bodies[n]['com_m'] for n in self.names], com)
        require(self.torch.allclose(mass, expected_mass[None, :], rtol=1.e-5, atol=1.e-8),
                'Constructor MildDR nominal mass does not match v1 contract')
        require(self.torch.allclose(com, expected_com[None, :, :], rtol=0., atol=1.e-6),
                'Constructor MildDR nominal COM does not match v1 contract')
        require(self.torch.equal(com, self.saved['D7.original_pose'][..., :3]),
                'D0 and D7 constructor nominal COM translations disagree')
        # Raw SDK inertia is captured from this NEW constructor and protected
        # below. Do not invent an SDF principal-axis -> SDK-frame conversion or
        # a new spectral/precision admission here; parent Native0PT must verify
        # the actual v1 point-delta inertia in the installed SDK representation.

    def assert_new_nominals_unchanged(self):
        require(tuple(self.robot.body_names) == self.names, 'Actual body order changed')
        for key, value in self._baselines().items():
            require(self.torch.equal(self.tensor(value), self.saved[key]),
                    'Fullstate restore overwrote NEW asset nominal cache: ' + key)

    def check_observations(self, observations):
        """Use an ALREADY computed observation; never call observation_manager here."""
        require(tuple(observations['policy'].shape) == (self.n, 35), 'Actor input changed')
        require(tuple(observations['critic'].shape) == (self.n, 38), 'Critic input changed')
        self.observation_shapes_checked = True

    def verify_live_parameters(self):
        """Read only; use existing SDK APIs and original expected-value auditor."""
        self.assert_new_nominals_unchanged()
        mass = self.tensor(self.robot.root_view.get_masses()).to(self.saved['D0.mass'].device)
        inertia = self.tensor(self.robot.root_view.get_inertias()).to(self.saved['D0.inertia'].device)
        expected_mass = self.saved['D0.mass'] * self.dr.factor[:, None]
        expected_inertia = self.saved['D0.inertia'] * self.dr.factor[:, None, None]
        require(self.torch.allclose(mass, expected_mass, rtol=1.e-5, atol=1.e-8),
                'Fresh DR masses are not NEW nominal times current episode factor')
        require(self.torch.allclose(inertia, expected_inertia, rtol=0., atol=1.e-6),
                'Fresh DR inertias are not NEW nominal times current episode factor')
        # This original auditor already incorporates D5 gas, D6 damping and D7
        # COM/PD wrappers. It reads parameters, not actor/compute/clip/physics.
        audit = self.dr.audit()
        require(audit['actual_parameters_pass'] is True, 'Existing parameter audit failed')
        self.assert_new_nominals_unchanged()  # auditors temporarily swap .com then restore it
        self.parameter_readback = audit
        return audit

    @contextmanager
    def around_original_fullstate_restore(self):
        """Wrap the original ONE fresh env.reset; do not add a second reset.

        Enter before runner.load if desired, or immediately before the original
        resume helper; do not step physics until the context exits successfully.
        """
        require(not self._inside and self.reset_calls == 0, 'Guard is one-use per new scene')
        original_reset = self.env.reset
        self._inside = True
        guard = self

        def guarded_reset(*args, **kwargs):
            require(guard.reset_calls == 0, 'Original restore attempted more than one env.reset')
            guard.assert_new_nominals_unchanged()
            result = original_reset(*args, **kwargs)
            guard.reset_calls += 1
            guard.verify_live_parameters()
            return result

        self.env.reset = guarded_reset
        try:
            yield self
            require(self.reset_calls == 1, 'Original fullstate restore did not do its ONE fresh reset')
            require(int(self.env._sim_step_counter) == 0, 'Physics stepped inside restore scope')
            self.verify_live_parameters()
            self.restore_completed = True
        finally:
            self.env.reset = original_reset
            self._inside = False

    def receipt(self):
        require(self.restore_completed and self.reset_calls == 1 and self.parameter_readback is not None,
                'No completed original fresh-episode reset/readback')
        return {'kind': 'MOD4V1_NEW_NOMINAL_RESTORE_GUARD',
                'usd_sha256': self.identity.usd_sha256,
                'contract_sha256': self.identity.contract_sha256,
                'body_names': list(self.names), 'num_envs': self.n,
                'original_fresh_reset_calls': self.reset_calls,
                'new_constructor_nominal_caches_preserved': True,
                'fresh_D0_mass_inertia_based_on_new_asset': True,
                'expected_interface': {'actor_obs': 35, 'critic_obs': 38, 'actions': 6},
                'observation_shapes_checked': self.observation_shapes_checked,
                'SDK_inertia_frame_conversion_or_new_spectral_gate': False,
                'target_native0PT_inertia_birth_check_still_required': True,
                'closure_episode_m': .01, 'mimic_rad': .01,
                'extra_physics_steps': 0, 'actor_calls': 0, 'optimizer_calls': 0,
                'checkpoint_reads': 0, 'random_draws_by_hook': 0,
                'physical_parameter_setters_by_hook': 0,
                'hardware_full_DR_coverage_proven': False,
                'skill_or_training_adaptation_passed': False}
