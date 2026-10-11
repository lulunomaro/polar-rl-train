"""Retain existing decisions; new immutable snapshots for the unperformed root/CPU work."""
from wave_io import *
import ast
assert list(R.glob('WAVE_CPU_AFTER_CACHE_REJECTED_*.json'))
assert not (R/'WAVE_TARGET_CPU_PASSED.json').exists()
assert json.loads((R/'WAVE_CACHE_RECLAIM_ACTUAL.json').read_bytes())['free_after_bytes']>12*1024**3
assert not (R/'WAVE_MISSING_ROOT_CPU_STARTED.json').exists()
save('WAVE_MISSING_ROOT_CPU_STARTED.json',dict(epoch=time.time(),original_resource_and_duplicate_snapshot_rejections_preserved=True,only_unperformed_root_CPU_work=True,no_old_GPU_or_stage_replay=True))
tree=ast.parse((D/'stage_wave_exposure_cpu_once.py').read_text(encoding='utf8'))
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main');fn.body=fn.body[2:]
renamed=0
for node in ast.walk(fn):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='save' and node.args and isinstance(node.args[0],ast.Constant):
  value=node.args[0].value
  if value in ('WAVE_EXPOSURE_DURATION_DECISION.json','WAVE_CANDIDATE142_UNUSED_ACTUAL.json'):
   node.args[0].value=value.replace('.json','_AFTER_CACHE.json');renamed+=1
assert renamed==2
exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(Path(__file__))+'::missing_root_and_CPU','exec'),globals())
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_MISSING_ROOT_CPU_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),all_previous_false_and_reports_preserved=True));raise
