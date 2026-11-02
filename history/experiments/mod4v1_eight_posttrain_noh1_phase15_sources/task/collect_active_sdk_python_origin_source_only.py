"""Read exactactiveprojectlauncher+Pythonmoduleorigin metadata only; no isaaclab import, App/GPU/model/raw/budget."""
from pathlib import Path
import json,hashlib,shlex
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1';assert not D.exists();D.mkdir();B='/home/lc01/Zonglin Li/zonglin2';c=connect72();s=c.open_sftp()
try:
 with s.open(B+'/run-python.sh','rb')as f:raw=f.read()
 (D/'run-python.sh').write_bytes(raw)
 code="import sys,json,importlib.metadata as m;v={'sys_path':sys.path,'distributions':{}};names=['isaaclab','isaacsim','roboticslab'];\nfor n in names:\n try:\n  d=m.distribution(n);v['distributions'][n]={'version':d.version,'base':str(d.locate_file('')),'metadata_path':str(d._path),'direct_url':d.read_text('direct_url.json')}\n except m.PackageNotFoundError:v['distributions'][n]=None\nprint(json.dumps(v))"
 i,o,e=c.exec_command(shlex.quote(B+'/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);meta=json.loads(text)
finally:s.close();c.close()
v={'kind':'ACTIVE_PROJECT_PYTHON_LAUNCHER_AND_MODULE_ORIGIN_METADATA_NO_SDK_IMPORT','launcher':{'path':B+'/run-python.sh','bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()},'python_origin':meta,'PT_raw_App_GPUdriver_canonical_access':False};(D/'ORIGIN_READ_RECEIPT.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(D);print(json.dumps(v,indent=2))
