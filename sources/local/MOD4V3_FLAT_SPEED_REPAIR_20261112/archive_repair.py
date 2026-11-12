"""Archive this completed, bounded repair, including all authorized full PT bytes."""
from pathlib import Path
import hashlib,json,sys,tempfile
T=Path(__file__).resolve().parent
R=T.parents[2]
ID='mod4-flat-speed-repair-01'
TAG='trial-20261112-'+ID
GLOBALS=['README.md','docs/DR_TRAINING_INDEX_20261111.md','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json','sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md','sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112/README.md']
MANIFEST=T/'evidence/FULL_ARTIFACT_MANIFEST.json'
FUTURE={'evidence/GIT_PUSH_RECEIPT.json','SYNC_REPORT.md'}
BINARY_SUFFIXES={'.pt','.pth','.npz','.npy','.png','.msh'}
def stage_files():
    files=[]
    for p in sorted(T.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix in {'.pyc','.pyo','.partial'}:
            continue
        rel=p.relative_to(T)
        if p==MANIFEST or rel.as_posix() in FUTURE:
            continue
        if 'kit_isolation' in rel.parts:
            kit_parts=rel.parts[rel.parts.index('kit_isolation')+1:]
            if kit_parts[:2]!=('logs','Kit') or p.suffix!='.log':
                continue
        files.append(p)
    return files
files=stage_files()+[R/f for f in GLOBALS]
rows=[]
for p in files:
    raw=p.read_bytes()
    kind='full_PPO_checkpoint_or_rejected_policy' if p.suffix=='.pt' else ('full_original_binary' if p.suffix in BINARY_SUFFIXES else 'source_or_report')
    rows.append(dict(path=p.relative_to(R).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),kind=kind))
pts=[r for r in rows if r['path'].endswith('.pt')]
assert len(pts)==14, 'Every saved PT (12 PPO checkpoints, rejected fit and selected alias) must be retained'
MANIFEST.write_text(json.dumps(dict(scope='Closed-stage source,reports,fullPTs,rawarrays,plots,physics logs and five navigation/catalog files;derived Kit cache/userconfig excluded',files=rows,total_bytes=sum(r['bytes'] for r in rows),pt_files=pts,exclusions=['__pycache__','*.pyc','*.pyo','*.partial','derived Kit caches/userconfig/telemetry','self manifest hash','future separately committed sync receipt']),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
files.append(MANIFEST)
paths=[p.relative_to(R).as_posix() for p in files]
binary=[p for p in paths if Path(p).suffix in BINARY_SUFFIXES]
text=[p for p in paths if p not in binary]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'))
import record_experiment as rec
original=rec.git
record=R/'history/experiments'/('20261112-'+ID+'.json')
def git(*args):
    if args[0]=='add':
        data=json.loads(record.read_text(encoding='utf8'))
        full=[]
        for name in binary:
            raw=(R/name).read_bytes()
            digest=hashlib.sha256(raw).hexdigest()
            data['source_and_evidence_sha256'][name]=digest
            full.append(dict(path=name,bytes=len(raw),sha256=digest))
        data['artifact_storage']='Human explicitly authorized full PT and original data in Git. Ordinary complete blobs: all 14 PT files (12 PPO saves, rejected offline fit, selected alias), raw arrays, plot and terrain meshes. Original mature delivery retained.'
        data['full_binary_artifacts']=full
        record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        names=[s for s in args[1:] if s!='--']+binary
        with tempfile.NamedTemporaryFile(mode='wb',prefix='flat-repair-git-',dir=R.parent/'tmp',delete=False) as f:
            for name in dict.fromkeys(names):
                f.write(name.encode('utf8')+b'\0')
            spec=Path(f.name)
        try:
            return original('--literal-pathspecs','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
        finally:
            spec.unlink()
    return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=git
sys.argv=['record_experiment.py','--id',ID,'--title','Repair flat speed tracking with bounded PPO and matched cross-engine validation','--kind','repair','--note-file',str(T/'REPORT.md'),'--validation','40m05.762s composite round; original nominal MuJoCo60/60; dense45/49 MAE0.07567m/s; native fullDR23/30pre24/30post; nominal PhysX24to20/30 regression retained; raised stairs retained in nominal single trials; leg100Hz/wheel400Hz explicit; all14PT full blobs; no real-car deployment; original mature parent retained','--files',*text]
rec.main()
print(json.dumps(dict(commit=git('rev-parse','HEAD'),tag=TAG,stage_and_navigation_files=len(files),full_PT_files=len(pts),binary_files=len(binary),manifest_bytes=sum(r['bytes'] for r in rows)),ensure_ascii=False),flush=True)
