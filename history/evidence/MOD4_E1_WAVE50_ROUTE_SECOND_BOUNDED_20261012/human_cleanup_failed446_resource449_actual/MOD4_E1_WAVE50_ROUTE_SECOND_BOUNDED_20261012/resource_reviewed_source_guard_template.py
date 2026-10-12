from pathlib import Path
import json,hashlib
from wave50_route_second_source_guard import verify_original_records,INIT_SHA,ORIGINAL35_SHA
FAILED=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012')

def verify_failed_boundary(own):
    j=lambda p:json.loads(p.read_bytes())
    end=j(FAILED/'reports/HUMAN_FAILED_END_BYTE_REVIEWED_ACTUAL.json')
    assert end['failed_child_ended'] and len(end['completed_own_segments'])==1
    for pid,start in ((3340858,94499080),(3340979,94499270)):
        p=own.identity(pid);assert not p or p['state']=='Z' or p['start_ticks']!=start
    assert not own.identity(3340947)
    b=own.s.q.base.budget_state();assert b['active_segment'] is None
    # This failed load/exit segment was charged once by its original parent.
    segments=[r for r in b['completed_segments'] if r['pid']==3340979]
    assert segments==end['completed_own_segments']
    assert not own.read(own.s.q.ctl.STATE_PATH).get('active_training') and not own.trainers()
    assert j(FAILED/'reports/POST_FAILURE_PINNED_ALLOCATION_ACTUAL.json')['passed']
    assert not list((FAILED/'learning_logs').rglob('model_*.pt'))
