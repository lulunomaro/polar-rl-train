"""Push the completed archive through7897, verify full PT blobs, then archive its sync receipt."""
from pathlib import Path
import json,subprocess,hashlib,time,sys
T=Path(__file__).resolve().parent;R=T.parents[2]
FINAL_TAG='trial-20261112-mod4-scut-rough-v0-2h-final-01'
SYNC_ID='mod4-scut-rough-v0-2h-sync-01';SYNC_TAG='trial-20261112-'+SYNC_ID
BASE=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):
 p=subprocess.run([*BASE,*args],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
 return p.stdout.strip(),p.stderr.strip()
source_head=git('rev-parse','HEAD')[0];assert git('rev-parse',FINAL_TAG+'^{}')[0]==source_head
blob_checks=[]
for path in sorted(T.rglob('*.pt')):
 rel=path.relative_to(R).as_posix();local=path.read_bytes()
 data=subprocess.run([*BASE,'show',source_head+':'+rel],capture_output=True,check=True).stdout
 assert len(data)==len(local) and hashlib.sha256(data).digest()==hashlib.sha256(local).digest(),rel
 blob_checks.append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),ordinary_full_blob_verified=True))
assert len(blob_checks)==28
out,err=git('push','--atomic','origin','HEAD','refs/tags/'+FINAL_TAG)
branch=git('branch','--show-current')[0]
def refs(*tags):
 names=['refs/heads/'+branch,'refs/heads/main']
 for tag in tags:names+=['refs/tags/'+tag,'refs/tags/'+tag+'^{}']
 raw=git('ls-remote','origin',*names)[0]
 return {line.split()[1]:line.split()[0] for line in raw.splitlines()}
remote=refs(FINAL_TAG)
assert remote['refs/heads/'+branch]==source_head and remote['refs/tags/'+FINAL_TAG+'^{}']==source_head
receipt=dict(epoch=time.time(),source_and_weights_commit=source_head,tag=FINAL_TAG,proxy='http://127.0.0.1:7897',TLS_verify=True,branch=branch,remote_refs=remote,full_PT_blobs=blob_checks,full_PT_files_verified=len(blob_checks),training_PT_files=26,probe_PT_alias_files=2,push_stdout=out,push_stderr=err)
receipt_path=T/'evidence/FINAL_GIT_PUSH_RECEIPT.json';receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note=f'''# 最终Git同步回执

2026-11-12，统一SCUT Rough-v0两小时的完整源码、26份训练PT、2份短探针PT原件、实际失败/日志、8组同批PhysX评测、README和全局模型索引已提交并通过7897代理推送，TLS校验开启。

- 权重/源码最终提交：`{source_head}`。
- 固定annotated tag：`{FINAL_TAG}`，远端peeled与该提交一致。
- 分支：`{branch}`；推送后该分支HEAD与该提交一致，实际查询时刻与main引用见evidence/FINAL_GIT_PUSH_RECEIPT.json。
- 逐个从Git对象实际读出28个PT，bytes与SHA256均等于本地已读回的完整PT，含26个训练文件和2个短探针同字节原件；都是完整blob，不是LFS指针或仅地址。
- 综合继续选r1round2_005m，本轮100m/120m未晋升，原冻结和实车包保持原身份。

本文件和推送回执由后续独立sync记录提交，不改最终权重/源码tag。该sync记录只添加同步材料；其最终远端确认由本次工具结果及最终回复提供，不再生成递归回执。
'''
(T/'SYNC_REPORT.md').write_text(note,encoding='utf-8')
print(json.dumps(dict(source_commit=source_head,final_tag=FINAL_TAG,full_PT_blobs_verified=28,source_push_verified=True),ensure_ascii=False),flush=True)
# The ordinary recorder handles this small text-only receipt record.
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
files=[(T/'SYNC_REPORT.md').relative_to(R).as_posix(),receipt_path.relative_to(R).as_posix(),Path(__file__).relative_to(R).as_posix()]
sys.argv=['record_experiment.py','--id',SYNC_ID,'--title','Record verified Rough-v0 archive push and full PT blob receipt','--kind','diagnostic','--note-file',str(T/'SYNC_REPORT.md'),'--validation','7897 proxy with TLS verification; remote branch and annotated final tag peeled match source commit;28 PT Git objects read and SHA/bytes checked; no model or training changes','--files',*files]
rec.main()
sync_head=git('rev-parse','HEAD')[0]
changed=set(git('diff','--name-only',source_head,sync_head)[0].splitlines())
assert changed==set(files)|{'history/experiments/20261112-'+SYNC_ID+'.json'}
git('push','--atomic','origin','HEAD','refs/tags/'+SYNC_TAG)
remote=refs(FINAL_TAG,SYNC_TAG)
assert remote['refs/heads/'+branch]==sync_head
assert remote['refs/tags/'+FINAL_TAG+'^{}']==source_head
assert remote['refs/tags/'+SYNC_TAG+'^{}']==sync_head
status=git('status','--short')[0]
print(json.dumps(dict(complete=True,source_commit=source_head,sync_commit=sync_head,final_tag=FINAL_TAG,sync_tag=SYNC_TAG,remote_refs=remote,full_PT_blobs_verified=28,training_PT_files=26,remaining_status=status),ensure_ascii=False),flush=True)
