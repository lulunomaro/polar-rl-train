"""Observe own bound-probe JSON and ACTUAL external parent wait, not PID disappearance.
No selected models/raw/SDK/C/GPU/locks/signals. Closed own logs copied once.
"""
from pathlib import Path
import json,sys,time,shlex
R=Path(__file__).resolve().parent;guard=R/'BOUND_ONLY_E3_W35_V1_ADMISSION2_OBSERVER_STARTED_ONCE.json';assert not guard.exists();d=json.loads((R/'reports/BOUND_ONLY_E3_W35_V1_ADMISSION2_ACTUAL_PARENT_DISPATCH_V1.json').read_bytes());assert d['returncode']==0;m=d['receipt'];root=d['root'];folder=R/'reports'/('ACTUAL_BOUND_ONLY_E3_W35_V1_ADMISSION2_'+time.strftime('%Y%m%d_%H%M%S'));folder.mkdir();pointer=R/'BOUND_ONLY_E3_W35_V1_ADMISSION2_LATEST_METADATA_WATCH.json';guard.write_text(json.dumps(dict(root=root,folder=str(folder),epoch=time.time(),sole_bound_probe_metadata_observer=True),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();last=None;roots=('PARENT_STARTED.json','BOUNDED_ORIGINAL_RESOURCE_WAIT.json','ACTUAL_GROUP_ADMISSION.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','TERMINAL_ROWS.json','FINAL.json','GROUP_ABORT.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json','BOUND_PROBE_PARENT_CONTROLLER_STARTED_V1.json','BOUND_PROBE_PARENT_DISPATCH_RECEIPT_V1.json','BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json','BOUND_PROBE_PARENT_CONTROLLER_ERROR_V1.json','BOUND_PROBE_GROUP_CLOSED_SOURCE_GRADE_V1.json');cases=('WORKER_SCENE_READY.json','WORKER_EVAL_STARTED.json','PROGRESS.json','FINAL.json','WORKER_ERROR.json','A1_EVAL_PRIMARY_ERROR_V2.json','BOUND_PROBE_POLICY_IDENTITY_V1.json')
def get(rel):
 try:
  with s.open(root+'/'+rel,'rb')as f:raw=f.read()
 except FileNotFoundError:return None
 assert len(raw)<16*1024**2;return json.loads(raw)
def controller_alive():
 p=m['controller'];code="from pathlib import Path;import json;p=Path('/proc/%d/stat');t=p.read_text()if p.exists()else '';f=t[t.rfind(')')+2:].split()if t else [];print(json.dumps(dict(alive=bool(f)and f[0]not in('Z','X')and f[19]==%r)))"%(p['pid'],str(p['linux_start_ticks']));i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=30);i.close();text=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err;return json.loads(text)['alive']
try:
 until=time.monotonic()+7200
 while time.monotonic()<until:
  top={n:get(n)for n in roots};wait=top['BOUND_PROBE_PARENT_WAITED_ACTUAL_V1.json'];exit_value=top['PARENT_EXIT_SCOPE.json'];grade=top['BOUND_PROBE_GROUP_CLOSED_SOURCE_GRADE_V1.json'];admit=top['ACTUAL_GROUP_ADMISSION.json'];earlydead=not wait and not controller_alive();rows=[]
  for role in('E3','W35'):
   v={n:get('cases/'+role+'/'+n)for n in cases};err=v['WORKER_ERROR.json']or v['A1_EVAL_PRIMARY_ERROR_V2.json'];status='BOUND_PROBE_WORKER_ERROR'if err else('BOUND_PROBE_FINAL_AWAITING_ACTUAL_WAIT'if v['FINAL.json']else('ACTUAL_BOUND_PROBE_EVALUATING'if v['WORKER_EVAL_STARTED.json']else('BOUND_PROBE_SCENE_READY'if v['WORKER_SCENE_READY.json']else('BOUND_PROBE_SDK_CACHE_STARTUP'if admit else'NOT_ADMITTED'))));rows.append(dict(role=role,status=status,**{n[:-5]:x for n,x in v.items()}))
  wait_bound=bool(wait and wait['actual_parent_p_wait_returned']and wait['group_id']==d['group_id']and wait['parent']['pid']==m['parent']['pid']and wait['parent']['linux_start_ticks']==m['parent']['linux_start_ticks']and wait['parent_source_SHA']==m['parent_source_SHA']);python_pid_matches_launcher=bool(top['PARENT_STARTED.json']and top['PARENT_STARTED.json']['pid']==m['parent']['pid']);qualified=bool(wait_bound and wait['returncode']==0 and not wait['controller_errors']and python_pid_matches_launcher and grade and grade['passed_closed_bound_probe_source_grade']and exit_value and exit_value['all_own_children_waited']and exit_value['original_single_GPU_private_EX_released']and exit_value['original_global_finite_EX_released']and not exit_value['errors']);value=dict(kind='ACTUAL_EMBEDDED_TEACHER_BOUND_PROBE_METADATA_NOT_SKILL_GRADUATION',epoch=time.time(),root=root,group_id=d['group_id'],top=top,rows=rows,closed=bool(wait),early_controller_dead_without_wait_proof=earlydead,actual_external_parent_wait_bound=wait_bound,actual_Python_parent_PID_matches_launcher=python_pid_matches_launcher,qualified_bound_probe_execution=qualified if wait else None,matched_UID_pose_cohort=None,relative_improvement=None,observer_model_raw_SDK_GPU_C_operations=0);target=folder/'CURRENT_METADATA.json';tmp=folder/'CURRENT_METADATA.json.partial';tmp.write_text(json.dumps(value,indent=2),encoding='utf-8');tmp.replace(target);pointer.write_text(json.dumps(dict(root=root,folder=str(folder),current=str(target),closed=bool(wait),qualified_bound_probe_execution=value['qualified_bound_probe_execution']),indent=2),encoding='utf-8');signature=(bool(wait),bool(admit),earlydead,tuple((r['status'],(r['PROGRESS']or{}).get('control',0)//200)for r in rows))
  if signature!=last:print('ORIGINAL_TEACHER_BOUND_PROBE_STATUS '+json.dumps(dict(root=root,closed=bool(wait),waiting_original_resources=bool(top['BOUNDED_ORIGINAL_RESOURCE_WAIT.json'])and not admit and not wait,qualified_bound_probe_execution=value['qualified_bound_probe_execution'],early_controller_dead=earlydead,rows=[dict(role=r['role'],status=r['status'],controls=(r['FINAL']or{}).get('controls'))for r in rows])),flush=True);last=signature
  if wait or earlydead:
   names=['GROUP_PLAN.json','STAGE_COMPLETE_BOUND_ONLY_NATIVE_V1.json','BOUND_PROBE_PARENT_DISPATCH_REQUEST_V1.json']+list(roots)
   if wait:
    names+=['BOUND_PROBE_PARENT_FULL_STDOUT_STDERR.log','BOUND_PROBE_PARENT_CONTROLLER_STDOUT_STDERR.log']
    for role in('E3','W35'):
     try:children=s.listdir(root+'/cases/'+role)
     except FileNotFoundError:children=[]
     names+=['cases/'+role+'/'+n for n in children if'/'not in n and'\\'not in n and(n.endswith('.json')or n=='SDK_FULL_STDOUT_STDERR.log')]
   copied=[]
   for rel in dict.fromkeys(names):
    assert not Path(rel).is_absolute()and'..'not in Path(rel).parts
    try:
     with s.open(root+'/'+rel,'rb')as f:raw=f.read()
    except FileNotFoundError:continue
    assert len(raw)<32*1024**2;dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);copied.append(dict(relative=rel,bytes=len(raw)))
   value['copied_files']=copied;(folder/'CLOSED_RESULT.json').write_text(json.dumps(value,indent=2),encoding='utf-8');(R/'BOUND_ONLY_E3_W35_V1_ADMISSION2_LATEST_CLOSED_RESULT_PATH.json').write_text(json.dumps(dict(root=root,path=str(folder/'CLOSED_RESULT.json'),early_controller_dead_without_wait_proof=earlydead),indent=2),encoding='utf-8');print('ORIGINAL_TEACHER_BOUND_PROBE_CLOSED '+str(folder/'CLOSED_RESULT.json'),flush=True);break
  time.sleep(20)
 else:raise TimeoutError('Own reference metadata observation cap; native processes not signalled or replayed')
finally:s.close();c.close()
