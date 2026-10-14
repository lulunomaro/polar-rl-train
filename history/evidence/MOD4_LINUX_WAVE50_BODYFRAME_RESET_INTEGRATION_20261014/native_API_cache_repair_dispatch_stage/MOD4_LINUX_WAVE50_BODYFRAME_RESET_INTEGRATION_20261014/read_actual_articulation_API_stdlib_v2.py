"""Independent stdlib-only source reader; previous missing-rg error retained."""
from pathlib import Path
import ast,json
import transport_bodyframe_pipeline_v2 as t

script=Path(__file__).with_name('read_actual_articulation_API_after_v2_error.py')
tree=ast.parse(script.read_bytes())
CODE=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='CODE' for x in n.targets))
CODE=CODE.replace('import json,subprocess,hashlib,shutil,psutil,fcntl','import json,subprocess,hashlib,shutil,psutil,fcntl,os')
old=" p=subprocess.run(['rg','-l','-g','*.py','class ArticulationView|def root_link_pose_w|def root_state_w',base],capture_output=True,text=True,timeout=40)\n for name in p.stdout.splitlines()[:30]:"
new=" names=[]\n for parent,dirs,files in os.walk(base):\n  dirs[:]=[d for d in dirs if d!='__pycache__']\n  for name in files:\n   if name in ('api.py','articulation_data.py','articulation_view.py'):\n    p=Path(parent)/name;text=p.read_text(errors='replace')\n    if 'class ArticulationView' in text or 'def root_link_pose_w' in text or 'def root_state_w' in text:names.append(str(p))\n for name in names[:30]:"
assert CODE.count(old)==1;CODE=CODE.replace(old,new)
c=None
try:
 c=t.connect();value,p=t.run(c,CODE,dict(root=t.ROOT),'ARTICULATION_ACTUAL_INSTALLED_SOURCE_STDLIB_V2',timeout=120)
 print(json.dumps(dict(report=str(p),files=[dict(path=x['path'],hits=x['hits']) for x in value['actual_installed_sources']],original13_count=len(value['original_startup_proofs']))))
finally:t.close(c)
