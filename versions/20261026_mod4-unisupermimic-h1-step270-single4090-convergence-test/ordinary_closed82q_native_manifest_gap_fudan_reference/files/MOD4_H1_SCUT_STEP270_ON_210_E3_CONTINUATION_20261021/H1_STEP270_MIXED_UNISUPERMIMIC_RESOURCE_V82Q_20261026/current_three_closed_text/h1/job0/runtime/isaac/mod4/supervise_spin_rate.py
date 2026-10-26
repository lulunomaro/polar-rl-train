"""One-shot safe takeover and measured pure-spin rate curriculum.

No new ledger. Preserve mature weights. Frozen evaluation never charges PPO.
Run --resume only after actual-process and abrupt-segment reconciliation.
"""
from pathlib import Path
import json
import os
import signal
import shutil
import subprocess
import sys
import time
import traceback

import supervise_spin as spin
import supervise_native_floor as base
import supervise_mild_trial as helpers
from admission_gate import assess
from rate_schedule import TARGET, LEVELS, next_limit, validate_limit

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / 'isaac/mod4'
REPORTS = ROOT / 'reports'
OLD = Path('/home/egde/rl_candidates/MOD4_scut_spin_stage1_20261002')
REVIEW = Path('/home/egde/rl_candidates/MOD4_AUTO_DIFFICULTY_20261002')
CANONICAL = Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
base.ROOT, base.CODE, base.REPORTS, base.BUDGET_PATH = ROOT, CODE, REPORTS, CANONICAL
spin.ROOT, spin.CODE, spin.REPORTS, spin.OLD, spin.CANONICAL = ROOT, CODE, REPORTS, OLD, CANONICAL
PROBES = ('/validate_speed.py', '/spin_probe.py', '/spin_rate_probe.py', '/spin_fullscale_probe.py', '/spin_rate_fullscale_probe.py')
spin.PROBES = PROBES
PARENT = None
HELD = False
LIVE = None


def read(p):
    return helpers.read(p)


def current_limit():
    return validate_limit(float(read(CODE / 'env.json')['RM_SPIN_MAX_RAD_S']))


def runtime():
    path = OLD / 'isaac/mod4/env.json' if os.environ.get('RM_SPIN_DISABLED_FALLBACK') == '1' else CODE / 'env.json'
    cfg = read(path)
    required = {'RM_SPIN_STAGE': 'pure_yaw_v1', 'RM_FLAT_NATIVE_PLANE': '1', 'RM_CONTACT_INTEGRATED': '1',
                'RM_CONTACT_EAGER5MS': '1', 'RM_KEEP_STD': '1', 'RM_DR_OFF': '1', 'RM_GYRO_CURRICULUM': '0',
                'RM_HEADING_CMD': '0', 'RM_REL_HEADING': '0', 'RM_SOLVER_POS': '16', 'RM_SOLVER_VEL': '4',
                'RM_MOD4_TERRAIN': 'flat', 'RM_MILD_DR_PROFILE': 'white_v1'}
    assert all(str(cfg.get(k)) == v for k, v in required.items()), 'Recipe drift'
    assert float(cfg['RM_SPIN_MIN_RAD_S']) == 1 and float(cfg['RM_SPIN_FRACTION']) == .3
    assert float(cfg['RM_REL_STANDING']) == .1 and float(cfg['RM_NOMINAL_HEIGHT']) == .25
    assert float(cfg['RM_CMD_VX_MIN']) == -1.5 and float(cfg['RM_CMD_VX_MAX']) == 1.5
    if path.parent == CODE:
        current_limit()
    else:
        assert float(cfg['RM_SPIN_MAX_RAD_S']) == 2
    env = {k: v for k, v in os.environ.items() if not k.startswith('RM_')}
    env.update({k: str(v) for k, v in cfg.items()})
    env.update(ISAACSIM_ACCEPT_EULA='Y', OMNI_KIT_ACCEPT_EULA='YES', PYTHONUNBUFFERED='1')
    return env


