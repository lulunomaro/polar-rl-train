"""Read only this new evaluator's receipts/log tail; no model or raw-trajectory reads."""
from pathlib import Path
import json,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_eval_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];result={'captured_local':datetime.datetime.now().astimezone().isoformat(),'job':job,'files':{}}
c=connect72();s=c.open_sftp()
try:
 for rel in ('PARENT_STARTED.json','ACTUAL_EVAL_ADMISSION.json','WORKER_IDENTITY.json','ACTUAL_ORIGINAL_WAIT.json','FINAL.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','actual_latest32/MOD4V1_FULLRESTORE_GUARD_ACTUAL.json','actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json','actual_latest32/NATIVE24_227_PART_OF_SAME_CASE.json','actual_latest32/ACTUAL227_CLOSED_RM70_SKILL_FACTS.json','actual_latest32/SOURCE227_FINAL_READ_COUNTS.json','actual_latest32/ORIGINAL227_EVAL_ERROR.json','actual_latest32/PARTIAL227_SKILL_FACTS_ON_ERROR.json','actual_latest32/PARTIAL227_OBSERVER_ERROR.json','actual_latest32/APP227_CLOSING.json','actual_latest32/ENV227_CLOSE_RETURNED.json'):
  try:
   st=s.stat(job+'/'+rel)
   if st.st_size>5000000:result['files'][rel]={'bytes':st.st_size,'not_read_large_receipt':True};continue
   with s.open(job+'/'+rel,'rb')as f:result['files'][rel]=json.loads(f.read())
  except FileNotFoundError:pass
 for rel in ('FULL_EVAL_STDOUT_STDERR.log','PARENT_STDOUT_STDERR.log'):
  try:
   st=s.stat(job+'/'+rel)
   with s.open(job+'/'+rel,'rb')as f:f.seek(max(0,st.st_size-32000));text=f.read().decode('utf-8','replace')
   result['files'][rel]={'bytes_at_snapshot':st.st_size,'tail_only':text}
  except FileNotFoundError:pass
 for cmd in ('nvidia-smi --query-gpu=index,uuid,memory.used,utilization.gpu --format=csv,noheader,nounits','nvidia-smi --query-compute-apps=pid,gpu_uuid,used_memory --format=csv,noheader,nounits'):
  i,o,e=c.exec_command(cmd,timeout=30);i.close();result.setdefault('gpu_now',[]).append({'stdout':o.read().decode(),'stderr':e.read().decode(),'exit':o.channel.recv_exit_status()})
finally:s.close();c.close()
p=R/'reports'/('W35_eval_snapshot_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p)
summary={k:v for k,v in result['files'].items() if not k.endswith('.log')};print(json.dumps({'status_files':summary,'gpu_now':result.get('gpu_now')},ensure_ascii=False,indent=2))
for k,v in result['files'].items():
 if k.endswith('.log'):print('LOG_TAIL',k,v['tail_only'][-4500:])
