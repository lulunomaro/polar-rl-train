"""Boundedownpublishedmetadata collector for two-candidate frozenretention; no model/raw/evalrerun."""
from pathlib import Path
import json,sys,time,datetime,hashlib
D=Path(__file__).resolve().parent;R=D.parent;sys.path.insert(0,str(R));from project_connector import connect72
m=D/'PAIR1_RETENTION_V4_COLLECTOR_ONCE.json';assert not m.exists();root=json.loads((D/'PAIR1_RETENTION_V4_PARENT_DISPATCH_ONCE.json').read_bytes())['root'];out=D/'reports'/('PAIR1_RETENTION_V4_CLOSED_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));out.mkdir(parents=True);m.write_text(json.dumps({'root':root,'metadataonly':True,'deadline_seconds':4500},indent=2),encoding='utf-8');c=connect72();s=c.open_sftp();end=time.monotonic()+4500;last=None

def get(rel):
 try:
  with s.open(root+'/'+rel,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None
try:
 while True:
  ex=get('PARENT_EXIT_SCOPE.json');bar=get('GROUP_BARRIER_STATUS.json');start=get('GROUP_EVAL_START.json');err=get('PARENT_ORIGINAL_ERROR.json');state={'root':root,'closed':ex is not None,'common_started':start is not None,'barrier':bar,'parent_error':err is not None};sig=json.dumps({k:v for k,v in state.items()if k!='barrier'},sort_keys=True)+str((bar or{}).get('ready'))+str((bar or{}).get('failed'))
  if sig!=last:print('RETENTION_ACTUAL_STATUS',json.dumps(state),flush=True);last=sig
  if ex is not None:
   final=get('FINAL.json');result={'kind':'PAIR1_POSTTRAIN_FROZEN_RETENTION_CLOSED_ACTUAL','root':root,'parent_exit':ex,'parent_error':err,'final':final,'raw_model_SDK_replays':0};files=[];paths=[a.filename for a in s.listdir_attr(root)if a.filename.endswith(('.json','.log'))]
   for role in('E0','CURB_PROTECTED878'):
    try:paths+=['cases/'+role+'/'+a.filename for a in s.listdir_attr(root+'/cases/'+role)if a.filename.endswith(('.json','.log'))]
    except FileNotFoundError:pass
   for rel in paths:
    st=s.stat(root+'/'+rel)
    if st.st_size>50000000:files.append({'remote':root+'/'+rel,'bytes':st.st_size,'large_artifact_retained':True});continue
    with s.open(root+'/'+rel,'rb')as z:raw=z.read()
    p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);files.append({'relative':rel,'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()})
   result['files']=files;p=out/'CLOSED_RESULT.json';p.write_text(json.dumps(result,indent=2),encoding='utf-8');(D/'PAIR1_RETENTION_V4_LATEST_CLOSED_RESULT_PATH.json').write_text(json.dumps({'path':str(p)},indent=2),encoding='utf-8');print('RESULT',p,flush=True);print(json.dumps({'parent_exit':ex,'error':err,'final_exists':final is not None},indent=2),flush=True);break
  if time.monotonic()>=end:raise TimeoutError('Originalboundedcollector4500s, noautomaticreplay')
  time.sleep(15)
finally:s.close();c.close()
