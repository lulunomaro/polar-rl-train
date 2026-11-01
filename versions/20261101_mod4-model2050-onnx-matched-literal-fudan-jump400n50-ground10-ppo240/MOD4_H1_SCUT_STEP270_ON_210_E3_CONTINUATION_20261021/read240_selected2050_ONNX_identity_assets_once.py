"""Human-selected model2050: bounded text-only provenance read; no model load."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,stat,subprocess,sys,time,traceback
import paramiko
T=Path(__file__).resolve().parent;W=T.parent
N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101/onnx_identity';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14);N.mkdir(exist_ok=False);R.mkdir()
 C4=T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/reports'
 assert read(C4/'ROOT_E2_GUARD01_V3_NORMAL900_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 assert read(C4/'ROOT_E2_GUARD01_V3_NEW_E2_FORMAL_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')['passed']
 base='D:/claude2/fangzhen';run=base+'/runs3060/fudan_stairs_actual/logs/2026-10-31_23-24-22_fudan_pyramid_stairs_up_fullDR_3060'
 selected=[base+'/train/deploy/mod4_fudan_recovery_model2050.onnx',base+'/train/deploy/mod4_fudan_recovery_model2050.onnx.data',base+'/scripts/export_sim2sim.py']
 folders=[]
 put('ROOT240_ONNX_NEW_EXACT_READ_PURPOSE_FROZEN.json',dict(epoch=time.time(),human_selection='ONNX exported from training checkpoint model_2050',
  selected_text_paths=selected,text_file_physical_open_max=len(selected),total_text_bytes_max=4000000,file_bytes_max=2000000,
  metadata_only_folders=folders,PT_NPZ_raw_opens=0,ONNX_graph_and_externaldata_opens_max=1,ONNX_binary_transfer_each_max=1,SDK_GPU_NN_account_or_remote_writes=0,
  previous_hash_mismatch_new_purpose='Selected exportPT vs same-number trainPT byte hashes differ; verify actual exported actor against selected fullPPO before continuation, not stats or Git',already_captured_player_source='USER3060_FULLDR_JUMP_READONLY_DETAILS_V239_20261101/reports/ROOT239_ORIGINAL3060_SELECTED_SOURCE_LOG_CONFIGS_ACTUAL.json'))
 pattern='read240_|transfer240_|install240_|start240_|read239_|collect237_|run_ROOT_latest32481_|launch_e2_solo_|collect_e2_solo_|run_ROOT238_|admit238_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(q.stdout) if q.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[a for a in rows if a['ProcessId']==os.getpid()];assert len(rows)==len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT240_ONNX_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 put('ROOT240_ONNX_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),PT_reads=0,ONNX_graph_and_external_reads_each_max=1,text_files_max=1,remote_writes=0))
 C=T/'W35_LATEST32481_FULL32S_SAMEUID_EVAL_SOURCE_V1_20261101';s=(C/'target_latest32_parent_ROOT_ONLY.py').read_text('utf8');tree=ast.parse(s)
 audit=ast.get_source_segment(s,next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='audit_current'))
 code="""from pathlib import Path
import hashlib,json,psutil,time
scope={};exec(v['contract'],scope);scope.update(Path=Path,hashlib=hashlib,json=json,psutil=psutil,time=time,read=lambda p:json.loads(Path(p).read_bytes()))
exec(v['audit'],scope);print(json.dumps(scope['audit_current'](v['binding'])))"""
 binding=read(T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101/reports/KNOWN_ACTIVE235_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 wrapper=mod('root239_2050_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v249.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(W/'polar-rl-train/archive_tools'));from capture_history import redact
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=mod('root239_2050_primary_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);secret=None
  fact=d.code(client,d.PY72,code,dict(contract=(C/'contract_latest32.py').read_text('utf8'),audit=audit,binding=binding),timeout=45)
  assert fact['scope']['mode']=='FRESH_CNONE_AFTER_MATCHING235_CLOSED'
  put('ROOT240_ONNX_FRESH72_MATCHING235_CLOSED_THEN_CLOSE72.json',fact);client.close();client=None
  secret,_=transport.recover('MOD4_EVAL_SSH_PASSWORD');assert secret
  sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));import eval_remote_io as pinned
  client=paramiko.SSHClient();client.load_system_host_keys();client.set_missing_host_key_policy(pinned.Pin())
  client.connect('10.24.4.249',username='lulunomaro',password=secret,timeout=15,banner_timeout=15,auth_timeout=15);secret=None
  assert hashlib.sha256(client.get_transport().get_remote_server_key().asbytes()).hexdigest()==pinned.HOST_SHA
  sf=client.open_sftp();sf.get_channel().settimeout(45);meta=[];texts=[];errors=[];total=0;artifacts=[];(N/'assets').mkdir()
  try:
   for folder in folders:
    try:
     for a in sorted(sf.listdir_attr(folder),key=lambda a:a.filename)[:180]:
      meta.append(dict(path=folder+'/'+a.filename,directory=stat.S_ISDIR(a.st_mode),bytes=a.st_size,mtime=a.st_mtime))
    except OSError as e:errors.append(dict(path=folder,error=str(e)))
   for p in selected:
    try:
     a=sf.stat(p);assert a.st_size<=2000000 and total+a.st_size<=4000000
     with sf.open(p,'rb') as f:b=f.read()
     total+=len(b)
     if p.endswith(('.onnx','.onnx.data')):
      dest=N/'assets'/Path(p).name
      with dest.open('xb') as local:local.write(b)
      artifacts.append(dict(path=p,local_path=str(dest),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),physical_opens=1,transfers=1))
     else:
      safe,count=redact(b.decode('utf-8-sig',errors='replace'))
      texts.append(dict(path=p,bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=safe,redactions=count,physical_opens=1))
    except OSError as e:errors.append(dict(path=p,error=str(e)))
  finally:sf.close()
  put('ROOT240_ONNX_EXPORT_TRAINING_PLAY_TEXTS_ACTUAL.json',dict(epoch=time.time(),passed=not errors,metadata_rows=meta,full_UTF8=texts,errors=errors,
   source_text_opens=len(texts),text_bytes=total,artifacts=artifacts,PT_raw_reads=0,ONNX_remote_opens=len(artifacts),task_GPU_SDK_neural_account_calls=0,remote_writes=0))
  print(json.dumps(dict(passed=not errors,files=[dict(path=x['path'],bytes=x['bytes'],SHA=x['SHA'])for x in texts],metadata_rows=len(meta),artifacts=artifacts,errors=errors)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT240_ONNX_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,
   SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(parents=True,exist_ok=True);put('ROOT240_ONNX_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry=True));raise
