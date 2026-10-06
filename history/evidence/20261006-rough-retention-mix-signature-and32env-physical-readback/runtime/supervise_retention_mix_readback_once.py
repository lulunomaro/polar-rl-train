"""One frozen component readback, holding the existing two canonical locks.

This is deliberately not a repair PPO executor. It exits after saving evidence.
"""
import hashlib
import json
import os
import time
import traceback
from pathlib import Path
import supervise_rough_intro_admission_review as c

H, R, P = c.H, c.R, c.P
STATE = R/'RETENTION_COMPONENT_STATE.json'
OLD = Path('/home/egde/rl_candidates/MOD4_ROUGH_INTRO_ADMISSION_REVIEW_20261006')
SOURCE = P/'logs/2026-10-06_05-04-08_auto_0282_physical_dr_stage1_learning_cap12.5664_white_v3/model_23509.pt'
SHA = '2f82374fe07a849dbbaeabbf8dd34b20d0df8da789f2ebc2be3e688a1b24498a'


def phase(name, **extra):
    c.base.atomic_json(STATE, dict(phase=name, epoch=time.time(), ppo_performed=False,
                                repair_executor_deployed=False, **extra))


def main():
    assert not STATE.exists(), 'This named component entry has already executed'
    c.helpers.acquire(P/'autonomy_controller.lock')
    c.helpers.acquire(c.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
    c.ctl.PROBES = tuple(c.ctl.PROBES) + ('/retention_mix_probe.py',)
    c.ctl.idle(); c.verify()
    assert c.w.read(OLD/'reports/ROUGH_INTRO_ADMISSION_STATE.json')['phase'] == 'rough_intro_stage1_review_ready'
    for name in ('ROUGH_INTRO_STARTED.json','ROUGH_INTRO_GUARDIAN_STARTED.json'):
        item = c.w.read(OLD/'reports'/name); saved = item.get('owner', item)
        actual = c.helpers.identity(saved['pid'])
        assert not actual or actual['state'] == 'Z' or actual['start_ticks'] != saved['start_ticks']
    budget = c.base.budget_state()
    assert budget['active_segment'] is None and not c.w.read(c.ctl.STATE_PATH).get('active_training')
    before = c.ctl.CANONICAL.read_bytes()
    info = c.base.checkpoint(SOURCE)
    assert info['sha256'] == SHA and info['finite_tensors'] == 68
    assert c.w.read(R/'CPU_LAYOUT_CONTRACT.json')['pass_']
    owner = c.helpers.identity(os.getpid())
    phase('retention_mixed_component_frozen_readback', owner=owner, source=info,
          budget_sha256=hashlib.sha256(before).hexdigest())
    output = R/'RETENTION_MIX_SDK_READBACK.json'
    child = c.base.spawn([str(c.CODE/'retention_mix_probe.py'), '--headless', '--checkpoint', str(SOURCE),
                         '--output', str(output), '--num_envs','32','--steps','300'], output.with_suffix('.log'))
    phase('retention_mixed_component_frozen_readback', owner=owner, child=c.helpers.identity(child.pid),
          source=info, output=str(output), budget_sha256=hashlib.sha256(before).hexdigest())
    try:
        result = c.base.wait_probe(child, output)
        text = output.with_suffix('.log').read_text(errors='replace')
        errors = [line for line in text.splitlines() if any(key in line for key in (
            'PhysX error:', 'buffer overflow', 'BV4 tree failed', 'Unable to create triangle mesh',
            'simulation will miss interactions', 'CUDA out of memory'))]
        assert not errors, errors[:10]
        assert result['pass_'] and result['steps_completed'] == 300 and result['actual_task_resets'] == 0
        assert [result[k] for k in ('actor_obs_dim','critic_obs_dim','action_dim')] == [35,38,6]
        assert result['initial_parameters']['actual_parameters_pass'] and result['final_parameters']['actual_parameters_pass']
        assert result['physics_callback_ticks'] >= 6000
        assert result['ground_fresh_readback_error'] < 1e-5 and result['height_reward_readback_error'] < 1e-6
        assert any(max(row) > 0 for row in result['mean_world_z_wheel_load_n'])
        assert c.ctl.CANONICAL.read_bytes() == before
        phase('retention_mixed_component_review_ready', owner=owner, source=info, output=str(output),
              component_pass=True, repair_training_started=False, budget_bytes_exact=True,
              budget_operations=0, remaining_s=budget['authorized_training_seconds']-budget['charged_training_seconds'])
    except BaseException:
        phase('retention_mixed_component_rejected', owner=owner, source=info,
              reason=traceback.format_exc(), output=str(output), budget_bytes_exact=c.ctl.CANONICAL.read_bytes()==before)
        raise


if __name__ == '__main__':
    main()
