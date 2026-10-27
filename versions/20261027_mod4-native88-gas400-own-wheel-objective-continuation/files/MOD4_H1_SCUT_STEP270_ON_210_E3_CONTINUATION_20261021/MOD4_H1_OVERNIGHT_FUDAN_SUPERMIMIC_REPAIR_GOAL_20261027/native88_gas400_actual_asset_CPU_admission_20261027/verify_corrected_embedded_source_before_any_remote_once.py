from pathlib import Path
import ast,json,time
S=Path(__file__).resolve().parent;R=S/'reports';R.mkdir(exist_ok=True)
p=S/'compose_nominal400_private_asset_with_actual_USD_CPU_unused_once.py'
t=ast.parse(p.read_bytes());parts=[n.value.value for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ('PREP','COMPOSE') for x in n.targets)]
assert len(parts)==2
for source in parts:ast.parse(source)
with (R/'LOCAL_EMBEDDED_SOURCE_AST_AND_SHELL_READER_ERRORS_CORRECTED_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),original_errors=['Outer triple-string decoded embedded byte-literal newline; AST rejected before remote','First attempted python-c correction suffered PowerShell quotation truncation before any Python operation'],correction='Preserve original bytes, add raw-string prefix via apply_patch, validate all three ASTs using this file',all3_source_AST_parsed=True,no_remote_asset_or_GPU_or_training=True),f,indent=2)
print('all3 source ASTs parsed; no actual remote/asset/GPU')
