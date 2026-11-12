"""Push full checkpoint payload through7897 and archive verified sync receipt."""
from pathlib import Path
import subprocess,json,hashlib,sys,time
T=Path(__file__).resolve().parent;R=T.parents[2]
TAG='trial-20261112-mod4-stair-lift-20m-01';ID='mod4-stair-lift-20m-sync-01';SYNC='trial-20261112-'+ID
BASE=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):return subprocess.run([*BASE,*args],capture_output=True,text=True,encoding='utf8',errors='replace',check=True).stdout.strip()
branch=git('branch','--show-current');source=git('rev-parse',TAG+'^{}');assert git('rev-parse','HEAD')==source and branch=='mod4v1-experts-fulldr-rm70'
def refs(*tags):
 names=['refs/heads/'+branch,'refs/heads/main']
 for tag in tags:names+=['refs/tags/'+tag,'refs/tags/'+tag+'^{}']
 return {line.split()[1]:line.split()[0] for line in git('ls-remote','origin',*names).splitlines()}
main_before=refs()['refs/heads/main'];print('PUSHING_FULL_PT_PAYLOAD '+source,flush=True);git('push','--atomic','origin','HEAD','refs/tags/'+TAG);remote=refs(TAG)
assert remote['refs/heads/'+branch]==source and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/heads/main']==main_before
weights=[]
for file in sorted((T/'weights').glob('*.pt')):
 rel=file.relative_to(R).as_posix();raw=subprocess.run([*BASE,'show',source+':'+rel],capture_output=True,check=True).stdout;digest=hashlib.sha256(raw).hexdigest();assert digest==hashlib.sha256(file.read_bytes()).hexdigest() and len(raw)==file.stat().st_size;weights.append(dict(path=rel,bytes=len(raw),sha256=digest,ordinary_full_blob=True))
receipt=dict(epoch=time.time(),payload_commit=source,payload_tag=TAG,branch=branch,proxy='http://127.0.0.1:7897',TLS_verify=True,remote_refs=remote,main_before=main_before,main_after=remote['refs/heads/main'],complete_checkpoint_blobs=weights,actual_status='Last confirmed635.524s; SSH lost; later15/20/final and nativefullDR pending; no claim of20m completion')
(T/'evidence/GIT_PUSH_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(T/'SYNC_REPORT.md').write_text(f'''# 台阶抬高底盘试验：Git同步回执

通过7897代理、TLS验证已开启。源码、原始配方、恢复与启动回执、3份完整PT、父/5m/10m名义MuJoCo台阶和平地结果、失败与目标SSH失联证据已经归档上传。

- Payload提交：`{source}`，annotated tag：`{TAG}`，远端peeled一致。
- 3个PT均作为普通完整Git blob读回核验，不是地址或LFS指针。
- 实验实际末段待目标恢复连接取回；没有把计划1200秒写成已确认完成1200秒，15/20/final与原生fullDR仍pending。
- 远端main保持`{main_before}`，分支`{branch}`已匹配payload提交。本回执随后独立提交并推送。
''',encoding='utf8')
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git
def proxied(*args):
 if args[0]=='add':return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f',*args[1:])
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=proxied
files=[(T/f).relative_to(R).as_posix() for f in ('SYNC_REPORT.md','evidence/GIT_PUSH_RECEIPT.json')]
sys.argv=['record_experiment.py','--id',ID,'--title','Record verified stair-lift experiment full PT upload and pending remote results','--kind','evaluation','--note-file',str(T/'SYNC_REPORT.md'),'--validation','Payload branch/tag/peeled matched;3complete PT ordinary Git bytes verified;7897proxy/TLS;main unchanged; incomplete remote status explicit','--files',*files,'--push'];rec.main();commit=git('rev-parse','HEAD');remote=refs(TAG,SYNC)
assert remote['refs/heads/'+branch]==commit and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/tags/'+SYNC+'^{}']==commit and remote['refs/heads/main']==main_before
print(json.dumps(dict(payload_commit=source,sync_commit=commit,payload_tag=TAG,sync_tag=SYNC,full_checkpoint_blobs=weights,remote_refs=remote),ensure_ascii=False),flush=True)
