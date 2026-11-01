"""Independent admission path repair; frozen original E1 controller retained."""
from pathlib import Path
import time
import supervise_e1_gentle_full_contract as w

def wait_actual_D7_boundary():
    r=w.OLD/'reports'
    while True:
        st=w.read(r/'D7_STATE.json')
        if (r/'D7_ATTENTION.json').exists():
            raise AssertionError('Actual D7 attention requires audit before new authority')
        if st['phase']=='E0_D7_saved_review_ready':
            assert (r/'D7_REVIEW_READY.json').exists()
            receipts=(st['owner'],w.read(r/'D7_GUARDIAN_STARTED.json'))
            exited=all(not (actual:=w.identity(p['pid'])) or actual['state']=='Z' or actual['start_ticks']!=p['start_ticks'] for p in receipts)
            if exited and not w.trainers() and w.s.q.base.budget_state()['active_segment'] is None and not w.read(w.s.q.ctl.STATE_PATH).get('active_training'):
                return
        w.phase('waiting_existing_D7_complete_saved_boundary',child=None,production_unchanged=True)
        time.sleep(15)

w.wait_existing=wait_actual_D7_boundary
if __name__=='__main__':
    import torch,traceback
    torch.set_num_threads(1)
    try:w.main()
    except BaseException:
        w.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(w.s.LIVE and w.s.LIVE.poll() is None),active_segment=w.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True))
        raise
