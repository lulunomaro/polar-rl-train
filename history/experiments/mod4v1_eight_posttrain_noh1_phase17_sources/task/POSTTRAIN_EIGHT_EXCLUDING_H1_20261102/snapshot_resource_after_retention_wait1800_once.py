"""Freshreadonlysnapshotafteractual1800swaitterminal, notloop/replay/newGO."""
from pathlib import Path
import ast,json,sys,shlex
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
p=D/'reports/PAIR1_RETENTION_AFTER_WAIT1800_RESOURCE_SNAPSHOT.json';assert not p.exists();t=ast.parse((D/'diagnose_original_retention_lock_wait_once.py').read_text(encoding='utf-8'));code=next(n.value.value for n in ast.walk(t)if isinstance(n,ast.Assign)and any(isinstance(a,ast.Name)and a.id=='code'for a in n.targets));c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(txt);v['snapshot_reason']='OriginalretentionV3closed1800sresourcewaitwithzeroPT/SDK; assesschangedconditionbeforenewunusedattempt';v['not_actual_admission_or_GO']=True;p.write_text(json.dumps(v,indent=2),encoding='utf-8');print(p);print(json.dumps(v,indent=2))
finally:c.close()
