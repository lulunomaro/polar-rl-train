from pathlib import Path
import subprocess,hashlib,json,time
S=Path(__file__).resolve().parent;R=S.parents[2]
git=['git','-C',str(R),'-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true']
def run(*a):return subprocess.check_output([*git,*a],text=True,encoding='utf8').strip()
head=run('rev-parse','HEAD');remote=run('ls-remote','origin','refs/heads/main','refs/heads/mod4v1-experts-fulldr-rm70');refs={a.split()[1]:a.split()[0] for a in remote.splitlines()};assert refs['refs/heads/mod4v1-experts-fulldr-rm70']==head
staged=set(run('diff','--cached','--name-only').splitlines());rows=[];verified={}
for line in run('ls-files','--stage','--','*.pt','*.pth').splitlines():
 meta,name=line.split('\t',1);mode,oid,stage=meta.split();path=R/name
 if stage!='0' or name in staged or not path.is_file() or path.is_symlink() or path.stat().st_size<2048:continue
 if oid not in verified:
  size=path.stat().st_size;blob=hashlib.sha1(('blob '+str(size)+'\0').encode());sha=hashlib.sha256();first=b''
  with path.open('rb') as f:
   for chunk in iter(lambda:f.read(4*1024*1024),b''):
    if not first:first=chunk[:100]
    blob.update(chunk);sha.update(chunk)
  if first.startswith(b'version https://git-lfs.github.com/spec/') or blob.hexdigest()!=oid:continue
  verified[oid]=(sha.hexdigest(),size)
 sha,size=verified[oid];rows.append(dict(git_path=name,git_blob=oid,bytes=size,sha256=sha,ordinary_full_blob=True))
 if len(rows)%100==0:print('verified',len(rows),'published full PT paths',flush=True)
d=dict(epoch=time.time(),git_commit=head,verified_remote_refs=refs,proxy='http://127.0.0.1:7897',TLS_verify=True,method='Published HEAD; unchanged stage0 index; full local bytes match canonical Git blob OID plus SHA256; no history fetch, LFS/untracked/modified files excluded',models=rows,unique_full_blobs=len(verified),main_observation='main observed2fbc883d.. versus earlier launch snapshotdc7259b..; cleanup reads main only and preserves its current value')
(S/'evidence/VERIFIED_GIT_MODELS.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(dict(archived_PT_paths=len(rows),unique_full_blobs=len(verified),verified_remote_commit=head)),flush=True)
