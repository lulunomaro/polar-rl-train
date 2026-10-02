"""Register once, save the live trainer, commit budget, replace only its supervisor."""
import fcntl
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path('/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001')
CODE = ROOT/'isaac/mod4'
sys.path.insert(0, str(CODE))
import supervise_mild_trial as mild
base = mild.base
IDENTIFIER = 'USER_ADD20H_20261001_2341'
REQUEST = ROOT/'reports'/f'{IDENTIFIER}_REQUEST.json'
APPLIED = ROOT/'reports'/f'{IDENTIFIER}_APPLIED.json'
PROGRESS = ROOT/'reports/BUDGET_EXTENSION20H_PROGRESS.json'


def progress(stage, **kwargs):
    base.atomic_json(PROGRESS, dict(stage=stage, updated_epoch=time.time(), **kwargs))
    print(json.dumps(dict(stage=stage, **kwargs)), flush=True)


def main():
    stream = (ROOT/'budget_extension20h_transaction.lock').open('a')
    fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
    request = mild.read(REQUEST)
    assert request['additional_training_seconds'] == 72000
    assert request['authorized_seconds_before'] == 36000 and request['authorized_seconds_after'] == 108000
    if APPLIED.exists():
        progress('already_applied_do_not_repeat', receipt=str(APPLIED))
        return
    state = mild.read(ROOT/'status.json')
    budget = base.budget_state()
    assert budget['authorized_training_seconds'] == 36000
    assert not budget.get('budget_extensions'), 'review prior extension history'
    assert state['canonical_budget'] == str(mild.CANONICAL)
    assert state['training_phase'] == 'continued_mild' and state['profile'] == 'white_v1'
    parent = mild.identity(int(state['supervisor_pid']))
    trainer = mild.identity(int(state['training_pid']))
    assert parent and trainer and parent['cwd'] == trainer['cwd'] == str(ROOT)
    assert any(a.endswith('/supervise_mild_trial.py') for a in parent['argv'])
    assert any(a.endswith('/train_mod4_ppo.py') for a in trainer['argv'])
    assert base.trainers() == [trainer['pid']]
    assert not mild.active_processes(('/validate_speed.py', '/mild_parameter_probe.py'))
    mild.environment()
    base.atomic_json(ROOT/'reports/BUDGET_BEFORE_ADD20H.json', budget)
    base.atomic_json(ROOT/'reports/STATUS_BEFORE_ADD20H.json', state)
    base.atomic_json(ROOT/'reports/PROCESSES_BEFORE_ADD20H.json', dict(parent=parent, trainer=trainer))
    ended = False
    os.kill(parent['pid'], signal.SIGSTOP)
    try:
        assert mild.identity(parent['pid'])['start_ticks'] == parent['start_ticks']
        assert not mild.active_processes(('/validate_speed.py', '/mild_parameter_probe.py'))
        log_dir = Path(state['log_dir'])
        assert log_dir.is_relative_to(ROOT/'logs')
        stop = log_dir/'STOP_AFTER_SAVE'
        assert not stop.exists(), 'pre-existing stop request needs review'
        stop.write_text('Explicit additional 20h budget: complete actor/critic/optimizer/std save before supervisor replacement.\n')
        progress('waiting_complete_save', parent_pid=parent['pid'], trainer_pid=trainer['pid'], request=str(REQUEST))
        began = time.time()
        while True:
            current = mild.identity(trainer['pid'])
            if current is None or current['state'] == 'Z':
                break
            assert current['start_ticks'] == trainer['start_ticks'], 'trainer PID reused'
            assert time.time()-began < 1200, 'save-boundary timeout'
            time.sleep(.5)
        ended_epoch = time.time()
        saved = mild.read(log_dir/'latest_complete.json')
        ck = Path(saved['checkpoint'])
        assert int(saved['pid']) == trainer['pid'] and ck.parent == log_dir
        assert float(saved['saved_at']) >= began-.5
        assert 'Full checkpoint saved; authorized budget or stop-file reached' in Path(state['active_log']).read_text(errors='replace')
        info = base.checkpoint(ck)
        ended = True
        # Close the old parent's launch and accounting authority before applying 108000.
        os.kill(parent['pid'], signal.SIGTERM)
        os.kill(parent['pid'], signal.SIGCONT)
        for _ in range(100):
            current = mild.identity(parent['pid'])
            if current is None or current['state'] == 'Z':
                break
            time.sleep(.1)
        assert current is None or current['state'] == 'Z', 'old parent remains alive'
        assert not base.trainers()
        b = base.budget_state()
        active = b['active_segment']
        assert active and active['pid'] == trainer['pid']
        tail = max(0., ended_epoch-float(active['accounted_through_epoch']))
        b['charged_training_seconds'] = float(b['charged_training_seconds'])+tail
        active.update(accounted_through_epoch=ended_epoch, ended_epoch=ended_epoch,
            end_evidence='verified complete checkpoint and normal trainer exit for explicit budget addition',
            observation_uncertainty_upper_s=.5)
        b.setdefault('completed_segments', []).append(active)
        b['active_segment'] = None
        addition = dict(extension_id=IDENTIFIER, additional_training_seconds=72000,
            authorization_basis='explicit_user_request', authorization=request['authorization'],
            requested_epoch=request['requested_epoch'], applied_epoch=time.time(), state='applied')
        b.setdefault('budget_extensions', []).append(addition)
        b['authorized_training_seconds'] = 108000
        b['remaining_training_seconds'] = max(0., 108000-b['charged_training_seconds'])
        b['deadline_epoch'] = time.time()+b['remaining_training_seconds']
        b['budget_scope'] = 'Original 10h plus explicitly authorized 20h; active PPO process time including preflight, not offline time'
        base.atomic_json(mild.CANONICAL, b)
        receipt = dict(extension_id=IDENTIFIER, additional_training_seconds=72000,
            total_authorized_seconds=108000, charged_training_seconds=b['charged_training_seconds'],
            remaining_training_seconds=b['remaining_training_seconds'], tail_charged_s=tail,
            canonical_budget=str(mild.CANONICAL), checkpoint=info,
            old_parent=parent, old_trainer=trainer, applied_epoch=time.time(),
            no_checkpoint_overwrite=True, physics_reward_ppo_changed=False)
        base.atomic_json(APPLIED, receipt)
        state.update(stage='budget_extended_starting', training_pid=None, supervisor_pid=None,
            canonical_budget=str(mild.CANONICAL), budget_seconds=108000, authorized_training_seconds=108000,
            charged_training_seconds=b['charged_training_seconds'], remaining_training_seconds=b['remaining_training_seconds'],
            deadline_epoch=b['deadline_epoch'], latest_checkpoint=str(ck), iteration=info['iteration_stored'],
            budget_extension_receipt=str(APPLIED), updated_at=time.time())
        base.atomic_json(ROOT/'status.json', state)
        progress('budget_committed', **{k:receipt[k] for k in ['total_authorized_seconds','charged_training_seconds','remaining_training_seconds','checkpoint']})
        log = ROOT/'supervisor_budget30h_20261001.log'
        assert not log.exists()
        with log.open('x') as out:
            proc = subprocess.Popen([base.PY, '-u', str(CODE/'supervise_budget30h.py')], cwd=ROOT,
                stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
        progress('new_supervisor_launched', supervisor_pid=proc.pid, log=str(log), receipt=str(APPLIED))
    finally:
        if not ended:
            current = mild.identity(parent['pid'])
            if current and current['start_ticks'] == parent['start_ticks']:
                os.kill(parent['pid'], signal.SIGCONT)


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        import traceback
        progress('attention_required', error=traceback.format_exc(),
                 instruction='Inspect actual processes and budget; do not repeat an applied addition or start another trainer.')
        raise
