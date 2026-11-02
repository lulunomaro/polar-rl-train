"""Wait for the independent new89aca source's own completed/closed scope, no busy host polling."""
from pathlib import Path
import json,time,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_postadapt_eval_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];deadline=time.time()+4500;c=connect72();s=c.open_sftp()
try:
 while True:
  try:
   with s.open(job+'/PARENT_EXIT_SCOPE.json','rb')as f:exit=json.loads(f.read())
  except FileNotFoundError:exit=None
  if exit is not None:
   record={'job':job,'observed_local':datetime.datetime.now().astimezone().isoformat(),'parent_exit':exit,'files':{},'model_reads_by_watcher':0,'canonical_reads_by_watcher':0}
   for rel in ('FINAL.json','PARENT_ORIGINAL_ERROR.json','ACTUAL_ORIGINAL_WAIT.json','actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json','actual_latest32/ACTUAL227_CLOSED_RM70_SKILL_FACTS.json','actual_latest32/SOURCE227_FINAL_READ_COUNTS.json','actual_latest32/ORIGINAL227_CLOSED_RM70_ERROR.json'):
    try:
     with s.open(job+'/'+rel,'rb')as f:record['files'][rel]=json.loads(f.read())
    except FileNotFoundError:pass
   p=R/'reports'/('W35_postadapt_terminal_watch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p)
   facts=record['files'].get('actual_latest32/ACTUAL227_CLOSED_RM70_SKILL_FACTS.json',{});brief={'parent_exit':exit,'source_SHA':facts.get('source_SHA'),'controls':facts.get('controls'),'bounded_window_complete':facts.get('bounded_window_complete'),'passed_execution':facts.get('passed_execution'),'facts':facts.get('facts'),'errors':{k:v for k,v in record['files'].items()if'ERROR'in k}}
   print(json.dumps(brief,ensure_ascii=False,indent=2));break
  if time.time()>deadline:raise TimeoutError('Newmodel evalwatch expired, evaluator not killed or restarted')
  time.sleep(45)
finally:s.close();c.close()
