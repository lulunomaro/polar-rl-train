from pathlib import Path
import json,sys,subprocess,hashlib,time
T=Path(__file__).resolve().parent;R=T.parents[2];TAG='trial-20261112-mod4-stair-speed-causal-audit-01';ID='mod4-stair-speed-audit-sync-01';SYNC='trial-20261112-'+ID;BASE=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):return subprocess.run([*BASE,*args],capture_output=True,text=True,encoding='utf8',errors='replace',check=True).stdout.strip()
branch=git('branch','--show-current');source=git('rev-parse',TAG+'^{}');assert git('rev-parse','HEAD')==source
assert branch=='mod4v1-experts-fulldr-rm70'
def refs(*tags):
 names=['refs/heads/'+branch,'refs/heads/main']
 for t in tags:names+=['refs/tags/'+t,'refs/tags/'+t+'^{}']
 return {line.split()[1]:line.split()[0] for line in git('ls-remote','origin',*names).splitlines()}
main_before=refs()['refs/heads/main'];print('PUSHING_AUDIT '+source,flush=True);git('push','--atomic','origin','HEAD','refs/tags/'+TAG);remote=refs(TAG)
assert remote['refs/heads/'+branch]==source and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/heads/main']==main_before
artifacts=[]
for file in sorted(T.rglob('*.npz')):
 rel=file.relative_to(R).as_posix();raw=subprocess.run([*BASE,'show',source+':'+rel],capture_output=True,check=True).stdout;digest=hashlib.sha256(raw).hexdigest();assert digest==hashlib.sha256(file.read_bytes()).hexdigest() and len(raw)==file.stat().st_size;artifacts.append(dict(path=rel,bytes=len(raw),sha256=digest,ordinary_full_blob=True))
receipt=dict(epoch=time.time(),payload_commit=source,tag=TAG,branch=branch,proxy='http://127.0.0.1:7897',TLS_verify=True,remote_refs=remote,main_before=main_before,main_after=remote['refs/heads/main'],full_diagnostic_arrays=artifacts,training_started=False,production_source_changed=False)
(T/'evidence/GIT_PUSH_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(T/'SYNC_REPORT.md').write_text(f'''# 平地超速只读调查同步回执

93个冻结回放、腿/轮控制通道互换、普通/高站姿对照、共同输入分析、精确奖励计算、9个历史检查点对照、图和原始NPZ均已通过7897代理上传，TLS验证开启。

Payload提交：`{source}`；annotated tag：`{TAG}`；远端branch/tag/peeled一致。{len(artifacts)}个NPZ已从Git作为完整blob读回核验。main保持`{main_before}`。没有启动训练，没有修改生产/冻结源、奖励、plant或PT。原生fullDR与训练奖励消融尚未执行的限制保留于报告。

本回执单独归档后再次推送，最终确认只在工具输出中展示。
''',encoding='utf8')
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'));import record_experiment as rec
original=rec.git
def proxy(*args):
 if args[0]=='add':return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f',*args[1:])
 return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=proxy
files=[(T/f).relative_to(R).as_posix() for f in ('evidence/GIT_PUSH_RECEIPT.json','SYNC_REPORT.md')]
sys.argv=['record_experiment.py','--id',ID,'--title','Record verified nominal speed causal audit upload','--kind','diagnostic','--note-file',str(T/'SYNC_REPORT.md'),'--validation','93frozen replays and original arrays archived; branch/tag/peeled and fullNPZ blobs verified;7897proxy/TLS;main unchanged; no training','--files',*files,'--push'];rec.main();sync=git('rev-parse','HEAD');remote=refs(TAG,SYNC)
assert remote['refs/heads/'+branch]==sync and remote['refs/tags/'+TAG+'^{}']==source and remote['refs/tags/'+SYNC+'^{}']==sync and remote['refs/heads/main']==main_before
print(json.dumps(dict(payload_commit=source,sync_commit=sync,payload_tag=TAG,sync_tag=SYNC,full_NPZ_blobs=artifacts,remote_refs=remote),ensure_ascii=False),flush=True)