base.runtime_env = runtime
spin.runtime = runtime


def status(stage=None, **kw):
    # Correct imported stage-one labels without changing its training implementation.
    kw.pop('scope', None)
    base.status(supervisor_pid=os.getpid(), canonical_budget=str(CANONICAL),
                profile='white_v1', dr_enabled=True, yaw_limit_rad_s=current_limit(),
                target_yaw_rad_s=TARGET, target_chassis_rev_s=2., speed_limit_m_s=1.5,
                spin_stage='pure_yaw_rate_v1', stand_fraction=.1, spin_fraction=.3, straight_fraction=.6,
                scope='Measured pure-spin rate curriculum; spin translation remains a separate lower-rate course',
                **({'stage': stage} if stage else {}), **kw)


spin.status = status


def freeze_run(folder):
    out = folder / 'spin_source_freeze.json'
    if out.exists(): return
    dest = folder / 'spin_source_snapshot'; dest.mkdir(exist_ok=True)
    evidence = {}; locations = {}
    for name, digest in read(REPORTS / 'SPIN_SOURCE_FREEZE.json')['sha256'].items():
        key = Path(name); source = key if key.is_absolute() else ROOT / key
        assert base.sha(source) == digest, 'Source drift ' + name
        relative = Path('_external') / digest[:12] / key.name if key.is_absolute() else key
        target = dest / relative
        assert target.resolve().is_relative_to(dest.resolve()) and source.resolve() != target.resolve()
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, target)
        evidence[name] = digest; locations[name] = str(relative)
    base.atomic_json(out, {'sha256': evidence, 'snapshot_relative_locations': locations,
                          'budget': str(CANONICAL), 'hardware_reward_ppo_unchanged': True})


spin.freeze_run = freeze_run


def set_limit(limit, reason):
    validate_limit(limit)
    cfg = read(CODE / 'env.json'); old = cfg['RM_SPIN_MAX_RAD_S']; cfg['RM_SPIN_MAX_RAD_S'] = repr(limit)
    base.atomic_json(CODE / 'env.json', cfg)
    manifest = read(REPORTS / 'SPIN_SOURCE_FREEZE.json')
    manifest['sha256']['isaac/mod4/env.json'] = base.sha(CODE / 'env.json')
    base.atomic_json(REPORTS / 'SPIN_SOURCE_FREEZE.json', manifest)
    name = 'limit_change_' + str(time.time_ns()) + '.json'
    base.atomic_json(REPORTS / name, {'old_rad_s': old, 'new_rad_s': limit, 'reason': reason,
                                     'only_command_range_changed': True, 'budget_added': False})


def verify_sources():
    for name, digest in read(REPORTS / 'SPIN_SOURCE_FREEZE.json')['sha256'].items():
        p = Path(name); p = p if p.is_absolute() else ROOT / p
        assert base.sha(p) == digest, 'Source drift ' + name
    assert base.budget_state()['authorized_training_seconds'] == 180000
    runtime()


def trainer_run(logs, trainer_pid):
    """A warm-start run can initially share/lower the previous iteration number."""
    matches = []
    for receipt in logs.glob('*/latest_complete.json'):
        if int(read(receipt)['pid']) == trainer_pid:
            matches.append(receipt.parent)
    assert len(matches) == 1, 'Current trainer has not saved its own unique complete receipt yet'
    return matches[0]


