from pathlib import Path
import sys,json,shlex
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent/'MOD4V3_CONTINUOUS_STAIRS_OWN_REPAIR_20261113'))
from remote_run import connect,execute
P=json.loads((T/'PLAN.json').read_text(encoding='utf8'));root=P['root'];c=connect()
try:
 execute(c,'mkdir -p '+shlex.quote(root))
 sftp=c.open_sftp();created={root}
 for p in [T/'PLAN.json',T/'launch_probe.py',*sorted((T/'support').rglob('*'))]:
  if not p.is_file() or '__pycache__' in p.parts:continue
  rel=p.relative_to(T).as_posix();dest=root+'/'+rel;parent=str(Path(dest).parent).replace('\\','/')
  if parent not in created:execute(c,'mkdir -p '+shlex.quote(parent));created.add(parent)
  sftp.put(str(p),dest)
 sftp.close()
 result=execute(c,shlex.quote(P['python'])+' -B '+shlex.quote(root+'/launch_probe.py'))
 (T/'evidence/NATIVE_PROBE_LAUNCH.json').write_text(result,encoding='utf8');print(result)
finally:c.close()
