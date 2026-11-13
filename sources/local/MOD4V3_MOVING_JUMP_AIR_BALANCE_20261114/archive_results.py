"""Append this experiment and all reports without staging unrelated work."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json
import sys
import tempfile

T = Path(__file__).resolve().parent
R = T.parents[2]
sys.path.insert(0, str(R.parent/'tmp/step7_archive_helper'))
import record_experiment as rec

original = rec.git
NET = ('-c', 'http.proxy=http://127.0.0.1:7897', '-c', 'http.sslVerify=true')
ID = 'moving-jump-air-balance-01'
date = datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d')
TAG = 'trial-'+date+'-'+ID
record = 'history/experiments/'+date+'-'+ID+'.json'
prefix = T.relative_to(R).as_posix()+'/'


def git(*args):
    if args[0] == 'add':
        names = [x for x in args[1:] if x != '--']
        with tempfile.NamedTemporaryFile(mode='wb', dir=R.parent/'tmp', prefix='moving-jump-index-', delete=False) as f:
            for name in dict.fromkeys(names):
                f.write(name.encode('utf8')+b'\0')
            path = Path(f.name)
        try:
            return original('--literal-pathspecs', *NET, 'add', '--sparse', '-f',
                            '--pathspec-from-file='+str(path), '--pathspec-file-nul')
        finally:
            path.unlink()
    if args[0] == 'commit':
        staged = original('diff', '--cached', '--name-only').splitlines()
        assert all(x.startswith(prefix) or x==record for x in staged), staged
    if args[0] == 'tag' and '-m' in args:
        i = args.index('-m')
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf8', newline='\n', dir=R.parent/'tmp',
                                         prefix='moving-jump-tag-', delete=False) as f:
            f.write(args[i+1])
            path = Path(f.name)
        try:
            return original(*NET, *args[:i], '-F', str(path), *args[i+2:])
        finally:
            path.unlink()
    return original(*NET, *args)


rec.git = git
assert not git('tag', '--list', TAG), 'Resume existing objects only after a push failure'
assert not git('diff', '--cached', '--name-only'), 'Preserve the existing staging area'
assert (T/'FINAL_REPORT.md').is_file()
selected = []
for path in sorted(T.rglob('*')):
    if not path.is_file() or '__pycache__' in path.parts:
        continue
    if path.suffix not in ('.py', '.md', '.json', '.jsonl', '.log', '.txt', '.xml', '.png', '.gif'):
        continue
    selected.append(path.relative_to(R).as_posix())
main_before = git('ls-remote', 'origin', 'refs/heads/main').split()[0]
sys.argv = ['record_experiment.py', '--id', ID,
    '--title', 'Record airborne leg and wheel balance feedback with matched moving jump trials',
    '--kind', 'evaluation', '--note-file', str(T/'FINAL_REPORT.md'),
    '--validation', '109 saved MuJoCo cases;15 pilot configurations,30 matched pairs,4 handoff probes,30 rejected fadeout cases; selected30/30 genuine air/full sequence/'
    'pitch10deg-roll5deg throughout flight/rolling landing; wheel-only and reversed-feedback failures retained; '
    'original plant/motors/35-6/clocks; no optimizer updates or policy promotion; rawSHA indexes; host72 jobs closed',
    '--files', *selected]
rec.main()
head = git('rev-parse', 'HEAD')
tag = git('rev-parse', TAG)
branch = git('branch', '--show-current')
assert git('rev-parse', TAG+'^{}') == head
git('push', '--atomic', 'origin', 'HEAD', 'refs/tags/'+TAG)
refs = {line.split()[1]:line.split()[0] for line in git('ls-remote', 'origin', 'refs/heads/main',
    'refs/heads/'+branch, 'refs/tags/'+TAG, 'refs/tags/'+TAG+'^{}').splitlines()}
assert refs['refs/heads/'+branch]==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head
print(json.dumps(dict(commit=head, tag=TAG, tag_object=tag, remote_verified=True,
    main_before=main_before, main_after=refs['refs/heads/main'], selected_files=len(selected)), indent=2), flush=True)
