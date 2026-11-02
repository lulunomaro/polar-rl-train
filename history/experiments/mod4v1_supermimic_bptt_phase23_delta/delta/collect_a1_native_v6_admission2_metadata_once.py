# NEW admission2 purpose: prior original1800 preGO timeout had zero physical GO; do not extend or replay it.
"""One NEW V6 metadata observer. No model/raw/SDK/canonical operation.
Only own published JSON during work; closed own stdout copied once after wait.
"""
from pathlib import Path
import json,sys,time,hashlib,datetime,shlex
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
m=json.loads((R/'A1_NATIVE_V6_ADMISSION2_ORIGINAL_OWNER_DISPATCH_ONCE.json').read_bytes());assert m.get('actual_Popen_calls')==1 and m.get('parent');root=m['root'];roles=['E3','W35','CURB_INDEPENDENT113','CURB_PROTECTED878','SLOPE135','SLOPE_INDEPENDENT50','E0','E2'];once=R/'A1_NATIVE_V6_ADMISSION2_OBSERVER_STARTED_ONCE.json';assert not once.exists();pointer=R/'A1_NATIVE_V6_ADMISSION2_LATEST_METADATA_WATCH.json';folder=R/'reports'/('ACTUAL_A1_NATIVE_V6_ADMISSION2_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'));folder.mkdir();once.write_text(json.dumps(dict(root=root,parent=m['parent'],folder=str(folder),seconds_cap=36000,poll_seconds=20,model_raw_SDK_C_operations=0),indent=2),encoding='utf-8');c=connect72();s=c.open_sftp();deadline=time.monotonic()+36000;began=time.monotonic();last=None;admission_seen=False;early_probe_done=False

def get(rel):
 assert '..'not in rel and not rel.startswith('/')
 try:
  with s.open(root+'/'+rel,'rb')as f:raw=f.read(4_000_001)
  assert len(raw)<=4_000_000,'Published small metadata unexpectedly oversized'
  return json.loads(raw)
 except FileNotFoundError:return None

def own_early_parent_alive():
 pid=int(m['parent']['pid']);ticks=str(m['parent']['linux_start_ticks']);code="from pathlib import Path;import json;p=Path('/proc/%d/stat');t=p.read_text()if p.exists()else '';a=t[t.rfind(')')+2:].split()if t else [];print(json.dumps(dict(own_parent_alive=bool(a)and a[0]!='Z'and a[19]==%r)))"%(pid,ticks);i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=30);i.close();text=o.read().decode();err=e.read().decode();assert o.channel.recv_exit_status()==0,err;return json.loads(text)['own_parent_alive']

