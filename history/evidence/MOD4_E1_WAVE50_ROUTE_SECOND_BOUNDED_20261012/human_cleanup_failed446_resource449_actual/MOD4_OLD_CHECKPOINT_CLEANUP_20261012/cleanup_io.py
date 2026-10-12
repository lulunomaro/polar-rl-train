from pathlib import Path
import sys,json,time,traceback,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012'))
import route_second_io as previous
io=previous.io;run=previous.run;H=previous.H
def save(name,value):
 p=R/name;assert not p.exists();p.write_bytes(json.dumps(value,ensure_ascii=False,indent=2).encode());return p
