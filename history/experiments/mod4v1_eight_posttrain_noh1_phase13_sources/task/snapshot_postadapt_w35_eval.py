"""Read only the newly trained89aca evaluator's scoped metadata/logtail; no model/ledger opens."""
from pathlib import Path
import json,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_postadapt_eval_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];v={'job':job,'observed_local':datetime.datetime.now().astimezone().isoformat(),'files':{},'model_reads':0,'canonical_reads':0};c=connect72();s=c.open_sftp()
try:
 for rel in ('PARENT_STARTED.json','WAIT_ORIGINAL_RESOURCES.json','PARENT_ORIGINAL_ERROR.json','ACTUAL_EVAL_ADMISSION.json','WORKER_IDENTITY.json','ACTUAL_ORIGINAL_WAIT.json','FINAL.json','PARENT_EXIT_SCOPE.json','actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json','actual_latest32/MOD4V1_FULLRESTORE_GUARD_ACTUAL.json','actual_latest32/ACTUAL227_CLOSED_RM70_SKILL_FACTS.json','actual_latest32/ORIGINAL227_CLOSED_RM70_ERROR.json','actual_latest32/SOURCE227_FINAL_READ_COUNTS.json'):
  try:
   size=s.stat(job+'/'+rel).st_size
   if size>3000000:v['files'][rel]={'size':size,'bounded_skip':True};continue
   with s.open(job+'/'+rel,'rb')as f:v['files'][rel]=json.loads(f.read())
  except FileNotFoundError:pass
 for rel in ('PARENT_STDOUT_STDERR.log','FULL_EVAL_STDOUT_STDERR.log'):
  try:
   size=s.stat(job+'/'+rel).st_size
   with s.open(job+'/'+rel,'rb')as f:f.seek(max(0,size-20000));text=f.read().decode('utf-8','replace')
   v['files'][rel]={'bytes':size,'tail_only':text}
  except FileNotFoundError:pass
finally:s.close();c.close()
p=R/'reports'/('W35_postadapt_eval_snapshot_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p)
for name,row in v['files'].items():
 if name.endswith('.log'):print('LOG_TAIL',name,row['tail_only'][-4000:])
 elif name=='FINAL.json':print(name,json.dumps({k:x for k,x in row.items()if k!='rows'},ensure_ascii=False))
 else:print(name,json.dumps(row,ensure_ascii=False))
