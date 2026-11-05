"""One bounded own-metadata observer. Never opens model/trajectory/canonical or changes a running task."""
from pathlib import Path
import sys,json,time
D=Path(__file__).resolve().parent;M=D/'FDN_W2_COLLECTOR_ONCE.json';assert not M.exists();root=json.loads((D/'FDN_W2_STAGE_RESULT.json').read_bytes())['root'];job=root+'/roles/E3';out=D/'reports'/('FDN_W2_'+time.strftime('%Y%m%d_%H%M%S'));out.mkdir(parents=True);M.write_text(json.dumps(dict(root=root,started_epoch=time.time(),output=str(out)),indent=2),encoding='utf8');sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();c.get_transport().set_keepalive(30);s=c.open_sftp();last=None;first=False

def get(p):
 try:
  with s.open(p,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None

def put(name,x):
 p=out/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2,allow_nan=False),encoding='utf8');t.replace(p)
try:
 deadline=time.monotonic()+6000
 while True:
  outer=get(root+'/OUTER_OWNER_WAIT_ACTUAL.json');owner=get(root+'/OWNER_CURRENT.json');wait=get(root+'/PREGO_RESOURCE_WAIT.json');identity=get(job+'/WORKER_IDENTITY_ACTUAL.json');update=get(job+'/production/FDN_NATIVE_UPDATE.json');err=get(job+'/production/FDN_NATIVE_ERROR.json');final=get(job+'/production/FDN_FINAL.json');snapshot=dict(epoch=time.time(),root=root,owner_current=owner,resource_wait=wait,worker_identity=identity,native_update=update,worker_error=err,worker_final=final,outer_owner_wait=outer);put('LATEST_METADATA_SNAPSHOT.json',snapshot)
  if identity and not first:
   snapshot['actual_GO']=get(job+'/GO_PRODUCTION.json');snapshot['actual_root_admission']=get(job+'/ROOT_ADMISSION_ACTUAL.json');snapshot['actual_parent_identity']=get(root+'/OWNER_PARENT_IDENTITY.json');put('FIRST_ACTUAL_ADMISSION.json',snapshot);(D/'FDN_W2_FIRST_ADMISSION_PATH.json').write_text(json.dumps(dict(path=str(out/'FIRST_ACTUAL_ADMISSION.json')),indent=2),encoding='utf8');first=True
  token=(bool(identity),str(wait.get('reason'))if wait and not identity else None,(update or {}).get('counters',{}).get('updates',-1)//10,bool(err),bool(outer))
  if token!=last:
   print(json.dumps(dict(epoch=time.time(),worker_identity=identity,updates=(update or {}).get('counters'),has_native_error=bool(err),resource_wait_reason=token[1],outer_owner_wait=outer)),flush=True);last=token
  if outer:
   data={}
   for n in('OWNER_EXIT_ACTUAL.json','COHORT_FINAL.json','OWNER_ORIGINAL_ERROR.json','OUTER_OWNER_WAIT_ACTUAL.json','OWNER_PARENT_IDENTITY.json'):data[n]=get(root+'/'+n)
   for n in('FDN_FINAL.json','FDN_PARENT_WAIT_QUALIFICATION.json','FDN_LATEST_COMPLETE_SAVE.json','FDN_SINGLE_SOURCE_NEW_BRANCH_WARM_START.json','FDN_FRESH_NEW_NOMINAL_RESET.json','FDN_NATIVE_UPDATE.json','FDN_NATIVE_ERROR.json','FDN_SAVE_ERROR.json','FDN_FINAL_METADATA_ERROR.json','FDN_APP_FAST_CLOSE_INTENT.json','FDN_APP_CLOSE_RETURNED.json','FDN_APP_CLOSE_ERROR.json','FDN_TASK_RESOURCE_BOUND_BEFORE_SDK_MODEL.json'):data[n]=get(job+'/production/'+n)
   logs={}
   for relative in('OWNER_STDOUT_STDERR.log','roles/E3/FDN_FULL_STDOUT_STDERR.log'):
    try:
     with s.open(root+'/'+relative,'rb')as f:f.seek(max(0,f.stat().st_size-18000));logs[relative]=f.read().decode('utf8','replace')
    except FileNotFoundError:pass
   result=dict(root=root,closed=True,metadata=data,diagnostic_log_tails_once=logs,models_raw_or_canonical_reads=0);put('CLOSED_RESULT.json',result);(D/'FDN_W2_LATEST_CLOSED_RESULT_PATH.json').write_text(json.dumps(dict(path=str(out/'CLOSED_RESULT.json')),indent=2),encoding='utf8');print(json.dumps(dict(closed_result=str(out/'CLOSED_RESULT.json'),original_owner_exit=data['OWNER_EXIT_ACTUAL.json'],outer=outer)),flush=True);break
  if time.monotonic()>=deadline:put('OBSERVER_TIMEOUT_METADATA_ONLY.json',snapshot);raise TimeoutError('Own observer6000 elapsed; original task unchanged')
  time.sleep(15)
finally:s.close();c.close()
