"""Append this task's reports and source using the existing trial helper."""
import argparse
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile

T=Path(__file__).resolve().parent
R=T.parents[2]
parser=argparse.ArgumentParser()
parser.add_argument('--phase',choices=['final'],default='final')
a=parser.parse_args()
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'))
import record_experiment as rec
original=rec.git
NET=('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true')
date=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')
ident='mujoco-jump-step-01'
tag='trial-'+date+'-'+ident
record='history/experiments/'+date+'-'+ident+'.json'
prefix=T.relative_to(R).as_posix()+'/'

def git(*items):
    if items[0]=='add':
        names=[x for x in items[1:] if x!='--']
        with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',prefix='height-index-',delete=False) as stream:
            for name in dict.fromkeys(names):stream.write(name.encode('utf8')+b'\0')
            path=Path(stream.name)
        try:return original('--literal-pathspecs',*NET,'add','--sparse','-f','--pathspec-from-file='+str(path),'--pathspec-file-nul')
        finally:path.unlink()
    if items[0]=='commit':
        staged=original('diff','--cached','--name-only').splitlines()
        assert all(p.startswith(prefix) or p==record for p in staged),staged
    if items[0]=='tag' and '-m' in items:
        i=items.index('-m')
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',prefix='height-tag-',delete=False) as stream:
            stream.write(items[i+1]);path=Path(stream.name)
        try:return original(*NET,*items[:i],'-F',str(path),*items[i+2:])
        finally:path.unlink()
    return original(*NET,*items)

rec.git=git
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
if not git('tag','--list',tag):
    assert not git('diff','--cached','--name-only'),'Preserve existing staged work'
    selected=[]
    artifacts=[]
    live={'progress_history.jsonl','pipeline.log','pipeline_error.log'}
    text={'.py','.md','.json','.jsonl','.log','.txt','.xml','.yaml','.yml','.usda','.csv','.sh','.toml','.png'}
    for path in sorted(T.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:continue
        if a.phase=='launch' and path.name in live:
            snapshot=path.with_name(path.stem+'_launch_snapshot'+path.suffix)
            snapshot.write_bytes(path.read_bytes())
            selected.append(snapshot.relative_to(R).as_posix())
            continue
        if path.suffix in text:
            selected.append(path.relative_to(R).as_posix())
        elif path.suffix in {'.pt','.npz','.gz','.png','.zip'}:
            artifacts.append(dict(path=str(path),bytes=path.stat().st_size,
                                  sha256=hashlib.sha256(path.read_bytes()).hexdigest(),body_in_Git=False))
    inputs=json.loads((T/'evidence/sweep_r2/INPUTS.json').read_bytes())
    index=T/('evidence/ARTIFACTS_'+a.phase.upper()+'.json')
    index.write_text(json.dumps(dict(epoch=datetime.now(timezone.utc).isoformat(),artifacts=artifacts,
                                    reused_checkpoints=inputs['models'],source=inputs['source'],
                                    physics_inputs='evidence/physics_inputs and original map BUILD receipts'),indent=2)+'\n',encoding='utf8')
    selected.append(index.relative_to(R).as_posix())
    note=T/'REPORT.md'
    assert note.is_file()
    sys.argv=['record_experiment.py','--id',ident,'--title',
              'Record actual MuJoCo jumping onto official stair tests and retained failures',
              '--kind','evaluation','--note-file',str(note),'--validation',
              '31 actual stair jump attempts;0 stable top landings;3 flat controls passed; one original terrain tile; no optimizer or dynamics change',
              '--files',*sorted(set(selected))]
    rec.main()
commit=git('rev-parse',tag+'^{}')
tag_object=git('rev-parse',tag)
head=git('rev-parse','HEAD')
branch=git('branch','--show-current')
git('push','--atomic','origin','HEAD','refs/tags/'+tag)
refs={line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/main',
      'refs/heads/'+branch,'refs/tags/'+tag,'refs/tags/'+tag+'^{}').splitlines()}
assert refs['refs/heads/'+branch]==head
assert refs['refs/tags/'+tag]==tag_object and refs['refs/tags/'+tag+'^{}']==commit
assert refs['refs/heads/main']==main_before
print(json.dumps(dict(commit=commit,tag=tag,tag_object=tag_object,remote_verified=True,
                      main_before=main_before,main_after=refs['refs/heads/main']),indent=2))
