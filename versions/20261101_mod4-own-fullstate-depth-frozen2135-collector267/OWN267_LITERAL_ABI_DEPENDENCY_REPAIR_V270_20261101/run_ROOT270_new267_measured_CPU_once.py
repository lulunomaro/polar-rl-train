from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_NEW267_MEASURED224_LITERAL_CPU270_20261101'
def put(n,x):
 with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,allow_nan=False)
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 p=argparse.ArgumentParser();p.add_argument('--source-index-SHA',required=True);a=p.parse_args();idx=N/'INDEX270_DATASET_CPU_SOURCE_FROZEN.json';assert H(idx)==a.source_index_SHA
 for row in read(idx)['files']:
  q=Path(row['path']);assert q.stat().st_size==row['bytes']and H(q)==row['SHA']
 pattern='run_ROOT270_|run_ROOT269_|run_ROOT267_|run_ROOT266_|run_ROOT265_|run_ROOT264_|read262_|run_ROOT261_|run_ROOT260_|run_ROOT258_|run_ROOT257_|run_ROOT256_|run_ROOT254_|run_ROOT250_|read253_|read252_|read251_|run_ROOT246_|run_ROOT242_|collect243_|collect240_|human241_|start240_|install240_|transfer240_|read240_|run_ROOT_latest32481_|run_ROOT240_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 x=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(x.stdout)if x.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['CreationDate']and rows[0]['ExecutablePath'].lower()==sys.executable.lower()and str(Path(__file__).resolve()).lower().replace('\\','/')in rows[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT270_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,exe=sys.executable,argv=sys.argv))
 client=transport=previous=secret=None
 try:
  wrapper=module('root270_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
  sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  secret=module('root270_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import hashlib,json,time
c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
p=Path(v['job']);assert p.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());p.mkdir(exist_ok=False);(p/'code').mkdir();(p/'native').mkdir()
print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,new_namespace=str(p),raw_model_reads=0,account_writes=0)))"""
  put('ROOT270_FRESH_CNONE_AND_NEW_NAMESPACE_ACTUAL.json',d.code(client,d.PY72,code,dict(job=J),timeout=45))
  files=[(str(p.relative_to(N/'source')).replace('\\','/'),p.read_bytes())for p in sorted((N/'source').rglob('*.py'))];files.append(('TASK270.json',(N/'TASK270_LOCAL_FROZEN.json').read_bytes()))
  sf=client.open_sftp()
  try:
   for relative,b in files:
    with sf.file(J+'/'+relative,'wx')as f:f.write(b);f.flush()
  finally:sf.close()
  code="""from pathlib import Path
import contextlib,hashlib,io,json,os,runpy,time,traceback
os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['PYTHONDONTWRITEBYTECODE']='1'
p=Path(v['job']);out=io.StringIO();error=None
for f in v['files']:
 b=(p/f['relative']).read_bytes();assert len(b)==f['bytes']and hashlib.sha256(b).hexdigest()==f['SHA']
try:
 with contextlib.redirect_stdout(out):runpy.run_path(str(p/'review270_NEW267_state_and_literal_frame_CPU_once.py'),run_name='__main__')
except BaseException:error=traceback.format_exc()
r=p/'REVIEW270_NEW267_MEASURED224_LITERAL_FRAME_CPU_RETURNED.json';result=json.loads(r.read_bytes())if r.is_file()else None
print(json.dumps(dict(epoch=time.time(),passed=bool(not error and result and result['passed']),error=error,result=result,original_stdout=out.getvalue(),account_writes=0)))"""
  actual=d.code(client,d.PY72,code,dict(job=J,files=[dict(relative=k,bytes=len(b),SHA=hashlib.sha256(b).hexdigest())for k,b in files]),timeout=300);put('ROOT270_NEW267_MEASURED224_LITERAL_CPU_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',actual)
  print(json.dumps(dict(passed=actual['passed'],error=actual['error'],result=actual['result'])))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT270_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT270_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