try:
 while time.monotonic()<deadline:
  state=get('OWNER_CURRENT.json');closed=get('OWNER_EXIT_ACTUAL.json');started=get('OWNER_STARTED.json');perror=get('OWNER_ORIGINAL_ERROR.json');wait=get('PREGO_RESOURCE_WAIT.json');active={x['role']for x in(state or{}).get('workers',{}).values()};terminal=set((state or{}).get('terminal_roles',[]));selected=active|terminal;admission_seen=admission_seen or bool(selected);early_dead=False
  if closed:selected=set(roles)
  if not started and not closed and not early_probe_done and time.monotonic()-began>40:
   early_probe_done=True;early_dead=not own_early_parent_alive()
  rows=[]
  for role in roles:
   if role not in selected and not early_dead:rows.append(dict(role=role,status='PENDING_NOT_ADMITTED'));continue
   base='roles/'+role+'/production/';startup=get(base+'STARTUP_ACTUAL_NATIVE_SUPERMIMIC.json');progress=get(base+'PROGRESS.json');final=get(base+'FINAL.json');waited=get('roles/'+role+'/PARENT_WAITED_ACTUAL.json')if closed or role in terminal else None;go=get('roles/'+role+'/GO_PRODUCTION.json');errors={name:value for name in('WORKER_ERROR.json','WORKER_ERROR_FALLBACK_V2.json','WORKER_PRESTART_ERROR_V2.json')if(value:=get(base+name))is not None};counts=(final or progress or{}).get('counts');semantic=(waited or{}).get('semantic_result')or{}
   status='ERROR'if errors or(waited or{}).get('original_error')else'CLOSED_UNSTARTED'if closed and not go and not startup and not final else'CLOSED_SAVED_EXECUTION_NOT_SKILL_PASS'if closed and final and semantic.get('passed_execution')is True else'CLOSED_UNCONFIRMED_FINAL'if closed and final else'FINAL_PENDING_ACTUAL_PARENT_WAIT'if final else'ACTUAL_NATIVE_TRAINING'if startup else'CLOSED_WITHOUT_FINAL'if closed else'CONSTRUCTING'
   rows.append(dict(role=role,status=status,actual_GO=go,actual_BPTT_policy_steps=None if counts is None else counts.get('pi_bptt_optimizer_steps'),iteration=((final or{}).get('checkpoint')or{}).get('iteration',(progress or{}).get('iteration')),counts=counts,startup=startup,progress=progress,final=final,errors=errors,actual_parent_waited=waited,pose_cache_install=get(base+'POSE_CACHE_RUNTIME_ADAPTER_INSTALL_V3.json'),pose_cache_events=get(base+'POSE_CACHE_RUNTIME_ADAPTER_EVENTS_V3.json'),command_binding=get(base+'ORIGINAL_COMMAND_BINDING_V2.json')))
  livewait=bool(wait)and not admission_seen and not closed and not early_dead
  latest=dict(kind='ACTUAL_A1_NATIVE_V6_PUBLISHED_METADATA_NOT_SKILL_PASS',root=root,run_id=m['run_id'],epoch=time.time(),parent_current=state,parent_started=started,parent_exit=closed,parent_error=perror,historical_preGO_wait=wait,waiting_original_resources=livewait,actual_admission_seen=admission_seen,parent_dead_before_started=early_dead,rows=rows,model_raw_SDK_C_operations=0)
  temporary=folder/'CURRENT_METADATA.json.partial';target=folder/'CURRENT_METADATA.json';assert temporary.resolve().parent==target.resolve().parent==folder.resolve();temporary.write_text(json.dumps(latest,indent=2),encoding='utf-8');temporary.replace(target);pointer.write_text(json.dumps(dict(root=root,folder=str(folder),current=str(target),closed=bool(closed),early_parent_dead=early_dead),indent=2),encoding='utf-8')
  sig=(bool(closed),bool(perror),livewait,early_dead,tuple((r['role'],r['status'],None if r.get('actual_BPTT_policy_steps')is None else r['actual_BPTT_policy_steps']//250)for r in rows))
  if sig!=last:print('A1_V6_ACTUAL_STATUS '+json.dumps(dict(root=root,closed=bool(closed),waiting_original_resources=livewait,parent_error=bool(perror),rows=[{k:r.get(k)for k in('role','status','iteration','actual_BPTT_policy_steps')}for r in rows])),flush=True);last=sig
  if closed or early_dead:
   files=[];rels=['OWNER_PLAN.json','OWNER_STARTED.json','OWNER_CURRENT.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json','COHORT_FINAL.json','OWNER_A1_V6_STDOUT_STDERR.log']
   for role in roles:
    J='roles/'+role;rels +=[J+'/'+name for name in('GO_PRODUCTION.json','ROOT_ADMISSION_ACTUAL.json','WORKER_IDENTITY_ACTUAL.json','PARENT_WAITED_ACTUAL.json','SUPERMIMIC_FULL_STDOUT_STDERR.log')];rels +=[J+'/production/'+name for name in('APP_FAST_CLOSE_INTENT_V5.json','WORKER_LIFECYCLE_COMPLETE_V3.json','OWN_BPTT_FRESH_ZERO_V2.json','OWN_BPTT_FULL_RESET_RESUME_V2.json')]
    try:names=s.listdir(root+'/'+J+'/production')
    except FileNotFoundError:names=[]
    rels +=[J+'/production/'+name for name in names if name.endswith('.json')and(name.startswith('WORKER_SECONDARY')or name.startswith('APP_CLOSE_BINDING'))and '/'not in name and'\\'not in name]
   for rel in dict.fromkeys(rels):
    assert '..'not in rel and not rel.startswith('/')
    try:
     with s.open(root+'/'+rel,'rb')as f:raw=f.read()
    except FileNotFoundError:continue
    dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);files.append(dict(relative=rel,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
   latest['files']=files;(folder/'CLOSED_RESULT.json').write_text(json.dumps(latest,indent=2),encoding='utf-8');(R/'A1_NATIVE_V6_ADMISSION2_LATEST_CLOSED_RESULT_PATH.json').write_text(json.dumps(dict(root=root,path=str(folder/'CLOSED_RESULT.json'),early_parent_dead=early_dead),indent=2),encoding='utf-8');print('A1_V6_CLOSED_RESULT '+str(folder/'CLOSED_RESULT.json'),flush=True);break
  time.sleep(20)
 else:raise TimeoutError('Published metadata cap reached; native parent not signalled; new observer-only continuation required')
except BaseException:
 import traceback
 (folder/'OBSERVER_ERROR.json').write_text(json.dumps(dict(error=traceback.format_exc(),native_owner_not_signalled=True),indent=2),encoding='utf-8');raise
finally:s.close();c.close()
