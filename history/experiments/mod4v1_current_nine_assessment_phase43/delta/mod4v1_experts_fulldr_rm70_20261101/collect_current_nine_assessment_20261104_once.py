"""One own-parent metadata observer. No model/trajectory/SDK/C/lock/signal operations."""
from pathlib import Path
import hashlib,json,sys,time
T=Path(__file__).resolve().parent;A=T.parent/'mod4v1_current_nine_assessment_20261104';dispatch=json.loads((A/'reports/DISPATCH_ONCE.json').read_bytes());assert dispatch['returncode']==0;root=dispatch['root'];out=A/'reports/CLOSED_RESULT.json';mark=A/'COLLECTOR_STARTED_ONCE.json';assert not out.exists()and not mark.exists();H=lambda b:hashlib.sha256(b).hexdigest();started=time.time();cache={};original={};history=[]
with mark.open('x',encoding='utf8')as f:json.dump(dict(epoch=started,root=root,metadata_only=True,cap_seconds=4800,original_native_deadlines_not_extended=True),f,indent=2)
sys.path.insert(0,str(T));from project_connector import connect72
c=connect72();s=c.open_sftp()
def meta(rel,optional=True,cap=100*1024*1024):
 if rel in cache:return cache[rel]
 try:
  with s.open(root+'/'+rel,'rb')as f:b=f.read(cap+1)
 except FileNotFoundError:
  if optional:return None
  raise
 assert len(b)<=cap,rel;v=json.loads(b);cache[rel]=v;original[rel]=dict(bytes=len(b),SHA256=H(b),physical_reads=1,decodes=1);p=A/'published'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);return v
try:
 while time.time()-started<4800:
  try:
   with s.open(root+'/NINE_ASSESSMENT_PARENT_WAITED_ACTUAL.json','rb')as f:b=f.read(1024*1024)
   wait=json.loads(b);cache['NINE_ASSESSMENT_PARENT_WAITED_ACTUAL.json']=wait;original['NINE_ASSESSMENT_PARENT_WAITED_ACTUAL.json']=dict(bytes=len(b),SHA256=H(b),physical_reads=1,decodes=1);p=A/'published/NINE_ASSESSMENT_PARENT_WAITED_ACTUAL.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);break
  except FileNotFoundError:pass
  status={}
  for rel in('GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','PARENT_EXIT_SCOPE.json','GROUP_ABORT.json'):
   try:
    with s.open(root+'/'+rel,'rb')as f:status[rel]=json.loads(f.read(1024*1024))
   except FileNotFoundError:status[rel]=None
  q=status['GROUP_BARRIER_STATUS.json']or{};state=dict(ready=q.get('ready',[]),failed=q.get('failed',[]),common_start=(status['GROUP_EVAL_START.json']or{}).get('epoch'),parent_exited=bool(status['PARENT_EXIT_SCOPE.json']),abort=bool(status['GROUP_ABORT.json']))
  if not history or state!=history[-1]['state']:
   row=dict(epoch=time.time(),state=state);history.append(row);print('ASSESSMENT_PROGRESS '+json.dumps(row),flush=True);(A/'reports/PROGRESS.json').write_text(json.dumps(row,indent=2),encoding='utf8')
  time.sleep(15)
 else:raise TimeoutError('Observer ended; original finite parent owns cleanup, do not replay')
 plan=meta('GROUP_PLAN.json',False);end=meta('PARENT_EXIT_SCOPE.json',False);final=meta('FINAL.json');error=meta('PARENT_ORIGINAL_ERROR.json');start=meta('GROUP_EVAL_START.json');admission=meta('ACTUAL_GROUP_ADMISSION.json');meta('NINE_ASSESSMENT_OUTER_DISPATCH.json',False)
 assert wait['actual_parent_p_wait_returned']and wait['parent']==dispatch['dispatch']['parent']and wait['controller']==dispatch['dispatch']['controller'];assert end['all_own_children_waited']and end['original_single_GPU_private_EX_released']and end['original_global_finite_EX_released'];waits={x['role']:x for x in end['child_waits']};rows=[]
 for role in plan['roles']:
  name=role['role'];p='cases/'+name+'/';data=meta(p+'FINAL.json');err=meta(p+'WORKER_ERROR.json');pre=meta(p+'PRE_CLOSE.json');ready=meta(p+'WORKER_SCENE_READY.json');go=meta(p+'WORKER_EVAL_STARTED.json');task=meta(p+'task.json');w=waits.get(name);passed=bool(data and data.get('passed_execution')and not err and pre and w and w['returncode']==0 and w['actual_waited']and go)
  try:
   with s.open(root+'/'+p+'SDK_FULL_STDOUT_STDERR.log','rb')as f:
    f.seek(0,2);size=f.tell();f.seek(max(0,size-16384));tail=f.read().decode('utf8','replace')
   dest=A/'published'/p/'SDK_LOG_TAIL.txt';dest.write_text(tail,encoding='utf8')
  except FileNotFoundError:pass
  rows.append(dict(role=name,qualified_execution=passed,selected_model_SHA=role['source_SHA'],source_path=role['source_path'],wait=w,final=data,error=err,pre_close=pre,ready=bool(ready),started=bool(go),task=task))
 v=dict(kind='CURRENT_NINE_MOD4V1_ORIGINAL_SCOPE_FROZEN_ASSESSMENT_CLOSED_V1',root=root,group_id=plan['group_id'],GPU_UUID=plan['GPU_UUID'],seed=20260928,outer_actual_wait=wait,parent_exit=end,parent_error=error,parent_group_final=final,actual_group_admission=admission,common_start=start,rows=rows,qualified_execution_count=sum(x['qualified_execution']for x in rows),all_nine_qualified=len(rows)==9 and all(x['qualified_execution']for x in rows)and error is None and not end['errors']and wait['returncode']==0 and not wait['errors'],original_byte_identities=original,watch_history=history,model_or_raw_reads=0,SDK_C_lock_or_foreign_signal_operations=0,new_training_updates=0,whole_skill_graduation_not_implied_by_execution=True)
 with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
 print(json.dumps(dict(report=str(out),all_nine_qualified=v['all_nine_qualified'],rows=[dict(role=x['role'],qualified=x['qualified_execution'],controls=(x['final']or{}).get('controls'),error=x['error'])for x in rows]),indent=2),flush=True)
 raise SystemExit(0 if v['all_nine_qualified']else 1)
finally:s.close();c.close()
