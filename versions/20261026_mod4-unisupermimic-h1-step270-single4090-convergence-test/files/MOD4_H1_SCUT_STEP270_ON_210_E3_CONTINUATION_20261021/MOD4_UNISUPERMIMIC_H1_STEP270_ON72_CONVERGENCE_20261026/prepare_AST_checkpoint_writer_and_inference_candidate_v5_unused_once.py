"""AST-only private bridge edit; tolerate original CRLF/blank-line formatting."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import shutil
import time

H=Path(__file__).resolve().parent;T=H.parent
O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026'
D=H/'candidate_source_v5';assert not D.exists();shutil.copytree(O/'payloads/e2/source',D,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
p=D/'h1_supermimic_bridge_v1.py';raw=p.read_bytes();tree=ast.parse(raw.decode('utf8'))
original=copy.deepcopy(tree)
run=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='run')
index=next(i for i,n in enumerate(run.body) if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Tuple) and [a.id for a in n.targets[0].elts]==['B','J','out'])
run.body.insert(index+1,ast.parse('runner.logger.writer=None').body[0])
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='H1Bridge')
for name in ('pack','current','before_action','step'):
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name);assert not fn.decorator_list
    fn.decorator_list=[ast.parse('torch.inference_mode()',mode='eval').body]
outer=next(n for n in run.body if isinstance(n,ast.Try) and n.finalbody)
assert len(outer.finalbody)==5
save=outer.finalbody[2];assert ast.unparse(save)=='save(str(path))'
handler=ast.parse("try:\n save(str(path))\nexcept BaseException:\n put(out/'NATIVE_FULLSAVE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_primary_learning_error_preserved=failed,partial_file_retained=True))\n if not failed:raise\nelse:\n pass\n").body[0]
handler.body=[save];handler.orelse=outer.finalbody[3:]
outer.finalbody=outer.finalbody[:2]+[handler]
ast.fix_missing_locations(tree)
p.write_text(ast.unparse(tree)+'\n','utf8',newline='\n')
verify=copy.deepcopy(tree);vrun=next(n for n in verify.body if isinstance(n,ast.FunctionDef) and n.name=='run')
vrun.body.pop(index+1)
vcls=next(n for n in verify.body if isinstance(n,ast.ClassDef) and n.name=='H1Bridge')
for fn in vcls.body:
    if isinstance(fn,ast.FunctionDef) and fn.name in ('pack','current','before_action','step'):fn.decorator_list=[]
vouter=next(n for n in vrun.body if isinstance(n,ast.Try) and n.finalbody)
vinner=vouter.finalbody[-1];vouter.finalbody=vouter.finalbody[:2]+vinner.body+vinner.orelse
assert ast.dump(verify,include_attributes=False)==ast.dump(original,include_attributes=False)
with (H/'reports/AST_CANDIDATE_V5_CHECKPOINT_BOOTSTRAP_AND_SAMPLING_CONTEXT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),candidate=str(D),original_bridge_SHA=hashlib.sha256(raw).hexdigest(),candidate_bridge_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),only_writer_initialization_four_physical_context_decorators_and_error_preserving_fullsave_handler_AST_changes=True,all_other_private_bridge_logic_AST_exact=True,original_V4_builder_failed_matching_adjacent_lines_separated_by_blank_lines=True,original_V4_followon_CPU_StopIteration_retained=True,no_qualified_metadata_or_original_plant_files_normalized=True,not_installed_or_GO=True),f,indent=2)
print(json.dumps(dict(AST_candidate_v5_ready=True,all_other_AST_exact=True)))
