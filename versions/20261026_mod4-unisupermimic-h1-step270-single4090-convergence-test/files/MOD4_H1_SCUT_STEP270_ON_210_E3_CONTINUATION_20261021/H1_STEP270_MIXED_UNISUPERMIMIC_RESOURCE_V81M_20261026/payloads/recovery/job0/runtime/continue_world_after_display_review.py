"""Unique continuation after reviewed display-only source change; no probe replay."""
import json,subprocess,time,sys
from pathlib import Path
import supervise_world_spin as w
R=w.R;read=w.read
assert not (R/'DISPLAY_CONTINUATION_LAUNCHED.json').exists(),'Continuation already attempted; inspect, never rerun'
before=read(w.STATE)
assert before['phase']=='repair_hold' and 'AssertionError: isaac/mod4/tui_spin_rate.py' in before['reason']
assert not w.helpers.identity(before['owner']['pid'])
assert not w.helpers.identity(read(R/'WORLD_GUARDIAN_STARTED.json')['pid'])
assert not w.helpers.identity(before['child']['pid'])
w.ctl.S=read(w.ctl.STATE_PATH);w.base.STATE.update(read(w.P/'status.json'))
w.ctl.idle();w.verify()
w.helpers.acquire(w.P/'autonomy_controller.lock');w.helpers.acquire(w.ctl.CANONICAL.parent/'native_floor_supervisor.lock')
budget_bytes=w.ctl.CANONICAL.read_bytes();budget=w.base.budget_state()
assert w.base.sha(w.ctl.CANONICAL)==read(R/'WORLD_CONTROLLER_INSTALL.json')['ledger_sha256']
assert budget['charged_training_seconds']==255462.13132548332 and budget['active_segment'] is None
source=Path(read(w.P/'reports/AUTONOMY_FINISHED.json')['checkpoint']['path'])
assert w.base.checkpoint(source)==before['last_validated_source']
reuse=dict(fullscale=str(w.P/'reports/auto_0148_world_20k_cap12.5664_white_v2.json'),flat=str(w.P/'reports/auto_0149_world_flat_cap12.5664_white_v2.json'))
assert w.fullscale(read(Path(reuse['fullscale'])))['pass_'] and w.assess_flat(read(Path(reuse['flat'])))['pass_']
assert w.ctl.CANONICAL.read_bytes()==budget_bytes
w.base.atomic_json(R/'DISPLAY_HOLD_RETAINED.json',before)
w.phase('world_preflight_continued_after_display_review',owner=w.helpers.identity(__import__('os').getpid()),source=w.base.checkpoint(source),
        reused_completed_reports=reuse,no_repeated_probe_or_budget_settlement=True)
with (w.D/'guardian_world_spin_display_continuation.log').open('x') as log:
 g=subprocess.Popen([w.base.PY,str(w.D/'supervise_world_spin.py'),'--guardian',str(__import__('os').getpid()),str(w.helpers.identity(__import__('os').getpid())['start_ticks'])],cwd=w.P,
                    stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
w.base.atomic_json(R/'DISPLAY_CONTINUATION_GUARDIAN_STARTED.json',w.helpers.identity(g.pid))
w.base.atomic_json(R/'DISPLAY_CONTINUATION_LAUNCHED.json',dict(owner=w.helpers.identity(__import__('os').getpid()),guardian=w.helpers.identity(g.pid),source=w.base.checkpoint(source),reused_reports=reuse,
                  no_PPO_yet=True,original_entry_not_rerun=True,ledger_bytes_exact=True,started_epoch=time.time()))
w.run_lesson(source,source,reused_prelude=reuse)
