from pathlib import Path
import sys,json,time,traceback,hashlib
B=Path(__file__).resolve().parent;R=B/'reports';sys.path.insert(0,str(B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
code=r'''
from pathlib import Path
import importlib.util,importlib.metadata as md,json,hashlib,sys,time,os
root=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));rows=[]
for name in ('scene/interactive_scene.py','sim/spawners/meshes/meshes.py','sim/spawners/from_files/from_files.py'):
 p=root/name;raw=p.read_bytes();rows.append(dict(relative=name,path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8')))
print(json.dumps(dict(epoch=time.time(),python=sys.executable,actual_packages={n:md.version(n) for n in ('torch','isaacsim','isaaclab','rsl-rl-lib')},sources=rows,CPU_file_read_only=True,no_app_GPU_or_process_or_current_training_or_account_change=True)))
'''
try:
 c=d.t.connect()
 try:v=d.code(c,d.t.PY,code,{},timeout=45)
 finally:c.close()
 D=B/'sdk210_source_snapshot_unmodified';D.mkdir()
 for row in v['sources']:
  p=D/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);raw=row.pop('text').encode();assert hashlib.sha256(raw).hexdigest()==row['SHA'];p.open('xb').write(raw);row['local_path']=str(p)
 (R/'SOURCE210_ACTUAL_SDK_TERRAIN_SPAWNER_CPU_READBACK_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(v,indent=2));print(json.dumps(v))
except BaseException:
 (R/'SOURCE210_SDK_READBACK_ORIGINAL_ERROR.json').open('x',encoding='utf8').write(json.dumps(dict(error=traceback.format_exc(),no_replay=True),indent=2));raise
