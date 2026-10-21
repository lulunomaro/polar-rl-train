from pathlib import Path
import json,sys,time
T=Path(__file__).resolve().parent;W=T.parent;R=T/'reports';D=T/'actual_SDK_termination_source_20261022'
assert not D.exists();D.mkdir();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
c=d.t.connect()
try:
 v=d.code(c,d.t.PY,"from pathlib import Path;import hashlib,json;B=Path('/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/managers');rows=[]\nfor name in ('termination_manager.py','manager_term_cfg.py','manager_base.py'):\n p=B/name;data=p.read_bytes();rows.append(dict(path=str(p),name=name,bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),text=data.decode('utf8')))\nprint(json.dumps(dict(files=rows,no_App_scene_or_GPU=True)))",{},timeout=30)
finally:c.close()
rows=[]
for x in v['files']:
 p=D/x['name'];p.write_text(x['text'],encoding='utf8',newline='\n');rows.append({k:value for k,value in x.items() if k!='text'})
(R/'H1_ARENA_REPAIR_ACTUAL_SDK_TERMINATION_SOURCE_CPU_RECEIPT.json').open('x',encoding='utf8').write(json.dumps(dict(epoch=time.time(),actual_installed_source=rows,no_App_scene_GPU_or_GO=True),indent=2))
print(json.dumps(dict(captured=len(rows),no_GPU=True)))
