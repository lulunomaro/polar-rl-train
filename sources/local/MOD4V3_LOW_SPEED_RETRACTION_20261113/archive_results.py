"""Record this completed bounded experiment with full PT blobs and unique trial."""
from pathlib import Path
import hashlib
import json
import sys
import tempfile

T=Path(__file__).resolve().parent;R=T.parents[2]
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'))
import record_experiment as rec
original=rec.git
NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true')
ID='low-speed-blocked-retraction-01';TAG='trial-20261113-'+ID
record=R/'history/experiments'/('20261113-'+ID+'.json')
binary=[p.relative_to(R).as_posix() for p in sorted(T.rglob('*.pt')) if '__pycache__' not in p.parts]
prefix=T.relative_to(R).as_posix()+'/'

def git(*args):
    if args[0]=='add':
        value=json.loads(record.read_text())
        for name in binary:value['source_and_evidence_sha256'][name]=hashlib.sha256((R/name).read_bytes()).hexdigest()
        value['artifact_storage']='Complete PT bodies are ordinary Git blobs by user instruction; other large originals are retained with SHA/path index.'
        record.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        names=[x for x in args[1:] if x!='--']+binary
        with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',prefix='low-speed-index-',delete=False) as f:
            for name in dict.fromkeys(names):f.write(name.encode('utf8')+b'\0')
            spec=Path(f.name)
        try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(spec),'--pathspec-file-nul')
        finally:spec.unlink()
    if args[0]=='commit':
        staged=original('diff','--cached','--name-only').splitlines()
        assert all(x.startswith(prefix) or x==record.relative_to(R).as_posix() for x in staged),staged
    if args[0]=='tag' and '-m' in args:
        i=args.index('-m')
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',prefix='low-speed-tag-',delete=False) as f:
            f.write(args[i+1]);note=Path(f.name)
        try:return original(*NET,*args[:i],'-F',str(note),*args[i+2:])
        finally:note.unlink()
    return original(*NET,*args)

rec.git=git
assert not git('tag','--list',TAG),'Existing objects must only resume their push'
assert not git('diff','--cached','--name-only'),'Preserve other staged work'
assert (T/'FINAL_REPORT.md').exists()
files=[]
for path in sorted(T.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts or path.suffix not in ('.py','.md','.json','.jsonl','.log','.txt','.yaml','.yml','.xml','.png'):
        continue
    if any(x in ('scene_assets','kit_isolation','cache','tmp') for x in path.relative_to(T).parts):
        continue
    files.append(path.relative_to(R).as_posix())
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
sys.argv=['record_experiment.py','--id',ID,'--title','Record blocked-wheel retraction failures and bounded dual4090 PPO contrasts',
          '--kind','evaluation','--note-file',str(T/'FINAL_REPORT.md'),
          '--validation','70 frozen MuJoCo courses;17 real blocked states; matched policy/pulse/5m/final continuations;280 native nominal episodes;2 bounded native PPO jobs,1210.690s aggregate;all8 complete PT files checked;no skill promotion;original assets,35/6,motors,2mmguards and210 training preserved',
          '--files',*files]
rec.main()
head=git('rev-parse','HEAD');tag=git('rev-parse',TAG);branch=git('branch','--show-current')
assert git('rev-parse',TAG+'^{}')==head
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/main','refs/heads/'+branch,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/'+branch]==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head
for name in binary:
    assert git('rev-parse',head+':'+name)==git('hash-object','--no-filters',str(R/name)),name
print(json.dumps(dict(commit=head,tag=TAG,tag_object=tag,remote_verified=True,main_before=main_before,main_after=refs['refs/heads/main'],ordinary_PT_blobs=len(binary),selected_source_report_files=len(files)),indent=2),flush=True)
