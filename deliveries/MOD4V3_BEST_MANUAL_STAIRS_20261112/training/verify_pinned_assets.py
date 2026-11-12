from pathlib import Path
import sys,json,hashlib,time
ROOT=Path(r'D:/claude2/fangzhen');sys.path.insert(0,str(ROOT/'tmp'))
from step7_remote_access import connect
T=ROOT/'_mod4v2_src_20261106/sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112';P=json.loads((T/'PLAN.json').read_text(encoding='utf-8'))
c=connect();s=c.open_sftp();rows=[]
for name,expected in P['asset_identity']['actual_training_assets'].items():
 path=P['package']+'/assets/'+name
 with s.open(path,'rb') as f:content=f.read()
 rows.append(dict(name=name,path=path,bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),expected_sha256=expected['sha256'],matches=hashlib.sha256(content).hexdigest()==expected['sha256']))
s.close();c.close()
r=dict(epoch=time.time(),scope='Post-training pinned asset-file verification; startup native mechanical limits/mass gates are recorded separately in STARTUP.json',assets=rows)
(T/'evidence/PINNED_ASSET_FILES_VERIFIED.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert all(x['matches'] for x in rows)
print(json.dumps(dict(assets=len(rows),all_pinned_hashes_match=True,root_USD_sha256=next(x['sha256'] for x in rows if x['name']=='robot.usd')),ensure_ascii=False))
