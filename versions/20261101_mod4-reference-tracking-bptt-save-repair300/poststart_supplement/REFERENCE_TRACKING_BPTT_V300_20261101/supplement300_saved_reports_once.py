"""Ordinary same-phase supplement; no record/tag/GPU/model/SSH operations."""
from pathlib import Path
import base64,hashlib,json,subprocess,sys,time
N=Path(__file__).resolve().parent;T=N.parent;G=T.parent/'polar-rl-train';R=N/'reports'
ID='mod4-reference-tracking-bptt-save-repair300';V=G/('versions/20261101_'+ID);TAG='trial-20261101-'+ID
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()}
assert not git('status','--porcelain')
base=json.loads((V/'CAPTURE_INDEX.json').read_bytes());old=base['alloldrefs'];oldtag=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}')
assert peel=='9f6381ada8c77b40ba0f5e9cf27154b3286ee7b8'
index=V/'CAPTURE_INDEX_POSTSTART_SUPPLEMENT.json';assert not index.exists()
known={row.get('path'):row.get('SHA')for row in base['files']}
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
binary={'.pt','.pth','.npz','.npy','.png','.jpg','.jpeg','.mp4','.usd','.usdc','.stl','.obj','.zip','.pyc'}
names=['DEPTH_STUDENT_RETENTION_REPAIR_V292_20261101','RETENTION292_POSTROUND_REPLAY_EVAL_V293_20261101','REFERENCE_TRACKING_BPTT_V295_20261101','REFERENCE_TRACKING_BPTT_V296_20261101','REFERENCE_TRACKING_BPTT_V297_20261101','RETENTION292_DEPENDENCY_REPLAY_EVAL_V299_20261101',N.name]
rows=[];selected=[]
for name in names:
 for p in sorted((T/name).rglob('*')):
  if not p.is_file()or'__pycache__'in p.parts or p.suffix.lower()in binary:continue
  b=p.read_bytes();sha=hashlib.sha256(b).hexdigest()
  if known.get(str(p))==sha:continue
  safe,count=redact(b.decode('utf8'));value=b if not count else safe.encode('utf8')
  out=V/'poststart_supplement'/name/p.relative_to(T/name);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(value)
  gp=out.relative_to(G).as_posix();selected.append(gp);rows.append(dict(path=str(p),bytes=len(b),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
assert any(row['path'].endswith('VIEW299_EXIT.json')for row in rows)
index.write_text(json.dumps(dict(epoch=time.time(),phase=ID,files=rows,ordinary_supplement_no_retag=True,reason='Old292actualreplayviewer safely exited naturally after1800seconds following initialphasecapture; retain late report and thissupplement source',originaltagobject=oldtag,originalpeel=peel),indent=2,ensure_ascii=False),encoding='utf8');selected.append(index.relative_to(G).as_posix())
for i in range(0,len(selected),24):git('add','--',*selected[i:i+24])
git('commit','-m','Retain natural replay299 exit after reference tracking300 launch archive')
git('push','origin','HEAD')
head=git('rev-parse','HEAD');remote=refs(git('ls-remote','--tags','origin'))
assert remote['refs/tags/'+TAG]==oldtag and remote['refs/tags/'+TAG+'^{}']==peel and all(remote.get(k)==v for k,v in old.items())
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==base['lqr']and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,newreports=len(rows),same_original_tag_object=oldtag,same_original_peel=peel,old_refs_and_lqr_protected=True,clean=True)))
