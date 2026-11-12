"""Push this completed Rough-v1 archive through7897 and commit its sync receipt."""
from pathlib import Path
import json,subprocess,hashlib,time,sys
T=Path(__file__).resolve().parent;R=T.parents[2]
FINAL_TAG='trial-20261112-mod4-scut-rough-v1-2h-final-01';SYNC_ID='mod4-scut-rough-v1-2h-sync-01';SYNC_TAG='trial-20261112-'+SYNC_ID
BASE=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):
 p=subprocess.run([*BASE,*args],capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
 return p.stdout.strip()
source=git('rev-parse','HEAD');assert git('rev-parse',FINAL_TAG+'^{}')==source
completion=json.loads((T/'evidence/TRAINING_COMPLETION.json').read_text(encoding='utf-8'))
blob_checks=[]
for path in sorted(T.rglob('*.pt')):
 rel=path.relative_to(R).as_posix();local=path.read_bytes()
 actual=subprocess.run([*BASE,'show',source+':'+rel],capture_output=True,check=True).stdout
 assert len(actual)==len(local) and hashlib.sha256(actual).digest()==hashlib.sha256(local).digest(),rel
 blob_checks.append(dict(path=rel,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest(),ordinary_full_blob=True))
assert len([p for p in blob_checks if '/weights/' in p['path']])==completion['full_training_PT_files']
branch=git('branch','--show-current')
def refs(*tags):
 names=['refs/heads/'+branch,'refs/heads/main']
 for tag in tags:names+=['refs/tags/'+tag,'refs/tags/'+tag+'^{}']
 return {x.split()[1]:x.split()[0] for x in git('ls-remote','origin',*names).splitlines()}
old_main=refs()['refs/heads/main']
git('push','--atomic','origin','HEAD','refs/tags/'+FINAL_TAG)
remote=refs(FINAL_TAG);assert remote['refs/heads/'+branch]==source and remote['refs/tags/'+FINAL_TAG+'^{}']==source and remote['refs/heads/main']==old_main
receipt=dict(epoch=time.time(),source_and_weights_commit=source,final_tag=FINAL_TAG,proxy='http://127.0.0.1:7897',TLS_verify=True,branch=branch,remote_refs=remote,training_PT_files=completion['full_training_PT_files'],all_PT_blobs_verified=len(blob_checks),blobs=blob_checks)
(T/'evidence/FINAL_GIT_PUSH_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
note=f'''# Rough-v1 最终同步回执

统一两小时Rough-v1的执行源码、配方、全部完整PT本体、每五分钟读回/回放、原始短探针、读者修复、恢复原训练盘记录和已收齐5组正式PhysX评测已通过7897代理推送，TLS校验开启。

- 权重与源码提交：`{source}`；固定annotated tag：`{FINAL_TAG}`，远端peeled匹配。
- 本阶段完整训练PT {completion['full_training_PT_files']}份；实际从Git对象逐个读出全部{len(blob_checks)}个PT，包括短探针原件，大小与SHA均匹配。均为完整普通blob。
- 实际训练父为Rough-v0 100m/iter23665/SHA0010283962…；未回退R1。目标机SSH超时导致其余5组评测待收齐，不能称验收完成或GPU已释放。最终比较和接续选择见FINAL_REPORT/DECISION，不覆盖原实车包。
- 原远端main引用保留；分支{branch}已同步。回执文件随本次独立sync提交归档，最后的远端确认只作工具输出，不产生递归回执文件。
'''
(T/'SYNC_REPORT.md').write_text(note,encoding='utf-8')
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git
def proxy_git(*args):
 if args[0]=='add':return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f',*args[1:])
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=proxy_git
files=[(T/name).relative_to(R).as_posix() for name in ('SYNC_REPORT.md','evidence/FINAL_GIT_PUSH_RECEIPT.json')]
sys.argv=['record_experiment.py','--id',SYNC_ID,'--title','Record verified Rough-v1 full PT archive sync','--kind','evaluation','--note-file',str(T/'SYNC_REPORT.md'),'--validation','Full ordinary PT blobs read from Git match source bytes; final annotated tag/branch verified through7897; main unchanged','--files',*files,'--push']
rec.main();sync=git('rev-parse','HEAD');remote=refs(FINAL_TAG,SYNC_TAG)
assert remote['refs/heads/'+branch]==sync and remote['refs/tags/'+FINAL_TAG+'^{}']==source and remote['refs/tags/'+SYNC_TAG+'^{}']==sync and remote['refs/heads/main']==old_main
print(json.dumps(dict(source_commit=source,sync_commit=sync,final_tag=FINAL_TAG,sync_tag=SYNC_TAG,full_PT_blobs_verified=len(blob_checks),remote_refs=remote,remaining_status=git('status','--short')),ensure_ascii=False))
