"""New human-selected2050 continuation: necessary PT provenance and one transfer."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
import paramiko
T=Path(__file__).resolve().parent;W=T.parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14);N.mkdir(exist_ok=False);R.mkdir();(N/'source_model').mkdir()
 selected='D:/claude2/fangzhen/train/deploy/mod4_fudan_recovery_model2050.pt'
 original='D:/claude2/fangzhen/runs3060/fudan_stairs_actual/logs/2026-10-31_23-24-22_fudan_pyramid_stairs_up_fullDR_3060/model_2050.pt'
 put('ROOT240_HUMAN_SELECTED2050_AND_NECESSARY_NEW_SOURCE_PURPOSE_FROZEN.json',dict(epoch=time.time(),
  human='从 model_2050 适配到总计划的400N、50Hz',full_PPO_not_ONNX_only=True,selected_checkpoint=selected,training_checkpoint=original,
  source_physical_byte_reads={selected:1,original:1},selected_transfer_to_ROOT=1,old_E0_or4999_native_model_reads=0,
  next_necessary_selected_CPU_decode_max=1,next_production_GPU_decode_max=1,ONNX_reads=0,source_files_never_written=True,
  task=dict(nominal_gas_k=2000,policy_Hz=50,feedback_Hz=100,physics_dt=.0025,TGS=[32,4],D0white_v3_D1_D7=True,
   literal_original_Fudan_JUMP=True,ground_disjoint_fraction=.1,save_seconds=3600,max_parent_seconds=3900),
  DR0_source_unselected=True,old_E0_branch_retired=True,no_new_GO_until_complete_source_native_admission=True))
 put('ROOT240_INITIAL_LOCAL_PATH_LOOKUP_ERRORS_PRESERVED.json',dict(epoch=time.time(),
  attempted_missing=['E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/launch_e2_solo_original_FIRST_ROOT_ONLY_once.py','E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/install_e2_solo_original_source_ROOT_ONLY_once.py'],
  actual_existing='launch_e2_solo_install_FIRST_ROOT_ONLY_once.py',network_model_or_task_actions_before_lookup=0))
 pattern='transfer240_|read240_|install240_|start240_|run_ROOT240_|read239_|collect_e2_solo_|launch_e2_solo_|run_ROOT_latest32481_|admit238_|run_ROOT238_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(q.stdout) if q.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()]
 assert len(rows)==len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT240_SOURCE_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 put('ROOT240_SELECTED2050_READ_AND_TRANSFER_ONCE_CONSUMED.json',dict(epoch=time.time(),physical_PT_reads_max=2,selected_transfer_max=1,CPU_decode_this_entry=0,NN_GPU_SDK_or_remote_writes=0))
 C=T/'W35_LATEST32481_FULL32S_SAMEUID_EVAL_SOURCE_V1_20261101';s=(C/'target_latest32_parent_ROOT_ONLY.py').read_text('utf8');tree=ast.parse(s)
 audit=ast.get_source_segment(s,next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='audit_current'))
 code="""from pathlib import Path
import hashlib,json,psutil,time
scope={};exec(v['contract'],scope);scope.update(Path=Path,hashlib=hashlib,json=json,psutil=psutil,time=time,read=lambda p:json.loads(Path(p).read_bytes()))
exec(v['audit'],scope);print(json.dumps(scope['audit_current'](v['binding'])))"""
 binding=read(T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101/reports/KNOWN_ACTIVE235_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 wrapper=module('root240_source_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v249.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('root240_source_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);secret=None
  fact=d.code(client,d.PY72,code,dict(contract=(C/'contract_latest32.py').read_text('utf8'),audit=audit,binding=binding),timeout=45)
  assert fact['scope']['mode']=='FRESH_CNONE_AFTER_MATCHING235_CLOSED'
  put('ROOT240_SOURCE_FRESH72_MATCHING235_CLOSED_THEN_CLOSE72.json',fact);client.close();client=None
  secret,_=transport.recover('MOD4_EVAL_SSH_PASSWORD');assert secret
  sys.path.insert(0,str(W/'MOD4_MOE_PLAN_EXECUTION_20261007'));import eval_remote_io as pinned
  client=paramiko.SSHClient();client.load_system_host_keys();client.set_missing_host_key_policy(pinned.Pin())
  client.connect('10.24.4.249',username='lulunomaro',password=secret,timeout=15,banner_timeout=15,auth_timeout=15);secret=None
  assert hashlib.sha256(client.get_transport().get_remote_server_key().asbytes()).hexdigest()==pinned.HOST_SHA
  sf=client.open_sftp();sf.get_channel().settimeout(90);proof=[];local=N/'source_model/model_2050_from_selected_export.pt'
  try:
   for p in (selected,original):
    before=sf.stat(p);assert before.st_size==386869
    with sf.open(p,'rb') as stream:b=stream.read()
    after=sf.stat(p);assert len(b)==before.st_size==after.st_size and before.st_mtime==after.st_mtime
    sha=hashlib.sha256(b).hexdigest();proof.append(dict(path=p,bytes=len(b),SHA=sha,physical_byte_opens=1,mtime=after.st_mtime,remote_writes=0))
    if p==selected:
     with local.open('xb') as f:f.write(b)
    del b
   assert proof[0]['SHA']==proof[1]['SHA'],'Selected export PT and training2050 differ; do not promote'
  finally:sf.close()
  result=dict(epoch=time.time(),passed=True,selected_path=str(local),source_SHA=proof[0]['SHA'],source_bytes=proof[0]['bytes'],
   selected_export_PT_equals_original_training_PT_SHA=True,source_proofs=proof,selected_transfer=1,CPU_or_GPU_decodes=0,
   ONNX_graph_and_external_data_identity_still_not_read=True,remote_task_or_SDK_or_GPU_actions=0,source_originals_unmodified=True)
  put('ROOT240_MODEL2050_FULLPPO_PROVENANCE_AND_ONE_TRANSFER_ACTUAL.json',result)
  print(json.dumps(dict(passed=True,SHA=proof[0]['SHA'],bytes=proof[0]['bytes'],two_source_paths_equal=True,local_path=str(local))),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT240_SOURCE_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(parents=True,exist_ok=True);put('ROOT240_SOURCE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry=True));raise
