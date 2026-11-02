"""Single observer: published own frozen-eval JSON, then closed own logs once.
Never models/raw JSONL/SDK/GPU/C; no signal/resource mutations or work replay.
"""
from pathlib import Path
import sys,json,time,shlex
R=Path(__file__).resolve().parent;guard=R/'FROZEN_E3_W35_BATCH_V1_OBSERVER_STARTED_ONCE.json';assert not guard.exists();d=json.loads((R/'reports/FROZEN_E3_W35_BATCH_V1_ACTUAL_PARENT_DISPATCH_V1.json').read_bytes());assert d['returncode']==0;m=d['receipt'];root=d['root'];pid=m['parent']['pid'];ticks=str(m['parent']['linux_start_ticks']);folder=R/'reports'/('ACTUAL_FROZEN_E3_W35_BATCH_V1_'+time.strftime('%Y%m%d_%H%M%S'));folder.mkdir();pointer=R/'FROZEN_E3_W35_BATCH_V1_LATEST_METADATA_WATCH.json';guard.write_text(json.dumps(dict(root=root,folder=str(folder),epoch=time.time(),one_published_metadata_observer=True),indent=2),encoding='utf-8');sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();last=None
roots=('PARENT_STARTED.json','BOUNDED_ORIGINAL_RESOURCE_WAIT.json','ACTUAL_GROUP_ADMISSION.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','TERMINAL_ROWS.json','FINAL.json','GROUP_ABORT.json','PARENT_ORIGINAL_ERROR.json','PARENT_EXIT_SCOPE.json');case_names=('WORKER_SCENE_READY.json','WORKER_EVAL_STARTED.json','PROGRESS.json','FINAL.json','WORKER_ERROR.json','A1_EVAL_PRIMARY_ERROR_V2.json')
def get(rel):
 try:
  with s.open(root+'/'+rel,'rb')as f:raw=f.read()
 except FileNotFoundError:return None
 assert len(raw)<16*1024**2;return json.loads(raw)
def own_alive():
 code="from pathlib import Path;import json;p=Path('/proc/%d/stat');t=p.read_text()if p.exists()else '';f=t[t.rfind(')')+2:].split()if t else [];print(json.dumps(dict(alive=bool(f)and f[0]not in('Z','X')and f[19]==%r)))"%(pid,ticks);i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=30);i.close();text=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err;return json.loads(text)['alive']
try:
 until=time.monotonic()+7200
 while time.monotonic()<until:
  top={n:get(n)for n in roots};exit_value=top['PARENT_EXIT_SCOPE.json'];started=top['PARENT_STARTED.json'];admit=top['ACTUAL_GROUP_ADMISSION.json'];earlydead=not started and not own_alive();rows=[]
  for role in('E3','W35'):
   values={n:get('cases/'+role+'/'+n)for n in case_names};final=values['FINAL.json'];error=values['WORKER_ERROR.json']or values['A1_EVAL_PRIMARY_ERROR_V2.json']
   status='ACTUAL_FROZEN_WORKER_ERROR'if error else('FROZEN_FINAL_AWAITING_ACTUAL_PARENT_WAIT'if final else('ACTUAL_FROZEN_EVALUATING'if values['WORKER_EVAL_STARTED.json']else('SCENE_READY_WAITING_ORIGINAL_BARRIER'if values['WORKER_SCENE_READY.json']else('SDK_OR_CACHE_STARTUP'if admit else'NOT_ADMITTED'))))
   rows.append(dict(role=role,status=status,**{n[:-5]:v for n,v in values.items()}))
  value=dict(kind='OWN_ACTUAL_FROZEN_QUALITY_METADATA_NOT_GRADUATION',epoch=time.time(),root=root,group_id=d['group_id'],top=top,rows=rows,closed=bool(exit_value),early_parent_dead=earlydead,waiting_original_resources=bool(top['BOUNDED_ORIGINAL_RESOURCE_WAIT.json'])and not admit and not exit_value,model_raw_JSONL_SDK_GPU_C_operations=0)
  target=folder/'CURRENT_METADATA.json';temp=folder/'CURRENT_METADATA.json.partial';assert target.parent==temp.parent==folder;temp.write_text(json.dumps(value,indent=2),encoding='utf-8');temp.replace(target);pointer.write_text(json.dumps(dict(root=root,folder=str(folder),current=str(target),closed=bool(exit_value),early_parent_dead=earlydead),indent=2),encoding='utf-8');signature=(bool(exit_value),bool(admit),earlydead,tuple((r['status'],(r['PROGRESS']or{}).get('control',0)//200)for r in rows))
  if signature!=last:print('FROZEN_QUALITY_ACTUAL_STATUS '+json.dumps(dict(root=root,closed=bool(exit_value),waiting_original_resources=value['waiting_original_resources'],early_parent_dead=earlydead,parent_error=bool(top['PARENT_ORIGINAL_ERROR.json']),rows=[dict(role=r['role'],status=r['status'],controls=(r['FINAL']or{}).get('controls'))for r in rows])),flush=True);last=signature
  if exit_value or earlydead:
   if exit_value:assert exit_value['all_own_children_waited']is True
   names=['GROUP_PLAN.json','STAGE_COMPLETE_MICROBATCH_V1.json','PARENT_FROZEN_MICROBATCH_DISPATCH_RECEIPT.json','PARENT_FROZEN_MICROBATCH_STDOUT_STDERR.log']+list(roots)
   if exit_value:
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
   value['copied_files']=copied;(folder/'CLOSED_RESULT.json').write_text(json.dumps(value,indent=2),encoding='utf-8');(R/'FROZEN_E3_W35_BATCH_V1_LATEST_CLOSED_RESULT_PATH.json').write_text(json.dumps(dict(root=root,path=str(folder/'CLOSED_RESULT.json'),early_parent_dead=earlydead),indent=2),encoding='utf-8');print('FROZEN_QUALITY_CLOSED_RESULT '+str(folder/'CLOSED_RESULT.json'),flush=True);break
  time.sleep(20)
 else:raise TimeoutError('Own metadata observation cap, native evaluation not signalled or replayed')
finally:s.close();c.close()
