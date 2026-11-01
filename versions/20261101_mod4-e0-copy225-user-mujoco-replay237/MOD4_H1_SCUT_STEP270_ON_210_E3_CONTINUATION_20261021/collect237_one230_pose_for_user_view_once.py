"""One explicit old230 pose transfer for a NEW human requested display;0models."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;N=T/'E0_CANDIDATE225_USER_MUJOCO_V237_20261101';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 purpose=read(R/'FROZEN237_FRESH_USER_E0_DISPLAY_PURPOSE_BEFORE_IO.json');artifact=purpose['selected_case']['producer']
 pattern='collect237_|run_ROOT_latest32481_|launch_e2_solo_|collect_e2_solo_|review_e2_solo_|collect235_failed_|run_actual|read234|parent234|run232|parent232|read233'
 q="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 r=subprocess.run(['pwsh.exe','-NoProfile','-Command',q],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(r.stdout) if r.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[a for a in rows if a['ProcessId']==os.getpid()];assert len(own)==1 and len(rows)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT237_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 put('ROOT237_VISUAL_TRANSFER_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),purpose=purpose,model_reads=0,new_GPU_or_SDK=0))
 C=T/'W35_LATEST32481_FULL32S_SAMEUID_EVAL_SOURCE_V1_20261101'
 text=(C/'target_latest32_parent_ROOT_ONLY.py').read_text('utf8');tree=ast.parse(text)
 audit=ast.get_source_segment(text,next(a for a in tree.body if isinstance(a,ast.FunctionDef) and a.name=='audit_current'))
 contract=(C/'contract_latest32.py').read_text('utf8')
 binding=read(T/'E2_ORIGINAL_WORLD_PPO_ADMISSION_FAILURE_V235_20261101/reports/KNOWN_ACTIVE235_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json')
 code="""from pathlib import Path
import hashlib,json,psutil,time
scope={};exec(v['contract'],scope);scope.update(Path=Path,hashlib=hashlib,json=json,psutil=psutil,time=time,read=lambda p:json.loads(Path(p).read_bytes()))
exec(v['audit'],scope);print(json.dumps(scope['audit_current'](v['binding'])))"""
 wrapper=mod('root237_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=mod('root237_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);fact=d.code(client,d.PY72,code,dict(contract=contract,audit=audit,binding=binding),timeout=45)
  put('ROOT237_FRESH72_EXACT235_OR_CLOSED_CNONE_THEN_CLOSE72.json',fact);client.close();client=None
  client=d.connect72(secret);secret=None;sf=client.open_sftp();sf.get_channel().settimeout(90)
  dest=N/'CASE230_literal_jump_FOR_NEW237_USER_VIEW.npz';digest=hashlib.sha256();total=0
  try:
   assert sf.stat(artifact['path']).st_size==artifact['bytes']
   with sf.open(artifact['path'],'rb') as src,dest.open('xb') as out:
    while True:
     b=src.read(262144)
     if not b:break
     out.write(b);digest.update(b);total+=len(b)
  finally:sf.close()
  assert total==artifact['bytes'] and digest.hexdigest()==artifact['SHA']
  receipt=dict(epoch=time.time(),passed=True,path=str(dest),bytes=total,SHA=digest.hexdigest(),producer_source=artifact,
   remote_physical_open=1,transfers=1,producer_and_transferred_same_stream_SHA_equal=True,local_pose_reads_so_far=0,
   local_model_reads=0,new_SDK_GPU_controls=0,read_purpose='Fresh237 user visual only,not statistics/Git')
  put('ROOT237_ONE_SELECTED230_POSE_TRANSFER_INTEGRITY_ACTUAL.json',receipt);print(json.dumps(receipt),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT237_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT237_ORIGINAL_TRANSFER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
