from pathlib import Path
import base64,hashlib,json,time,urllib.parse,urllib.request,traceback
N=Path(__file__).resolve().parent;R=N/'reports';commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
put('ROOT188_PLANE_TERRAIN_SOURCE_PURPOSE_CONSUMED.json',dict(epoch=time.time(),paths=['plane/wheel_legged_gym/utils/terrain.py'],reason='Exact selected 上台阶3 snapshot configuration uses plane terrain helper, not jump variant',models=0))
try:
 rel='plane/wheel_legged_gym/utils/terrain.py'
 url='https://api.github.com/repos/yly-true/fudan_rl_wheel_leg/contents/'+urllib.parse.quote(rel,safe='/')+'?ref='+commit
 req=urllib.request.Request(url,headers={'User-Agent':'MOD4-authorized-stairs188','Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=45) as f:value=json.loads(f.read())
 raw=base64.b64decode(value['content']);assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==value['sha']
 p=N/'upstream'/rel;p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb') as f:f.write(raw)
 put('ROOT188_PLANE_TERRAIN_EXACT_SOURCE_RETURNED_ACTUAL.json',dict(epoch=time.time(),commit=commit,relative=rel,path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),git_blob_SHA=value['sha'],source_edits=0))
 print(json.dumps(dict(source=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())))
except BaseException:
 put('ROOT188_PLANE_TERRAIN_SOURCE_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_retry=True));raise
