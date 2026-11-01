"""Explicit continuation after pre-worker checkpoint-dictionary reader rejection."""
import json,subprocess,time
from pathlib import Path
import supervise_world_drift as new
D=new.D;R=new.R;w=new.w
assert not (R/'SOURCE_RECORD_REVIEW_CONTINUATION.json').exists()
assert not w.STATE.exists() and not new.base.budget_state()['active_segment']
new.ctl.idle();new.verify()
hand=w.read(R/'REWARD_HANDOVER.json');ck=Path(hand['checkpoint']['path'])
actual=new.base.checkpoint(ck)
assert all(actual[k]==hand['checkpoint'][k] for k in ('path','sha256','iteration_stored','finite_tensors'))
with (D/'supervisor_world_drift_source_record_review.log').open('x') as log:
    p=subprocess.Popen([new.base.PY,str(D/'supervise_world_drift.py')],cwd=w.P,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
new.base.atomic_json(R/'SOURCE_RECORD_REVIEW_CONTINUATION.json',dict(parent=new.helpers.identity(p.pid),
    source=actual,prior_error_retained=str(R/'INITIAL_SOURCE_RECORD_ERROR.txt'),
    old_attempt_no_workers_or_PPO=True,no_migration_or_budget_settlement_repeated=True,epoch=time.time()))
print(json.dumps(new.helpers.identity(p.pid)))
