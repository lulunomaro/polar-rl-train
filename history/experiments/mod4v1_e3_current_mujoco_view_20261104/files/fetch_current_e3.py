from pathlib import Path
import json,sys,hashlib,time
D=Path(__file__).resolve().parent;T=D.parent/'mod4v1_experts_fulldr_rm70_20261101';A=D.parent/'mod4v1_current_nine_assessment_20261104';sys.path.insert(0,str(T));from project_connector import connect72
m=next(x for x in json.loads((A/'MODEL_SELECTION.json').read_bytes())['models']if x['role']=='E3');out=D/'current_E3.pt';receipt=D/'SOURCE_MODEL.json';assert not out.exists()and not receipt.exists();c=connect72();s=c.open_sftp()
try:
 with s.open(m['source_path'],'rb')as f:b=f.read(m['source_bytes']+1)
finally:s.close();c.close()
sha=hashlib.sha256(b).hexdigest();assert len(b)==m['source_bytes']and sha==m['source_SHA'];out.write_bytes(b);receipt.write_text(json.dumps(dict(epoch=time.time(),purpose='User-requested NEW local MuJoCo live E3 visualisation, not status or Git',source=m,local_path=str(out),source_physical_reads=1,source_SHA_calculations=1,source_bytes=len(b),native_SDK_training_budget_locks=0),indent=2),encoding='utf8');print(json.dumps(dict(local=str(out),bytes=len(b),SHA256=sha,iteration=m['iteration'])))
