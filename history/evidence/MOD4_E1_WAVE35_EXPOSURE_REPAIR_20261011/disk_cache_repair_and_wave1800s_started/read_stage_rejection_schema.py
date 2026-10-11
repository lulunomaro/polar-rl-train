from wave_io import *
import ast
tree=ast.parse((D/'stage_wave_exposure_cpu_once.py').read_text(encoding='utf8'))
for node in ast.walk(tree):
 if isinstance(node,ast.Constant) and isinstance(node.value,str) and node.value.startswith('from pathlib import Path\nimport sys,json,time,hashlib,torch,shutil,fcntl'):
  for k,line in enumerate(node.value.splitlines(),1):
   if 28<=k<=36:print(k,line)
v=json.loads((R/'WAVE_REUSE_PROOF_SOURCE_READONLY.json').read_bytes())
c=v['all_saved_old366_startup']['E1_COMMAND_RETENTION_STARTUP_VERIFIED.json']['value']
print(json.dumps({k:val for k,val in c.items() if not isinstance(val,(list,dict))},indent=2))
