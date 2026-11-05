from pathlib import Path
import json
from shared_control_access import connection
N=Path(__file__).resolve().parent
R=N/'reports/newton_setup01'
code="""from pathlib import Path
import json,psutil,time
r=Path('/home/lc01/Zonglin Li/zonglin2/toolchains/mod4v2_newton17')
files={}
for name in ['READY.json','ERROR.json','CLOSED.json']:
 p=r/name
 if p.exists():files[name]=json.loads(p.read_bytes())
p=r/'SETUP.log'
if p.exists():files['SETUP.log']=p.read_text(errors='replace')
print(json.dumps(dict(epoch=time.time(),files=files,pid_exists=psutil.pid_exists(1689333))))
"""
with connection(R,'NEWTON_SETUP_FINITE_RETURN') as(c,t):out=t.code(c,t.PY72,code,{},timeout=40)
path=R/'SETUP_RETURNED01.json'
with path.open('x',encoding='utf8')as f:json.dump(out,f,indent=2)
print(json.dumps(out))
