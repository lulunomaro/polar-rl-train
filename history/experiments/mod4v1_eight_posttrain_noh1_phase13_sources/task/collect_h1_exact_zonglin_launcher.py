from pathlib import Path
import json,hashlib
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/NINE_V3_EXACT_LAUNCHER_SOURCES/H1_normal';root=json.loads((R/'NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V2.json').read_bytes())['root'];remote=root+'/runtimes/H1_normal/lib/zonglin2_app_launcher.py';c=connect72();s=c.open_sftp()
try:
 with s.open(remote,'rb')as f:raw=f.read()
finally:s.close();c.close()
p=D/'lib/zonglin2_app_launcher.py';assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);v={'path':remote,'local_path':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'kind':'EXACT_DEPLOYED_H1_IMPORT_FIRST_SYS_PATH_SOURCE_ONLY','PT_SDK_GPU_budget_calls':0};(D/'H1_EXACT_LAUNCHER_READ.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
