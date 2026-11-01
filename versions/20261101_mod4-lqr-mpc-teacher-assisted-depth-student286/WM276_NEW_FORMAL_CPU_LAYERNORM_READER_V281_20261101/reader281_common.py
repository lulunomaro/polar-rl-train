from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;T=D.parent;N=T/'OWN_DEPTH_WM_ONLY_ONLINE_WARM_V276V3_20261101';W=T.parent;R=N/'reports'
INDEX='INDEX281_BEFORE_USE_CPU_READER_FROZEN.json'
SHA='0f5de75a488b79bfe9513b2cd01664d8bf98450800b785b8e787301276552a07'
sys.path.insert(0,str(N/'control276'))
from wm_task275 import _go_identity
def read(p):return json.loads(Path(p).read_bytes())
def verify_index(p,expected):
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected
 for r in read(p)['files']:
  f=Path(r['path']);assert f.stat().st_size==r['bytes']and hashlib.sha256(f.read_bytes()).hexdigest()==r['SHA']
def validate_original_go(g,run):return _go_identity(g,run,read(N/'TASK276_FROZEN.json'))
def normal900_eligible(g,now,closed):return g['nominal_end_epoch']-now<=900 or closed
