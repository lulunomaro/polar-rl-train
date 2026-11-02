"""Own canonical case JSON/log collector only; no selectedPT/GPU/foreignscope reads."""
from pathlib import Path
import argparse,datetime,hashlib,json,stat,sys
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
p=argparse.ArgumentParser();p.add_argument('--locator',type=Path,required=True);a=p.parse_args();loc=json.loads(a.locator.read_bytes());root=loc['remote_root'];name=loc.get('canonical','SLOPE135');assert root.startswith('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E1_')
out=T/'reports'/(name+'_actual_case_collect_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));out.mkdir(exist_ok=False);values={};files=[];done=set();client=sf=None
try:
 client=connect72();sf=client.open_sftp()
 def get(rel):
  if rel in done:return
  try:
   with sf.open(root+'/'+rel,'rb') as f:raw=f.read()
  except OSError as e:
   if getattr(e,'errno',None)==2:return
   raise
  done.add(rel);dst=out/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);files.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
  if rel.endswith('.json'):
   try:values[rel]=json.loads(raw)
   except Exception as e:values[rel]=dict(reader_error=str(e))
 for n in ['PARENT_STARTED.json','CHILDREN.json','SDK_DISPATCH_ONCE.json','RESOURCE_WAIT_CHECKS.json','WAIT_RESOURCE_TIMEOUT.json','TERMINAL_ROWS.json','FINAL.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','SUPERVISOR_FULL_STDOUT_STDERR.log','OWN_METADATA_WAIT_CANCELLED_FOR_NEW_GPU0_PERMISSION.json']:get(n)
 def walk(rel):
  try:entries=sf.listdir_attr(root+'/'+rel)
  except OSError as e:
   if getattr(e,'errno',None)==2:return
   raise
  for entry in entries:
   n=entry.filename
   if n in ('private','__pycache__'):continue
   sub=rel+'/'+n
   if stat.S_ISDIR(entry.st_mode):walk(sub)
   elif n.endswith(('.json','.log')):get(sub)
 walk('gpu1')  # Historicaldirectory label only; actualGPUidentity is explicitTask/ResourceUUID.
 result=dict(kind='OWN_E1_ACTUAL_RAW_JSON_LOG_COLLECTION_NOT_EXTRA_MODEL_READ',remote_root=root,canonical=name,files=values,collected_file_index=files,selected_source_PT_reads=0,canonical_access=False)
 path=out/'COLLECTION.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');final=values.get('FINAL.json');closed=values.get('PARENT_EXIT_SCOPE.json');row=(final or {}).get('rows',[{}])[0];data=row.get('actual_complete') or {}
 print(json.dumps(dict(collection=str(path),root=root,canonical=name,final_status=(final or {}).get('status'),passed=(final or {}).get('passed'),child=values.get('CHILDREN.json'),returncode=row.get('returncode'),actual_waited=row.get('actual_waited'),actual_complete_summary={k:data[k] for k in ['canonical','passed','num_envs','controls','physics_callbacks','feedback_samples','source_SHA','one_original_fresh_reset','one_explicit_fresh_reset','forbidden_calls','sentinels'] if k in data},exit_scope=closed,wait_checks=len(values.get('RESOURCE_WAIT_CHECKS.json',[])),errors={k:v for k,v in values.items() if 'ERROR' in k}),ensure_ascii=False,indent=2))
 with (B/(name+'_LATEST_COLLECTION_LOCATOR.json')).open('w',encoding='utf-8') as f:json.dump(dict(collection=str(path),remote_root=root),f,indent=2)
finally:
 if sf:sf.close()
 if client:client.close()
