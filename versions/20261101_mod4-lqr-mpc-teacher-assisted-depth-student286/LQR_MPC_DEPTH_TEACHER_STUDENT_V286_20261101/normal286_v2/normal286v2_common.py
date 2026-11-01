from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;N=D.parent;T=N.parent;W=T.parent;R=N/'reports'
INDEX='INDEX286_NORMAL_V2_SOURCE_FROZEN.json'
SHA='cbd25c80a55c87296b4b2a50eb21869e4b12127f9aa3a5d5f9a607823d44242b'
sys.path.insert(0,str(N/'control286'))
from teacher_task286 import go_identity
def read(p):return json.loads(Path(p).read_bytes())
def verify_index(p,expected):
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected
 for r in read(p)['files']:
  f=Path(r['path']);assert f.stat().st_size==r['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==r['SHA']
def validate_original_go(g,run):return go_identity(g,run,read(N/'TASK286_FROZEN.json'))
def normal900_eligible(g,now,closed):return g['nominal_end_epoch']-now<=900 or closed
