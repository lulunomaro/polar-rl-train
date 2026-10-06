"""Save the actual trainer, then hold only frozen launch authority.

This is a new, PID-bound transaction. The parent accounts its own active tail;
this helper never writes the ledger or starts a GPU worker. SIGSTOP is verified
with a bounded acknowledgement wait, rather than an immediate state sample.
"""
import os,sys,time,signal,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;R=HERE/'reports';R.mkdir(exist_ok=True)
X=Path('/home/egde/rl_candidates/MOD4_ROUGH_RETENTION_SOURCE_REVIEW_20261006')
sys.path.insert(0,str(X));import continue_retention_saved_source_review_once as q
c=q.c
PID=603527;TICKS=44921376
RUN=c.P/'logs/2026-10-06_21-44-03_auto_0388_retention_mixed_learning_cap12.5664_white_v3'
INIT_SHA='0ab9aea049e390a8164515200f2b2992fd71061b398e9b60fce678e3e238a152'

def current(saved):
    if not saved:return None
    a=c.helpers.identity(saved['pid'])
    return a if a and a['start_ticks']==saved['start_ticks'] and a['state']!='Z' else None

def write(name,**kw):c.base.atomic_json(R/name,dict(epoch=time.time(),**kw))

def stop_and_ack(parent,timeout=2.0):
    """Signals are asynchronous; require the same actual stopped identity."""
    os.kill(parent['pid'],signal.SIGSTOP)
    until=time.monotonic()+timeout
    while time.monotonic()<until:
        a=current(parent)
        if a and a['state']=='T':return a
        if not a:raise AssertionError('Launch parent exited before stop acknowledgement')
        time.sleep(.02)
    raise AssertionError('Same launch parent did not acknowledge SIGSTOP within2s')

def main():
    assert not (R/'SAVE_BOUNDARY_STARTED.json').exists(),'Already executed; inspect receipts, never rerun'
    c.verify();parent=c.w.read(c.R/'SAVED_SOURCE_LAUNCHED.json');guardian=c.w.read(c.R/'RETENTION_GUARDIAN_STARTED.json')
    actual=current(dict(pid=PID,start_ticks=TICKS));assert actual and actual['cwd']==str(c.P)
    assert str(X/'isaac/mod4/train_mod4_ppo.py') in actual['argv']
    b=c.base.budget_state();assert b['active_segment']['pid']==PID and c.base.trainers()==[PID]
    m=c.w.read(RUN/'run_manifest.json');assert m['init_checkpoint_sha256']==INIT_SHA
    for n,h in m['src_sha256'].items():assert c.base.sha(RUN/'src_snapshot'/n)==h
    stop=RUN/'STOP_AFTER_SAVE';assert not stop.exists()
    write('SAVE_BOUNDARY_STARTED.json',owner=c.helpers.identity(os.getpid()),parent=parent,guardian=guardian,trainer=actual,
          run=str(RUN),source_manifest_sha256=c.base.sha(RUN/'run_manifest.json'),budget_operations=0,
          failed_previous_signal_reader_retained=True,signal_ack_timeout_s=2.0)
    with stop.open('x') as f:f.write('Authorized balanced retained-skill source progression; complete full save then stop.\n')
    write('OWN_TRAINER_SAVE_REQUESTED.json',trainer=actual,run=str(RUN),marker=str(stop),no_forced_trainer_signal=True,budget_operations=0)
    held=False;resolved=False
    try:
        limit=time.time()+1800
        while current(dict(pid=PID,start_ticks=TICKS)):
            assert time.time()<limit,'Own complete saved-stop timeout'
            time.sleep(.5)
        latest=c.w.read(RUN/'latest_complete.json');assert latest['pid']==PID and latest['log_dir']==str(RUN)
        info=c.base.checkpoint(Path(latest['checkpoint']));assert info['finite_tensors']==68
        assert Path(info['path']).parent==RUN and latest['iteration']==info['iteration_stored']
        active_log=Path(b['active_segment']['log']);text=active_log.read_text(errors='replace')
        assert '[rescue] Full checkpoint saved' in text and '[INFO]: SimulationContext cleared' in text
        while True:
            budget=c.base.budget_state();s=c.w.read(c.ctl.STATE_PATH)
            if not budget['active_segment'] and not s.get('active_training'):break
            assert time.time()<limit,'Parent has not completed its own accounting'
            time.sleep(.2)
        segments=[s for s in budget['completed_segments'] if s['pid']==PID];assert len(segments)==1
        write('OWN_TRAINER_SAVED_AND_PARENT_ACCOUNTED.json',trainer_pid=PID,own_latest_complete=latest,checkpoint=info,
              actual_segment=segments[0],parent_charged_once=True,budget_operations=0,
              new_candidate_not_claimed_paired_or_mature=True)
        while time.time()<limit:
            ident=current(parent)
            if not ident:
                write('OLD_PARENT_AT_SAVED_REVIEW.json',state=c.w.read(c.w.STATE),parent_exited=True);resolved=True;return
            state=c.w.read(c.w.STATE);worker=current(state.get('child'))
            if not worker or not str(state.get('phase','')).startswith('frozen_'):
                time.sleep(.2);continue
            assert not c.base.budget_state()['active_segment'] and not c.w.read(c.ctl.STATE_PATH).get('active_training')
            assert not c.base.trainers();assert ident['cwd']==str(c.P)
            argv=worker['argv'];assert '--checkpoint' in argv and argv[argv.index('--checkpoint')+1]==info['path']
            wchan=(Path('/proc')/str(parent['pid'])/'wchan').read_text().strip()
            if wchan not in ('hrtimer_nanosleep','clock_nanosleep'):time.sleep(.1);continue
            before=c.ctl.CANONICAL.read_bytes();c.verify();held=True;ack=stop_and_ack(parent)
            assert c.ctl.CANONICAL.read_bytes()==before
            output=Path(argv[argv.index('--output')+1])
            write('SAVED_LAUNCH_AUTHORITY_HELD.json',parent=ack,guardian=current(guardian),worker=worker,output=str(output),
                  own_checkpoint=info,budget_sha256=c.base.sha(c.ctl.CANONICAL),budget_bytes_exact=True,
                  actual_stop_acknowledged=True,worker_continues_unchanged=True,no_trainer_paused=True)
            while current(worker):time.sleep(.5)
            assert output.exists();raw=c.w.read(output)
            assert raw.get('pass_') and raw.get('actual_task_resets',0)==0 and not raw.get('nonfinite',False)
            assert raw['checkpoint_sha256']==info['sha256']
            assert c.ctl.CANONICAL.read_bytes()==before
            write('SAVED_FROZEN_WORKER_COMPLETED.json',parent=ack,guardian=current(guardian),worker=worker,
                  output=str(output),report_sha256=c.base.sha(output),own_checkpoint=info,
                  actual_segment=segments[0],budget_bytes_exact=True,review_deadline_epoch=time.time()+1200)
            deadline=time.time()+1200
            while time.time()<deadline:
                if (R/'SAFE_HANDOVER_COMPLETED.json').exists() or not current(parent):resolved=True;return
                time.sleep(1)
            return
        raise AssertionError('Frozen saved launch boundary was not reached')
    except BaseException:
        write('SAVE_BOUNDARY_ERROR_RETAINED.json',error=traceback.format_exc(),budget_operations=0)
        raise
    finally:
        if held and not resolved and current(parent):
            os.kill(parent['pid'],signal.SIGCONT)
            write('SAVE_BOUNDARY_AUTHORITY_RETURNED.json',same_verified_parent_resumed=True,budget_operations=0)

if __name__=='__main__':main()
