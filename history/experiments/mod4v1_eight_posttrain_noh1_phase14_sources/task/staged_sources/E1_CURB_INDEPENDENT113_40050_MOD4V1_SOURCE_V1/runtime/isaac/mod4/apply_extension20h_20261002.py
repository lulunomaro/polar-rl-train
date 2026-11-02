"""Apply this explicitly authorized addition exactly once without stopping PPO.

Pause only the verified supervisor while it is inside clock_nanosleep, outside
its ledger read/write critical section. The trainer and optimizer keep running.
"""
from pathlib import Path
import json,os,signal,sys,time,subprocess

ROOT=Path('/home/egde/rl_candidates/MOD4_scut_spin_stage1_20261002')
CANONICAL=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
ID='USER_ADD20H_20261002_1520'
SECONDS=72000
REPORTS=ROOT/'reports';RECEIPT=REPORTS/(ID+'_APPLIED.json')
sys.path.insert(0,str(ROOT/'isaac/mod4'))
from budget_authority import validate_budget
SUDO_INPUT=None


def read(path):return json.loads(path.read_text())


def atomic(path,data):
    temp=path.with_name(path.name+'.'+ID+'.partial')
    temp.write_text(json.dumps(data,indent=2),encoding='utf8');os.replace(temp,path)


def identity(pid):
    p=Path('/proc')/str(pid)
    try:
        st=(p/'stat').read_text().rsplit(')',1)[1].split()
        return dict(pid=pid,state=st[0],start_ticks=int(st[19]),cwd=str((p/'cwd').resolve()),
                    argv=[v.decode() for v in (p/'cmdline').read_bytes().split(b'\0') if v])
    except (OSError,ValueError):return None


def read_syscall(proc):
    global SUDO_INPUT
    path=proc/'syscall'
    try:return path.read_text()
    except PermissionError:
        # Read only this verified same-account supervisor. Never run the ledger
        # transaction as root: its files must stay writable by the trainer account.
        if SUDO_INPUT is None:
            SUDO_INPUT=sys.stdin.readline().rstrip('\n')
            assert SUDO_INPUT,'read-only process inspection authentication unavailable'
        command=['sudo','-S','-p','','cat',str(path)]
        p=subprocess.run(command,input=SUDO_INPUT+'\n',text=True,capture_output=True,timeout=5)
        assert p.returncode==0,'read-only syscall inspection failed'
        return p.stdout


def main():
    b=read(CANONICAL);validate_budget(b)
    matches=[e for e in b.get('budget_extensions',[]) if e['extension_id']==ID]
    if matches:
        assert len(matches)==1 and matches[0]['additional_training_seconds']==SECONDS
        assert b['authorized_training_seconds']==180000
        if not RECEIPT.exists():
            atomic(RECEIPT,dict(extension_id=ID,additional_training_seconds=SECONDS,
                recovered_receipt=True,authorization_basis='explicit_user_request',
                authorized_training_seconds=b['authorized_training_seconds'],budget_mutated_again=False))
        print('ALREADY_APPLIED',json.dumps(read(RECEIPT)),flush=True);return
    assert b['authorized_training_seconds']==108000,'different budget requires inspection'
    s=read(ROOT/'status.json');parent=identity(int(s['supervisor_pid']));trainer=identity(int(s['training_pid']))
    assert parent and trainer and parent['cwd']==str(ROOT) and trainer['cwd']==str(ROOT)
    assert any(a.endswith('/supervise_spin.py') for a in parent['argv'])
    assert any(a.endswith('/train_mod4_ppo.py') for a in trainer['argv'])
    assert s['stage']=='training' and s['training_phase']=='trial_45min'
    assert b['active_segment']['pid']==trainer['pid'] and b['owner_root']==str(ROOT)
    paused=False;sleep_evidence=None
    try:
        for _ in range(200):
            proc=Path('/proc')/str(parent['pid']);current=identity(parent['pid'])
            assert current and current['start_ticks']==parent['start_ticks'],'supervisor identity changed'
            before=read_syscall(proc)
            if before.split()[0]!='230':time.sleep(.05);continue
            # x86_64 clock_nanosleep: sole deliberate sleep in the active training loop.
            os.kill(parent['pid'],signal.SIGSTOP);paused=True
            for _ in range(100):
                current=identity(parent['pid'])
                if current['state'] in ('T','t'):break
                time.sleep(.005)
            after=read_syscall(proc)
            if current['state'] in ('T','t') and after.split()[0]=='230':
                sleep_evidence=dict(before=before.strip(),stopped=after.strip(),state=current['state']);break
            os.kill(parent['pid'],signal.SIGCONT);paused=False;time.sleep(.05)
        assert paused and sleep_evidence,'could not establish safe ledger-write pause'
        b=read(CANONICAL);validate_budget(b)
        assert b['authorized_training_seconds']==108000 and b['active_segment']['pid']==trainer['pid']
        assert not any(e['extension_id']==ID for e in b.get('budget_extensions',[]))
        assert identity(trainer['pid'])['start_ticks']==trainer['start_ticks']
        atomic(REPORTS/(ID+'_LEDGER_BEFORE.json'),b)
        atomic(REPORTS/(ID+'_STATUS_BEFORE.json'),s)
        charged=float(b['charged_training_seconds']);now=time.time()
        extension=dict(extension_id=ID,additional_training_seconds=SECONDS,
            authorization_basis='explicit_user_request',authorization='User: 预算再添加20小时',
            requested_epoch=now,applied_epoch=now,state='applied')
        b.setdefault('budget_extensions',[]).append(extension)
        b['authorized_training_seconds']+=SECONDS
        b['remaining_training_seconds']=b['authorized_training_seconds']-charged
        b['deadline_epoch']=float(b['deadline_epoch'])+SECONDS
        b['latest_explicit_extension_receipt']=str(RECEIPT)
        validate_budget(b);assert charged==float(b['charged_training_seconds'])
        atomic(CANONICAL,b)
        result=dict(extension_id=ID,additional_training_seconds=SECONDS,
            authorization_basis='explicit_user_request',authorized_training_seconds=b['authorized_training_seconds'],
            charged_training_seconds_preserved=charged,remaining_training_seconds=b['remaining_training_seconds'],
            canonical_budget=str(CANONICAL),deadline_epoch=b['deadline_epoch'],
            current_trial_deadline_unchanged=s['trainer_deadline_epoch'],
            trainer=trainer,supervisor=parent,supervisor_pause_outside_ledger_write=sleep_evidence,
            training_interrupted=False,checkpoint_or_optimizer_reset=False,
            status_cache_note='Current 45min phase keeps its acceptance deadline; next training phase reads updated total dynamically. TUI already reads canonical total and remaining.',
            applied_epoch=now)
        atomic(RECEIPT,result);print('APPLIED',json.dumps(result),flush=True)
    finally:
        if paused:
            current=identity(parent['pid'])
            if current and current['start_ticks']==parent['start_ticks']:os.kill(parent['pid'],signal.SIGCONT)


if __name__=='__main__':main()
