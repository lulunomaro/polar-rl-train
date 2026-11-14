"""Scoped Git trials through the existing helper, including requested full PTs."""
import argparse
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile

T = Path(__file__).resolve().parent
R = T.parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--phase',choices=['launch','revision','guidance','final'],required=True)
args = parser.parse_args()
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'))
import record_experiment as rec

ID = 'forward-jump-repair2h-'+args.phase+'-01'
date = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')
TAG = 'trial-'+date+'-'+ID
record = 'history/experiments/'+date+'-'+ID+'.json'
prefix = T.relative_to(R).as_posix()+'/'
original = rec.git
NET = ('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true')
checkpoints = sorted(p.relative_to(R).as_posix() for p in (T/'weights').glob('*.pt'))


def git(*items):
    if items[0] == 'add':
        names = [x for x in items[1:] if x != '--']+checkpoints
        with tempfile.NamedTemporaryFile(mode='wb',dir=R.parent/'tmp',prefix='jump-rl-index-',delete=False) as stream:
            for name in dict.fromkeys(names):
                stream.write(name.encode('utf8')+b'\0')
            path = Path(stream.name)
        try:
            return original('--literal-pathspecs',*NET,'add','--sparse','-f',
                '--pathspec-from-file='+str(path),'--pathspec-file-nul')
        finally:
            path.unlink()
    if items[0] == 'commit':
        staged = original('diff','--cached','--name-only').splitlines()
        assert all(x.startswith(prefix) or x == record for x in staged),staged
    if items[0] == 'tag' and '-m' in items:
        i = items.index('-m')
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf8',newline='\n',dir=R.parent/'tmp',prefix='jump-rl-tag-',delete=False) as stream:
            stream.write(items[i+1])
            path = Path(stream.name)
        try:
            return original(*NET,*items[:i],'-F',str(path),*items[i+2:])
        finally:
            path.unlink()
    return original(*NET,*items)


rec.git = git
assert not git('tag','--list',TAG),'Continue pushing existing objects after a push failure'
assert not git('diff','--cached','--name-only'),'Preserve existing staged work'
note = T/({'launch':'LAUNCH_REPORT.md','revision':'REVISION_R2_REPORT.md','guidance':'REVISION_R3_REPORT.md','final':'FINAL_REPORT.md'}[args.phase])
assert note.is_file()
artifacts = []
selected = []
if args.phase != 'final':
    for history in (T/'evidence').glob('progress_history*.jsonl'):
        if '_snapshot' in history.stem:continue
        (T/'evidence'/(history.stem+'_'+args.phase+'_snapshot.jsonl')).write_bytes(history.read_bytes())
text_suffixes = {'.py','.md','.json','.jsonl','.log','.txt','.xml','.yaml','.yml','.usda','.csv','.png','.rst','.toml','.cfg','.ini','.sh','.bat','.ps1','.urdf'}
for path in sorted(T.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:
        continue
    if args.phase != 'final' and path.name in ('progress_history.jsonl','progress_history_r2.jsonl','progress_history_r3.jsonl'):
        continue
    if path.suffix in text_suffixes or path.name.endswith('.json.partial') or 'LICENSE' in path.name.upper() or path.name.upper()=='COPYING':
        selected.append(path.relative_to(R).as_posix())
    elif path.suffix in {'.pt','.npz','.usd','.stl','.obj','.png','.mp4','.gif','.gz','.zip'}:
        artifacts.append(dict(path=str(path),git_path=path.relative_to(R).as_posix(),bytes=path.stat().st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            full_body_in_commit=path.suffix == '.pt',status='full checkpoint' if path.suffix == '.pt' else 'actual original indexed'))
index = T/('evidence/ARTIFACTS_'+args.phase.upper()+'.json')
index.write_text(json.dumps(dict(epoch=datetime.now(timezone.utc).isoformat(),files=artifacts),indent=2)+'\n')
selected.append(index.relative_to(R).as_posix())
main_before = git('ls-remote','origin','refs/heads/main').split()[0]
sys.argv = ['record_experiment.py','--id',ID,'--title',
    'Record measured-tuck forward jump repair and new two-hour PPO '+args.phase,
    '--kind','training','--note-file',str(note),'--validation',
    'See frozen per-attempt native reports; actual full PPO updates; original plant, motor and timing; one7200s owner; full PT bodies retained; no production promotion',
    '--files',*sorted(set(selected))]
rec.main()
head = git('rev-parse','HEAD')
tag_object = git('rev-parse',TAG)
branch = git('branch','--show-current')
assert git('rev-parse',TAG+'^{}') == head
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
refs = {line.split()[1]:line.split()[0] for line in git('ls-remote','origin','refs/heads/main',
    'refs/heads/'+branch,'refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/'+branch] == head and refs['refs/tags/'+TAG] == tag_object and refs['refs/tags/'+TAG+'^{}'] == head
print(json.dumps(dict(commit=head,tag=TAG,tag_object=tag_object,remote_verified=True,
    main_before=main_before,main_after=refs['refs/heads/main'],text_files=len(set(selected)),
    complete_checkpoint_bodies=len(checkpoints)),indent=2),flush=True)
