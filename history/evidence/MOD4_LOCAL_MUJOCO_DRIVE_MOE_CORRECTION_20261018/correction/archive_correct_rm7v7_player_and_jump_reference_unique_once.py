"""Archive actual corrected player, map conversion failures and local jump audit."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
B=Path(__file__).resolve().parent;W=B.parent;D=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008';R=W/'polar-rl-train'
DEST=R/'history/evidence'/B.name
BASE='1aeaf945721182196a0cf15d120d93d01e531995';ID='rm7v7-original-panel-latest-moe-jump-reference-audit';TAG='trial-20261018-'+ID
def g(*args):
    p=subprocess.run(['git','-C',str(R),*args],capture_output=True,text=True,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stderr)
    return p.stdout.strip()
def H(raw):return hashlib.sha256(raw).hexdigest()
def FH(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024**2),b''):h.update(block)
    return h.hexdigest()
def put(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert g('rev-parse','HEAD')==BASE and not g('status','--porcelain') and not g('tag','--list',TAG) and not DEST.exists()
old={}
for line in g('for-each-ref','--format=%(refname) %(objectname) %(*objectname)','refs/tags').splitlines():
    z=line.split();old[z[0]]=z[1:]
assert len(old)==1384
DEST.mkdir(parents=True)
sys.path.insert(0,str(R/'archive_tools'))
from capture_history import redact
entries=[];text={'.py','.ps1','.bat','.md','.txt','.json','.xml','.obj'}
for root,label in ((B,'correction'),(D,'requested_player')):
    for p in sorted(root.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix.lower() not in text:continue
        raw=p.read_bytes();assert len(raw)<50_000_000
        try:value=raw.decode('utf-8-sig')
        except UnicodeDecodeError:value=raw.decode('latin1')
        clean,n=redact(value);data=raw if not n else clean.encode('utf-8')
        q=DEST/label/p.relative_to(root);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(data)
        entries.append(dict(original_path=str(p),bytes=len(raw),source_SHA=H(raw),Git_path=q.relative_to(R).as_posix(),
            archived_SHA=H(data),redactions=n,capture='complete' if not n else 'capture_only_credential_redacted',original_retained=True))
# New generated binaries receive actual indexes; training PT SHA comes only from
# the already complete producer/CPU proof, with no archival rehash or download.
meta=json.loads((D/'latest_moe_hour4_20261018.json').read_text(encoding='utf-8'))
research=json.loads((B/'reports/LOCAL_FUDAN_JUMP_MODEL_SCUT_JUMP_REWARDS_RESEARCH_ACTUAL.json').read_text(encoding='utf-8'))
artifacts=dict(checkpoints=meta['sources'],fudan_jump=research['fudan_jump_deployed_model'],generated=[])
for p in [D/'latest_moe_hour4_20261018.onnx',D/'latest_moe_20261018.onnx',D/'rm7v7_latest_moe.mjb',B/'FULL_RM7V7_LATEST_MOE_PREVIEW.png']:
    artifacts['generated'].append(dict(path=str(p),bytes=p.stat().st_size,SHA=FH(p),original_retained=True))
put(DEST/'ARTIFACT_INDEX.json',artifacts)
put(DEST/'REPORT_CAPTURE_INDEX.json',dict(epoch=time.time(),entries=entries,artifacts=artifacts,deferred=[],
    live_player_metadata_frozen_at_capture_not_future_skill_FINAL=True,wrong_previous_window_attempt_preserved_in_prior_stage=True))
put(DEST/'PREEXISTING_TAG_OBJECTS_AND_PEELS.json',old)
files=[p.relative_to(R).as_posix() for p in sorted(DEST.rglob('*')) if p.is_file()]
args=[sys.executable,str(R/'archive_tools/record_experiment.py'),'--id',ID,'--title',
    'Correct local driver to supplied RM7v7 full CAD map with latest MoE and inspect released jump references',
    '--kind','deployment','--note-file',str(DEST/'correction/HANDOFF_AND_EXPERIMENT_NOTE.md'),
    '--validation','Full field compiled; original robot retained; CAD3770 ray V2 passed with original tolerances; latest4thhour ONNX; local Fudan jump graph and SCUT reward definitions verified; prior failures retained.',
    '--files',*files,'--push']
p=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
if p.returncode:
    put(B/'reports/RM7V7_CORRECTION_GIT_ORIGINAL_ERROR.json',dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr,current_HEAD=g('rev-parse','HEAD'),tag=g('tag','--list',TAG)))
    raise RuntimeError('Record or push failed; resume existing objects only if commit exists')
head=g('rev-parse','HEAD');obj=g('rev-parse',TAG)
remote={line.split()[1]:line.split()[0] for line in g('ls-remote','origin','refs/heads/main','refs/tags/*').splitlines()}
assert remote['refs/heads/main']==head and remote['refs/tags/'+TAG]==obj and remote['refs/tags/'+TAG+'^{}']==head
for ref,objects in old.items():
    assert remote[ref]==objects[0]
    if len(objects)>1:assert remote[ref+'^{}']==objects[1]
for row in entries:
    raw=subprocess.run(['git','-C',str(R),'show',head+':'+row['Git_path']],capture_output=True,check=True).stdout
    assert H(raw)==row['archived_SHA']
assert len(g('tag','--list').splitlines())==1385
print(json.dumps(dict(status='REMOTE_VERIFIED',commit=head,tag=TAG,object=obj,total_tags=1385,
    all1384oldtags_objects_peels_exact=True,tracked_text_entries=len(entries),deferred=[])))
