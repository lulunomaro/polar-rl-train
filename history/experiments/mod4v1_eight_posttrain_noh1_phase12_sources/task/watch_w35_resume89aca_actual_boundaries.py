"""One 45s-cadence metadata watcher: firstactualPPO then originalsettled ownerexit. No model/ledger reads."""
from pathlib import Path
import json,time,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_resume89aca_adaptation_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];deadline=time.time()+4500;first_seen=False;c=connect72();s=c.open_sftp()
def get(rel):
 try:
  with s.open(job+'/'+rel,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None
try:
 while True:
  if not first_seen:
   first=get('production/FIRST_ACTUAL_NEW_PPO_UPDATE.json')
   if first is not None:
    report={'job':job,'observed_local':datetime.datetime.now().astimezone().isoformat(),'first_actual_PPO':first,'resources':get('ACTUAL_RESOURCE_LEASES.json'),'fullrestore':get('production/ACTUAL_W35_RM70_V3_FULLSTATE_BEFORE_NEW_CONTROL.json'),'native24':get('production/NATIVE24_W35_RM70_V3_ACTUAL.json'),'model_or_canonical_reads_by_watcher':0};p=R/'reports'/('W35_resume89aca_first_actual_update_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('FIRST_ACTUAL_UPDATE_REPORT',p,flush=True);print(json.dumps(first,ensure_ascii=False),flush=True);first_seen=True
  exit=get('OWNER_EXIT_ACTUAL.json')
  if exit is not None:
   result={'job':job,'observed_local':datetime.datetime.now().astimezone().isoformat(),'owner_exit':exit,'files':{},'model_reads':0,'canonical_reads':0}
   for name in('COHORT_FINAL.json','OWNER_ORIGINAL_ERROR.json','production/FINAL.json','production/ORIGINAL_W35_RM70_V3_ERROR.json','production/LATEST_PROGRESS.json','production/SOURCE208_V3_FINAL_READ_COUNTS.json'):
    item=get(name)
    if item is not None:result['files'][name]=item
   p=R/'reports'/('W35_resume89aca_exit_watch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');final=result['files'].get('production/FINAL.json',{});print('EXIT_REPORT',p,flush=True);print(json.dumps({'owner_exit':exit,'first_actual_seen':first_seen,'new_PPO_updates':final.get('actual_new_PPO_updates'),'new_transitions':final.get('new_environment_transitions'),'saved_model':final.get('final'),'error':result['files'].get('OWNER_ORIGINAL_ERROR.json')},ensure_ascii=False,indent=2),flush=True);break
  if time.time()>deadline:raise TimeoutError('Originalowner exitreceipt absent, noimplicitstop/reset/replay')
  time.sleep(45)
finally:s.close();c.close()
