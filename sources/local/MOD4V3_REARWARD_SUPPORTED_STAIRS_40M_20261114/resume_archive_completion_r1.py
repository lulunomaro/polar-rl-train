"""Resume the original failed completion archive, preserving its original trial ID."""
from pathlib import Path
import subprocess,json,hashlib,tempfile,time
T=Path(__file__).resolve().parent;R=T.parents[2];E=T/'evidence';TAG='trial-20261114-rearward-supported-stairs-40m-complete-01';record=R/'history/experiments/20261114-rearward-supported-stairs-40m-complete-01.json'
NET=['-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):
 r=subprocess.run(['git',*NET,*args],cwd=R,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(str(args[:3])+' '+r.stderr[-6000:])
 return r.stdout.strip()
assert git('branch','--show-current')=='mod4v1-experts-fulldr-rm70'
assert not git('tag','--list',TAG),'Existing objects must only resume pushing'
d=json.loads(record.read_text(encoding='utf8'));extra=[Path(__file__),T/'pipeline_error.log',E/'PIPELINE_ERROR.json']
for p in extra:
 if p.is_file():d['source_and_evidence_sha256'][p.relative_to(R).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
for n in d['source_and_evidence_sha256']:d['source_and_evidence_sha256'][n]=hashlib.sha256((R/n).read_bytes()).hexdigest()
d['archive_recovery']='Original git-add exit128 retained in pipeline_error.log. Original record and trial ID resumed; no training/evaluation repeated.';record.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
names=[record.relative_to(R).as_posix(),*d['source_and_evidence_sha256']]
with tempfile.NamedTemporaryFile('wb',dir=R.parent/'tmp',delete=False)as f:
 for n in names:f.write(n.encode()+b'\0')
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
git('push','--atomic','origin','HEAD','refs/tags/'+TAG);head=git('rev-parse','HEAD');tag=git('rev-parse',TAG);refs={s.split()[1]:s.split()[0]for s in git('ls-remote','origin','refs/heads/main','refs/heads/mod4v1-experts-fulldr-rm70','refs/tags/'+TAG,'refs/tags/'+TAG+'^{}').splitlines()};assert refs['refs/heads/mod4v1-experts-fulldr-rm70']==head and refs['refs/tags/'+TAG]==tag and refs['refs/tags/'+TAG+'^{}']==head
binary=[n for n in names if n.endswith('.pt')]
for n in binary:assert git('rev-parse',head+':'+n)==git('hash-object','--no-filters',str(R/n))
receipt=dict(epoch=time.time(),commit=head,tag=TAG,remote_verified=True,ordinary_full_PT_files=len(binary),main_before=main_before,main_after=refs['refs/heads/main'],no_training_or_evaluation_repeated=True)
(E/'ARCHIVE_COMPLETE_RECOVERY_R1.json').write_text(json.dumps(receipt,indent=2)+'\n');(E/'PIPELINE_COMPLETE_RECOVERED_R1.json').write_text(json.dumps(dict(**receipt,bounded40m_complete=True,no_more_training=True),indent=2)+'\n');print(json.dumps(receipt),flush=True)
