"""New bounded source/log read purpose following actual3060 inventory;no tasks."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,stat,subprocess,sys,time,traceback
import paramiko
T=Path(__file__).resolve().parent;W=T.parent;N=T/'USER3060_FULLDR_JUMP_READONLY_DETAILS_V239_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14);N.mkdir(exist_ok=False);R.mkdir()
 old=T/'USER3060_FULLDR_JUMP_READONLY_V239V2_20261101/reports'
 assert read(old/'ROOT239_INVENTORY_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 roots=['D:/claude2/fangzhen/runs3060/supermimic_fullDR_40050','D:/claude2/fangzhen/runs3060/fudan_stairs_actual','D:/claude2/fangzhen/runs3060/fudan_stairs_smoke','D:/claude2/fangzhen/runs4090/fudan_stairs_remote_20261101','D:/claude2/fangzhen/train/deploy']
 explicit=['D:/claude2/fangzhen/scripts/play_mod4_fudan_stairs_mujoco.py','D:/claude2/fangzhen/runs3060/mujoco_model2000_viewer.out.log','D:/claude2/fangzhen/runs3060/supermimic_live_viewer.out.log']
 put('ROOT239_DETAILS_NEW_READ_PURPOSE_FROZEN.json',dict(epoch=time.time(),human_requested_actual3060_fullDR_jump=True,roots=roots,explicit_sources=explicit,
  model_binary_NPZ_raw_content_reads=0,source_log_physical_byte_open_max=32,total_text_bytes_max=8000000,
  maximum_file_text_bytes=2000000,tree_depth_max=3,metadata_rows_max=500,task_neural_GPU_SDK_or_account_calls=0,remote_writes=0))
 pattern='read239_|collect237_|run_ROOT_latest32481_|launch_e2_solo_|collect_e2_solo_|review_e2_solo_|run_ROOT238_|admit238_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(q.stdout) if q.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[a for a in rows if a['ProcessId']==os.getpid()];assert len(rows)==len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT239_DETAILS_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 put('ROOT239_DETAILS_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),model_reads=0,remote_writes=0,selected_logs_newpurpose=True))
 C=T/'W35_LATEST32481_FULL32S_SAMEUID_EVAL_SOURCE_V1_20261101';s=(C/'target_latest32_parent_ROOT_ONLY.py').read_text('utf8');tree=ast.parse(s)
 audit=ast.get_source_segment(s,next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='audit_current'))
 code="""from pathlib import Path
import hashlib,json,psutil,time
scope={};exec(v['contract'],scope);scope.update(Path=Path,hashlib=hashlib,json=json,psutil=psutil,time=time,read=lambda p:json.loads(Path(p).read_bytes()))
exec(v['audit'],scope);print(json.dumps(scope['audit_current'](v['binding'])))"""
 binding=read(T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101/reports/KNOWN_ACTIVE235_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 wrapper=mod('root239_details_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v249.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(W/'polar-rl-train/archive_tools'));from capture_history import redact
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=mod('root239_details_primary_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);secret=None;fact=d.code(client,d.PY72,code,dict(contract=(C/'contract_latest32.py').read_text('utf8'),audit=audit,binding=binding),timeout=45)
  put('ROOT239_DETAILS_FRESH72_EXACT235_THEN_CLOSE72.json',fact);client.close();client=None
  secret,_=transport.recover('MOD4_EVAL_SSH_PASSWORD');assert secret
  sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));import eval_remote_io as pinned
  client=paramiko.SSHClient();client.load_system_host_keys();client.set_missing_host_key_policy(pinned.Pin());client.connect('10.24.4.249',username='lulunomaro',password=secret,timeout=15,banner_timeout=15,auth_timeout=15);secret=None
  assert hashlib.sha256(client.get_transport().get_remote_server_key().asbytes()).hexdigest()==pinned.HOST_SHA
  sf=client.open_sftp();sf.get_channel().settimeout(45);queue=[(p,0)for p in roots];meta=[];errors=[];selected=list(explicit);seen=set()
  try:
   while queue and len(meta)<500:
    folder,depth=queue.pop(0)
    if folder in seen:continue
    seen.add(folder)
    try:items=sorted(sf.listdir_attr(folder),key=lambda a:a.st_mtime,reverse=True)
    except OSError as e:errors.append(dict(path=folder,error=str(e)));continue
    for a in items[:80]:
     p=folder+'/'+a.filename;directory=stat.S_ISDIR(a.st_mode);meta.append(dict(path=p,directory=directory,bytes=a.st_size,mtime=a.st_mtime))
     if directory and depth<3 and a.filename.lower() not in ('__pycache__','assets','.git'):queue.append((p,depth+1))
     if not directory and Path(p).suffix.lower() in ('.json','.yaml','.yml','.py','.md','.txt','.log') and a.st_size<=2000000:
      if Path(p).suffix.lower() in ('.json','.yaml','.yml','.log','.md') or any(z in a.filename.lower()for z in ('config','reward','dr','eval','jump','fudan','manifest','train')):selected.append(p)
     if len(meta)>=500:break
   texts=[];total=0
   for p in list(dict.fromkeys(selected))[:32]:
    try:
     a=sf.stat(p)
     if a.st_size>2000000 or total+a.st_size>8000000:continue
     with sf.open(p,'rb') as f:b=f.read()
     total+=len(b);safe,count=redact(b.decode('utf-8-sig',errors='replace'))
     texts.append(dict(path=p,bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=safe,redactions=count,physical_opens=1))
    except OSError as e:errors.append(dict(path=p,error=str(e)))
  finally:sf.close()
  value=dict(epoch=time.time(),passed=True,host='Pinned original3060/LULU',metadata_rows=meta,full_UTF8=texts,errors=errors,
   source_text_opens=len(texts),text_bytes=total,model_binary_raw_reads=0,task_GPU_SDK_neural_or_account_calls=0,remote_writes=0)
  put('ROOT239_ORIGINAL3060_SELECTED_SOURCE_LOG_CONFIGS_ACTUAL.json',value)
  print(json.dumps(dict(passed=True,source_text_files=[dict(path=x['path'],bytes=x['bytes'],SHA=x['SHA'],redactions=x['redactions'])for x in texts],metadata_rows=len(meta),errors=errors)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT239_DETAILS_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:R.mkdir(parents=True,exist_ok=True);put('ROOT239_DETAILS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry=True));raise
