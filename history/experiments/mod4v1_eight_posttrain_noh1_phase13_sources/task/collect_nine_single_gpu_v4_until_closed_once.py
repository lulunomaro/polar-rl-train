"""BoundedoneV2grouppublisherwatch+closedJSON/fullstdoutcopy. No models/evalraw/NPZ/SDK/driver/budget."""
from pathlib import Path
import json,time,datetime,hashlib
from project_connector import connect72
R=Path(__file__).resolve().parent;once=R/'NINE_GROUP_V4_COLLECTOR_CONSUMED.json';assert not once.exists();d=json.loads((R/'NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V4.json').read_bytes());root=d['root'];once.write_text(json.dumps({'root':root,'kind':'ONE_OWNGROUP_METADATA_TERMINAL_COLLECTOR_NO_RAW'},indent=2),encoding='utf-8');out=R/'reports'/('NINE_SINGLE_GPU_V4_CLOSED_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));out.mkdir();c=connect72();s=c.open_sftp();started=time.time();last=None;closed=None

def readsmall(rel,optional=True):
 try:
  with s.open(root+'/'+rel,'rb')as f:raw=f.read()
 except FileNotFoundError:
  if optional:return None
  raise
 assert len(raw)<100*1024**2;return json.loads(raw)
try:
 plan=readsmall('GROUP_PLAN.json',False);history=[]
 while time.time()-started<4500:
  closed=readsmall('PARENT_EXIT_SCOPE.json');status=readsmall('GROUP_BARRIER_STATUS.json')or{};st=readsmall('GROUP_EVAL_START.json');key=(tuple(status.get('ready',[])),tuple(status.get('failed',[])),bool(st),bool(closed))
  if key!=last:
   row={'epoch':time.time(),'ready':status.get('ready',[]),'failed':status.get('failed',[]),'actual_eval_start':st,'closed':bool(closed)};history.append(row);print('GROUP_STATUS',json.dumps(row),flush=True);last=key
  if closed:break
  time.sleep(15)
 assert closed is not None,'V2boundedwatchexpired; owngroupleftfororiginalsupervisorboundedclose'
 names=['GROUP_PLAN.json','PARENT_STARTED.json','ACTUAL_GROUP_ADMISSION.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','PARENT_ORIGINAL_ERROR.json','GROUP_ABORT.json','PARENT_EXIT_SCOPE.json','GROUP_GPU_MEMORY_SAMPLES.json','FINAL.json'];files=[];payload={}
 for rel in names:
  value=readsmall(rel)
  if value is None:continue
  p=out/rel;p.write_text(json.dumps(value,indent=2),encoding='utf-8');payload[rel]=value;files.append({'relative':rel,'local_copy':str(p),'kind':'published_JSON'})
 rows=[]
 for role in plan['roles']:
  name=role['role'];v={}
  for n in('task.json','WORKER_SCENE_READY.json','WORKER_EVAL_STARTED.json','FINAL.json','PRE_CLOSE.json','WORKER_ERROR.json'):
   value=readsmall('cases/'+name+'/'+n)
   if value is None:continue
   p=out/name/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2),encoding='utf-8');v[n]=value
  rel='cases/'+name+'/SDK_FULL_STDOUT_STDERR.log'
  try:
   with s.open(root+'/'+rel,'rb')as f:raw=f.read()
   p=out/name/'SDK_FULL_STDOUT_STDERR.log';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);v['stdout_metadata']={'remote_path':root+'/'+rel,'local_path':str(p),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest(),'fullclosed_read_count':1}
  except FileNotFoundError:pass
  waits={r['role']:r for r in closed['child_waits']};final=v.get('FINAL.json');error=v.get('WORKER_ERROR.json');wait=waits.get(name);passed=bool(final and final.get('passed_execution')and error is None and wait and wait['returncode']==0 and v.get('PRE_CLOSE.json'));row={'role':name,'passed_execution':passed,'wait':wait,'ready':bool(v.get('WORKER_SCENE_READY.json')),'actual_started':bool(v.get('WORKER_EVAL_STARTED.json')),'final':final,'error':error,'stdout':v.get('stdout_metadata')};rows.append(row)
 report={'kind':'ACTUAL_ONE_GPU_V4_NINE_N80_FRESH_FULLDR_CLOSED_RESULTS','root':root,'GPU_UUID':plan['GPU_UUID'],'group_id':plan['group_id'],'all_own_children_waited':closed['all_own_children_waited'],'single_GPU_EX_released':closed['original_single_GPU_private_EX_released'],'global_finite_EX_released':closed['original_global_finite_EX_released'],'parent_errors':closed['errors'],'common_barrier':payload.get('GROUP_EVAL_START.json'),'actual_execution_passed_count':sum(r['passed_execution']for r in rows),'rows':rows,'source20k_DR_sliced':False,'freshN80_not_saved20k_resume':True,'raw_or_NPZ_or_PT_reader_opens':0,'SDK_or_canonical_access':False,'new_PPO_BPTT':False,'published_watch_history':history,'local_result_directory':str(out)};(out/'CLOSED_RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(R/'reports/NINE_SINGLE_GPU_V4_LATEST_CLOSED_RESULT_PATH.json').write_text(json.dumps({'path':str(out/'CLOSED_RESULT.json'),'root':root},indent=2),encoding='utf-8');print('RESULT',out/'CLOSED_RESULT.json',flush=True);print(json.dumps({k:v for k,v in report.items()if k not in('rows','published_watch_history')},indent=2),flush=True);print('ROLE_EXECUTIONS',json.dumps([{'role':r['role'],'passed':r['passed_execution'],'error':r['error'],'controls':(r['final']or{}).get('controls')}for r in rows]),flush=True)
finally:s.close();c.close()
