"""Explicit continuation after installer-lock race, before any worker or PPO."""
import argparse
from pathlib import Path
import supervise_retention_train as c
c.ENTRY=Path(__file__).resolve()
original_status=c.status
def status(stage=None,**kw):
    if 'repair_training_started' not in kw:
        active=c.ctl.S.get('active_training')
        kw['repair_training_started']=bool(active and active['phase']=='retention_mixed_learning')
    original_status(stage,**kw)
c.status=c.w.status=c.ctl.status=status
def continuation():
    assert not c.w.STATE.exists() and not (c.R/'RETENTION_TRAIN_STARTED.json').exists()
    old=c.w.read(c.R/'RETENTION_TRAIN_LAUNCHED.json');actual=c.helpers.identity(old['pid'])
    assert not actual or actual['state']=='Z' or actual['start_ticks']!=old['start_ticks']
    text=(c.H/'retention_train_supervisor.log').read_text()
    assert 'BlockingIOError: [Errno 11] Resource temporarily unavailable' in text
    assert c.base.sha(c.ctl.CANONICAL)==c.w.read(c.R/'RETENTION_INSTALL_BOUNDARY.json')['budget_sha256']
    assert not c.base.budget_state()['active_segment'] and not c.base.trainers()
    c.base.atomic_json(c.R/'LOCK_RACE_REVIEW.json',dict(old_parent=old,old_error_log_sha256=c.base.sha(c.H/'retention_train_supervisor.log'),failure_before_state_worker_PPO=True,budget_bytes_exact=True,repair='Installer releases both verified locks before dispatch; new sole controller reacquires them',old_main_not_relaunched=True))
    c.controller()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
    if a.guardian:c.guardian(int(a.guardian[0]),a.guardian[1])
    else:continuation()
