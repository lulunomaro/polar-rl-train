"""Wait on original finite owner's fully settled/waited boundary, not just a PT save."""
from pathlib import Path
import json,time,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_adaptation_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];deadline=time.time()+4500;c=connect72();s=c.open_sftp()
try:
 while True:
  try:
   with s.open(job+'/OWNER_EXIT_ACTUAL.json','rb')as f:exit=json.loads(f.read())
  except FileNotFoundError:exit=None
  if exit is not None:
   result={'job':job,'observed_local':datetime.datetime.now().astimezone().isoformat(),'owner_exit':exit,'files':{},'model_reads':0,'canonical_reads':0}
   for name in ('COHORT_FINAL.json','OWNER_ORIGINAL_ERROR.json','production/FINAL.json','production/ORIGINAL_W35_RM70_V3_ERROR.json','production/LATEST_PROGRESS.json','production/SOURCE208_V3_FINAL_READ_COUNTS.json'):
    try:
     with s.open(job+'/'+name,'rb')as f:result['files'][name]=json.loads(f.read())
    except FileNotFoundError:pass
   p=R/'reports'/('W35_adaptation_exit_watch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(result,ensure_ascii=False,indent=2));break
  if time.time()>deadline:raise TimeoutError('Original owner still has no exit receipt; watch does not kill/clear/restart it')
  time.sleep(45)
finally:s.close();c.close()
