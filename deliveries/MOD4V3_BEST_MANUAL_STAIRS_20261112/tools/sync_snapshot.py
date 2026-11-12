from pathlib import Path
import subprocess,json,hashlib,sys,time,shutil
R=Path(r'D:/claude2/fangzhen/_mod4v2_src_20261106');P=R/'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
TAG='trial-20261112-mod4-best-manual-stairs-01';SYNC_ID='mod4-best-manual-stairs-sync-01';SYNC_TAG='trial-20261112-'+SYNC_ID
BASE=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):
 result=subprocess.run([*BASE,*args],capture_output=True,text=True,encoding='utf8',errors='replace',check=True)
 return result.stdout.strip()
branch=git('branch','--show-current');source=git('rev-parse',TAG+'^{}');assert git('rev-parse','HEAD')==source
assert branch=='mod4v1-experts-fulldr-rm70'
def refs(*tags):
 names=['refs/heads/'+branch,'refs/heads/main']
 for t in tags:names+=['refs/tags/'+t,'refs/tags/'+t+'^{}']
 return {line.split()[1]:line.split()[0] for line in git('ls-remote','origin',*names).splitlines()}
before=refs();main_before=before['refs/heads/main']
print('PUSHING_MODEL_AND_RECIPE',source,flush=True)
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
remote=refs(TAG)
assert remote['refs/heads/'+branch]==source and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/heads/main']==main_before
model='deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/model/training_checkpoint.pt'
raw=subprocess.run([*BASE,'show',source+':'+model],capture_output=True,check=True).stdout
expected=json.loads((P/'MODEL_IDENTITY.json').read_text(encoding='utf8'))['sha256']
assert hashlib.sha256(raw).hexdigest()==expected and len(raw)==(R/model).stat().st_size
receipt=dict(date='2026-11-12',timezone='Asia/Shanghai',payload_commit=source,tag=TAG,branch=branch,proxy='http://127.0.0.1:7897',TLS_verify=True,remote_refs_after_payload_push=remote,model=dict(path=model,bytes=len(raw),sha256=expected,ordinary_full_blob=True),local_portable_replay=json.loads((P/'evidence/PORTABLE_REPLAY_CHECK.json').read_text(encoding='utf8'))['success'],main_before=main_before,main_after=remote['refs/heads/main'],epoch=time.time())
(P/'evidence/GIT_PUSH_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(P/'SYNC_REPORT.md').write_text(f'''# 11月12日命名模型上传核验

用户选定快照“11月12日最牛逼的模型”、完整PT本体、实际训练参数/源码/启动记录、当前机械资产、手动方向/高度控制、全部750块地形、成功和失败原记录已通过7897代理推送，TLS校验开启。

- 模型和配方提交：`{source}`。
- 固定annotated tag：`{TAG}`，远端peeled对象与提交一致。
- 分支：`{branch}`，远端分支已匹配模型提交；本同步回执再补一次提交。
- 当前PT为完整普通Git blob，实际从Git读回{len(raw)}字节，SHA256 `{expected}`，与当前播放文件相同。
- 独立包已复现0.365m机身高度、2.2m/s前进指令助跑，登上连续两级16.5cm并在33cm平台停车保持，0重置；0.40m条件的原短回放也成功。旧低速失败和完整DR PhysX报告一起保留。
- 远端main保持`{main_before}`。以下回执随本次sync提交保存；最终同步确认只在工具输出报告。
''',encoding='utf8')
copy=P/'tools/sync_snapshot.py'
if Path(__file__).resolve()!=copy.resolve():shutil.copy2(__file__,copy)
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git
def proxied(*args):
 if args[0]=='add':return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f',*args[1:])
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=proxied
files=[(P/name).relative_to(R).as_posix() for name in ['SYNC_REPORT.md','evidence/GIT_PUSH_RECEIPT.json','tools/sync_snapshot.py']]
sys.argv=['record_experiment.py','--id',SYNC_ID,'--title','Record verified Nov12 selected model and full recipe upload','--kind','evaluation','--note-file',str(P/'SYNC_REPORT.md'),'--validation','Payload branch/tag/peeled match; full11746021-byte ordinary PT blob SHA verified from Git; 7897proxy/TLS; main unchanged; portable stair-ascent evidence preserved','--files',*files,'--push']
rec.main();sync=git('rev-parse','HEAD');remote=refs(TAG,SYNC_TAG)
assert remote['refs/heads/'+branch]==sync and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/tags/'+SYNC_TAG+'^{}']==sync and remote['refs/heads/main']==main_before
print(json.dumps(dict(payload_commit=source,sync_commit=sync,tag=TAG,sync_tag=SYNC_TAG,branch=branch,model_sha256=expected,full_PT_bytes=len(raw),remote_refs=remote,remaining_status=git('status','--short')),ensure_ascii=False),flush=True)
