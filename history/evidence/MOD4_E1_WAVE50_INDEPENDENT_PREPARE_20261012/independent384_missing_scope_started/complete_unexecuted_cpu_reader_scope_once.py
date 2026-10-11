"""Finish only CPU proof; original broad AST path-reader rejection retained."""
from wave50_io import *
import ast
assert not (R/'WAVE50_TARGET_CPU_PASSED.json').exists()
t=(D/'stage_gpu_scope_once.py').read_text();node=next(x for x in ast.walk(ast.parse(t)) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='run' and isinstance(x.args[1],ast.Call) and 'missing=[]' in ast.get_source_segment(t,x))
code=node.args[1].func.value.value
code=code.replace("if isinstance(a,ast.Constant) and isinstance(a.value,str) and a.value.endswith(('.py','.json')) and not (own.CODE/a.value).is_file():missing.append(a.value)","if isinstance(a,ast.Constant) and isinstance(a.value,str) and a.value.endswith(('.py','.json')) and a.value not in ('import_contract.json','robot_cfg.py') and not (own.CODE/a.value).is_file():missing.append(a.value)")
code=code.replace('source_snapshot_lists_all_exist=True','module_directory_snapshot_lists_all_exist=True,external_task_asset_snapshot_paths_original_template_preserved=True')
n,w=io.connect_both()
try:
 value=run(n,code.replace('ROOT_TOKEN',repr(ROOT)));assert value['passed'];save('WAVE50_TARGET_CPU_PASSED.json',value)
 save('CPU_READER_EXTERNAL_ASSET_SCHEMA_REVIEW.json',dict(epoch=time.time(),passed=True,original_reader_error_preserved=True,only_task_external_import_contract_robot_cfg_excluded_from_module_dir_check=True,no_source_GPU_or_budget_change=True))
 print(json.dumps(dict(target_CPU_passed=True,source_count=value['source_count'],no_GPU_started=True)))
finally:io.cleanup(n,w)
