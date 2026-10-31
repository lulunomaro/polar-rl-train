"""Sole72 original finite authority; one human-selected actual forward210 role.
Source/native0PT admission already returned. This is the only new GO/FIRST entry.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,secrets,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
J='/mnt/mod4_linux_durable_20261013/MOD4_E0_82_LITERAL_FUDAN_JUMP_PLANE40050_20261031v195/seed27'
OWNER='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ONE195_E0_START_FUDAN_JUMP40050_2610v195/owner'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
AUTH="""from pathlib import Path
import json,time,hashlib
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');b=p.read_bytes();c=json.loads(b)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['active_segment'] is None and c['new_authority_budget_extensions']==[] and c['authorized_training_seconds']==2268000
assert c['remaining_training_seconds']>86412.86069250107+3900
print(json.dumps(dict(epoch=time.time(),CNone=True,remaining_snapshot=c['remaining_training_seconds'],SHA=hashlib.sha256(b).hexdigest(),no_account_write=True)))"""
SPAWN="""from pathlib import Path
import importlib.util,sys,os,json,psutil
B=Path(v['root']);sys.path.insert(0,str(B));p=B/v['module']
s=importlib.util.spec_from_file_location('owned195_launch',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert not (B/v['console']).exists()
pid=os.fork()
if pid:
 q=psutil.Process(pid);print(json.dumps(dict(pid=pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd(),root=str(B),role=v['role'])),flush=True)
else:
 os.setsid();fd=os.open(str(B/v['console']),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd)
 if v['role']=='owner':m.owner(v['config'])
 else:m.node(v['config'])
"""
FIRST="""from pathlib import Path
import json,time,hashlib
B=Path(v['job']);C=B/'control';first=B/'production/FIRST_ACTUAL_NEW_PPO_UPDATE.json';end=time.time()+850
while time.time()<end and not first.is_file() and not (C/'NODE_TERMINAL_ACTUAL.json').is_file():time.sleep(2)
paths=[C/'NODE_IDENTITY.json',C/'WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json',C/'ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json',C/'NODE_ORIGINAL_ERROR.json',C/'NODE_TERMINAL_ACTUAL.json',C/'NODE_EXIT_ACTUAL.json',B/'GO_PRODUCTION.json',B/'production/ACTUAL_SOURCE195_LITERAL_REWARD_AND_TARGET_PLANT_BEFORE_ACTION.json',B/'production/ACTUAL195_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json',first,B/'production/latest_complete.json',B/'production/LATEST_PROGRESS.json',B/'production/ORIGINAL_ERROR.json',B/'production/FAILED_PREFIX_SAVE_ORIGINAL_ERROR.json',B/'production/FINAL.json']
rows=[]
for p in paths:
 if not p.is_file():continue
 raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
f=json.loads(first.read_bytes()) if first.is_file() else None
log=C/'production_WORKER.log';prefix=None
if log.is_file():
 size=log.stat().st_size
 with log.open('rb') as stream:raw=stream.read(size)
 prefix=dict(path=str(log),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace'),scope='Actual stdout prefix at FIRST collection; writer may remain open, not final full log')
print(json.dumps(dict(epoch=time.time(),passed=bool(f and f.get('passed') and f.get('actual_new_PPO_updates')==1),first=f,full_selected_UTF8=rows,original_stdout_prefix=prefix,first_wait_seconds=850,no_second_watcher=True,still_running_is_snapshot_only=True)))"""
def main():
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'start195_literal_JUMP_plane_single4090_FIRST_once|install195_literal_jump_plane_admission|collect188_|start188_|install_capture193_|install_evaluate191_|capture195_target_|install_evaluate187_totalplan|admit_delivered185|capture_delivered185|inspect_user_delivered_forward|find_existing_forwarded210_jump|install_and_probe_A_original_fudan|collect_E3_source210|run_ONE178_selected|collect_ONE178_original' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 cim=dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,exact_CIM=rows,other_known_control_finites=other)
 put('ROOT195_FIRSTV2_FRESH_LOCAL_EXACT_CIM.json',cim)
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other and time.time()-cim['epoch']<30
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 actual=json.loads((R/'ROOT195ADMITV2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json').read_bytes())
 assert actual['passed_execution'] and actual['CPU_returncode']==0 and actual['returncode']==0 and not actual['worker_errors'] and actual['private_EX_released']
 assert actual['result']['controls']==8 and actual['result']['physics_callbacks']==64 and actual['result']['num_envs']==64
 task=json.loads((N/'train_package/TASK195.json').read_bytes());manifest=json.loads((N/'TRAIN195_COMPLETE_MANIFEST.json').read_bytes());mh=H(N/'TRAIN195_COMPLETE_MANIFEST.json')
 source_cpu=json.loads((T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json').read_bytes())
 e0_task_cpu=json.loads((R/'ROOT195_E0_START_LITERAL_REWARD_SOURCE_AND_TaskGO_CPU_ACTUAL.json').read_bytes())
 assert e0_task_cpu['passed'] and e0_task_cpu['negative_count']==18
 assert source_cpu['passed'] and source_cpu['literal19_text_identity'] and H(T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/ROOT194_NEW_LITERAL_JUMP50_SOURCE_CPU_ACTUAL.json')==task['reward_source_CPU_report_SHA']
 cpu185=T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027/reports/E0_89D_FORMAL_FINAL_WHOLE_INITIAL_CPU_REVIEW_ACTUAL_V2.json'
 witness=json.loads(cpu185.read_bytes());assert witness['passed'] and witness['review']['all_whole_model_tensors_finite'] and witness['model']['SHA']==task['source_SHA'] and witness['review']['Adam_step']==641200
 admission=dict(passed=True,kind='JUMP195_LITERAL_400N50_ACTUAL_CPU_NATIVE8_AND_DELIVERY31984_FULLSTATE_REUSE',source_SHA=task['source_SHA'],source_iteration=31984,Adam_step=641200,
  all_actor_critic_optimizer_tensors_finite=True,actual_35_38_6_shapes=True,manifest_SHA=mh,literal_reward_text_identity19=True,
  target_CPU_actual_waited_RC=0,target_GPU0PT_actual_waited_RC=0,actual_native_controls=8,actual_physics_callbacks=64,target64_private_EX_released=True,
  original_target_source_admission_report_SHA=H(R/'ROOT195ADMITV2_ORIGINAL_TARGET_FROZEN_EVAL_RETURNED_ACTUAL.json'),delivery_fullstate_CPU_report_SHA=H(cpu185),
  originalJUMP195_source_CPU_SHA=task['reward_source_CPU_report_SHA'],target_fullstate_CUDA_restore_required_before_new_control=True,no_previous_saved_DR_falsely_inherited=True)
 put('ROOT195_FIRSTV2_ACTUAL_ADMISSION_BINDING.json',admission)
 put('ROOT195_FIRSTV2_ONCE_CONSUMED_BEFORE_ANY_GO.json',dict(epoch=time.time(),source_SHA=task['source_SHA'],source_iteration=31984,only_role='h1_210',max_parent_seconds=3900,save_seconds=3600,exit_seconds=300,
  human='User selected E0 flat expert for a new original finite jump window after194 closes; retain full E0 actor/critic/STD/17Adam and400N50DR, original JUMP reward unchanged.',no_plain186_or_comparison=True,first_collector_calls=1,source_manifest_SHA=mh))
 wrapper=module('root195_first_session',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 transport=None;previous=None;client=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('root195_memory_authority',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret)
  try:put('ROOT195_FIRSTV2_FRESH72_CNONE_RESERVE_READONLY.json',d.code(client,d.PY72,AUTH,{},timeout=45))
  finally:client.close();client=None
  client=route.connect()
  pre="""from pathlib import Path
import json,subprocess,hashlib
B=Path(v['job']);assert B==Path('/mnt/mod4_linux_durable_20261013/MOD4_E0_82_LITERAL_FUDAN_JUMP_PLANE40050_20261031v195/seed27')
m=json.loads(subprocess.check_output(['findmnt','--json','--target',str(B),'-o','UUID,OPTIONS'],text=True))['filesystems'][0];assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',')
f=json.loads((B/'admission64/FUNCTION_RETURNED.json').read_bytes());assert f['passed'] and f['actual_controls']==8 and not (B/'production').exists()
(B/'control').mkdir()
print(json.dumps(dict(passed=True,UUID_rw=m,actual_native_admission=f,new_control_namespace=True)))"""
  put('ROOT195_FIRSTV2_TARGET_CURRENT_UUID_NATIVE_ADMISSION_PROVED.json',d.code(client,route.PY,pre,dict(job=J),timeout=30))
  sf=client.open_sftp()
  try:
   for row in json.loads((N/'CONTROL195_MANIFEST.json').read_bytes())['files']:sf.put(row['local_path'],J+'/control/'+row['relative'])
   sf.put(str(N/'TRAIN195_COMPLETE_MANIFEST.json'),J+'/TRAIN195_COMPLETE_MANIFEST.json')
   with sf.file(J+'/FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json','wx') as f:f.write(json.dumps(admission,indent=2).encode())
  finally:sf.close()
  client.close();client=None
  client=d.connect72(secret)
  try:
   put('ROOT195_FIRSTV2_72_CNONE_AGAIN_BEFORE_OWNER.json',d.code(client,d.PY72,AUTH,{},timeout=45))
   create="""from pathlib import Path
import json
B=Path(v['root']);assert str(B)=='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ONE195_E0_START_FUDAN_JUMP40050_2610v195/owner';B.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(passed=True,root=str(B))))"""
   put('ROOT195_FIRSTV2_ORIGINAL72_OWNER_NAMESPACE_CREATED.json',d.code(client,d.PY72,create,dict(root=OWNER),timeout=30))
   sf=client.open_sftp()
   try:
    for name in ['jump195_finite_owner_authority72.py','jump195_protocol.py','three_slot_common_v1.py','single_writer72_authority_V85M_source.py']:sf.put(str(N/'control'/name),OWNER+'/'+name)
   finally:sf.close()
   token=secrets.token_hex(32);run='ONE195_FUDAN_JUMP195_400N50_'+str(time.time_ns())
   spec=dict(key='h1_210',execution_backend='source210',GPU_UUID='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e',max_parent_seconds=3900,exit_headroom_seconds=300,
    source_SHA=task['source_SHA'],source_Adamstep=641200,source_iteration=31984,manifest_file='TRAIN195_COMPLETE_MANIFEST.json',manifest_SHA=mh,
    job_root=J,python=route.PY,private_lock='/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock',
    worker_script='run195_literal_jump_plane_worker.py',num_envs=20000,seed=27,literal_jump195_400N50=True,reuse_delivered_fullstate=True,no_comparison_arms=True,
    run_id=run,token=token,owner_ssh_password=secret,owner_control_dependency_binding_SHA=H(N/'control/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'))
   cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts={'h1_210':spec},deferred_experts=[])
   identity=d.code(client,d.PY72,SPAWN,dict(root=OWNER,module='jump195_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg),timeout=30)
   put('ROOT195_FIRSTV2_ORIGINAL72_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=identity,spec={k:v for k,v in spec.items() if k not in ('token','owner_ssh_password')}))
  finally:client.close();client=None
  client=route.connect()
  node=d.code(client,route.PY,SPAWN,dict(root=J+'/control',module='jump195_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=spec),timeout=30)
  put('ROOT195_FIRSTV2_FORWARD210_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=node))
  first=d.code(client,route.PY,FIRST,dict(job=J),timeout=900)
  put('ROOT195_FIRSTV2_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json',first)
  client.close();client=None
  client=d.connect72(secret)
  proof="""from pathlib import Path
