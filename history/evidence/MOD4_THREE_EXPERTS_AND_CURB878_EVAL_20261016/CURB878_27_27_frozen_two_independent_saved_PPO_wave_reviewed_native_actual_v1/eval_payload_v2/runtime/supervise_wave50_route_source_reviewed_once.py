"""Retain the prepared controller; additionally keep original source/expert assertions."""
import supervise_wave50_route_CPU_reviewed_once as previous
import torch,argparse,time,traceback
checked=previous.fullsave
def fullsave(path,count=20000):
 info=checked(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False)
 assert ck['independent_terrain_expert']=='E1_WAVE50' and ck['E1_WAVE50_initial_source_sha256']==previous.prior.SOURCE_SHA
 info['initial_source_and_expert_identity_exact']=True;return info
previous.prior.fullsave=fullsave
D=previous.D;R=previous.R;CODE=previous.CODE;s=previous.s;prior=previous.prior
verify=previous.verify;wait_existing=previous.wait_existing;source=previous.source;identity=previous.identity
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:prior.main()
 except BaseException:
  prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
