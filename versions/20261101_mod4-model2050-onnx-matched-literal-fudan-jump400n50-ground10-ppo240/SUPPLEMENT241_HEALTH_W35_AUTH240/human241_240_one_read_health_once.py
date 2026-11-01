"""One new human-requested240 health snapshot, no model or training changes."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
REMOTE=r'''from pathlib import Path
import hashlib,json,os,psutil,re,time
b=v['binding'];O=Path(b['owner']['root']);J=Path(v['job']);C=J/'control240'
P=Path(b['canonical_path']);raw=P.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
identity=json.loads((O/'OWNER_IDENTITY.json').read_bytes());current=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert identity['pid']==b['owner']['pid'] and identity['creation']==b['owner']['creation'] and current['go']==b['go']
a=c['active_segment'];assert a is None or a['owner_parent_pid']==b['owner']['pid']
assert all(g['run_id']==b['run_id'] for g in current['go'].values())
facts={}
for label,known in [('owner',b['owner']),('node',b['node']),('worker',b['worker_at_FIRST_node_report'])]:
 try:
  p=psutil.Process(known['pid']);creation=p.create_time();status=p.status();expected_cwd=known.get('cwd',known.get('root'))
  fact=dict(pid=p.pid,creation=creation,exe=p.exe(),argv=p.cmdline(),cwd=p.cwd(),status=status,RSS=p.memory_info().rss,CPU_seconds=sum(p.cpu_times()[:2]))
  assert creation==known['creation'] and fact['exe']==known['exe'] and fact['argv']==known['argv'] and fact['cwd']==expected_cwd,label
  fact['exact_known_process_identity_matched']=True;fact['executing_not_original_zombie']=status!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:fact=dict(pid=known['pid'],known_original_process_OUT=True)
 facts[label]=fact
if a is not None:
 assert facts['owner'].get('executing_not_original_zombie')
 assert a['experts']['jump_72']['started_epoch']==b['go']['jump_72']['learning_started_epoch']
rows=[]
paths=[J/'production'/n for n in ('LATEST_PROGRESS.json','latest_complete.json','FINAL.json','ORIGINAL_ERROR.json')]
paths += [C/'NODE_ORIGINAL_ERROR.json',C/'NODE_TERMINAL_ACTUAL.json',C/'NODE_EXIT_ACTUAL.json',O/'OWNER_ORIGINAL_ERROR.json',O/'COHORT_FINAL.json',O/'OWNER_EXIT_ACTUAL.json']
for p in paths:
 if not p.is_file():continue
 assert p.stat().st_size<100000
 with p.open('rb')as f:
  before=os.fstat(f.fileno());data=f.read();after=os.fstat(f.fileno())
 assert before.st_size==after.st_size==len(data)and before.st_mtime_ns==after.st_mtime_ns
 rows.append(dict(path=str(p),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),UTF8=data.decode('utf8'),value=json.loads(data),physical_opens=1))
log=C/'production_WORKER.log';tail=None;issues=[]
if log.is_file():
 with log.open('rb')as f:
  size=os.fstat(f.fileno()).st_size;start=max(0,size-65536);f.seek(start);data=f.read(size-start)
 text=data.decode('utf8','replace')
 for line in text.splitlines():
  if re.search(r'Traceback \(most recent call last\)|CUDA out of memory|illegal memory access|FloatingPointError|non-finite|(?<![A-Za-z])(?:NaN|[+-]?inf)(?![A-Za-z])',line,re.I)or('PxPhysics::createMaterial'in line and'64K'in line):issues.append(line)
 tail=dict(path=str(log),full_file_bytes_at_open=size,offset=start,selected_bytes=len(data),selected_SHA=hashlib.sha256(data).hexdigest(),UTF8=text,physical_opens=1,scope='New humanhealthpurpose one bounded tail, not full training log or trajectory')
print(json.dumps(dict(epoch=time.time(),passed_read=True,run_id=b['run_id'],authority=dict(canonical_None=a is None,exact_current240_owner_run_fullGO_matched=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),account_write=False),
 process_facts=facts,files=rows,owned_log_tail=tail,selected_log_issue_lines=issues,selected_log_issue_count=len(issues),
 saved_checkpoint_metadata_only=True,model_PT_raw_NPZ_SDK_GPU_or_optimizer_calls=0,no_remote_write_or_signal=True)))
'''
def main():
 assert sys.version_info[:2]==(3,14)
 pattern='human241_|start240_|install240_|transfer240_|read240_|collect240_|run_ROOT240_|run_ROOT_latest32481_|collect_e2_solo_|read239_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];assert len(rows)==len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT241_HUMAN_HEALTH_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 binding=read(R/'KNOWN_ACTIVE240_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 put('ROOT241_NEW_HUMAN_HEALTH_READ_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),human='现在训练健康吗',
  known240_processes_only=['owner','node','worker'],canonical_owner_identity_current_JSON_reads=3,maximum_progress_error_small_JSON_reads=10,
  owned_log_tail_max_bytes=65536,owned_log_opens_max=1,checkpoint_content_transfer_hash_reads=0,GPU_util_or_free_queries=0,
  SDK_NN_optimizer_training_account_write_or_signals=0,no_periodic_watcher_or_early_formal_collector=True))
 wrapper=module('root241_status_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('root241_status_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);secret=None
  value=d.code(client,d.PY72,REMOTE,dict(binding=binding,job=read(R/'INSTALL240_SOURCE_ASSET_MANIFEST.json')['job_root']),timeout=60)
  put('ROOT241_ACTUAL240_ONE_HUMAN_HEALTH_SNAPSHOT_RETURNED.json',value)
  small={Path(x['path']).name:x['value']for x in value['files']}
  latest=small.get('LATEST_PROGRESS.json',{});save=small.get('latest_complete.json',{})
  print(json.dumps(dict(passed_read=value['passed_read'],read_epoch=value['epoch'],active240=not value['authority']['canonical_None'],
   known_processes={k:x.get('executing_not_original_zombie',False)for k,x in value['process_facts'].items()},latest_progress=latest,
   latest_complete_metadata=save,progress_age_s=value['epoch']-latest.get('epoch',value['epoch']),save_age_s=value['epoch']-save.get('epoch',value['epoch']),
   selected_log_issue_count=value['selected_log_issue_count'],error_or_final_files=[x for x in small if 'ERROR'in x or x=='FINAL.json'])),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT241_HUMAN_HEALTH_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT241_HUMAN_HEALTH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_repeat=True));raise
