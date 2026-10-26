"""Reviewed admission wrapper; original378 source retained, no original main replay."""
import supervise_curb20_fullstate_once as prior
from curb20_fullsave_cpu import fullsave as complete_validation
def fullsave(path,count=20000):
 import torch
 info=complete_validation(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False)
 assert ck['independent_terrain_expert']=='E1_CURB' and ck['E1_CURB_initial_source_sha256']==prior.SOURCE_SHA
 return info
prior.fullsave=fullsave
old_phase=prior.phase
def phase(name,**kw):
 if name=='bounded_E1_G3_command_retention_learning':name='bounded_E1_CURB20_independent_learning'
 old_phase(name,**kw)
prior.phase=phase
if __name__=='__main__':
 import argparse,time,traceback
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:prior.main()
 except BaseException:
  prior.write('E1_REVIEWED_CONTROLLER_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(prior.s.LIVE and prior.s.LIVE.poll() is None),active_segment=prior.s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
