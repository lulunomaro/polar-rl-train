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
known={}
previous=DEST/'NATIVE_EVIDENCE_INDEX.json'
if previous.exists():
    for row in json.loads(previous.read_bytes())['files']:
        if row.get('git_path'):known[(row.get('archived_SHA',row['SHA']),Path(row['git_path']).suffix)]=G/row['git_path']
for path in sorted(N.rglob('*')):
    if not path.is_file()or path.suffix.lower()not in ('.py','.json','.log','.md'):continue
    if '__pycache__'in path.parts:continue
    raw=path.read_bytes();text=raw.decode('utf8');redacted,count=redact(text)
    data=redacted.encode();dest=known.get((H(data),path.suffix),DEST/'objects'/(H(data)+path.suffix))
    if not dest.exists():
        with dest.open('xb')as f:f.write(data)
    index.append(dict(path=str(path),bytes=len(raw),SHA=H(raw),git_path=dest.relative_to(G).as_posix(),
        archived_SHA=H(data),redactions=count))
for path in [N/'evaluation80_inference_fix01/selected_actual_poses.npz',N/'evaluation80_inference_fix01/actual400hz.npz']:
    receipt=json.loads((N/'reports/EVAL80_INFERENCE_FIX01_RETURNED.json').read_bytes())['files']['evaluation/RESULT.json']
    row=receipt['actual_poses' if path.name.startswith('selected')else'all80_manifold']
    index.append(dict(path=str(path),bytes=path.stat().st_size,SHA=row['SHA'],git_path=None,external_large_artifact=True))
transfer=N/'env20000_1h/reports/POSTROUND_FORMAL_TRANSFERS.json'
if transfer.exists():
    for row in json.loads(transfer.read_bytes())['files']:
        path=Path(row['local_path']);assert path.stat().st_size==row['bytes']
        index.append(dict(path=str(path),remote_path=row['path'],bytes=row['bytes'],SHA=row['SHA'],
            git_path=None,external_large_artifact=True,SHA_source=str(transfer),archive_reads=0))
for report in N.rglob('RENDER_REPORT.json'):
    for name in json.loads(report.read_bytes()).get('media',[]):
        path=Path(name)
        with path.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        index.append(dict(path=str(path),bytes=path.stat().st_size,SHA=digest,git_path=None,
            external_large_artifact=True,actual_saved_pose_render=True))
for path in [S/'admin/CURRENT_STATE.json',Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml')]:
    raw=path.read_bytes();text,count=redact(raw.decode('utf8'));data=text.encode()
    dest=DEST/'objects'/(H(data)+path.suffix)
    if not dest.exists():
        with dest.open('xb')as f:f.write(data)
    index.append(dict(path=str(path),bytes=len(raw),SHA=H(raw),git_path=dest.relative_to(G).as_posix(),archived_SHA=H(data),redactions=count))
stamp=datetime.now(timezone.utc).isoformat()
target=DEST/'NATIVE_EVIDENCE_INDEX.json'
target.write_text(json.dumps(dict(captured_at=stamp,files=index,checkpoint_deserializations=0,physics=0),ensure_ascii=False,indent=2))
print(json.dumps(dict(files=len(index),report=str(target),total_textbytes=sum(x['bytes']for x in index if x.get('git_path')))))
