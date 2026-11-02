"""Bounded own-diagnostic metadata wait, no model/raw/SDK/ledger access or retry."""
from pathlib import Path
import json,time,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_motion_trace_dispatch_*.json'))[-1].read_bytes());job=d['new_job'];endtime=time.time()+1500;c=connect72();s=c.open_sftp()
try:
 while True:
  try:
   with s.open(job+'/PARENT_EXIT_SCOPE.json','rb')as f:scope=json.loads(f.read())
  except FileNotFoundError:scope=None
  if scope is not None:
   v={'job':job,'parent_exit':scope,'files':{},'model_raw_or_canonical_opens':0}
   for rel in('FINAL.json','PARENT_ORIGINAL_ERROR.json','ACTUAL_TRACE_ADMISSION.json','WORKER_IDENTITY.json','ACTUAL_ORIGINAL_WAIT.json','actual_latest32/FULLRESTORE227_BEFORE_CONTROL.json','actual_latest32/NATIVE24_227_PART_OF_SAME_CASE.json','actual_latest32/MOTION_COMMAND_OBS_ACTION_ACTUAL_TRACE.json','actual_latest32/ORIGINAL227_EVAL_ERROR.json','actual_latest32/SOURCE227_FINAL_READ_COUNTS.json'):
    try:
     with s.open(job+'/'+rel,'rb')as f:v['files'][rel]=json.loads(f.read())
    except FileNotFoundError:pass
   p=R/'reports'/('W35_motion_trace_terminal_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps({'parent_exit':scope,'final':{k:x for k,x in v['files'].get('FINAL.json',{}).items()if k!='facts'},'errors':{k:x for k,x in v['files'].items()if 'ERROR'in k},'trace_present':'actual_latest32/MOTION_COMMAND_OBS_ACTION_ACTUAL_TRACE.json'in v['files']},ensure_ascii=False,indent=2));break
  if time.time()>endtime:raise TimeoutError('Metadata waitexpired; originaltraceparent notkilled/restarted')
  time.sleep(45)
finally:s.close();c.close()