import json,time,hashlib
B=Path(v['root']);c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment'];row=json.loads((B/'OWNER_CURRENT.json').read_bytes())
if a is not None:assert a['owner_parent_pid']==v['pid']
files=[]
for name in ['OWNER_IDENTITY.json','THREE_SLOT_ORIGINAL_FINITE_ACCOUNTING_CONTRACT.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json']:
 p=B/name
 if p.is_file():
  b=p.read_bytes();files.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8')))
print(json.dumps(dict(epoch=time.time(),owner_matches_original_canonical=a is not None and a['owner_parent_pid']==v['pid'],canonical_None=a is None,remaining_snapshot=c['remaining_training_seconds'],owner_current=row,files=files,no_account_write=True)))"""
  state=d.code(client,d.PY72,proof,dict(root=OWNER,pid=identity['pid']),timeout=45)
  put('ROOT195_FIRSTV2_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST.json',state)
  f=first.get('first') or {}
  print(json.dumps(dict(first_passed=first['passed'],run_id=run,owner=identity,node=node,updates=f.get('actual_new_PPO_updates'),new_Adam=f.get('new_Adam_step'),first_complete=f.get('first_complete'),canonical_owner_matched=state['owner_matches_original_canonical'],GO=state['owner_current'].get('go'))),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT195_FIRSTV2_ALL_SSH_CLOSED_SESSION_RESTORED_LEASE_FREE.json',dict(epoch=time.time(),all_owned_control_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_lease='FREE',runtime_owned_original_owner_control_remains_only_if_job_active=True))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT195_FIRSTV2_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_new_GO=True));raise
