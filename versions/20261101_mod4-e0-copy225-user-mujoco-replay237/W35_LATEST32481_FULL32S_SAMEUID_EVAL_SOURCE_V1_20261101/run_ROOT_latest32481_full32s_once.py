"""ROOT-only Py314 serial metadata+one full32s eval caller. Never GO/account writes."""
from pathlib import Path,PurePosixPath
import argparse,ast,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
from contract_latest32 import metadata,qualified,KNOWN235_RUN
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
INDEX='INDEX_W35_LATEST32481_FULL32S_FROZEN.json'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def stage(sf,p,data):
 with sf.file(p,'wx') as f:f.write(data);f.flush()
AUTH='''from pathlib import Path
import hashlib,json,psutil,time
scope={};exec(v['contract_source'],scope)
scope.update(Path=Path,hashlib=hashlib,json=json,psutil=psutil,time=time,read=lambda p:json.loads(Path(p).read_bytes()))
exec(v['audit_source'],scope)
fact=scope['audit_current'](v['binding']);assert fact['scope']['active_GPU_UUID']!=v['GPU_UUID']
print(json.dumps(fact))'''
EXEC='''from pathlib import Path
import contextlib,hashlib,io,json,runpy,sys,time,traceback
B=Path(v['job'])
for r in v['files']:
 p=B/r['relative'];raw=p.read_bytes();assert len(raw)==r['bytes'] and hashlib.sha256(raw).hexdigest()==r['SHA']
capture=io.StringIO();error=None
try:
 sys.path.insert(0,str(B));sys.argv=[str(B/'target_latest32_parent_ROOT_ONLY.py'),'--task',str(B/'TASK_LATEST32_PENDING_ADMISSION.json')]
 with contextlib.redirect_stdout(capture):runpy.run_path(sys.argv[0],run_name='__main__')
except BaseException:error=traceback.format_exc()
if error:
 with (B/'ROOT_LATEST32_REMOTE_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=error,no_automatic_retry=True),f,indent=2)
p=B/'ACTUAL_LATEST32_ORIGINAL_PARENT_RETURNED.json';value=json.loads(p.read_bytes()) if p.is_file() else None
texts=[]
for folder in (B,B/'actual_latest32'):
 for p in sorted(folder.iterdir()) if folder.is_dir() else []:
  if p.is_file() and p.suffix in ('.json','.log'):
   raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),passed_execution=bool(not error and value and value['passed_execution']),original_parent=value,
 wrapper_error=error,original_parent_stdout=capture.getvalue(),full_UTF8=texts,model_copies=0,artifact_transfers=0,GUI=False)))'''

