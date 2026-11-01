from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;N=D.parent;T=N.parent;W=T.parent;R=N/'reports'
INDEX='INDEX305_NORMAL_SOURCE_FROZEN.json'
SHA='e700e546e3cada81dee7cdd6ed1aa59d51eb0d0d1932f0dfda928799de7812a8'
sys.path.insert(0,str(N/'control305'))
from teacher_task305 import go_identity
def read(p):return json.loads(Path(p).read_bytes())
def verify_index(p,expected):
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected
 for r in read(p)['files']:
  f=Path(r['path']);assert f.stat().st_size==r['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==r['SHA']
def validate_original_go(g,run):return go_identity(g,run,read(N/'TASK305_FROZEN.json'))
def normal900_eligible(g,now,closed):return g['nominal_end_epoch']-now<=900 or closed
