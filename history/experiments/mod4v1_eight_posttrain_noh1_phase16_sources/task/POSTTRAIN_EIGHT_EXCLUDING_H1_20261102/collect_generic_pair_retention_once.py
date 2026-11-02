"""Oneboundedownpublishedtwo-memberretentioncollector, rolesaredispatchdata. Nevermodel/raw/evalreruns/Coperations."""
from pathlib import Path
import argparse,json,sys,time,datetime,hashlib
D=Path(__file__).resolve().parent;R=D.parent;sys.path.insert(0,str(R));from project_connector import connect72
q=argparse.ArgumentParser();q.add_argument('--pair',required=True,type=int,choices=(2,3,4));a=q.parse_args();tag='PAIR'+str(a.pair)+'_FROZEN_RETENTION_V1';dispatch=json.loads((D/(tag+'_DISPATCH_ONCE.json')).read_bytes());roles=dispatch['roles'];assert len(roles)==2 and len(set(roles))==2 and'H1'not in roles;root=dispatch['root'];marker=D/(tag+'_COLLECTOR_ONCE.json');assert not marker.exists();out=D/'reports'/(tag+'_CLOSED_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));out.mkdir(parents=True);marker.write_text(json.dumps({'root':root,'roles':roles,'metadata_only':True,'bounded_seconds':4500},indent=2),encoding='utf-8');c=connect72();s=c.open_sftp();end=time.monotonic()+4500;last=None

def get(rel):
 try:
  with s.open(root+'/'+rel,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None
try:
 while True:
  ex=get('PARENT_EXIT_SCOPE.json');bar=get('GROUP_BARRIER_STATUS.json');start=get('GROUP_EVAL_START.json');err=get('PARENT_ORIGINAL_ERROR.json');state=dict(root=root,closed=ex is not None,common_started=start is not None,barrier=bar,parent_error=err is not None);sig=json.dumps({k:v for k,v in state.items()if k!='barrier'},sort_keys=True)+str((bar or{}).get('ready'))+str((bar or{}).get('failed'))
  if sig!=last:print('GENERIC_RETENTION_ACTUAL_STATUS',json.dumps(state),flush=True);last=sig
  if ex is not None:
   final=get('FINAL.json');result=dict(kind='GENERIC_PAIR_POSTTRAIN_FROZEN_RETENTION_CLOSED_ACTUAL_NOT_GLOBALPASS',pair=a.pair,roles=roles,root=root,parent_exit=ex,parent_error=err,final=final,model_raw_SDK_Coperations_bycollector=0);files=[];paths=[x.filename for x in s.listdir_attr(root)if x.filename.endswith(('.json','.log'))]
   for role in roles:
    try:paths+=['cases/'+role+'/'+x.filename for x in s.listdir_attr(root+'/cases/'+role)if x.filename.endswith(('.json','.log'))]
    except FileNotFoundError:pass
   for rel in paths:
    st=s.stat(root+'/'+rel)
    if st.st_size>50000000:files.append(dict(remote=root+'/'+rel,bytes=st.st_size,large_original_metadata_retained=True));continue
    with s.open(root+'/'+rel,'rb')as z:raw=z.read()
    p=out/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);files.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
   result['files']=files;p=out/'CLOSED_RESULT.json';p.write_text(json.dumps(result,indent=2),encoding='utf-8');(D/(tag+'_LATEST_CLOSED_RESULT_PATH.json')).write_text(json.dumps({'path':str(p)},indent=2),encoding='utf-8');print('RESULT',p,flush=True);print(json.dumps(dict(parent_exit=ex,error=err,final_exists=final is not None),indent=2),flush=True);break
  if time.monotonic()>=end:raise TimeoutError('Originalbounded4500smetadatawatch,noautomaticphysicalretry')
  time.sleep(15)
finally:s.close();c.close()
