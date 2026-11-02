"""Finite dependency chain only: existing one saved-model evaluator→closed scope→one ownnewrawCPU.
No newPPO/GO, models, oldraw, ledger orautomaticretry. Waitforlocaldispatchresult toavoidduplicatewatch.
"""
from pathlib import Path
import json,time,datetime,hashlib,runpy,traceback
from project_connector import connect72
R=Path(__file__).resolve().parent;source=R/'reports/W35_AUTO_AFTER_RESUME_FULL32_BOUNDARY_RESULT_V1.json';out=R/'reports/W35_AFTER_RESUME_EVAL_AND_OWN_CPU_ONCE_RESULT_V1.json';assert not out.exists();deadline=time.time()+7200;cpu=R/'run_after_resume89aca_own_telemetry_CPU_ROOT_v1_once.py';cpuSHA=hashlib.sha256(cpu.read_bytes()).hexdigest();report={'kind':'ORIGINAL_ONE_POSTRESUME_EVAL_THEN_ONE_OWN_RAW_CPU_FINITE_CHAIN','oldmodel_raw_or_canonical_access':False,'new_PPO_windows':0,'planned_CPU_rootrunner_SHA':cpuSHA}
while not source.exists():
 if time.time()>deadline:raise TimeoutError('Existingownedone-evaldispatchboundaryresultabsent; noimplicitcasecreation')
 time.sleep(45)
d=json.loads(source.read_bytes())
if d['status']!='ONE_NEW_FULL32_PARENT_DISPATCHED_NOT_PASS_CLAIM':
 report.update(status='NO_NEW_EVAL_TO_READ_NO_RAW_OPEN',upstream_status=d['status']);out.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2));raise SystemExit(0)
job=d['new_eval_job'];report['job']=job;c=connect72();s=c.open_sftp();enddeadline=time.time()+4500
def get(rel):
 try:
  with s.open(job+'/'+rel,'rb')as f:return json.loads(f.read())
 except FileNotFoundError:return None
try:
 while True:
  scope=get('PARENT_EXIT_SCOPE.json')
  if scope is not None:break
  if time.time()>enddeadline:raise TimeoutError('Originalboundedfull32evaluatorhasnotclosed; collectorcreatesnoothercase')
  time.sleep(45)
 final=get('FINAL.json');v={'job':job,'parent_exit':scope,'FINAL':final,'files':{},'collector_model_or_canonical_access':False}
 for rel in('TASK.json','TASK_PENDING.json','PARENT_ORIGINAL_ERROR.json','PARENT_RESOURCE_SCOPE_ERROR.json','WAIT_RESOURCE.json','actual_latest32/ORIGINAL227_EVAL_ERROR.json','actual_latest32/SOURCE_FINAL_READ_COUNTS.json','actual_latest32/SOURCE208_V3_FINAL_READ_COUNTS.json','actual_latest32/APP_CLOSED.json','actual_latest32/ENV_CLOSE_RETURNED.json'):
  row=get(rel)
  if row is not None:v['files'][rel]=row
 terminal=R/'reports'/('W35_after_resume89aca_eval_terminal_watch_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');terminal.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');report['terminal_report']=str(terminal)
finally:s.close();c.close()
okay=bool(scope['all_own_children_waited']and scope['owned_private_validation_locks_released']and scope['error']is None and final and final['passed_execution']and final['bounded32s_complete']and final['returncode']==0 and final['optimizer_updates']==0)
if not okay:
 report.update(status='ORIGINAL_EVAL_NOT_COMPLETE_SUCCESS_NO_RAW_PURPOSE_CONSUMED',original_scope=scope);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0)
assert hashlib.sha256(cpu.read_bytes()).hexdigest()==cpuSHA
try:
 runpy.run_path(str(cpu),run_name='__main__');p=sorted((R/'reports').glob('W35_after_resume89aca_own_raw_CPU_*.json'))[-1];result=json.loads(p.read_bytes());assert result['job']==job;report.update(status='ACTUAL_NEW_OWN_RAW_CPU_COMPLETE'if result['status']=='ACTUAL_OWN_BYTES_SHA_ROWS_VERIFIED'else'OWN_RAW_CPU_FAILED_NO_AUTORETRY',CPU_report=str(p),CPU_status=result['status'])
except BaseException:
 report.update(status='OWN_RAW_CPU_ONCE_FAILED_PRESERVED_NO_AUTORETRY',error=traceback.format_exc());out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');raise
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('FULL32_THEN_OWN_CPU_RESULT',out);print(json.dumps(report,ensure_ascii=False,indent=2))
