"""One-shot save-boundary multi-seed review, never a trainer or budget owner.

Waits for the existing supervisor's frozen window AFTER a complete PPO save.
Pauses only that parent, lets its existing probe finish, then performs sequential
frozen spin/flat pairs. Finally resumes the parent without changing PPO, weights,
std, hardware, gates or the unique effective-time ledger. An independent watchdog
restores a stopped parent if this reviewer exits unexpectedly.
"""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback

OLD = Path('/home/egde/rl_candidates/MOD4_scut_spin_stage1_20261002')
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'reports'
PY = '/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
sys.path.insert(0, str(OLD / 'isaac/mod4'))
import supervise_native_floor as base
import supervise_mild_trial as helpers
from admission_gate import assess

PARENT = None
STOPPED = False
CHILD = None


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.partial')
    tmp.write_text(json.dumps(data, indent=2), encoding='utf8')
    os.replace(tmp, path)


def read(path):
    return json.loads(path.read_text())


def state(stage, **kw):
    old = read(ROOT / 'status.json') if (ROOT / 'status.json').exists() else {}
    old.update(stage=stage, reviewer_pid=os.getpid(), updated_at=time.time(), **kw)
    atomic(ROOT / 'status.json', old)


def ledger():
    p = Path(read(OLD / 'status.json')['canonical_budget'])
    b = read(p)
    base.validate_budget(b)
    return p, b


def resume():
    global STOPPED
    if STOPPED and PARENT:
        item = helpers.identity(PARENT['pid'])
        if item and item['start_ticks'] == PARENT['start_ticks'] and item['state'] != 'Z':
            os.kill(PARENT['pid'], signal.SIGCONT)
        STOPPED = False


def cleanup_owned_probes():
    """Stop only evaluators whose output is inside this review's unique directory."""
    owned = []
    for item in helpers.active_processes(('/validate_speed.py', '/spin_probe.py')):
        args = item['argv']
        if '--output' in args and args[args.index('--output') + 1].startswith(str(OUT) + '/'):
            owned.append(item)
    for item in owned:
        for sig, duration in ((signal.SIGINT, 45), (signal.SIGTERM, 10), (signal.SIGKILL, 5)):
            now = helpers.identity(item['pid'])
            if not now or now['state'] == 'Z' or now['start_ticks'] != item['start_ticks']:
                break
            os.kill(item['pid'], sig)
            end = time.time() + duration
            while time.time() < end:
                now = helpers.identity(item['pid'])
                if not now or now['state'] == 'Z' or now['start_ticks'] != item['start_ticks']:
                    break
                time.sleep(.5)
    remaining = [i for i in helpers.active_processes(('/validate_speed.py', '/spin_probe.py'))
                 if '--output' in i['argv'] and i['argv'][i['argv'].index('--output') + 1].startswith(str(OUT) + '/')]
    assert not remaining, 'Own evaluator still active; original parent must remain stopped'


def cancel(signum, frame):
    raise KeyboardInterrupt('Reviewer canceled; cleanup then restore original supervisor')


def watchdog(reviewer_pid, reviewer_ticks, parent_pid, parent_ticks):
    while True:
        person = helpers.identity(reviewer_pid)
        if not person or person['state'] == 'Z' or person['start_ticks'] != reviewer_ticks:
            cleanup_owned_probes()
            parent = helpers.identity(parent_pid)
            if parent and parent['start_ticks'] == parent_ticks and parent['state'] == 'T':
                os.kill(parent_pid, signal.SIGCONT)
                atomic(OUT / 'WATCHDOG_RESTORED_PARENT.json', {'parent_pid': parent_pid, 'at': time.time()})
            return
        time.sleep(5)


def await_existing(pid, path):
    end = time.time() + 1800
    while True:
        item = helpers.identity(pid)
        if not item or item['state'] == 'Z':
            break
        if time.time() > end:
            raise TimeoutError('Existing scheduled evaluation still active; restore original parent')
        time.sleep(2)
    if not path.exists() or Path(str(path) + '.error.txt').exists():
        raise RuntimeError('Existing scheduled probe failed; preserved error requires diagnosis')
    return read(path)


