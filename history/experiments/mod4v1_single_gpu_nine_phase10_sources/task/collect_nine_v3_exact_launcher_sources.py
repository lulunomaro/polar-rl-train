"""ExactownedV2installedsourceinspection only. No selectedPT/SDK/raw/canonical."""
from pathlib import Path
import json,hashlib,shlex,base64
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/NINE_V3_EXACT_LAUNCHER_SOURCES';assert not D.exists();D.mkdir(parents=True);g=json.loads((R/'NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V2.json').read_bytes())['root'];code="""from pathlib import Path
import json,hashlib,base64
B=Path(%r);files=[]
for role in ('H1_normal','W35'):
 root=B/'runtimes'/role;prefix=root/'job0/runtime/isaac/mod4'if role=='H1_normal'else root/'runtime/isaac/mod4';paths=list(root.rglob('launcher*.py'));paths.append(prefix/('train_H1_ground_prelaunch_fullstate_v2.py'if role=='H1_normal'else'train_mod4v1_w35.py'))
 for p in sorted(set(paths)):
  raw=p.read_bytes();files.append({'role':role,'relative':p.relative_to(root).as_posix(),'path':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode()})
print(json.dumps({'kind':'ACTUAL_OWNED_INSTALLED_LAUNCHER_SOURCE_BYTE_COPIES','files':files,'PT_SDK_raw_GPU_canonical_calls':0}))
"""%g;c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=90);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
for row in v['files']:
 raw=base64.b64decode(row.pop('base64'));assert hashlib.sha256(raw).hexdigest()==row['SHA'];p=D/row['role']/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);row['local_copy']=str(p)
(D/'INDEX.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
