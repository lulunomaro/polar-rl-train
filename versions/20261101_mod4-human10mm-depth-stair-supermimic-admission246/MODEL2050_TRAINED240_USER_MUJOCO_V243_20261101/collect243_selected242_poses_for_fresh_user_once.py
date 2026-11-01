"""Four new242 pose transfers for fresh human view; no model/SDK/NN reads."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports';T=N.parent;W=T.parent
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
AUTH="""from pathlib import Path
import hashlib,json,time
raw=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]and c['active_segment']is None
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),account_writes=0)))"""
def main():
 assert sys.version_info[:2]==(3,14)
 purpose=read(R/'FROZEN243_FRESH_USER_DISPLAY_PURPOSE_BEFORE_IO.json')
 for r in purpose['source_files']:
  b=Path(r['path']).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['SHA']
 pattern='collect243_|collect240_|human241_|run_ROOT242_|start240_|install240_|transfer240_|read240_|run_ROOT_latest32481_|launch_e2_solo_|collect_e2_solo_|review_e2_solo_|run_actual|run_ROOT240_|read233|parent232|run232'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 a=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(a.stdout)if a.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[r for r in rows if r['ProcessId']==os.getpid()];assert len(rows)==len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT243_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows))
 put('ROOT243_FRESH_VIEW_TRANSFER_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),purpose=purpose,model_reads=0,new_physics_or_neural=0))
 wrapper=mod('root243_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None;receipts=[]
 try:
  transport,previous=wrapper.install();s=mod('root243_memory_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=s.recover();client=d.connect72(secret);secret=None
  put('ROOT243_FRESH72_CNONE_BEFORE_POSE_READ_ACTUAL.json',d.code(client,d.PY72,AUTH,{},timeout=45))
  sf=client.open_sftp();sf.get_channel().settimeout(90)
  try:
   for case in purpose['cases']:
    artifact=case['producer'];dest=N/('CASE242_'+case['name']+'_FOR_USER243_VIEW.npz');digest=hashlib.sha256();total=0
    assert sf.stat(artifact['path']).st_size==artifact['bytes']
    with sf.open(artifact['path'],'rb')as src,dest.open('xb')as out:
     while True:
      b=src.read(262144)
      if not b:break
      out.write(b);digest.update(b);total+=len(b)
    assert total==artifact['bytes']and digest.hexdigest()==artifact['SHA']
    row=dict(name=case['name'],path=str(dest),bytes=total,SHA=digest.hexdigest(),producer_source=artifact,remote_byte_opens=1,transfers=1,producer_and_transferred_same_stream_SHA_equal=True,local_pose_reads_so_far=0)
    receipts.append(row);put('ROOT243_'+case['name']+'_POSE_TRANSFER_INTEGRITY_ACTUAL.json',row)
  finally:sf.close()
  put('ROOT243_SELECTED242_POSE_TRANSFERS_ACTUAL.json',dict(epoch=time.time(),passed=True,cases=receipts,model_reads=0,SDK_GPU_neural_controls=0,not_for_stats_or_Git=True));print(json.dumps(dict(passed=True,case_transfers=len(receipts),bytes=sum(r['bytes']for r in receipts),model_reads=0)))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT243_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT243_ORIGINAL_TRANSFER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
