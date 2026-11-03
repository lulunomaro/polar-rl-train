"""Append current native evidence to Git; no checkpoint reads or physics."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
S=N.parents[1]
DEST=G/'history/reviews/20261103-mod4v1-scut-native-training'
sys.path.insert(0,str(G/'archive_tools'))
from capture_history import redact
DEST.mkdir(exist_ok=True);(DEST/'objects').mkdir(exist_ok=True)
H=lambda raw:hashlib.sha256(raw).hexdigest()
index=[]
for path in sorted(N.rglob('*')):
    if not path.is_file()or path.suffix.lower()not in ('.py','.json','.log','.md'):continue
    if '__pycache__'in path.parts:continue
    raw=path.read_bytes();text=raw.decode('utf8');redacted,count=redact(text)
    data=redacted.encode();dest=DEST/'objects'/(H(data)+path.suffix)
    if not dest.exists():
        with dest.open('xb')as f:f.write(data)
    index.append(dict(path=str(path),bytes=len(raw),SHA=H(raw),git_path=dest.relative_to(G).as_posix(),
        archived_SHA=H(data),redactions=count))
for path in [N/'evaluation80_inference_fix01/selected_actual_poses.npz',N/'evaluation80_inference_fix01/actual400hz.npz']:
    receipt=json.loads((N/'reports/EVAL80_INFERENCE_FIX01_RETURNED.json').read_bytes())['files']['evaluation/RESULT.json']
    row=receipt['actual_poses' if path.name.startswith('selected')else'all80_manifold']
    index.append(dict(path=str(path),bytes=path.stat().st_size,SHA=row['SHA'],git_path=None,external_large_artifact=True))
stamp=datetime.now(timezone.utc).isoformat()
target=DEST/'NATIVE_EVIDENCE_INDEX.json'
target.write_text(json.dumps(dict(captured_at=stamp,files=index,checkpoint_deserializations=0,physics=0),ensure_ascii=False,indent=2))
print(json.dumps(dict(files=len(index),report=str(target),total_textbytes=sum(x['bytes']for x in index if x.get('git_path')))))
