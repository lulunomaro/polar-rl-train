"""Resume the existing final closure record after git add's sparse-path refusal."""
from pathlib import Path
import json,subprocess,tempfile,hashlib
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';TAG='trial-20261114-rearward-contact-repair-round-closed-01';p=R/'history/experiments/20261114-rearward-contact-repair-round-closed-01.json';NET=['-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):
 r=subprocess.run(['git',*NET,*args],cwd=R,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(str(args[:3])+' '+r.stderr[-6000:])
 return r.stdout.strip()
assert git('branch','--show-current')=='mod4v1-experts-fulldr-rm70';assert not git('tag','--list',TAG)
d=json.loads(p.read_text(encoding='utf8'))
for file in [Path(__file__),E/'FINAL_ARCHIVE_SPARSE_ADD_FAILURE_R1.json']:d['source_and_evidence_sha256'][file.relative_to(R).as_posix()]=hashlib.sha256(file.read_bytes()).hexdigest()
for name in d['source_and_evidence_sha256']:assert hashlib.sha256((R/name).read_bytes()).hexdigest()==d['source_and_evidence_sha256'][name],name
d['archive_recovery']='Original record reused after sparse git-add refusal; explicit --sparse -f; no scientific job repeated.';p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
names=[p.relative_to(R).as_posix(),*d['source_and_evidence_sha256']];staged=git('diff','--cached','--name-only').splitlines();assert set(staged)<=set(names)
with tempfile.NamedTemporaryFile('wb',dir=R.parent/'tmp',delete=False)as f:
 for name in names:f.write(name.encode()+b'\0')
 path=Path(f.name)
try:git('--literal-pathspecs','add','--sparse','-f','--pathspec-from-file='+str(path),'--pathspec-file-nul')
finally:path.unlink()
main_before=git('ls-remote','origin','refs/heads/main').split()[0]
with tempfile.NamedTemporaryFile('w',encoding='utf8',dir=R.parent/'tmp',delete=False)as f:f.write(d['title']+'\n\nExperiment: '+TAG+'\nValidation: '+d['validation']);path=Path(f.name)
try:git('commit','-F',str(path))
finally:path.unlink()
with tempfile.NamedTemporaryFile('w',encoding='utf8',dir=R.parent/'tmp',delete=False)as f:f.write(d['title']+'\n\n'+d['repair_or_experiment_note']);path=Path(f.name)
try:git('tag','-a',TAG,'-F',str(path))
finally:path.unlink()
head=git('rev-parse','HEAD');tag=git('rev-parse',TAG);git('push','--atomic','origin','HEAD','refs/tags/'+TAG);refs={x.split()[1]:x.split()[0]for x in git('ls-remote','origin','refs/heads/main','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()};assert refs['refs/heads/mod4v1-experts-fulldr-rm70']==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head and refs['refs/heads/main']==main_before
print(json.dumps(dict(final_commit=head,tag=TAG,remote_verified=True,main_unchanged=True,complete_PT_body_commit='b0091fe26b7980c46569d782417da26c66c33895',complete_ordinary_PT_files=12,no_training_repeated=True),indent=2),flush=True)
