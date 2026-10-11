"""CPU fixture loads exact reset-cache AST; simulator configure imports require AppLauncher."""
from entry_io import *
import ast
def main():
 assert (R/'SOURCE_FREEZE.json').exists() and not (R/'ENTRY_TARGET_CPU_PASSED.json').exists()
 source=(D/'stage_entry_and_target_cpu_once.py').read_text();tree=ast.parse(source)
 blocks=[x.value for x in ast.walk(tree) if isinstance(x,ast.Constant) and isinstance(x.value,str) and x.value.startswith('from pathlib import Path\nimport sys,json,time,torch,ast,contextlib')];assert len(blocks)==1
 code=blocks[0].replace('ROOT_TOKEN',repr(ROOT))
 prefix='''import types
runtime_path=own.CODE/'wave50_entry_runtime.py';tree=ast.parse(runtime_path.read_text())
tree.body=[node for node in tree.body if not (isinstance(node,ast.ImportFrom) and node.module=='g4_retention_runtime')]
runtime=types.ModuleType('wave50_entry_runtime');runtime.__file__=str(runtime_path)
exec(compile(ast.fix_missing_locations(tree),str(runtime_path)+'::exact_CPU_cache_function','exec'),runtime.__dict__)
sys.modules['wave50_entry_runtime']=runtime
'''
 code=code.replace('import test_wave50_entry_target_cpu as test',prefix+'import test_wave50_entry_target_cpu as test')
 code=code.replace('no_GPU_or_budget_write=True)', 'no_GPU_or_budget_write=True,CPU_fixture_used_exact_reset_cache_AST=True,simulator_configuration_import_deferred_until_AppLauncher=True)')
 n,w=io.connect_both()
 try:
  v=run(n,code);save('ENTRY_TARGET_CPU_PASSED.json',v);print(json.dumps(dict(passed=v['passed'],source_count=v['source_count'],actual_GPU_pending=True)))
 finally:io.cleanup(n,w)
if __name__=='__main__':
 try:main()
 except BaseException:save('TARGET_CPU_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_source_hotpatch=True));raise
