"""Collect only own new H1 case JSON/logs. Never PT/budget/GPU0/foreign case."""
from pathlib import Path
import argparse,datetime,hashlib,json,stat,sys
B=Path(__file__).resolve().parent;T=B.parent;sys.path.insert(0,str(T));from project_connector import connect72
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['fresh','n20k'],required=True);a=p.parse_args()
locator=B/('CURRENT_FRESH80_CASE.json' if a.mode=='fresh' else 'CURRENT_N20K_CASE.json');loc=json.loads(locator.read_text(encoding='utf-8'));root=loc['remote_root'];assert root.startswith('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_H1_')
stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');out=T/'reports'/('H1_'+a.mode+'_collect_'+stamp);out.mkdir(exist_ok=False);values={};files=[];client=sf=None
try:
 client=connect72();sf=client.open_sftp()
 def get(rel):
  try:
   with sf.open(root+'/'+rel,'rb') as f:raw=f.read()
  except FileNotFoundError:return
  except OSError as e:
   if getattr(e,'errno',None)==2:return
   raise
  dst=out/rel;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw);files.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
  if rel.endswith('.json'):
   try:values[rel]=json.loads(raw)
   except Exception as e:values[rel]=dict(reader_error=str(e))
 for n in ['PARENT_STARTED.json','CHILDREN.json','WAIT_RESOURCE.json','TERMINAL_ROWS.json','FINAL.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','SUPERVISOR_FULL_STDOUT_STDERR.log']:get(n)
 def walk(rel):
  try:entries=sf.listdir_attr(root+'/'+rel)
  except OSError:return
  for entry in entries:
   name=entry.filename
   if name in ('private','__pycache__'):continue
   child=rel+'/'+name
   if stat.S_ISDIR(entry.st_mode):walk(child)
   elif name.endswith(('.json','.log')) and entry.st_size<20*1024*1024:get(child)
 walk('gpu1')
 report=dict(remote_root=root,mode=a.mode,files=values,collected_file_index=files,source_PT_reads_by_collector=0,canonical_access=False,no_Ready_or_actualpass_inferred=True)
 (out/'COLLECTION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 final=values.get('FINAL.json',{});print(json.dumps(dict(local_collection=str(out/'COLLECTION.json'),remote_root=root,final=final if final else None,children=values.get('CHILDREN.json'),exit_scope=values.get('PARENT_EXIT_SCOPE.json'),wait=values.get('WAIT_RESOURCE.json'),errors={k:v for k,v in values.items() if 'ERROR' in k}),ensure_ascii=False,indent=2))
finally:
 if sf:sf.close()
 if client:client.close()
