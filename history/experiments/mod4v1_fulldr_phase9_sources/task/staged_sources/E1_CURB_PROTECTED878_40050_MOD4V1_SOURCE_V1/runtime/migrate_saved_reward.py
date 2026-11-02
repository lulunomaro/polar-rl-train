import fcntl,hashlib,json,os,shutil,signal,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002')
OLD=Path('/home/egde/rl_candidates/MOD4_WORLD_SPIN_RUNTIME_20261005')
STAGING=Path('/home/egde/rl_candidates/MOD4_WORLD_DRIFT_REWARD_20261005')
CANONICAL=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
PY='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python'
ID='WORLD_DRIFT_REWARD_20261005';PROGRESS=STAGING/'reports/REWARD_MIGRATION_PROGRESS.json'
def read(p):
    return json.loads(p.read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def atomic(p, d):
    q = p.with_name(p.name + '.' + ID + '.partial')
    q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    os.replace(q, p)

def identity(pid):
    if not pid:
        return None
    p = Path('/proc') / str(pid)
    try:
        st = (p / 'stat').read_text().rsplit(')', 1)[1].split()
        try:
            cwd = os.readlink(p / 'cwd')
        except OSError:
            cwd = None
        return {'pid': pid, 'state': st[0], 'start_ticks': int(st[19]), 'ppid': int(st[1]), 'session': int(st[3]), 'cwd': cwd, 'argv': (p / 'cmdline').read_bytes().decode().split('\x00')[:-1], 'exit_code_encoded': int(st[49]) if len(st) > 49 else None}
    except (OSError, ValueError):
        return None

def same(p):
    now = identity(p['pid'])
    return now and now['start_ticks'] == p['start_ticks']

def live(p):
    now = identity(p['pid'])
    return now and now['start_ticks'] == p['start_ticks'] and (now['state'] != 'Z')

def processes():
    result = []
    for d in Path('/proc').glob('[0-9]*'):
        p = identity(int(d.name))
        if p and p['state'] != 'Z' and ('-c' not in p['argv']) and (p['cwd'] == str(ROOT)):
            result.append(p)
    return result

def checkpoint(path):
    import torch
    torch.set_num_threads(1)
    d = torch.load(path, map_location='cpu', weights_only=True)

    def floats(x):
        if torch.is_tensor(x) and x.is_floating_point():
            yield x
        elif isinstance(x, dict):
            for v in x.values():
                yield from floats(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                yield from floats(v)
    fs = list(floats(d))
    assert len(fs) == 68 and all((bool(torch.isfinite(t).all()) for t in fs))
    assert all((k in d for k in ('actor_state_dict', 'critic_state_dict', 'optimizer_state_dict', 'iter')))
    assert any(('std' in k.lower() for k in d['actor_state_dict']))
    return {'path': str(path), 'iteration_stored': d['iter'], 'sha256': sha(path), 'finite_tensors': len(fs), 'actor_critic_optimizer_std_iter_preserved': True}

def complete_run(pid):
    matches = [p.parent for p in (ROOT / 'logs').glob('*/latest_complete.json') if int(read(p)['pid']) == pid]
    assert len(matches) == 1, 'No unique complete receipt bound to this actual trainer'
    return matches[0]

def syscall(pid, secret):
    p = Path('/proc') / str(pid) / 'syscall'
    try:
        return p.read_text().strip()
    except PermissionError:
        assert secret, 'Read-only process inspection credential unavailable'
        r = subprocess.run(['sudo', '-S', '-p', '', 'cat', str(p)], input=secret + '\n', text=True, capture_output=True, timeout=5)
        assert r.returncode == 0, 'Verified process syscall inspection failed'
        return r.stdout.strip()

def pause_sleep(parent, secret):
    for _ in range(150):
        assert same(parent) and live(parent)
        before = syscall(parent['pid'], secret)
        if not before or before.split()[0] != '230':
            time.sleep(0.05)
            continue
        os.kill(parent['pid'], signal.SIGSTOP)
        stopped = identity(parent['pid'])
        for _ in range(80):
            if stopped and stopped['state'] in ('T', 't'):
                break
            time.sleep(0.005)
            stopped = identity(parent['pid'])
        after = syscall(parent['pid'], secret)
        if stopped and stopped['state'] in ('T', 't') and after and (after.split()[0] == '230'):
            return {'before': before, 'stopped': after, 'state': stopped['state'], 'outside_ledger_write': True}
        if same(parent):
            os.kill(parent['pid'], signal.SIGCONT)
    raise AssertionError('No safe supervisor accounting pause; do not modify budget')

def progress(stage,**kw):
    atomic(PROGRESS,dict(stage=stage,epoch=time.time(),**kw))
    print(json.dumps(dict(stage=stage,**kw)),flush=True)

def watchdog(parent,ticks,deadline):
    while time.time()<deadline:
        p=identity(parent)
        if not p or p['start_ticks']!=ticks or p['state']=='Z':return
        if (STAGING/'reports/REWARD_HANDOVER.json').exists():return
        time.sleep(1)
    p=identity(parent)
    if p and p['start_ticks']==ticks and p['state'] in ('T','t'):
        os.kill(parent,signal.SIGCONT)
        atomic(STAGING/'reports/WATCHDOG_RESTORED_PARENT.json',dict(epoch=time.time(),parent=p))

def main():
    tx=(STAGING/'reward_migration.lock').open('a');fcntl.flock(tx,fcntl.LOCK_EX|fcntl.LOCK_NB)
    assert not PROGRESS.exists() and not (STAGING/'reports/REWARD_HANDOVER.json').exists(),'Transaction already started; inspect instead of repeating'
    import supervise_world_drift as new
    new.verify()
    b=read(CANONICAL);assert b['authorized_training_seconds']==324000
    a=read(ROOT/'reports/AUTONOMY_STATE.json');s=read(ROOT/'status.json')
    parent=identity(s['supervisor_pid']);trainer=identity(s['training_pid'])
    assert parent and trainer and parent['cwd']==trainer['cwd']==str(ROOT)
    assert str(OLD/'continue_world_after_display_review.py') in parent['argv']
    assert str(OLD/'isaac/mod4/train_mod4_ppo.py') in trainer['argv'] and trainer['ppid']==parent['pid']
    assert b['active_segment']['pid']==a['active_training']['pid']==trainer['pid']
    assert new.base.trainers()==[trainer['pid']]
    guardians=[p for p in processes() if '--guardian' in p['argv'] and str(parent['pid']) in p['argv']]
    assert len(guardians)==1;guardian=guardians[0]
    run=complete_run(trainer['pid']);checkpoint(Path(read(run/'latest_complete.json')['checkpoint']))
    before=STAGING/'reports/migration_before';before.mkdir()
    for p,name in [(CANONICAL,'canonical.json'),(ROOT/'reports/AUTONOMY_STATE.json','autonomy_state.json'),(ROOT/'status.json','status.json'),(OLD/'reports/WORLD_SPIN_STATE.json','world_state.json')]:shutil.copy2(p,before/name)
    secret=sys.stdin.readline().rstrip('\n')
    with (STAGING/'reward_migration_watchdog.log').open('x') as log:
        watcher=subprocess.Popen([PY,str(STAGING/'migrate_saved_reward.py'),'--watchdog',str(parent['pid']),str(parent['start_ticks']),str(time.time()+1200)],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    paused=False;retired=False;stop=run/'STOP_AFTER_SAVE'
    try:
        proof=pause_sleep(parent,secret);secret=None;paused=True
        assert live(trainer) and not stop.exists()
        stop.write_text('User authorized isolated world-cycle cross-drift reward: full atomic save then stop.\n')
        began=time.time();progress('waiting_full_save',parent=parent,trainer=trainer,guardian=guardian,watchdog=identity(watcher.pid),safe_pause=proof)
        while live(trainer):
            assert same(parent) and identity(parent['pid'])['state'] in ('T','t') and time.time()-began<900
            time.sleep(.25)
        ended=time.time();exited=identity(trainer['pid'])
        if exited:assert exited['state']=='Z' and exited['start_ticks']==trainer['start_ticks'] and exited['exit_code_encoded']==0
        saved=read(run/'latest_complete.json');assert saved['pid']==trainer['pid'] and saved['saved_at']>=began-.5
        ck=Path(saved['checkpoint']);assert ck.parent==run
        log=Path(s['active_log']).read_text(errors='replace')
        assert 'Full checkpoint saved; authorized budget or stop-file reached' in log and 'Traceback (most recent call last)' not in log
        info=checkpoint(ck)
        manifest=read(run/'run_manifest.json')
        assert manifest['env']['RM_KEEP_STD']=='1' and manifest['env']['RM_MILD_DR_PROFILE']=='white_v2'
        assert float(manifest['env']['RM_SPIN_WORLD_PROGRESS_M_S'])==.5
        assert same(parent) and same(guardian)
        os.kill(guardian['pid'],signal.SIGTERM);os.kill(parent['pid'],signal.SIGKILL);retired=True;paused=False
        for _ in range(100):
            if not live(parent) and not live(guardian):break
            time.sleep(.05)
        assert not live(parent) and not live(guardian) and not live(trainer)
        new.helpers.acquire(ROOT/'autonomy_controller.lock');new.helpers.acquire(CANONICAL.parent/'native_floor_supervisor.lock')
        b=read(CANONICAL);assert b['active_segment']['pid']==trainer['pid']
        segment=b['active_segment'];tail=max(0,ended-segment['accounted_through_epoch']);charged_before=b['charged_training_seconds']
        segment.update(accounted_through_epoch=ended,ended_epoch=ended,end_reason='saved boundary for user-authorized isolated drift reward',observation_uncertainty_upper_s=.25,end_evidence=saved)
        b['charged_training_seconds']+=tail;b['completed_segments'].append(segment);b['active_segment']=None
        b['remaining_training_seconds']=b['authorized_training_seconds']-b['charged_training_seconds']
        assert b['budget_extensions']==read(before/'canonical.json')['budget_extensions'] and b['authorized_training_seconds']==324000
        atomic(CANONICAL,b)
        state=read(ROOT/'reports/AUTONOMY_STATE.json');assert state['active_training']['pid']==trainer['pid']
        state['active_training']=None;state['chosen_checkpoint']=str(ck);atomic(ROOT/'reports/AUTONOMY_STATE.json',state)
        hand=dict(checkpoint=info,retired=[parent,guardian,trainer],bound_complete_receipt=saved,exit_evidence=exited,
            old_runtime=str(OLD),new_runtime=str(STAGING),tail_charged_once_s=tail,charged_before_tail=charged_before,
            charged_training_seconds=b['charged_training_seconds'],remaining_training_seconds=b['remaining_training_seconds'],
            exit_observation_uncertainty_upper_s=.25,authorization='[REDACTED]',
            only_new_world_cycle_cross_reward=True,budget_added=False)
        atomic(STAGING/'reports/REWARD_HANDOVER.json',hand)
        oldstate=read(OLD/'reports/WORLD_SPIN_STATE.json');oldstate.update(phase='retired_saved_world_reward_handover',handover=str(STAGING/'reports/REWARD_HANDOVER.json'));atomic(OLD/'reports/WORLD_SPIN_STATE.json',oldstate)
        s.update(stage='world_reward_saved_boundary',supervisor_pid=None,training_pid=None,evaluation_pid=None,validation_pid=None,latest_checkpoint=str(ck),active_code_root=str(STAGING));atomic(ROOT/'status.json',s)
        for handle in new.helpers.LOCKS:handle.close()
        with (STAGING/'supervisor_world_drift.log').open('x') as log:
            child=subprocess.Popen([PY,str(STAGING/'supervise_world_drift.py')],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        atomic(STAGING/'reports/REWARD_CONTINUATION_LAUNCHED.json',identity(child.pid));progress('new_independent_controller_launched',parent=identity(child.pid),checkpoint=info)
    finally:
        if paused and not retired and same(parent):
            if live(trainer) and stop.exists():stop.unlink()
            os.kill(parent['pid'],signal.SIGCONT)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--watchdog':watchdog(int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]));raise SystemExit
    try:main()
    except BaseException:
        progress('attention_required',error=traceback.format_exc(),handover_exists=(STAGING/'reports/REWARD_HANDOVER.json').exists(),instruction='Preserve journal/checkpoints/budget; inspect actual children, never repeat transaction')
        raise