def main():
 assert sys.version_info[:2]==(3,14),'Existing Py314 compression.zstd transport required'
 p=argparse.ArgumentParser()
 for k in ('closing','new-cpu','authority-binding','auth-provider'):p.add_argument('--'+k,type=Path,required=True)
 for k in ('root-lease-label','run-id','purpose-id','remote-job-root','GPU-UUID','additional-control-pattern','source-index-SHA'):p.add_argument('--'+k,required=True)
 a=p.parse_args();closed,cr=metadata(a.closing);cpu,qr=metadata(a.new_cpu);qualified(closed,cpu,qr['SHA']);binding,br=metadata(a.authority_binding)
 assert binding['run_id']==KNOWN235_RUN and a.root_lease_label.startswith('ROOT_W35_LATEST32_EXCLUSIVE_') and a.additional_control_pattern
 assert H(N/INDEX)==a.source_index_SHA
 for r in read(N/INDEX)['files']:
  q=Path(r['path']);assert q.suffix in ('.py','.json','.md') and q.stat().st_size==r['bytes'] and H(q)==r['SHA']
 assert read(R/'CPU_LATEST32_NEW_INTERFACE_ACTUAL.json')['passed']
 job=PurePosixPath(a.remote_job_root);assert job.is_absolute() and job.is_relative_to('/home/lc01/Zonglin Li/zonglin2/tasks')
 pattern='run_ROOT_latest32481_|run_ROOT222_|launch_e2_solo_|collect_e2_solo_|review_e2_solo_|launch227D_|collect227D_|'+a.additional_control_pattern
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern.replace("'","''")+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 cim=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(cim.stdout) if cim.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT_LATEST32_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),passed=True,PID=os.getpid(),rows=rows))
 put('ROOT_LATEST32_ONCE_BEFORE_NETWORK.json',dict(epoch=time.time(),run_id=a.run_id,purpose_id=a.purpose_id,source_refs=[cr,qr,br],
  selected_model_new_byte_decode=[1,1],local_model_asset_raw_reads=0,case_controls_max=1600,worker_seconds=3600,parent_seconds=3780,new_GO=False,account_writes=0))
 wrapper=module('latest32_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 text=(N/'target_latest32_parent_ROOT_ONLY.py').read_text(encoding='utf8');tree=ast.parse(text)
 audit=ast.get_source_segment(text,next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='audit_current'))
 authargs=dict(contract_source=(N/'contract_latest32.py').read_text(encoding='utf8'),audit_source=audit,binding=binding,GPU_UUID=a.GPU_UUID)
 client=transport=previous=secret=None;actual=None
 try:
  transport,previous=wrapper.install();sec=module('latest32_memory_auth',a.auth_provider);secret=sec.recover();client=d.connect72(secret)
  put('ROOT_LATEST32_FRESH72_EXACT235_OR_CLOSED_CNONE_THEN_CLOSE72.json',d.code(client,d.PY72,AUTH,authargs,timeout=45));client.close();client=None
  staging=N/'ROOT_LATEST32_ACTUAL_SOURCE_TASK_STAGING'
  command=[sys.executable,'-B','-X','utf8',str(N/'make_latest32_Task_SOURCE_ONLY.py'),
   '--closing',str(a.closing),'--new-cpu',str(a.new_cpu),'--authority-binding',str(a.authority_binding),
   '--run-id',a.run_id,'--purpose-id',a.purpose_id,'--GPU-UUID',a.GPU_UUID,'--sdk-python',d.PY72,'--out-new',str(staging)]
  made=subprocess.run(command,capture_output=True,text=True,encoding='utf8');put('ROOT_LATEST32_REAL_METADATA_TASK_GENERATOR_RETURNED.json',dict(returncode=made.returncode,stdout=made.stdout,stderr=made.stderr));assert made.returncode==0
  pack=read(staging/'PACKAGE_LATEST32_SOURCE_AND_TASK.json')
  client=d.connect72(secret);secret=None
  create="from pathlib import Path\nimport json\nB=Path(v['job']);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());B.mkdir(parents=True,exist_ok=False)\nprint(json.dumps(dict(passed=True,new_job=str(B),model_copies=0)))"
  put('ROOT_LATEST32_NEW_UNUSED_NAMESPACE.json',d.code(client,d.PY72,create,dict(job=str(job)),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for r in pack['files']+[dict(relative='PACKAGE_LATEST32_SOURCE_AND_TASK.json')]:stage(sf,str(job/r['relative']),(staging/r['relative']).read_bytes())
  finally:sf.close()
  actual=d.code(client,d.PY72,EXEC,dict(job=str(job),files=pack['files']),timeout=3900)
  put('ROOT_LATEST32_ORIGINAL_METADATA_AND_FULL32S_CASE_RETURNED.json',actual)
  value=actual.get('original_parent') or {};result=value.get('result') or {}
  print(json.dumps(dict(passed_execution=actual['passed_execution'],complete32s=value.get('complete32s'),controls=result.get('controls'),seconds=result.get('seconds'),facts=result.get('facts'),wrapper_error=actual.get('wrapper_error'))),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT_LATEST32_ALL_SSH_CLOSED_SESSION_RESTORED.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,
   global_serial_control_client_lease='FREE',SDK_child_and_physical_EX_free='Use actual original parent wait/release receipts;UNKNOWN on transport exception',no_signals_or_automatic_retry=True))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT_LATEST32_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
