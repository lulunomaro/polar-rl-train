"""Authorized actual evidence transport only; no controller or ledger mutation."""
from pathlib import Path
import sys,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
P=D.parent/'MOD4_E1_CURB20_FULL_STATE_PREPARE_20261011';sys.path.insert(0,str(P))
from stage_formal_dispatch_reviewed_once import E,B,NEW,connect_both,cleanup,linux_json,put
H=lambda b:hashlib.sha256(b).hexdigest()
def save(name,v):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());return p
