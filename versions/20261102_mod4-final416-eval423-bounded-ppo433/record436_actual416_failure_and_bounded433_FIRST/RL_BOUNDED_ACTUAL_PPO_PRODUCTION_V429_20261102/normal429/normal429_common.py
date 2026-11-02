from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent
N=D.parent;T=N.parent;W=T.parent;R=N/'reports'
INDEX='INDEX429_NORMAL_SOURCE_FROZEN.json'
sys.path.insert(0,str(N/'control429'))
from teacher_task429 import go_identity
def read(p):return json.loads(Path(p).read_bytes())
def verify_index(p,expected):
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected
 for row in read(p)['files']:
  path=Path(row['path']);assert path.stat().st_size==row['bytes']and hashlib.sha256(path.read_bytes()).hexdigest()==row['SHA']
 task=read(N/'TASK429_FROZEN.json')
 assert task['run_id']==read(N/'TASK429_FROZEN.json')['run_id']
 assert not(R/'ROOT429_NORMAL900_RECOVERY_ONCE_CONSUMED.json').exists()
 assert not(R/'ROOT429_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').exists()
def validate_original_go(g,run):return go_identity(g,run,read(N/'TASK429_FROZEN.json'))
def normal900_eligible(g,now,closed):return g['nominal_end_epoch']-now<=900 or closed
