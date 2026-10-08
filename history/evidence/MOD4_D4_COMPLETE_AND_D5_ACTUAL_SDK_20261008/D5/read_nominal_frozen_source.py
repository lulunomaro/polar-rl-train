from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect
c=connect()
try:
    code="""from pathlib import Path
import zipfile,json,hashlib
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
archive=E/'artifacts/d5-nominal-spring-si-sdk-frozen.zip'
assert hashlib.sha256(archive.read_bytes()).hexdigest()=='9c4d18bffd50da978981154dfd87c8404f85985866fe09b8c509019f5b5166fc'
with zipfile.ZipFile(archive) as z:
 print(json.dumps(dict(source=z.read('runtime/isaac/mod4/frozen_history_flat.py').decode(),env=z.read('runtime/isaac/mod4/env.json').decode())))
"""
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=20)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw)
    (D/'reviewed_sources/nominal_frozen_history_flat.py').write_text(v['source'],encoding='utf8')
    (D/'reviewed_sources/nominal_env.json').write_text(v['env'],encoding='utf8')
    print(json.dumps(dict(source_read=True,env=json.loads(v['env']))))
finally:c.close()
