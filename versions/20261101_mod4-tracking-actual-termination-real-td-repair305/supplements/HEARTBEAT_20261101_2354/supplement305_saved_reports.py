"""Append saved same-phase text reports; no trial, model, SSH or ledger writes."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
N=Path(__file__).resolve().parent;G=N.parent.parent/'polar-rl-train'
V=G/'versions/20261101_mod4-tracking-actual-termination-real-td-repair305'
TAG='trial-20261101-mod4-tracking-actual-termination-real-td-repair305'
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return{x.split()[1]:x.split()[0]for x in s.splitlines()}
parser=argparse.ArgumentParser();parser.add_argument('--label',required=True);a=parser.parse_args();assert a.label.replace('_','').isalnum()
index=V/('CAPTURE_INDEX_SUPPLEMENT_'+a.label+'.json');assert not index.exists()and not git('status','--porcelain')
base=json.loads((V/'CAPTURE_INDEX.json').read_bytes());old=base['alloldrefs'];tag=git('rev-parse','refs/tags/'+TAG);peel=git('rev-parse','refs/tags/'+TAG+'^{}')
known={}
for p in V.glob('CAPTURE_INDEX*.json'):
 for row in json.loads(p.read_bytes())['files']:
  if row.get('SHA'):known[row['path']]=row['SHA']
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
rows=[];paths=[]
for p in sorted(N.rglob('*')):
 if not p.is_file()or'__pycache__'in p.parts or p.suffix not in('.py','.json','.md','.log','.txt'):continue
 raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest()
 if known.get(str(p))==sha:continue
 safe,count=redact(raw.decode('utf8'));value=raw if not count else safe.encode('utf8')
 out=V/'supplements'/a.label/p.relative_to(N);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(value)
 gp=out.relative_to(G).as_posix();paths.append(gp);rows.append(dict(path=str(p),bytes=len(raw),SHA=sha,Git_path=gp,archive_SHA=hashlib.sha256(value).hexdigest(),redactions=count,capture='credential_pattern_redacted'if count else'full_UTF8_byte_exact'))
assert rows
index.write_text(json.dumps(dict(epoch=time.time(),files=rows,ordinary_samephase_supplement=True,originaltagobject=tag,originalpeel=peel),indent=2,ensure_ascii=False),encoding='utf8');paths.append(index.relative_to(G).as_posix())
for i in range(0,len(paths),24):git('add','--',*paths[i:i+24])
git('commit','-m','Retain tracking305 saved status reports '+a.label);git('push','origin','HEAD')
head=git('rev-parse','HEAD');remote=refs(git('ls-remote','--tags','origin'));assert all(remote.get(k)==v for k,v in old.items())
assert remote['refs/tags/'+TAG]==tag and remote['refs/tags/'+TAG+'^{}']==peel
assert git('ls-remote','origin','refs/heads/main').split()[0]==head and git('ls-remote','origin','refs/heads/lqr').split()[0]==base['lqr']and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,saved_reports=len(rows),phase_tag_unchanged=True,alloldrefs_lqr_protected=True,clean=True)))
