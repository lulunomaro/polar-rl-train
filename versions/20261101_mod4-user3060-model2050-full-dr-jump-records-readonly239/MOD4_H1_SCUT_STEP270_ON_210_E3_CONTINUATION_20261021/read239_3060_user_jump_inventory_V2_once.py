"""User explicitly requested3060 read-only experiment lookup; no GPU/tasks/models."""
from pathlib import Path
import ast,base64,hashlib,importlib.util,json,os,sys,subprocess,time,traceback
import paramiko
T=Path(__file__).resolve().parent;W=T.parent;N=T/'USER3060_FULLDR_JUMP_READONLY_V239V2_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14);N.mkdir(exist_ok=False);R.mkdir()
 put('ROOT239_USER_READONLY_PURPOSE_FROZEN.json',dict(epoch=time.time(),human_exact='我在3060主机上实验了一下，full dr并不影响跳跃，你链接3060主机查一下',
 target='Original pinned10.24.4.249 Windows3060',only_existing_project_records=True,
 model_binary_raw_reads=0,new_GPU_SDK_neural_task_or_training=0,remote_writes=0,account_writes=0,
 search_scope=['D:/claude2/fangzhen','D:/MOD4_async_eval'],maximum_directory_metadata_rows=600,no_unknown_PID_or_GPU_PID_scan=True,
 no_auth_in_argv_env_or_disk=True,no_changes_to_user_experiment=True))
 pattern='read239_|collect237_|run_ROOT_latest32481_|launch_e2_solo_|collect_e2_solo_|review_e2_solo_|collect235_failed_|run_ROOT238_|admit238_|run_actual'
 q="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 v=subprocess.run(['pwsh.exe','-NoProfile','-Command',q],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(v.stdout) if v.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];assert len(own)==len(rows)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT239_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 put('ROOT239_INVENTORY_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),read_only=True,model_reads=0,source='human3060counterexample lookup'))
 C=T/'W35_LATEST32481_FULL32S_SAMEUID_EVAL_SOURCE_V1_20261101';s=(C/'target_latest32_parent_ROOT_ONLY.py').read_text('utf8');tree=ast.parse(s)
 audit=ast.get_source_segment(s,next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='audit_current'))
 code="""from pathlib import Path
import hashlib,json,psutil,time
scope={};exec(v['contract'],scope);scope.update(Path=Path,hashlib=hashlib,json=json,psutil=psutil,time=time,read=lambda p:json.loads(Path(p).read_bytes()))
exec(v['audit'],scope);print(json.dumps(scope['audit_current'](v['binding'])))"""
 binding=read(T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101/reports/KNOWN_ACTIVE235_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 wrapper=mod('root239_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v249.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=mod('root239_primary_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);secret=None
  fact=d.code(client,d.PY72,code,dict(contract=(C/'contract_latest32.py').read_text('utf8'),audit=audit,binding=binding),timeout=45)
  put('ROOT239_FRESH72_EXACT235_OR_CLOSED_THEN_CLOSE72.json',fact);client.close();client=None
  secret,count=transport.recover('MOD4_EVAL_SSH_PASSWORD');assert secret
  sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));import eval_remote_io as pinned
  client=paramiko.SSHClient();client.load_system_host_keys();client.set_missing_host_key_policy(pinned.Pin())
  client.connect('10.24.4.249',username='lulunomaro',password=secret,timeout=15,banner_timeout=15,auth_timeout=15);secret=None
  assert hashlib.sha256(client.get_transport().get_remote_server_key().asbytes()).hexdigest()==pinned.HOST_SHA
  ps="[pscustomobject]@{hostname=[Environment]::MachineName;utc=[DateTime]::UtcNow.ToString('o');read_only=$true}|ConvertTo-Json -Compress"
  _,o,e=client.exec_command('powershell.exe -NoProfile -NonInteractive -EncodedCommand '+base64.b64encode(ps.encode('utf-16le')).decode(),timeout=30)
  raw=o.read();err=e.read();rc=o.channel.recv_exit_status();assert rc==0,err.decode('utf8','replace')[-2000:]
  host=json.loads(raw.decode('utf-8-sig'));sf=client.open_sftp();sf.get_channel().settimeout(30);out=[];errors=[]
  roots=['D:/claude2/fangzhen','D:/MOD4_async_eval'];queue=[(x,0)for x in roots];seen=set()
  try:
   while queue and len(out)<600:
    folder,depth=queue.pop(0)
    if folder in seen:continue
    seen.add(folder)
    try:items=sorted(sf.listdir_attr(folder),key=lambda z:z.st_mtime,reverse=True)
    except OSError as ex:errors.append(dict(path=folder,error=str(ex)));continue
    limit=50 if depth==0 else 24
    for a in items[:limit]:
     import stat
     directory=stat.S_ISDIR(a.st_mode);p=folder+'/'+a.filename
     out.append(dict(path=p,directory=directory,bytes=a.st_size,mtime=a.st_mtime))
     name=a.filename.lower()
     if directory and depth<2 and (depth==0 or any(z in name for z in ('jump','fudan','2026-11','20261101','log','run','train','dr','experiment','deploy'))):
      if name not in ('.git','.venv-isaaclab','.venv','__pycache__','node_modules','assets','data','third_party','source_700n'):queue.append((p,depth+1))
     if len(out)>=600:break
  finally:sf.close()
  value=dict(epoch=time.time(),passed=True,host=host,target='10.24.4.249',host_pin=pinned.HOST_SHA,metadata_rows=out,errors=errors,
   visited_directories=sorted(seen),model_binary_raw_content_reads=0,source_or_log_content_reads=0,remote_writes=0,GPU_SDK_task_calls=0)
  put('ROOT239_ORIGINAL3060_PROJECT_INVENTORY_ACTUAL.json',value)
  print(json.dumps(dict(passed=True,host=host,rows=len(out),recent=[x for x in out if x['mtime']>1793433600][:55],errors=errors)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT239_INVENTORY_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(parents=True,exist_ok=True);put('ROOT239_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry=True));raise
