"""Continue the existing pending trial after Git sparse-checkout add failure.
No new experiment ID is allocated. Only exact archived text paths are added --sparse.
"""
from pathlib import Path
import json,hashlib,subprocess,sys
REPO=Path(r'F:\RMPOLAR-RL\repo-lqr');ROOT=Path(__file__).resolve().parent
REL=Path('history/session_artifacts/mod4-cad-usd-20261101-v1');D=REPO/REL
REC=Path('history/experiments/20261101-mod4-cad-usd-scut-fudan-v1.json');TAG='trial-20261101-mod4-cad-usd-scut-fudan-v1'
def git(*args):return subprocess.run(['git','-C',str(REPO),*args],check=True,capture_output=True,text=True,encoding='utf-8').stdout.strip()
def sha(raw):return hashlib.sha256(raw).hexdigest()
assert git('branch','--show-current')=='mod4-usd-scut-fudan-20261101'
assert not git('tag','--list',TAG),'Reuse existing objects; do not retag'
m=json.loads((D/'STAGE_MANIFEST.json').read_text(encoding='utf-8'));raw=(REPO/REC).read_bytes();record=json.loads(raw)
original=D/'ARCHIVE_PENDING_RECORD_ORIGINAL.json';assert not original.exists();original.write_bytes(raw)
# Local archive attributes preserve exact source report bytes, including CRLF/BOM.
attributes=D/'.gitattributes';assert not attributes.exists();attributes.write_text('* -text\n',encoding='utf-8')
script=D/'finish_archive_sparse.py';script.write_bytes(Path(__file__).read_bytes())
report={'initial_attempt':'record_experiment.py created the planned record, then git add returned1; no commit or tag was created','diagnosis':'Paths are outside this checkout sparse definition; git check-ignore found no ignore matches. Reproduced stderr explicitly advises --sparse.','recovery':'Continue same record and tag; add exact UTF8 metadata paths with --sparse, without changing checkout sparse rules. BinaryCAD/USD/ZIP remain indexed only.','status':'sparse_add_repair_precommit','source_original_pending_record_sha256':sha(raw)}
reportpath=D/'ARCHIVE_SPARSE_REPAIR.json';reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# Keep this new repair report in the task folder too, with an indexed exact archive copy.
(ROOT/'ARCHIVE_SPARSE_REPAIR.json').write_bytes(reportpath.read_bytes())
extras=[(REL/p.name).as_posix() for p in (original,attributes,script,reportpath)]
supp=D/'SOURCE_INDEX_SUPPLEMENT_001.json'
suppdata={'reason':'Archive workflow correction after initial source-index capture; original97-file index preserved','entries':[{'source_path':str(p),'source_sha256':sha(p.read_bytes()),'bytes':p.stat().st_size,'archive_path':(REL/dest).as_posix(),'archive_sha256':sha((D/dest).read_bytes())} for p,dest in [(Path(__file__),'finish_archive_sparse.py'),(ROOT/'ARCHIVE_SPARSE_REPAIR.json','ARCHIVE_SPARSE_REPAIR.json')]],'generated_archive_metadata':[p.as_posix() for p in map(Path,extras)]}
supp.write_text(json.dumps(suppdata,ensure_ascii=False,indent=2),encoding='utf-8');extras.append((REL/supp.name).as_posix())
for rel in extras:record['source_and_evidence_sha256'][rel]=sha((REPO/rel).read_bytes())
record['archive_workflow_correction']={'initial_git_add':'failed_sparse_checkout_paths','continuation':'same record, git add --sparse, exact text metadata only','initial_pending_record_preserved_at':(REL/original.name).as_posix()}
(REPO/REC).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
paths=[REC.as_posix(),*m['files'],*extras]
existing=set(git('diff','--cached','--name-only').splitlines());assert existing<=set(paths),'Do not mix another staged change'
git('add','--sparse','--',*paths)
# Verify staged Git object bytes match all recorded report bytes exactly.
fmt=git('rev-parse','--show-object-format');p=subprocess.run(['git','-C',str(REPO),'ls-files','--stage','-z','--',*paths],check=True,capture_output=True)
indexed={}
for entry in p.stdout.split(b'\0'):
 if not entry:continue
 header,name=entry.split(b'\t',1);indexed[name.decode('utf-8')]=header.decode().split()[1]
for rel in paths:
 content=(REPO/rel).read_bytes();expected=hashlib.new(fmt,b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest();assert indexed[rel]==expected,rel+' staged bytes differ'
git('commit','-m',m['title']+'\n\nExperiment: '+TAG+'\nValidation: '+m['validation'])
git('tag','-a',TAG,'-m',m['title']+'\n\n'+record['repair_or_experiment_note'])
print(json.dumps({'tag':TAG,'commit':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'staged_text_record_bytes_verified':len(paths),'prior_record_id_reused':True,'main_and_lqr_branch_pointers_not_modified':True,'worktree_status':git('status','--porcelain')},ensure_ascii=False,indent=2))
