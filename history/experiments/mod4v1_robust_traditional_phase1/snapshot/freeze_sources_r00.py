"""Preserveactualinitialsourcesbeforeanytuningchanges. No models/physics/weights readforarchive."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent;D=R/'source_snapshots/r00';assert not D.exists();D.mkdir(parents=True);rows=[]
for p in sorted(R.glob('*.py'))+sorted((R/'configs').glob('*.json'))+[R/'nominal_gain_v1.json']:
 raw=p.read_bytes();q=D/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(raw);rows.append(dict(source=str(p),relative=q.relative_to(D).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
(D/'INDEX.json').write_text(json.dumps(dict(kind='SOURCE_SNAPSHOT_R00_NOT_NEW_EXPERIMENT',files=rows,large_model_rawopens=0,oldPTreads=0),indent=2),encoding='utf-8');print(D)
