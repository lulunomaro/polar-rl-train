"""Ordinary supplement, no second experiment/tag or training intervention."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
N=Path(__file__).resolve().parent;W=N.parent.parent;G=W/'polar-rl-train';V=G/'versions/20261101_mod4-student286-replay-retention-repair292';D=V/'supplement_live_progress_20261101'
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
assert not git('status','--porcelain') and not D.exists()
assert git('rev-parse','HEAD')=='37278756b9cf3083a794c98d41841872684d16bb'
tag='trial-20261101-mod4-student286-replay-retention-repair292';obj=git('rev-parse','refs/tags/'+tag);assert obj=='2e1f814da92097a6a7005a568e63351f7666d97a'
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
known={r['path']:r for r in json.loads((V/'CAPTURE_INDEX.json').read_bytes())['files']}
snap=json.loads((N/'reports/ROOT292_STATUS_POSTARCHIVE1.json').read_bytes());sel={Path(r['path']).name:json.loads(r['UTF8'])for r in snap['full_selected_UTF8']}
assert 'ORIGINAL_ERROR.json'not in sel and 'NODE_ORIGINAL_ERROR.json'not in sel and 'OWNER_ORIGINAL_ERROR.json'not in sel
progress=sel['LATEST_PROGRESS.json'];assert progress['actual_new_Pi_updates']==progress['actual_new_critic_updates']==123
assert progress['actual_new_WM_updates']==493 and progress['total_WM_updates']==7580 and progress['controls']==524
D.mkdir();rows=[];selected=[]
for p in sorted(N.rglob('*')):
    if not p.is_file()or'__pycache__'in p.parts or p.suffix not in('.py','.json','.md','.txt','.log','.toml','.xml','.csv','.sh'):continue
    b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
    if p.as_posix() in known and known[p.as_posix()].get('SHA')==sha:continue
    if str(p) in known and known[str(p)].get('SHA')==sha:continue
    safe,count=redact(b.decode('utf8'));out=D/p.relative_to(N);out.parent.mkdir(parents=True,exist_ok=True);v=b if not count else safe.encode();out.write_bytes(v)
    gp=out.relative_to(G).as_posix();selected.append(gp);rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(v).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
index=D/'CAPTURE_INDEX_SUPPLEMENT_LIVE.json';index.write_text(json.dumps(dict(epoch=time.time(),files=rows,latest_real_progress=progress,parent_trial=tag,trial_object=obj,no_model_raw_GPU_reads_for_Git=True,postround_local_waiter_pid=48920,postround_eval_pending=True,ordinary_append=True),indent=2),encoding='utf8');selected.append(index.relative_to(G).as_posix())
for i in range(0,len(selected),24):git('add','--',*selected[i:i+24])
git('commit','-m','Append live repair292 progress and postround scheduler receipt')
git('push','origin','HEAD');head=git('rev-parse','HEAD')
assert git('ls-remote','origin','refs/heads/main').split()[0]==head
remote={x.split()[1]:x.split()[0]for x in git('ls-remote','--tags','origin').splitlines()}
assert remote['refs/tags/'+tag]==obj and remote['refs/tags/'+tag+'^{}']=='37278756b9cf3083a794c98d41841872684d16bb'
assert git('ls-remote','origin','refs/heads/lqr').split()[0]=='5848b45a99b8c32af02eb61b507c3f95ab39e4ad'
assert not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,files=len(rows),trial_unchanged=True,remote_main_and_tag_and_peel_verified=True,clean=True)))
