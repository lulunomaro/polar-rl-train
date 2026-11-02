"""One bounded wait for actual new PPO update or owner/worker terminal error."""
from pathlib import Path
import json,time,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;dispatch=json.loads(sorted((R/'reports').glob('W35_adaptation_dispatch_*.json'))[-1].read_bytes());job=dispatch['new_job'];deadline=time.time()+1200;c=connect72();s=c.open_sftp()
try:
 while True:
  found={}
  for rel in ('production/FIRST_ACTUAL_NEW_PPO_UPDATE.json','production/LATEST_PROGRESS.json','production/NATIVE24_W35_RM70_V3_ACTUAL.json','production/ORIGINAL_W35_RM70_V3_ERROR.json','OWNER_ORIGINAL_ERROR.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json'):
   try:
    with s.open(job+'/'+rel,'rb')as f:found[rel]=json.loads(f.read())
   except FileNotFoundError:pass
  done=('production/FIRST_ACTUAL_NEW_PPO_UPDATE.json'in found or any(k in found for k in ('OWNER_ORIGINAL_ERROR.json','production/ORIGINAL_W35_RM70_V3_ERROR.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json')))
  if done or time.time()>=deadline:
   result={'job':job,'observed_local':datetime.datetime.now().astimezone().isoformat(),'records':found,'watch_timeout_not_task_failure':not done,'model_opens':0,'canonical_access':False};p=R/'reports'/('W35_actual_update_watch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(result,ensure_ascii=False,indent=2));break
  time.sleep(45)
finally:s.close();c.close()
