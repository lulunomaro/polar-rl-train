"""Collect three original own JSON receipts only; no model/raw/SDK/GPU reads."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,x):
 with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 paths=[f'/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_NEW267_MEASURED224_LITERAL_CPU{i}_20261101/REVIEW{i}_ONCE_CONSUMED_BEFORE_RAW_IO.json'for i in(269,270)]
 paths.append('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_NEW267_MEASURED224_LITERAL_CPU270_20261101/REVIEW270_NEW267_MEASURED224_LITERAL_FRAME_CPU_RETURNED.json')
 put('FROZEN270_EXACT_THREE_ORIGINAL_SMALL_JSON_REPORTS_READ_PURPOSE.json',dict(epoch=time.time(),paths=paths,each_report_reads_max=1,maximum_each_bytes=65536,no_directory_scan=True,models_raw_SDK_GPU_account=0,experiment_or_once_reexecution=False))
 pattern='collect270_exact_|run_ROOT270_|run_ROOT269_|run_ROOT267_|run_ROOT266_|run_ROOT265_|run_ROOT264_|read262_|run_ROOT261_|run_ROOT260_|run_ROOT258_|run_ROOT257_|run_ROOT256_|run_ROOT254_|run_ROOT250_|read253_|read252_|read251_|run_ROOT246_|run_ROOT242_|collect243_|collect240_|human241_|start240_|install240_|transfer240_|read240_|run_ROOT_latest32481_|run_ROOT240_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 x=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(x.stdout)if x.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['CreationDate']and rows[0]['ExecutablePath'].lower()==sys.executable.lower()and str(Path(__file__).resolve()).lower().replace('\\','/')in rows[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT270_EXACT_SMALL_TEXT_FRESH_LOCAL_CIM.json',dict(epoch=time.time(),rows=rows,exe=sys.executable,argv=sys.argv))
 client=transport=previous=secret=None
 try:
  transport,previous=module('root270reports_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  secret=module('root270reports_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import json,time
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,account_writes=0)))"""
  authority=d.code(client,d.PY72,code,{},timeout=45);sf=client.open_sftp();reports=[]
  try:
   for p in paths:
    assert p.endswith('.json')and Path(p).name in('REVIEW269_ONCE_CONSUMED_BEFORE_RAW_IO.json','REVIEW270_ONCE_CONSUMED_BEFORE_RAW_IO.json','REVIEW270_NEW267_MEASURED224_LITERAL_FRAME_CPU_RETURNED.json')
    st=sf.stat(p);assert 0<st.st_size<=65536
    with sf.file(p,'rb')as f:b=f.read(65537)
    assert len(b)==st.st_size;v=json.loads(b);reports.append(dict(path=p,bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8'),reads=1))
  finally:sf.close()
  put('ROOT270_EXACT_THREE_ORIGINAL_SMALL_UTF8_REPORTS_RETURNED_ACTUAL.json',dict(passed=True,epoch=time.time(),authority=authority,reports=reports,models_raw_SDK_GPU_account=0,no_experiment_reexecution=True))
  print(json.dumps(dict(passed=True,original_text_reports=len(reports),model_raw_GPU_reads=0)))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT270_EXACT_TEXT_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT270_EXACT_TEXT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