def probe(checkpoint, kind, profile, seed, steps=1500):
    global CHILD
    if base.trainers() or ledger()[1].get('active_segment'):
        raise RuntimeError('Frozen review must not overlap PPO or ledger accounting')
    if helpers.active_processes(('/validate_speed.py', '/spin_probe.py')):
        raise RuntimeError('Another frozen evaluator is active; do not duplicate it')
    name = f'model{checkpoint.stem.split("_")[-1]}_{kind}_{profile}_seed{seed}_{steps}steps'
    result = OUT / (name + '.json')
    if result.exists():
        item = read(result)
        assert item['checkpoint'] == str(checkpoint) and item['seed'] == seed
        return item
    cfg = read(OLD / 'isaac/mod4/env.json')
    env = {k: v for k, v in os.environ.items() if not k.startswith('RM_')}
    env.update({k: str(v) for k, v in cfg.items()})
    env.update(ISAACSIM_ACCEPT_EULA='Y', OMNI_KIT_ACCEPT_EULA='YES', PYTHONUNBUFFERED='1')
    script = 'spin_probe.py' if kind == 'spin' else 'validate_speed.py'
    args = [PY, 'isaac/mod4/' + script, '--headless', '--checkpoint', str(checkpoint),
            '--dr-profile', profile, '--seed', str(seed), '--num_envs', str(72 if kind == 'spin' else 80),
            '--steps', str(steps), '--output', str(result)]
    if kind == 'flat':
        args += ['--speed_limit', '1.5', '--ramp_suite']
    log = result.with_suffix('.log')
    assert not log.exists(), 'Failed previous probe must be reviewed, not overwritten'
    with log.open('x') as stream:
        CHILD = subprocess.Popen(args, cwd=OLD, env=env, stdout=stream,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    state('paired_frozen_review', checkpoint=str(checkpoint), evaluation_pid=CHILD.pid,
          evaluation_path=str(result), active_log=str(log), profile=profile, seed=seed, kind=kind)
    end = time.time() + 1800
    while CHILD.poll() is None:
        if time.time() > end:
            CHILD.send_signal(signal.SIGINT)
            CHILD.wait(timeout=90)
            raise TimeoutError('Own evaluator timed out; original supervisor restored')
        time.sleep(5)
    code = CHILD.returncode
    CHILD = None
    if code != 0 or not result.exists():
        raise RuntimeError('Frozen evaluator failed: ' + str(log))
    item = read(result)
    assert item['checkpoint'] == str(checkpoint) and item['seed'] == seed and item['seconds'] == 15
    return item


def spin_gate(report):
    selected = [g for g in report['groups'] if g['profile'] in ('spin', 'spin_ramp_stop_reverse')]
    assert len(selected) == 6
    return (report['seconds'] >= 15 and report['physical_smoke_pass']
            and all(g['spin_skill_fraction'] >= .8 for g in selected))


def paired_initial_state(a, b):
    keys = ['reset_joint_pos_before_physics', 'reset_root_before_physics']
    return all(k in a and k in b and a[k] == b[k] for k in keys)


def main():
    global PARENT, STOPPED
    OUT.mkdir(parents=True, exist_ok=True)
    lock = (ROOT / 'reviewer.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    if (OUT / 'MULTISEED_SPIN_ADMISSION.json').exists():
        raise RuntimeError('One-shot review already complete; read its receipt')
    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)
    state('waiting_existing_save_and_frozen_window', training_interrupted=False, new_budget=False)
    deadline = time.time() + 6 * 3600
    while True:
        s = read(OLD / 'status.json')
        if s.get('error') or s['stage'].startswith('attention'):
            raise RuntimeError('Old supervisor requires diagnosis before review')
        parent = helpers.identity(int(s['supervisor_pid']))
        if not parent or parent['cwd'] != str(OLD) or not any(a.endswith('/supervise_spin.py') for a in parent['argv']):
            raise RuntimeError('Unexpected original supervisor identity')
        p, b = ledger()
        evaluation = helpers.identity(s.get('evaluation_pid')) if s.get('evaluation_pid') else None
        if (s['stage'].startswith('frozen_') and not s.get('training_pid') and not base.trainers()
                and not b.get('active_segment') and evaluation and evaluation['cwd'] == str(OLD)):
            PARENT = parent
            os.kill(parent['pid'], signal.SIGSTOP)
            STOPPED = True
            # Recheck after stopping: never rely on a stale status window.
            if base.trainers() or ledger()[1].get('active_segment'):
                resume()
                time.sleep(2)
                continue
            now = helpers.identity(parent['pid'])
            assert now and now['start_ticks'] == parent['start_ticks']
            own = helpers.identity(os.getpid())
            subprocess.Popen([PY, str(Path(__file__).resolve()), '--watchdog', str(os.getpid()),
                              str(own['start_ticks']), str(parent['pid']), str(parent['start_ticks'])],
                             cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            state('letting_existing_evaluator_finish', old_parent=parent, canonical_budget=str(p))
            scheduled = await_existing(evaluation['pid'], Path(s['evaluation_path']))
            checkpoint = Path(scheduled['checkpoint'])
            import torch
            torch.set_num_threads(1)
            info = base.checkpoint(checkpoint)
            before = ledger()[1]
            break
        if time.time() > deadline:
            raise TimeoutError('No safe save/frozen window; original training untouched')
        time.sleep(2)
    try:
        data = {}
        for seed in (20261002, 20261003):
            for profile in ('nominal', 'white_v1'):
                data[(seed, profile, 'spin')] = probe(checkpoint, 'spin', profile, seed)
                data[(seed, profile, 'flat')] = probe(checkpoint, 'flat', profile, seed)
        rows = []
        passes = []
        for seed in (20261002, 20261003):
            for kind in ('spin', 'flat'):
                a, b = data[(seed, 'nominal', kind)], data[(seed, 'white_v1', kind)]
                pair = paired_initial_state(a, b)
                gates = [spin_gate(x) if kind == 'spin' else assess(x)['eligible_for_mild_dr_trial'] for x in (a, b)]
                rows.append({'seed': seed, 'kind': kind, 'same_initial_root_q': pair, 'gates': gates,
                             'original_overall_spin_skill_flags': [x.get('spin_skill_pass') for x in (a, b)],
                             'original_strict_window_flags': [x.get('strict_pass_window') for x in (a, b)]})
                passes.append(pair and all(gates))
        after = ledger()[1]
        assert not after.get('active_segment')
        assert after['charged_training_seconds'] == before['charged_training_seconds'], 'Frozen review must not charge PPO'
        result = {'spin_specific_admission': all(passes), 'checkpoint': info, 'pair_results': rows,
                  'original_total_flags_preserved': True, 'gate_scope': 'Six spin groups plus independent flat regression; not overall graduation or real-robot certification',
                  'next_allowed_task': 'Isolated .15m/s world-progress command/physics/PPO validation before save-boundary warm start' if all(passes) else 'Continue existing spin; diagnose failed pair before increasing difficulty',
                  'canonical_budget': str(p), 'charged_unchanged': True,
                  'budget_added': False, 'trainer_interrupted': False, 'new_curriculum_deployed': False}
        atomic(OUT / 'MULTISEED_SPIN_ADMISSION.json', result)
        atomic(OLD / 'reports/AUTO_DIFFICULTY_MULTISEED_ADMISSION.json', result)
        state('review_complete', spin_specific_admission=all(passes), checkpoint=info, evaluation_pid=None,
              next_task=result['next_allowed_task'])
    finally:
        cleanup_owned_probes()
        resume()


if __name__ == '__main__':
    if len(sys.argv) == 6 and sys.argv[1] == '--watchdog':
        watchdog(*(int(x) for x in sys.argv[2:]))
    else:
        try:
            main()
        except BaseException:
            cleanup_owned_probes()
            resume()
            state('review_needs_diagnosis', error=traceback.format_exc(), evaluation_pid=CHILD.pid if CHILD and CHILD.poll() is None else None)
            raise
