"""Wait on our one existing evaluator's metadata only; no duplicated work/model read."""
from pathlib import Path
import json,time,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_eval_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];deadline=time.time()+3900;c=None;s=None
try:
 c=connect72();s=c.open_sftp()
 while True:
  result=None
  for name in ('FINAL.json','PARENT_EXIT_SCOPE.json'):
   try:
    with s.open(job+'/'+name,'rb')as f:value=json.loads(f.read())
    if name=='FINAL.json':result={'terminal_file':name,'value':value}
    elif result is None:result={'terminal_file':name,'value':value}
   except FileNotFoundError:pass
  if result is not None:
   result.update(job=job,observed_local=datetime.datetime.now().astimezone().isoformat());p=R/'reports'/('W35_eval_terminal_watch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(result,ensure_ascii=False,indent=2));break
  if time.time()>deadline:raise TimeoutError('Metadata watch expired; does not stop or restart evaluator')
  time.sleep(45)
finally:
 if s is not None:s.close()
 if c is not None:c.close()