def probe(ck, name, kind='spin', steps=1500, profile='white_v1', seed=20261002):
    global LIVE
    assert not base.trainers() and not helpers.active_processes(PROBES)
    assert not base.budget_state().get('active_segment')
    out = REPORTS / (name + '.json')
    assert not out.exists(), 'Probe already exists; inspect instead of overwriting'
    args = ['isaac/mod4/' + ('spin_rate_probe.py' if kind == 'spin' else 'validate_speed.py'),
            '--headless', '--checkpoint', str(ck), '--seed', str(seed), '--dr-profile', profile,
            '--num_envs', '22' if steps < 1500 and kind == 'spin' else '88' if kind == 'spin' else '80',
            '--steps', str(steps), '--output', str(out)]
    if kind == 'spin':
        args += ['--max-rate', repr(current_limit())]
    else:
        args += ['--speed_limit', '1.5', '--ramp_suite']
    p = base.spawn(args, out.with_suffix('.log')); LIVE = p
    status('frozen_' + kind + '_evaluation', training_pid=None, evaluation_pid=p.pid,
           active_log=str(out.with_suffix('.log')), evaluation_path=str(out))
    result = base.wait_probe(p, out); LIVE = None
    status(evaluation_pid=None, **({'latest_spin_evaluation': spin.compact_spin(result)} if kind == 'spin'
                                 else {'latest_evaluation': result, 'experimental_admission': assess(result)}))
    return result


def fullscale(ck, label):
    global LIVE
    assert not base.trainers() and not helpers.active_processes(PROBES)
    out = REPORTS / (label + '_20k.json')
    p = base.spawn(['isaac/mod4/spin_rate_fullscale_probe.py', '--headless', '--checkpoint', str(ck),
                    '--num_envs', '20000', '--steps', '120', '--max-rate', repr(current_limit()),
                    '--output', str(out)], out.with_suffix('.log')); LIVE = p
    status('rate_20k_physics', training_pid=None, validation_pid=p.pid, active_log=str(out.with_suffix('.log')))
    r = base.wait_probe(p, out); LIVE = None
    passed, acceptance = base.accept_physics_smoke(r)
    assert passed and r['mild_initial_parameters']['actual_parameters_pass'] and r['mild_final_parameters']['actual_parameters_pass']
    base.atomic_json(REPORTS / (label + '_20k_acceptance.json'), acceptance)
    status(validation_pid=None, physics_preflight_acceptance=acceptance)


def resume_old_parent():
    global HELD
    if HELD and PARENT:
        item = helpers.identity(PARENT['pid'])
        if item and item['start_ticks'] == PARENT['start_ticks']:
            os.kill(item['pid'], signal.SIGCONT)
    HELD = False


def owned_probe_cleanup():
    for ident in helpers.active_processes(PROBES):
        args = ident['argv']
        if '--output' not in args:
            continue
        output = Path(args[args.index('--output') + 1])
        if not output.is_relative_to(REPORTS):
            continue
        now = helpers.identity(ident['pid'])
        if now and now['start_ticks'] == ident['start_ticks']:
            os.kill(ident['pid'], signal.SIGINT)
            deadline = time.time() + 60
            while time.time() < deadline:
                now = helpers.identity(ident['pid'])
                if not now or now['state'] == 'Z': break
                time.sleep(1)
            now = helpers.identity(ident['pid'])
            if now and now['state'] != 'Z' and now['start_ticks'] == ident['start_ticks']:
                os.kill(ident['pid'], signal.SIGKILL)


def watchdog(owner_pid, owner_ticks, parent_pid, parent_ticks):
    while True:
        owner = helpers.identity(owner_pid)
        if not owner or owner['state'] == 'Z' or owner['start_ticks'] != owner_ticks: break
        time.sleep(5)
    if (REPORTS / 'handover_completed.json').exists(): return
    owned_probe_cleanup()
    parent = helpers.identity(parent_pid)
    if parent and parent['start_ticks'] == parent_ticks and parent['state'] == 'T':
        os.kill(parent_pid, signal.SIGCONT)
        base.atomic_json(REPORTS / 'WATCHDOG_RESTORED_PARENT.json', {'parent': parent, 'time': time.time()})


