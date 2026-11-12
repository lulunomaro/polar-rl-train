"""Push completed repair and separately archive the concrete verified upload receipt."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
T=Path(__file__).resolve().parent
R=T.parents[2]
TAG='trial-20261112-mod4-flat-speed-repair-01'
ID='mod4-flat-speed-repair-sync-01'
SYNC='trial-20261112-'+ID
BASE=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def git(*args):
    result=subprocess.run([*BASE,*args],capture_output=True,text=True,encoding='utf8',errors='replace')
    if result.returncode:
        raise RuntimeError('Git '+args[0]+' failed: '+result.stderr.strip())
    return result.stdout.strip()
branch=git('branch','--show-current')
source=git('rev-parse',TAG+'^{}')
assert git('rev-parse','HEAD')==source
assert branch=='mod4v1-experts-fulldr-rm70'
def refs(*tags):
    names=['refs/heads/'+branch,'refs/heads/main']
    for tag in tags:
        names+=['refs/tags/'+tag,'refs/tags/'+tag+'^{}']
    return {line.split()[1]:line.split()[0] for line in git('ls-remote','origin',*names).splitlines()}
main_before=refs()['refs/heads/main']
print('PUSHING_REPAIR '+source,flush=True)
git('push','--atomic','origin','HEAD','refs/tags/'+TAG)
remote=refs(TAG)
assert remote['refs/heads/'+branch]==source
assert remote['refs/tags/'+TAG]==git('rev-parse',TAG)
assert remote['refs/tags/'+TAG+'^{}']==source
assert remote['refs/heads/main']==main_before
manifest=json.loads((T/'evidence/FULL_ARTIFACT_MANIFEST.json').read_text(encoding='utf8'))
artifacts=[]
for entry in manifest['files']:
    path=entry['path']
    if Path(path).suffix not in {'.pt','.pth','.npz','.npy','.png','.msh'}:
        continue
    raw=subprocess.run([*BASE,'show',source+':'+path],capture_output=True,check=True).stdout
    digest=hashlib.sha256(raw).hexdigest()
    assert digest==entry['sha256'] and len(raw)==entry['bytes'], path
    assert digest==hashlib.sha256((R/path).read_bytes()).hexdigest(), path
    assert not raw.startswith(b'version https://git-lfs.github.com/spec/'), path
    artifacts.append(dict(path=path,bytes=len(raw),sha256=digest,ordinary_full_blob=True))
assert sum(x['path'].endswith('.pt') for x in artifacts)==14
print('VERIFIED_FULL_BINARY_BLOBS '+str(len(artifacts)),flush=True)
receipt=dict(epoch=time.time(),payload_commit=source,tag=TAG,branch=branch,proxy='http://127.0.0.1:7897',TLS_verify=True,remote_refs=remote,main_before=main_before,main_after=remote['refs/heads/main'],verification='Remote branch/tag/peeled refs identify accepted payload commit; all binary artifacts read from the committed Git objects and checked against original local sizes and SHA256 (not LFS pointers).',full_binary_artifacts=artifacts,full_PT_count=14,training_completed=True,training_seconds=2405.762491941452,further_training_started=False,original_mature_snapshot_retained=True,real_robot_deployed=False)
(T/'evidence/GIT_PUSH_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(T/'SYNC_REPORT.md').write_text(f'''# 平地欠速/超速恢复实验同步回执

40分5.762秒两段同轮训练、全部12个完整PPO检查点、1个被拒绝离线PT、1个最终完整PT别名、原始轨迹、所有成功/失败/未采用实验、训练源码、实际依赖、配方、图表和五份管理索引已通过7897代理上传，TLS验证开启。

Payload提交：{source}

Annotated tag：{TAG}

远端branch、tag对象与peeled commit一致。全部{len(artifacts)}个二进制原件（含14个PT）已从提交对象读回核验完整字节大小及SHA256，未存成LFS指针。main保持{main_before}。

原六项名义MuJoCo60/60；扩展49点45/49、MAE0.0757m/s；原生完整DR23/30，推扰后24/30。名义PhysX24/30到20/30的退步与部分高站姿残余保留在REPORT中。抬高上阶和下阶仅按实际名义单次对照保留能力。轮400Hz/腿100Hz为明确配方；未部署实车，未覆盖原成熟包，也未据此宣布跨引擎全部毕业。

本回执另用唯一trial归档并推送，最后远端核验仅在工具输出中展示。
''',encoding='utf8')
sys.path.insert(0,str(R.parent/'tmp/step7_archive_helper'))
import record_experiment as rec
original=rec.git
def proxy(*args):
    if args[0]=='add':
        return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','add','--sparse','-f',*args[1:])
    return original('-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true',*args)
rec.git=proxy
files=[(T/f).relative_to(R).as_posix() for f in ['evidence/GIT_PUSH_RECEIPT.json','SYNC_REPORT.md']]
sys.argv=['record_experiment.py','--id',ID,'--title','Record verified flat speed repair full checkpoint upload','--kind','repair','--note-file',str(T/'SYNC_REPORT.md'),'--validation','Payload branch/tag/peeled and all14fullPT plus original binary blobs verified;7897proxy/TLS;main unchanged;original mature parent retained;no further training or real-car deployment','--files',*files,'--push']
rec.main()
sync=git('rev-parse','HEAD')
remote=refs(TAG,SYNC)
assert remote['refs/heads/'+branch]==sync
assert remote['refs/tags/'+TAG]==git('rev-parse',TAG)
assert remote['refs/tags/'+TAG+'^{}']==source
assert remote['refs/tags/'+SYNC]==git('rev-parse',SYNC)
assert remote['refs/tags/'+SYNC+'^{}']==sync
assert remote['refs/heads/main']==main_before
print(json.dumps(dict(payload_commit=source,sync_commit=sync,payload_tag=TAG,sync_tag=SYNC,full_PT_files=14,full_binary_files=len(artifacts),remote_refs=remote),ensure_ascii=False),flush=True)
