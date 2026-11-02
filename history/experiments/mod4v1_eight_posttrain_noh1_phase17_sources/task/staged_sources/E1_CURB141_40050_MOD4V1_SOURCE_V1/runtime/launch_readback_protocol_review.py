"""Explicit review: reuse a completed 22env reward audit, keep 88env regressions."""
import json,subprocess,time
from pathlib import Path
import supervise_world_drift as new
D=new.D;R=new.R;w=new.w
assert not (R/'READBACK_PROTOCOL_REVIEW.json').exists()
new.ctl.idle();new.verify()
state=w.read(w.STATE);assert state['phase']=='repair_hold' and 'group_samples_incomplete' in state['reason']
assert not new.base.budget_state()['active_segment']
old=w.read(R/'SOURCE_RECORD_REVIEW_CONTINUATION.json')['parent'];actual=new.helpers.identity(old['pid'])
assert not actual or actual.get('state')=='Z' or actual['start_ticks']!=old['start_ticks']
source=w.read(R/'REWARD_HANDOVER.json')['checkpoint'];off=w.read(R/'REWARD_READBACK_off.json')
assert off['checkpoint']==source['path'] and off['steps']==1500 and off['seconds']==15 and len(off['alive'])==22
original=w.evidence(off,'spin',15.);reviewed=w.evidence(off,'spin',3.)
assert original['reasons']==['group_samples_incomplete'] and reviewed['pass_']
assert not (R/'REWARD_READBACK_cycle_v1.json').exists()
new.base.atomic_json(R/'READBACK_PROTOCOL_HELD_STATE.json',state)
new.base.atomic_json(R/'READBACK_PROTOCOL_REVIEW.json',dict(only_readback_group_count_contract_corrected=True,
    completed_off_reused=True,original_formal_88env_verdict=original,readback_22env_15s_verdict=reviewed,
    formal_regression_88env_gate_unchanged=True,budget_sha256=new.base.sha(new.ctl.CANONICAL),prior_parent=old,source=source,epoch=time.time()))
with (D/'supervisor_world_drift_readback_review.log').open('x') as log:
    p=subprocess.Popen([new.base.PY,str(D/'supervise_world_drift.py'),'--readback-review-continuation'],cwd=w.P,
        stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
new.base.atomic_json(R/'READBACK_PROTOCOL_CONTINUATION_LAUNCHED.json',new.helpers.identity(p.pid))
print(json.dumps(new.helpers.identity(p.pid)))