def handover():
    global PARENT, HELD
    assert not (REPORTS / 'handover_completed.json').exists(), 'One-time handover already done'
    status('waiting_multiseed_and_existing_save_window', training_pid=None)
    limit = time.time() + 3 * 3600
    while True:
        decision = REVIEW / 'reports/MULTISEED_SPIN_ADMISSION.json'
        if decision.exists():
            assert read(decision)['spin_specific_admission'], 'Mature spin multi-seed review failed'
            assert read(REVIEW / 'status.json')['stage'] == 'review_complete'
            old = read(OLD / 'status.json'); parent = helpers.identity(old['supervisor_pid'])
            assert parent and parent['cwd'] == str(OLD) and any(a.endswith('/supervise_spin.py') for a in parent['argv'])
            trainer = helpers.identity(old.get('training_pid')) if old.get('training_pid') else None
            active_trainer = trainer and trainer['state'] != 'Z' and trainer['cwd'] == str(OLD)
            safe_frozen = (old['stage'].startswith('frozen_') and not old.get('training_pid')
                           and not base.trainers() and not base.budget_state().get('active_segment'))
            safe_training = (active_trainer and base.trainers() == [trainer['pid']]
                             and not helpers.active_processes(PROBES)
                             and (base.budget_state().get('active_segment') or {}).get('pid') == trainer['pid'])
            if parent['state'] != 'T' and (safe_frozen or safe_training):
                PARENT = parent; os.kill(parent['pid'], signal.SIGSTOP); HELD = True
                if safe_frozen and (base.trainers() or base.budget_state().get('active_segment')):
                    resume_old_parent(); time.sleep(2); continue
                own = helpers.identity(os.getpid())
                subprocess.Popen([base.PY, str(Path(__file__).resolve()), '--watchdog', str(os.getpid()),
                                 str(own['start_ticks']), str(parent['pid']), str(parent['start_ticks'])],
                                 cwd=ROOT, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                tail = 0.
                if safe_training:
                    assert helpers.identity(trainer['pid'])['start_ticks'] == trainer['start_ticks']
                    # A globally highest checkpoint can still belong to the previous segment.
                    # Pin the actual live PID, not iteration or status.log_dir.
                    until = time.time() + 1200
                    while True:
                        try:
                            folder = trainer_run(OLD / 'logs', trainer['pid']); break
                        except AssertionError:
                            assert time.time() < until
                            now = helpers.identity(trainer['pid'])
                            assert now and now['state'] != 'Z' and now['start_ticks'] == trainer['start_ticks']
                            time.sleep(1)
                    stop = folder / 'STOP_AFTER_SAVE'
                    assert not stop.exists(), 'Existing stop request requires diagnosis'
                    stop.write_text('User-authorized yaw-rate curriculum: save complete actor/critic/optimizer/std at the next complete boundary.\n')
                    status('waiting_complete_save', training_pid=trainer['pid'], active_log=old['active_log'])
                    until = time.time() + 1200
                    while True:
                        now = helpers.identity(trainer['pid'])
                        if not now or now['state'] == 'Z': break
                        assert now['start_ticks'] == trainer['start_ticks'] and time.time() < until
                        time.sleep(.5)
                    ended = time.time(); latest = base.latest(OLD / 'logs'); saved = read(latest.parent / 'latest_complete.json')
                    assert Path(saved['checkpoint']) == latest and int(saved['pid']) == trainer['pid']
                    assert 'Full checkpoint saved; authorized budget or stop-file reached' in Path(old['active_log']).read_text(errors='replace')
                    ledger = base.budget_state(); segment = ledger['active_segment']; assert segment['pid'] == trainer['pid']
                    tail = max(0., ended - segment['accounted_through_epoch'])
                    ledger['charged_training_seconds'] += tail
                    ledger['remaining_training_seconds'] = ledger['authorized_training_seconds'] - ledger['charged_training_seconds']
                    segment.update(accounted_through_epoch=ended, ended_epoch=ended,
                                   end_evidence='verified complete save and graceful trainer exit', observation_uncertainty_upper_s=.5)
                    ledger.setdefault('completed_segments', []).append(segment); ledger['active_segment'] = None
                    base.atomic_json(CANONICAL, ledger)
                    status(training_pid=None)
                before = base.budget_state()
                status('waiting_existing_frozen_probe', old_parent=parent)
                while helpers.active_processes(PROBES):
                    assert not base.trainers() and not base.budget_state().get('active_segment')
                    assert time.time() < limit
                    time.sleep(2)
                source = base.latest(OLD / 'logs'); assert source
                info = base.checkpoint(source)
                assert Path(read(source.parent / 'latest_complete.json')['checkpoint']) == source
                short = probe(source, 'rate3_short_physics', steps=300)
                assert short['physical_smoke_pass'] and not short['nonfinite'], 'Rate3 physical preflight failed'
                assert short['initial_parameter_audit']['actual_parameters_pass'] and short['final_parameter_audit']['actual_parameters_pass']
                flat = probe(source, 'latest_source_flat15s', kind='flat', seed=20260927)
                assert assess(flat)['eligible_for_mild_dr_trial'], 'Latest full source lost mature flat behavior'
                assert base.budget_state()['charged_training_seconds'] == before['charged_training_seconds']
                saved_parent = helpers.identity(parent['pid'])
                assert saved_parent and saved_parent['start_ticks'] == parent['start_ticks']
                os.kill(parent['pid'], signal.SIGTERM); os.kill(parent['pid'], signal.SIGCONT)
                HELD = False
                until = time.time() + 20
                while time.time() < until:
                    item = helpers.identity(parent['pid'])
                    if not item or item['state'] == 'Z': break
                    time.sleep(.2)
                assert not base.trainers() and not helpers.active_processes(PROBES)
                helpers.acquire(CANONICAL.parent / 'native_floor_supervisor.lock')
                assert base.budget_state()['charged_training_seconds'] == before['charged_training_seconds']
                base.update_budget(owner_root=str(ROOT))
                base.atomic_json(REPORTS / 'handover_completed.json', {'source_checkpoint': info, 'old_parent': parent,
                    'canonical_budget': str(CANONICAL), 'charged_unchanged': True, 'trainer_interrupted': False,
                    'tail_charged_s': tail, 'graceful_stop_after_save_used': bool(safe_training),
                    'prior_multiseed_candidate': read(decision)['checkpoint'],
                    'latest_source_flat_pass': True, 'new_budget': False, 'short_physical_pass': True, 'old_weights_preserved': True})
                old.update(stage='handed_over_to_rate_curriculum', supervisor_pid=None, training_pid=None,
                           evaluation_pid=None, handover_root=str(ROOT), updated_at=time.time())
                base.atomic_json(OLD / 'status.json', old)
                return source
        assert time.time() < limit, 'No safe frozen window; existing training remains untouched'
        time.sleep(2)


def decision(ck, label):
    flat = probe(ck, label + '_flat', kind='flat', seed=20260927)
    rate = probe(ck, label + '_rate')
    physical = assess(flat)['eligible_for_mild_dr_trial'] and rate['physical_smoke_pass']
    result = {'continue_current_rate': physical, 'current_rate_skill_pass': rate['spin_skill_pass'],
              'flat_admission': assess(flat), 'checkpoint': base.checkpoint(ck), 'rate_limit': current_limit(),
              'target_rate_rad_s': TARGET, 'target_achieved': current_limit() == TARGET and rate['spin_skill_pass']}
    base.atomic_json(REPORTS / (label + '_decision.json'), result)
    status(latest_rate_decision=result)
    return physical, physical and rate['spin_skill_pass']


def ppo_preflight(ck, label):
    spin.training(ck, label, count=128)
    receipt = read(REPORTS / 'PPO_PREFLIGHT_128.json')
    base.atomic_json(REPORTS / (label + '_receipt_' + str(time.time_ns()) + '.json'), receipt)


def multiseed(ck, label):
    pairs = []; passed = True
    for seed in (20261002, 20261003):
        for kind in ('flat', 'spin'):
            a = probe(ck, f'{label}_{kind}_nominal_{seed}', kind=kind, profile='nominal', seed=seed)
            b = probe(ck, f'{label}_{kind}_mild_{seed}', kind=kind, profile='white_v1', seed=seed)
            exact = all(a[k] == b[k] for k in ['reset_joint_pos_before_physics', 'reset_root_before_physics'])
            gates = [assess(x)['eligible_for_mild_dr_trial'] if kind == 'flat' else x['spin_skill_pass'] for x in (a, b)]
            pairs.append({'seed': seed, 'kind': kind, 'same_initial_root_q': exact, 'gates': gates})
            passed &= exact and all(gates)
    base.atomic_json(REPORTS / (label + '_multiseed.json'), {'pass': bool(passed), 'pairs': pairs,
        'limit_rad_s': current_limit(), 'checkpoint': base.checkpoint(ck), 'real_robot_certified': False})
    return passed


def fallback(source, reason):
    # The preserved stage-one source controls its own 2rad/s recipe.
    status('restoring_preserved_2rad_s', fallback_reason=reason)
    set_limit(3., 'Rate preflight/physical regression; preserve source and restore original low-rate commands')
    ck = spin.training(source, 'preserved_2rad_s_fallback', spin=False)
    os.environ['RM_SPIN_DISABLED_FALLBACK'] = '1'
    try:
        for name, script, count in [('flat', 'validate_speed.py', '80'), ('spin', 'spin_probe.py', '72')]:
            out = REPORTS / ('final_fallback_' + name + '.json')
            args = [str(OLD / 'isaac/mod4' / script), '--headless', '--checkpoint', str(ck), '--steps', '1500',
                    '--num_envs', count, '--seed', '20261002', '--dr-profile', 'white_v1', '--output', str(out)]
            if name == 'flat': args += ['--speed_limit', '1.5', '--ramp_suite']
            p = base.spawn(args, out.with_suffix('.log')); base.wait_probe(p, out)
    finally:
        os.environ.pop('RM_SPIN_DISABLED_FALLBACK', None)
    status('finished_fallback', final_checkpoint=base.checkpoint(ck), outcome=reason, training_pid=None)


def main(resume=False):
    import torch
    torch.set_num_threads(1)
    REPORTS.mkdir(exist_ok=True)
    helpers.acquire(ROOT / 'rate_supervisor.lock')
    verify_sources()
    if resume:
        assert (REPORTS / 'handover_completed.json').exists()
        assert not base.trainers() and not helpers.active_processes(PROBES)
        assert not base.budget_state().get('active_segment'), 'Reconcile abrupt segment first'
        assert base.budget_state()['owner_root'] == str(ROOT)
        helpers.acquire(CANONICAL.parent / 'native_floor_supervisor.lock')
        source = Path(read(REPORTS / 'handover_completed.json')['source_checkpoint']['path'])
        chosen = base.latest(ROOT / 'logs') or source
    else:
        source = handover()
        try:
            fullscale(source, 'rate3_initial')
            ppo_preflight(source, 'rate3_preflight')
        except BaseException:
            if base.trainers() or base.budget_state().get('active_segment'): raise
            fallback(source, traceback.format_exc()); return
        base.atomic_json(REPORTS / 'RATE_PRODUCTION_STARTED.json', {'source': base.checkpoint(source),
            'limit_rad_s': current_limit(), 'target_rad_s': TARGET, 'preflight_weights_discarded': True,
            'canonical_budget': str(CANONICAL), 'budget_added': False})
        chosen = spin.training(source, 'rate3_trial45', duration=2700)
    if resume and not (REPORTS / 'RATE_PRODUCTION_STARTED.json').exists():
        # Recovery from an auxiliary archival failure before real training.
        # Cache only verified full-scale/PPO evidence; discard its policy weights.
        smoke = read(REPORTS / 'rate3_initial_20k_acceptance.json')
        preflight = read(REPORTS / 'PPO_PREFLIGHT_128.json')
        assert smoke['physical_smoke_pass'] and preflight['pass']
        assert preflight['production_source'] == str(source)
        assert preflight['charged_same_ledger'] and preflight['weights_discarded']
        base.atomic_json(REPORTS / 'RATE_PRODUCTION_STARTED.json', {'source': base.checkpoint(source),
            'limit_rad_s': current_limit(), 'target_rad_s': TARGET, 'preflight_weights_discarded': True,
            'canonical_budget': str(CANONICAL), 'budget_added': False, 'cached_verified_preflight_reused': True})
        chosen = spin.training(source, 'rate3_trial45', duration=2700)
    consecutive = 0
    while True:
        label = 'rate' + str(current_limit()).replace('.', 'p') + '_model' + str(base.checkpoint(chosen)['iteration_stored'])
        physical, skilled = decision(chosen, label)
        if not physical:
            fallback(source, 'Physical or mature flat regression; rate weights preserved'); return
        consecutive = consecutive + 1 if skilled else 0
        remaining = base.budget_state()['remaining_training_seconds']
        higher = next_limit(current_limit())
        if consecutive >= 2 and higher is not None and remaining > 3600:
            if multiseed(chosen, label):
                previous = current_limit(); set_limit(higher, 'Two consecutive skill checks and two-seed nominal/DR exact-reset pairs passed')
                try:
                    short = probe(chosen, label + '_next_short', steps=300)
                    assert short['physical_smoke_pass'] and not short['nonfinite']
                    fullscale(chosen, label + '_next')
                    ppo_preflight(chosen, 'next_rate_preflight')
                except BaseException:
                    if base.trainers() or base.budget_state().get('active_segment'): raise
                    base.atomic_json(REPORTS / (label + '_promotion_rejected.json'), {'error': traceback.format_exc(), 'preserved_checkpoint': str(chosen)})
                    set_limit(previous, 'Next-rate physical/PPO preflight rejected; resume current validated rate')
                consecutive = 0
        remaining = base.budget_state()['remaining_training_seconds']
        if remaining <= 120: break
        chosen = spin.training(chosen, 'rate_continued', duration=min(7200, remaining))
        if base.budget_state()['remaining_training_seconds'] <= 120: break
    final_flat = probe(chosen, 'final_flat', kind='flat')
    final_rate = probe(chosen, 'final_rate_mild')
    final_nominal = probe(chosen, 'final_rate_nominal', profile='nominal')
    status('finished', training_pid=None, final_checkpoint=base.checkpoint(chosen),
           final_evaluation={'flat': assess(final_flat), 'rate_mild': spin.compact_spin(final_rate), 'rate_nominal': spin.compact_spin(final_nominal)},
           outcome='Budget complete; requested 2rev/s is a target, only measured rates and failures may be reported as achieved')


def cancel(*_):
    raise KeyboardInterrupt('Supervisor interrupted; reconcile live trainer/ledger before recovery')


if __name__ == '__main__':
    if len(sys.argv) == 6 and sys.argv[1] == '--watchdog':
        watchdog(*(int(x) for x in sys.argv[2:]))
    else:
        signal.signal(signal.SIGINT, cancel); signal.signal(signal.SIGTERM, cancel)
        try:
            main(resume='--resume' in sys.argv)
        except BaseException:
            if not (REPORTS / 'handover_completed.json').exists():
                owned_probe_cleanup(); resume_old_parent()
            status('attention_required', error=traceback.format_exc(),
                   instructions='Inspect actual trainer/evaluator identities and canonical active segment. Never duplicate handover, budget or trainer.')
            raise
