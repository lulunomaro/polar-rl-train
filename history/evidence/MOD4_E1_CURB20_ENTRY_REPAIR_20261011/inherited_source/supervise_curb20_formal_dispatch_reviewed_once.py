"""Correct reviewed389 main. Never dispatch preserved historical controller."""
import argparse
from pathlib import Path
import supervise_curb20_split_state_admission_once as own
old_wait=own.wait_existing
OLD=Path('/home/egde/rl_candidates/MOD4_S3_E1_CURB20_SPLIT_STATE_ADMITTED_20261011')
def actual_old388_exited():
 st=own.read(OLD/'reports/E1_STATE.json')
 for loc in [st['owner'],st['child'],own.read(OLD/'reports/E1_GUARDIAN_STARTED.json')]:
  a=own.identity(loc['pid']);assert not a or a['state']=='Z' or a['start_ticks']!=loc['start_ticks'],'Own old388 still alive; protect natural exit'
 att=own.read(OLD/'reports/E1_ATTENTION.json');assert not att['own_child_still_alive'] and att['active_segment'] is None
def wait_existing():
 old_wait();actual_old388_exited()
own.wait_existing=wait_existing
if __name__=='__main__':
 import traceback,time
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:own.previous.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:own.main()
 except BaseException:
  own.write('E1_FORMAL_DISPATCH_REVIEWED_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(own.s.LIVE and own.s.LIVE.poll() is None),active_segment=own.s.q.base.budget_state()['active_segment'],do_not_blind_resume=True));raise
