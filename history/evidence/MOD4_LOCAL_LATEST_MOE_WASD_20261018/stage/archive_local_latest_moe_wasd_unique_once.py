"""Capture this local deployment exactly once; external models remain indexed."""
from pathlib import Path
import hashlib, json, subprocess, sys
W = Path(__file__).resolve().parent
BASE = W.parent
R = BASE/'polar-rl-train'
L = BASE/'mod4-onnx-mujoco-launcher'
DEST = R/'history/evidence/MOD4_LOCAL_LATEST_MOE_WASD_20261018'
ID = 'local-latest-moe-wasd-player'
TAG = 'trial-20261018-'+ID
EXPECTED = 'f906510357e978a2288994ea951804fc535ae2c9'

def g(*a):
    p = subprocess.run(['git','-C',str(R),*a], capture_output=True,text=True,encoding='utf-8')
    if p.returncode: raise RuntimeError(p.stderr)
    return p.stdout.strip()
def H(b): return hashlib.sha256(b).hexdigest()
def put(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

assert g('rev-parse','HEAD') == EXPECTED
assert not DEST.exists() and not g('tag','--list',TAG)
assert not g('status','--porcelain')
baseline={}
for line in g('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
    parts=line.split();baseline[parts[0]]=parts[1:]
assert len(baseline)==1382
DEST.mkdir(parents=True)
sys.path.insert(0,str(R/'archive_tools'))
from capture_history import redact
entries=[]
text={'.py','.ps1','.bat','.md','.txt','.json'}
for root,label in ((W,'stage'),(L,'player')):
    for p in sorted(root.rglob('*')):
        if not p.is_file() or any(x in p.relative_to(root).parts for x in ('.git','.runtime','__pycache__')):continue
        if p.suffix.lower() not in text:continue
        raw=p.read_bytes(); rel=Path(label)/p.relative_to(root)
        value=raw.decode('utf-8-sig');clean,n=redact(value)
        out=DEST/rel;out.parent.mkdir(parents=True,exist_ok=True)
        # Preserve original UTF8 bytes when no redaction is needed.
        archived=raw if clean==value else clean.encode('utf-8')
        out.write_bytes(archived)
        entries.append(dict(original_path=str(p),bytes=len(raw),original_SHA=H(raw),
            archived_path=out.relative_to(R).as_posix(),archived_SHA=H(archived),
            capture='complete' if archived==raw else 'credential-redacted',redactions=n))
meta=json.loads((L/'policies/imported/mod4_latest_moe_20261018.json').read_text(encoding='utf-8'))
artifacts=dict(checkpoints=meta['sources'],onnx=dict(path=str(L/'policies/imported/mod4_latest_moe_20261018.onnx'),
    bytes=(L/'policies/imported/mod4_latest_moe_20261018.onnx').stat().st_size,sha256=meta['onnx_sha256']),
    initial_graph=json.loads((W/'reports/LOCAL_ONNX_SYMBOLIC_SHAPE_FIXED_ACTUAL.json').read_text())['original'])
put(DEST/'ARTIFACT_INDEX.json',artifacts)
put(DEST/'REPORT_CAPTURE_INDEX.json',dict(entries=entries,all_saved_current_texts_captured=True,
    earlier_report_overwrite_defects_explicitly_documented=True,external_artifacts=artifacts,deferred=[]))
put(DEST/'PREEXISTING_TAG_OBJECTS_AND_PEELS.json',baseline)
files=[p.relative_to(R).as_posix() for p in sorted(DEST.rglob('*')) if p.is_file()]
note=DEST/'stage/HANDOFF.md'
cmd=[sys.executable,str(R/'archive_tools/record_experiment.py'),'--id',ID,'--title',
    'Deploy latest closed H1 E2 E3 manual MoE to local WASD MuJoCo player',
    '--kind','deployment','--note-file',str(note),'--validation',
    '1000 MuJoCo rows finite; clipped ONNX parity max8.5831e-6; actual responding window; not skill qualification',
    '--files',*files,'--push']
p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
if p.returncode:
    # Preserve failure outside the captured stage. Never rerun record after a commit.
    put(W/'reports/LOCAL_PLAYER_GIT_ORIGINAL_ERROR.json',dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,
        current_HEAD=g('rev-parse','HEAD'),tag=g('tag','--list',TAG)))
    raise RuntimeError('Git record/push failed; inspect original error and resume existing objects only')
head=g('rev-parse','HEAD');obj=g('rev-parse',TAG)
remote={line.split()[1]:line.split()[0] for line in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
for ref,objects in baseline.items():
    assert remote[ref]==objects[0]
    if len(objects)>1:assert remote[ref+'^{}']==objects[1]
for row in entries:
    out=subprocess.run(['git','-C',str(R),'show',head+':'+row['archived_path']],capture_output=True,check=True).stdout
    assert H(out)==row['archived_SHA']
assert len(g('tag','--list').splitlines())==1383
print(json.dumps(dict(status='RECORDED_REMOTE_VERIFIED',head=head,tag=TAG,object=obj,
    all_1382_previous_tag_objects_peels_exact=True,tracked_capture_entries=len(entries),deferred=[])))
