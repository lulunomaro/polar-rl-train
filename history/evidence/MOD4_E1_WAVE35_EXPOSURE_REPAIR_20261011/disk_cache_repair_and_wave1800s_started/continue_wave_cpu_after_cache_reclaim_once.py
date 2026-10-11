"""First stage stopped before creating any root; continue only that unperformed work."""
from wave_io import *
import ast
assert (R/'WAVE_STAGE_STARTED.json').exists()
assert list(R.glob('WAVE_STAGE_CPU_REJECTED_*.json'))
cache=json.loads((R/'WAVE_CACHE_RECLAIM_ACTUAL.json').read_bytes());assert cache['completed'] and cache['free_after_bytes']>12*1024**3
assert not (R/'WAVE_CPU_AFTER_CACHE_STARTED.json').exists()
save('WAVE_CPU_AFTER_CACHE_STARTED.json',dict(epoch=time.time(),original_preGPU_resource_rejection_preserved=True,old_root_not_created_before_rejection=True,only_unperformed_new_root_CPU_admission_continued=True,no_GPU_or_old_stage_replay=True))
tree=ast.parse((D/'stage_wave_exposure_cpu_once.py').read_text(encoding='utf8'))
fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
assert isinstance(fn.body[0],ast.Assert) and isinstance(fn.body[1],ast.Expr)
fn.body=fn.body[2:]
module=ast.Module(body=[fn],type_ignores=[])
exec(compile(ast.fix_missing_locations(module),str(Path(__file__))+'::unperformed_root_and_CPU_admission','exec'),globals())
if __name__=='__main__':
 try:main()
 except BaseException:save('WAVE_CPU_AFTER_CACHE_REJECTED_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),original_rejection_and_source_preserved=True));raise
