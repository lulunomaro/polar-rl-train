"""Immutable prepared controller reused; all own fullsave validation pins parent SHA."""
import supervise_wave50_route_lifecycle_once as prior
from wave50_route_fullsave_CPU_parent_reviewed import fullsave as checked
def fullsave(path,count=20000):
 info=checked(path,count=count)
 assert info['route_lifecycle_state_verified'] and info['parent_route_boundary_source_CPU_exact']
 return info
prior.fullsave=fullsave
D=prior.D;R=prior.R;CODE=prior.CODE;s=prior.s
verify=prior.verify;wait_existing=prior.wait_existing;source=prior.source;identity=prior.identity
if __name__=='__main__':
 import argparse,traceback,time
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:prior.main()
 except BaseException:
  prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
