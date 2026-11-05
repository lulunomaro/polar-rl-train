"""One bounded own-metadata observer. Never reads models, old raw, C or GPU state."""
from pathlib import Path
import json,time,sys
D=Path(__file__).resolve().parent;marker=D/'COLLECT_NINE_ADMISSION2_ONCE.json';assert not marker.exists();s=json.loads((D/'STAGE_NINE_ADMISSION2_RESULT.json').read_bytes());root=s['root'];plan=json.loads((D/'SOURCE_PLAN_ADMISSION2_ACTUAL_V1.json').read_bytes());out=D/'reports'/s['run_id'];out.mkdir(parents=True,exist_ok=False);marker.write_text(json.dumps(dict(epoch=time.time(),root=root,output=str(out),model_raw_or_canonical_reads=0),indent=2),encoding='utf8')
sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();ftp=c.open_sftp();cache={};last=None;closed=False
root_names=['OWNER_STARTED.json','PREGO_RESOURCE_WAIT.json','OWNER_PROGRESS.json','COHORT_FINAL.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','OUTER_OWNER_IDENTITY.json','OUTER_OWNER_WAIT_ACTUAL.json']
prod_names=['V2_NATIVE_INITIALIZED.json','V2_LEARNER_LOADED.json','V2_COMPLETE_SAVE.json','V2_MIGRATION_FINAL.json','V2_APP_CLOSE_INTENT.json','ENV_CLOSE_RETURNED.json','APP_CLOSED.json']
def get(path):
 assert path.startswith(root+'/')and path.endswith('.json')
 try:
  st=ftp.stat(path);signature=(st.st_mtime,st.st_size)
  if path in cache and cache[path][0]==signature:return cache[path][1]
  with ftp.open(path,'r')as f:value=json.loads(f.read())
  cache[path]=(signature,value);return value
 except FileNotFoundError:return None

def put(name,value):
 p=out/name;tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(value,indent=2),encoding='utf8');tmp.replace(p)

try:
 until=time.monotonic()+24000
 while time.monotonic()<until:
  meta={name:get(root+'/'+name)for name in root_names};cases={};summary=[]
  for e in plan['entries']:
   role=e['role'];p=root+'/roles/'+role;row={name:get(p+'/production/'+name)for name in prod_names};row['GO_PRODUCTION.json']=get(p+'/GO_PRODUCTION.json');row['WORKER_IDENTITY_ACTUAL.json']=get(p+'/WORKER_IDENTITY_ACTUAL.json');row['PARENT_WAITED_ACTUAL.json']=get(p+'/PARENT_WAITED_ACTUAL.json')
   try:names=ftp.listdir(p+'/production')
   except FileNotFoundError:names=[]
   row['ERROR_JSON']={n:get(p+'/production/'+n)for n in names if n.endswith('.json')and 'ERROR'in n};cases[role]=row;final=row['V2_MIGRATION_FINAL.json'];save=row['V2_COMPLETE_SAVE.json']or{};q=row['PARENT_WAITED_ACTUAL.json']or{}
   summary.append(dict(role=role,GO=row['GO_PRODUCTION.json']is not None,native_before_PT=row['V2_NATIVE_INITIALIZED.json']is not None,learner_loaded=row['V2_LEARNER_LOADED.json']is not None,actual_new_updates=(final or{}).get('completed_actual_updates',save.get('actual_new_updates')),worker_error=bool(row['ERROR_JSON']),actual_parent_wait=q.get('returncode'),qualified=(q.get('semantic_qualification')or{}).get('qualified')))
  value=dict(epoch=time.time(),root=root,metadata=meta,cases=cases,models_raw_or_canonical_reads=0);put('LATEST_METADATA.json',value);token=json.dumps(dict(summary=summary,exit=meta['OWNER_EXIT_ACTUAL.json']is not None,outer=meta['OUTER_OWNER_WAIT_ACTUAL.json']),sort_keys=True)
  if token!=last:print(json.dumps(dict(epoch=value['epoch'],roles=summary,owner_exit=meta['OWNER_EXIT_ACTUAL.json']is not None,outer_actual_wait=meta['OUTER_OWNER_WAIT_ACTUAL.json'])),flush=True);last=token
  outer=meta['OUTER_OWNER_WAIT_ACTUAL.json']
  if outer is not None and (meta['OWNER_EXIT_ACTUAL.json']is not None or outer['actual_wait_returncode']!=0):
   value['closed']=True;value['all9_execution_qualified']=all(x['qualified']is True for x in summary);value['skill_graduation_not_claimed']=True
   with ftp.open(root+'/OWNER_STDOUT_STDERR.log','r')as f:
    f.seek(0,2);length=f.tell();f.seek(max(0,length-24000));value['own_owner_log_tail_once']=f.read().decode('utf8',errors='replace')
   put('CLOSED_RESULT.json',value);(D/'NINE_ADMISSION2_CLOSED_RESULT_PATH.json').write_text(json.dumps(dict(path=str(out/'CLOSED_RESULT.json'),root=root),indent=2),encoding='utf8');print(json.dumps(dict(closed_result=str(out/'CLOSED_RESULT.json'),all9_execution_qualified=value['all9_execution_qualified'],owner_exit=meta['OWNER_EXIT_ACTUAL.json'],outer=outer,skill_not_claimed=True)),flush=True);closed=True;break
  time.sleep(15)
 if not closed:raise TimeoutError('Own metadata observer bound expired; no resource extension/foreign action')
finally:ftp.close();c.close()
