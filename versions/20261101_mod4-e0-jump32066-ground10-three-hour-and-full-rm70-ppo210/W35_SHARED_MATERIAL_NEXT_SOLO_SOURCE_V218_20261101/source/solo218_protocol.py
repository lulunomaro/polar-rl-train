"""W35-only one-hour protocol for the original owner template. No ledger I/O.

Root derives a NEW owner/node namespace: replace only protocol import, role-set,
Ready filename and human-readable task label; preserve original HMAC, fcntl,
charge, authority-budget admission, STOP/save/close/wait logic byte-for-byte.
"""
from contract218 import (KIND, SHA, ITER, ADAM, GPUS, GENERATION, OLD_CPU_SHA,
                         validate_ready as _ready, owner_ready_sha)


def validate_schedule(cfg):
    assert set(cfg['experts']) == {'w35_72'} and cfg['deferred_experts'] == []
    spec = cfg['experts']['w35_72']
    assert spec['key'] == 'w35_72' and spec['execution_backend'] == 'target72'
    assert spec['GPU_UUID'] in GPUS and spec['num_envs'] == 20000
    assert spec['source_SHA'] == SHA and spec['source_iteration'] == ITER
    assert spec['source_Adamstep'] == ADAM and spec['source_kind'] == KIND
    assert spec['max_parent_seconds'] == 3900 and spec['exit_headroom_seconds'] == 300
    assert spec['no_physics_change'] and spec['prelaunch_control_snapshot_id']
    assert len(spec['manifest_SHA']) == 64 and len(spec['launch_evidence_SHA']) == 64
    return True


def valid_ready(row, spec):
    closed = row.get('closed_source_CPU') or {}
    value = closed.get('value') or {}
    return bool(row.get('key') == 'w35_72' and row.get('phase') == 'ready' and
        row.get('manifest_SHA') == spec['manifest_SHA'] and not row.get('original_error') and
        closed.get('SHA') == owner_ready_sha(value) and
        closed.get('actual_CPU_waited_EXIT0') is True and _ready(value, spec))


def flat_go_fields(spec):
    return dict(role_key='w35_72', GPU_UUID=spec['GPU_UUID'], authority_generation=GENERATION,
        source_qualification_kind=KIND, source_model_SHA=SHA, source_iteration=ITER,
        input_Adam=ADAM, actor_obs=35, critic_obs=38, action_dim=6, num_envs=20000,
        preserve_learned_STD=True, physics_dt=.0025, TGS=[32, 4], policy_hz=50,
        feedback_hz=100, nominal_gas_k_N_m=2000, discount_gamma=.9801, discount_lam=.9025,
        one_original_writer=True, full_actor_critic_STD_17Adam_restore_required=True,
        explicit_fresh_physics_replay_history=True, genuine_W35_full_original_RM70_course=True,
        launch_evidence_SHA=spec['launch_evidence_SHA'],
        prelaunch_control_snapshot_id=spec['prelaunch_control_snapshot_id'],
        source_saved_fullstate_CPU_SHA=OLD_CPU_SHA,
        not_a_native_SuperMimic_conversion=True, no_success_claim=True)
