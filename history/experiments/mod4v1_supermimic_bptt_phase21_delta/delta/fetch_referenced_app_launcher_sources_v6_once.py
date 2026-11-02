"""Read the exact SDK app-launcher Python directory after real class-pin mismatch.
Source only, no imports/SDK instance/GPU/checkpoint/C/GO or process changes.
"""
from pathlib import Path
import sys,json,hashlib
R=Path(__file__).resolve().parent;out=R/'reports/SDK_ACTUAL_APP_LAUNCHER_SOURCES_V6.json';D=R/'discovery/sdk_app_launcher_actual_v6';assert not out.exists()and not D.exists();D.mkdir(parents=True);base='/home/lc01/Zonglin Li/zonglin2/src/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/app';sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();rows=[]
try:
 names=sorted(s.listdir(base));selected=[n for n in names if n.endswith('.py')];assert 1<=len(selected)<=20
 for name in selected:
  assert '/'not in name and'\\'not in name
  with s.open(base+'/'+name,'rb')as f:raw=f.read()
  assert len(raw)<1_000_000;(D/name).write_bytes(raw);rows.append(dict(remote=base+'/'+name,path=str(D/name),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
 value=dict(kind='REFERENCED_ACTUAL_APPLAUNCHER_CLASS_BRANCH_SOURCE_ONLY_V6',bounded_directory_names=names,files=rows,reason='V5 actual application exact class differs; past exact class not published, inspect referenced creation branch before new binding implementation',actual_native_instance_observation=None,SDK_GPU_PT_C_GO_or_mutation_operations=0);out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2))
finally:s.close();c.close()
