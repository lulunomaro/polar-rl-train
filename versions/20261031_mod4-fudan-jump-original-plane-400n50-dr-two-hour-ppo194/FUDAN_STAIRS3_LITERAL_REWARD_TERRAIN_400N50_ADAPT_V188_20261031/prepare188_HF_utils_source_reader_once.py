from pathlib import Path
import ast
N=Path(__file__).resolve().parent
p=N/'capture188_target_HF_and_original_step_sources_once.py';s=p.read_text(encoding='utf8');t=ast.parse(s)
n=next(x for x in t.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='REMOTE' for y in x.targets))
r="""from pathlib import Path
import importlib.util,json,time,hashlib
root=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))/'terrains/height_field/utils'
paths=sorted(root.rglob('*.py'));assert len(paths)<=12
rows=[]
for p in paths:
 b=p.read_bytes();assert len(b)<200000;rows.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8'),byte_reads=1))
assert rows,'Installed heightfield utils source directory absent'
print(json.dumps(dict(epoch=time.time(),purpose='Exact installed heightfield-to-triangle geometry conversion used by selected Fudan staircase SDK bridge',files=rows,source_files_read=len(rows),model_reads=0,SDK_Torch_imports=0,no_remote_writes=True)))
"""
lines=s.splitlines(keepends=True);s=''.join(lines[:n.lineno-1])+('REMOTE='+repr(r)+'\n')+''.join(lines[n.end_lineno:])
s=s.replace('ROOT188API','ROOT188HF').replace('capture188_target_HF_and_original_step_sources_once','capture188_target_HF_utils_sources_once')
ast.parse(s);(N/'capture188_target_HF_utils_sources_once.py').write_text(s,encoding='utf8')
