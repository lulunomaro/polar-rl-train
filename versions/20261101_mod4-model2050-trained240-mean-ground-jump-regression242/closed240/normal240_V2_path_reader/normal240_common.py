from pathlib import Path
import hashlib,json,sys
D=Path(__file__).resolve().parent;N=D.parent;T=N.parent;W=T.parent;R=N/'reports'
SHA='aac0ef67b8dc7e2b616e45952bf71e09b1ffb24bfcb84644f4d68550ed228869'
BYTES=386869;ITER=2050;ADAM=41240;LR=.00011390625000000006
INDEX='INDEX240_NORMAL_READERS_V2_PATH_FROZEN.json'
sys.path.insert(0,str(N/'control240'))
from model2050_task240 import flat_go_fields

def read(p):return json.loads(Path(p).read_bytes())
def verify_index(p,expected):
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==expected
 for r in read(p)['files']:
  f=Path(r['path']);assert f.stat().st_size==r['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==r['SHA']
def validate_original_go(g,run):
 task=read(N/'package/TASK240.json')
 for k,v in flat_go_fields(task).items():assert g[k]==v,k
 assert g['run_id']==run and g['role_key']=='jump_72' and g['source_SHA']==SHA
 assert g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300
 assert g['save_deadline']==g['learning_started_epoch']+3600 and g['nominal_end_epoch']==g['learning_started_epoch']+3900
 return True
def normal900_eligible(g,now,closed):return g['nominal_end_epoch']-now<=900 or closed
