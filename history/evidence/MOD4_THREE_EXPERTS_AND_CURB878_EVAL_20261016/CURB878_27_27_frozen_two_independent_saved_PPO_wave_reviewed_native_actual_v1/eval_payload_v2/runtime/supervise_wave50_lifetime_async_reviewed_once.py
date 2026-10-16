from pathlib import Path
import ast,json,time,os,argparse,traceback
import supervise_wave50_lifetime_once as parent
prior=parent.prior;D=parent.D;R=parent.R;CODE=parent.CODE;s=parent.s;read=parent.read;identity=parent.identity
def publish_or_pending(saved):
 p=R/'CANDIDATE_JOB_UNUSED_ACTUAL.json'
 if not p.exists():
  prior.write('E1_WAVE50_ASYNC_PUBLICATION_PENDING.json',dict(epoch=time.time(),own_checkpoint=prior.fullsave(saved),reason='3060 SSH unavailable before dispatch; fresh twohost unused-number admission still required',no_number_claimed=True,no_job_published=True,normal_training_not_blocked_by_eval_transport=True))
  return False
 admission=read(p);assert admission['actual_bothhost_unused'] and admission['number'] is not None
 prior.publish(saved);return True
def candidate_metadata():
 p=R/'CANDIDATE_JOB_UNUSED_ACTUAL.json';return read(p) if p.exists() else dict(number=None,actual_bothhost_unused=False)
node=next(x for x in ast.parse((D/'supervise_wave50_route_lifecycle_once.py').read_text()).body if isinstance(x,ast.FunctionDef) and x.name=='main')
class PendingPublish(ast.NodeTransformer):
 def visit_Constant(self,n):
  if isinstance(n.value,str):
   for a,b in parent.replacements.items():n.value=n.value.replace(a,b)
  return n
 def visit_Call(self,n):
  n=self.generic_visit(n)
  if isinstance(n.func,ast.Name) and n.func.id=='publish':n.func=ast.Name(id='publish_or_pending',ctx=ast.Load())
  if isinstance(n.func,ast.Name) and n.func.id=='read' and n.args and 'CANDIDATE_JOB_UNUSED_ACTUAL.json' in ast.unparse(n.args[0]):return ast.Call(func=ast.Name(id='candidate_metadata',ctx=ast.Load()),args=[],keywords=[])
  return n
prior.publish_or_pending=publish_or_pending;prior.candidate_metadata=candidate_metadata;prior.__file__=__file__
exec(compile(ast.fix_missing_locations(ast.Module(body=[PendingPublish().visit(node)],type_ignores=[])),str(__file__)+'#training-independent-of-eval-transport','exec'),vars(prior))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:prior.main()
 except BaseException:prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],original_failure_retained=True,no_blind_resume=True));raise
