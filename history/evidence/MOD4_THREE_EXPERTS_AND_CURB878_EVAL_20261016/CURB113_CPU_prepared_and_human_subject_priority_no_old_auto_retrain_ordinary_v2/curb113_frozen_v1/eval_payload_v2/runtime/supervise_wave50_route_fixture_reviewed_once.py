"""Independent root continues only missing fixture/native admission, old failure retained."""
from pathlib import Path
import ast,argparse,time,traceback
import supervise_wave50_route_source_reviewed_once as original
prior=original.prior
source=(Path(__file__).with_name('supervise_wave50_route_lifecycle_once.py')).read_text()
node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='native_contract')
class NewFixtureEntry(ast.NodeTransformer):
 def visit_Constant(self,n):
  if n.value=='native_e1_wave50_route_lifecycle_scope_probe.py':n.value='native_e1_wave50_route_fixture_v2_scope_probe.py'
  return n
exec(compile(ast.fix_missing_locations(ast.Module(body=[NewFixtureEntry().visit(node)],type_ignores=[])),str(Path(__file__))+'#independent-native-fixture-entry', 'exec'),vars(prior))
D=original.D;R=original.R;CODE=original.CODE;s=original.s
verify=original.verify;wait_existing=original.wait_existing;source=original.source;identity=original.identity;fullsave=original.fullsave
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--guardian',nargs=2);a=p.parse_args()
 try:
  if a.guardian:prior.guardian(int(a.guardian[0]),int(a.guardian[1]))
  else:prior.main()
 except BaseException:
  prior.write('E1_ATTENTION.json',dict(epoch=time.time(),error=traceback.format_exc(),own_child_still_alive=bool(s.LIVE and s.LIVE.poll() is None),active_segment=s.q.base.budget_state()['active_segment'],all_weights_retained=True,no_blind_resume=True));raise
