"""Exact parent control path with a private flat-task frame; not installed."""
import types
import torch
from native_wheel_leg_bridge_v4 import NativeWheelLegBridge
from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY
from native_flat_jump_adapter_v1 import encode_frame, FlatJumpPhase
from flat_real_physics_events_v3_original_support import make_authored_preedge_cached_provider, install_readonly_phase_hook

class FlatWheelLegBridge(NativeWheelLegBridge):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flat_env_ids = torch.arange(self.num_envs, device=self.device, dtype=torch.long)

    def _encode_current_frame(self, state):
        row = state.info[SUPERMIMIC_STATE_KEY]
        # Parent already copied the actual public age. No additional SDK read.
        row['f'] = encode_frame(row['f'], self.flat_env_ids)
        return state

    def init_state(self):
        return self._encode_current_frame(super().init_state())

    def step(self, actions):
        # Parent keeps exact action identity, terminal pre-reset s1, reward(f+1),
        # static selected resets, previous action, errors and final cleanup.
        return self._encode_current_frame(super().step(actions))

def install_flat_real_counter(env,*,height_m):
    phase = env.h1_phase
    original_provider = make_authored_preedge_cached_provider(phase)
    ids = torch.arange(env.num_envs, device=env.device, dtype=torch.long)
    schedule = FlatJumpPhase(height_m=height_m)

    def provider(current, kw):
        row = original_provider(current, kw)
        # Private task requests, not original270 public request100..179.
        row['request'] = schedule.targets(current.age_control, ids)['flight']
        return row

    provider.floor_support_basis = original_provider.floor_support_basis
    counter = install_readonly_phase_hook(phase, provider, height_m=height_m)
    return counter, provider.floor_support_basis

def install_stationary_flat_command(env):
    """Explicit new-course command override, before first control; no action setter.

    Original public modes/request/phase/counters and native physical plant remain.
    An independent audit replaces only the old forward-.8 command assertion for
    this typed flat task. No existing step task file is modified.
    """
    import spin_commands
    from h1_external_operator_command_v1 import H1ExternalOperatorCommand
    from h1_original_directional_runtime import audit as directional_audit
    assert not getattr(env, '_own_flat_stationary_command_installed', False)

    def publish(this):
        if this.h1_phase is not None:
            this._mod4_mode_bit = this.h1_phase.public_mode()
            term = this.command_manager.get_term('twist')
            term.set_manual_evaluation_mode()
            term.vel_command_b.zero_()

    def audit(this):
        result = directional_audit(this)
        term = this.command_manager.get_term('twist')
        assert isinstance(term, H1ExternalOperatorCommand)
        assert torch.equal(term.command, torch.zeros_like(term.command)), 'flat command must be exactly stationary'
        result.update(stage='MOD4_own_flat5cm_stationary_command_v1', flat_task_command_zero=True,
                      original_public_phase_modes_unchanged=True, not_step_forward_command=True)
        return result

    env._h1_publish_external_request = types.MethodType(publish, env)
    spin_commands.audit = audit
    env._own_flat_stationary_command_installed = True
    env._h1_publish_external_request()
    return audit(env)
