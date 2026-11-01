from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;N=D.parent;T=N.parent;W=T.parent;R=N/'reports'
INDEX='INDEX300_NORMAL_SOURCE_FROZEN.json'
SHA='4ace1eec00c763c2e19a858e4a119953ec6b58debcd58fc362c7e281d5d9452d'
sys.path.insert(0,str(N/'control300'))
from teacher_task300 import go_identity
def read(p):return json.loads(Path(p).read_bytes())
def verify_index(p,expected):
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected
 for r in read(p)['files']:
  f=Path(r['path']);assert f.stat().st_size==r['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==r['SHA']
def validate_original_go(g,run):return go_identity(g,run,read(N/'TASK300_FROZEN.json'))
def normal900_eligible(g,now,closed):return g['nominal_end_epoch']-now<=900 or closed
