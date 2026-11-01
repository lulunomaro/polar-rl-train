"""ROOT caller source/receipt helpers. No transport/model/runtime at import."""
from pathlib import Path
import hashlib,importlib.util,json,sys
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
SOURCE=T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SOURCE_NEXT_V1_20261101'
FINITE=T/'E2_QUALIFIED_FULLSTATE_SOLO_PPO_SAVE_FINITE_V2_20261101'
SOURCE_INDEX_SHA='041499685899f180140936b47488b8ae0ac9d13ce17ae4cfd39f199c86ce14f1'
FINITE_INDEX_SHA='109c00e95eb58ad891245d4ee2a95467a7841d2eb4f8888dbee4b1b015a7419a'
INDEX='INDEX_E2_GUARD01_V3_FROZEN.json'
CONTROL_CWD='/home/lc01/Zonglin Li/zonglin2'
sys.path.insert(0,str(SOURCE))
from e2_solo_contract import SHA,BYTES,ITER,ADAM,LR,KIND,WORKER_KIND,MODEL,ROLE,GPUS

def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(v):return json.dumps(v,indent=2,allow_nan=False).encode()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def verify_index(index_path,expected_sha):
 assert H(index_path)==expected_sha
 for row in read(index_path)['files']:
  p=Path(row['path']) if 'path' in row else index_path.parent/row['relative']
  assert p.suffix in ('.py','.json','.md') and p.stat().st_size==row['bytes'] and H(p)==row['SHA']
def validate_original_go(g,run):
 assert g['run_id']==run and g['role_key']==ROLE and g['source_model_SHA']==SHA and g['source_SHA']==SHA
 assert g['source_iteration']==ITER and g['input_Adam']==ADAM and g['source_saved_LR']==LR
 assert g['genuine_original_E2_WORLD_MOVING_SIGNED4'] and g['one_original_writer']
 assert g['max_parent_seconds']==3900 and g['exit_headroom_seconds']==300
 assert g['save_deadline']==g['learning_started_epoch']+3600 and g['nominal_end_epoch']==g['learning_started_epoch']+3900
 return True
def normal900_eligible(g,now,already_closed):
 return g['nominal_end_epoch']-now<=900 or already_closed

