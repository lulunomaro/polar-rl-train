"""Complete the already-created sync record after its plain git-add path refusal."""
from pathlib import Path
import json,subprocess,hashlib,time,datetime
T=Path(__file__).resolve().parent;R=T.parents[2]
SYNC_ID='mod4-scut-rough-v0-2h-sync-01';SYNC_TAG='trial-20261112-'+SYNC_ID;FINAL_TAG='trial-20261112-mod4-scut-rough-v0-2h-final-01'
record_path=R/'history/experiments'/('20261112-'+SYNC_ID+'.json')
receipt=json.loads((T/'evidence/FINAL_GIT_PUSH_RECEIPT.json').read_text(encoding='utf-8'));source=receipt['source_and_weights_commit']
base=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):
 p=subprocess.run([*base,*args],capture_output=True,text=True,encoding='utf-8',errors='replace')
 if p.returncode:raise RuntimeError(p.stderr or p.stdout)
 return p.stdout.strip()
assert git('rev-parse','HEAD')==source
assert git('rev-parse',FINAL_TAG+'^{}')==source
assert not git('tag','--list',SYNC_TAG)
files=[(T/'SYNC_REPORT.md').relative_to(R).as_posix(),(T/'evidence/FINAL_GIT_PUSH_RECEIPT.json').relative_to(R).as_posix(),(T/'sync_archive.py').relative_to(R).as_posix(),Path(__file__).resolve().relative_to(R).as_posix()]
record_rel=record_path.relative_to(R).as_posix();allowed=set(files)|{record_rel}
staged=set(git('diff','--cached','--name-only').splitlines());assert staged<=allowed
note=T/'SYNC_REPORT.md'
with note.open('a',encoding='utf-8') as f:f.write('\n补录：首次同步回执的普通git add返回exit1，未形成sync提交/tag；主体final提交/28个PT的推送与读回验证已经成功。此处继续同一个已创建的sync记录，使用本项目既有的--sparse -f路径加入方式；原失败执行源码sync_archive.py保留，恢复源码见finish_receipt.py。不重做训练、评测或权重推送。\n')
d=json.loads(record_path.read_text(encoding='utf-8'))
d['initial_sync_note']=d['repair_or_experiment_note'];d['initial_source_and_evidence_sha256']=d['source_and_evidence_sha256']
d['repair_or_experiment_note']=note.read_text(encoding='utf-8')
d['source_and_evidence_sha256']={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in files}
d['sync_resume']=dict(epoch=time.time(),first_failed_operation='plain git add of sync receipt returned exit1 before commit/tag',continuation='same existing sync record, explicit --sparse -f; original failed source retained')
record_path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
git('add','--sparse','-f','--',record_rel,*files)
git('commit','-m',d['title']+'\n\nExperiment: '+SYNC_TAG+'\nValidation: '+d['validation'])
git('tag','-a',SYNC_TAG,'-m',d['title']+'\n\n'+d['repair_or_experiment_note'])
sync=git('rev-parse','HEAD');assert set(git('diff','--name-only',source,sync).splitlines())==allowed
git('push','--atomic','origin','HEAD','refs/tags/'+SYNC_TAG)
branch=git('branch','--show-current')
refs_raw=git('ls-remote','origin','refs/heads/'+branch,'refs/heads/main','refs/tags/'+FINAL_TAG,'refs/tags/'+FINAL_TAG+'^{}','refs/tags/'+SYNC_TAG,'refs/tags/'+SYNC_TAG+'^{}')
refs={x.split()[1]:x.split()[0] for x in refs_raw.splitlines()}
assert refs['refs/heads/'+branch]==sync and refs['refs/tags/'+FINAL_TAG+'^{}']==source and refs['refs/tags/'+SYNC_TAG+'^{}']==sync
print(json.dumps(dict(complete=True,source_commit=source,sync_commit=sync,final_tag=FINAL_TAG,sync_tag=SYNC_TAG,remote_refs=refs,full_PT_blobs_verified=receipt['full_PT_files_verified'],training_PT_files=receipt['training_PT_files'],remaining_status=git('status','--short')),ensure_ascii=False),flush=True)
