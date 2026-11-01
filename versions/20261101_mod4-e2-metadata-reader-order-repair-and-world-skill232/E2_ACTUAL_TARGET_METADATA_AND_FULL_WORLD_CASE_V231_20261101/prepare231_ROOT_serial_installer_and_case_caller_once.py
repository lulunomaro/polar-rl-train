from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';S=N/'source'
def read(p):return json.loads(p.read_bytes())
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
V=T/'E2_TARGET_METADATA_TYPED_EVIDENCE_SOURCE_FROM226_V2_20261101';idx=V/'INDEX_E2_FROM226_V2_FROZEN.json'
assert H(idx)=='ffb3521be10662e643d19e19ddf838516939079a81bf9eb0694afef5c732cd87'
for x in read(idx)['files']:
 p=Path(x['path'])if'path'in x else V/x['relative'];assert p.stat().st_size==x['bytes'] and H(p)==x['SHA']
rows=read(next((T/'E2_QUALIFIED_METADATA_TASK_READY_SOURCE_V226_20261101').rglob('INSTALL226_EXACT_SOURCE_BINDINGS.json')))['files']
extras=[]
for name in ('contract_e2_from226.py','run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py','finalize_e2_from226_actual_evidence_ROOT_ONLY.py'):
 p=V/name;extras.append(dict(relative=name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)))
E=T/'E2_QUALIFIED_METADATA_TASK_READY_SOURCE_V226_20261101'
for name in ('EXPECTED226_TARGET_METADATA.json','FROZEN_CASE_TASK_PENDING226.json'):
 p=next(E.rglob(name));extras.append(dict(relative=name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)))
for p in sorted(S.iterdir()):
 if p.suffix in('.json','.py'):extras.append(dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)))
bp=T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/reports/KNOWN_ACTIVE227D_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json'
binding=read(bp);p=S/'EXPECTED227D_BINDING.json';p.write_text(json.dumps(binding,indent=2),encoding='utf8');extras.append(dict(relative=p.name,local_path=str(p),bytes=p.stat().st_size,SHA=H(p)))
assert len({r['relative']for r in rows+extras})==len(rows)+len(extras) and not any(Path(x['relative']).suffix=='.pt'for x in rows+extras)
pack=dict(original226=rows,extras=extras,metadata_V2_INDEX_SHA=H(idx));(S/'INSTALL231_FROZEN.json').write_text(json.dumps(pack,indent=2),encoding='utf8')
caller=r'''from pathlib import Path
import ast,contextlib,hashlib,importlib.util,io,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';S=N/'source'
J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E2_FULL_WORLD_METADATA_CASE231_20261101/case'
def read(p):return json.loads(Path(p).read_bytes())
def put(name,v):
 with(R/name).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sys.modules[name]=m;sp.loader.exec_module(m);return m
POSTCOPY=r"""from pathlib import Path
import hashlib,json,time
B=Path(v['job'])
for r in v['files']:
 p=B/r['relative'];assert p.resolve().is_relative_to(B.resolve()) and p.suffix!='.pt' and p.stat().st_size==r['bytes']
 with p.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==r['SHA'],str(p)
value=dict(epoch=time.time(),actual_postcopy_fullSHA_verified=True,job_root=str(B),files=v['original226'],selected_formal_bytes_copies_hash_stat=0)
for name in('E2_INSTALLED226_SOURCE_ASSET_PRODUCER_RECEIPT.json','SOURCE_INSTALL231_ACTUAL.json'):
 with(B/name).open('x',encoding='utf8')as f:json.dump(value,f,indent=2)
print(json.dumps(dict(passed=True,files=len(v['files']),all_postcopy_once=True,old_model_bytes_stat_hash_copy=0)))
"""
EXEC=r"""from pathlib import Path
import contextlib,hashlib,io,json,runpy,sys,time,traceback
B=Path(v['job']);sys.path.insert(0,str(B));capture=io.StringIO();error=None
try:
 sys.argv=[str(B/'target231_E2_metadata_and_case_parent.py'),'--job-root',str(B),'--purpose-id',v['purpose'],'--sdk-python',v['python']]
 with contextlib.redirect_stdout(capture):runpy.run_path(sys.argv[0],run_name='__main__')
except BaseException:error=traceback.format_exc()
if error:
 with(B/'ROOT231_ORIGINAL_REMOTE_WRAPPER_ERROR.json').open('x',encoding='utf8')as f:json.dump(dict(error=error,no_auto_retry=True),f,indent=2)
texts=[];artifacts=[]
selected=[p for p in B.iterdir()if p.is_file()and(p.name.startswith(('ACTUAL231','E2_FROM226','E2_TARGET','FROZEN_CASE_TASK','METADATA226','ORIGINAL226','ROOT231','E2_NEW86')))]
O=B/'frozen_regression'
if O.is_dir():selected+=list(O.rglob('*'))
for p in sorted(set(selected)):
 if not p.is_file():continue
 if p.suffix in('.json','.log','.txt'):
  raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
 elif p.suffix in('.pt','.jsonl','.npz','.npy','.usd','.usda'):artifacts.append(dict(path=str(p),bytes=p.stat().st_size,SHA='unknown_unless_existing_producer_report',content_read_for_collection=False))
returned=B/'ACTUAL231_PARENT_RETURNED.json';parent=json.loads(returned.read_bytes())if returned.is_file()else None
bounded=O/'BOUNDED_FROZEN_E2_N20K_PROFILES_ACTUAL.json';result=json.loads(bounded.read_bytes())if bounded.is_file()else None
print(json.dumps(dict(epoch=time.time(),passed_execution=not error and bool(parent and parent['passed_execution']),wrapper_error=error,parent=parent,bounded_case=result,full_UTF8=texts,artifacts_metadata_only=artifacts,stdout=capture.getvalue(),no_new_learning_GO_or_account_write=True)))
"""
def main():
 pack=read(S/'INSTALL231_FROZEN.json');plan=read(S/'PLAN231.json');expected=read(S/'EXPECTED227D_BINDING.json')
 assert read(T/'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/D_BEFORE_USE_CWD_REPAIR_SOURCE/reports/ROOT227D_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 query=r"""Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'run_ROOT231_E2_|launch227|collect227|review227|run_ROOT230|run_ROOT229|run_ROOT228|run_ROOT223' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"""
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);x=json.loads(q.stdout)if q.stdout.strip()else[];x=x if isinstance(x,list)else[x]
 own=[r for r in x if r['ProcessId']==os.getpid()];other=[r for r in x if r['ProcessId']!=os.getpid()]
 put('ROOT231_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=x,other=other))
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')
 for r in pack['extras']:
  p=Path(r['local_path']);raw=p.read_bytes();assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA']
  if p.suffix=='.py':ast.parse(raw)
 put('ROOT231_ONCE_NEW_E2_NECESSARY_PURPOSE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),plan=plan,metadata_V2=pack['metadata_V2_INDEX_SHA'],original226_source_asset_transfer_postcopy_once=True,selected_model_symlink_only=True,worker_new_model_byte_hash_decode=1,old_model_CPU_read=0,physical_state_and_learning_unchanged=True,model_read_NOT_for_Git=True))
 wrapper=module('case231_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('case231_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret)
  auth=(S/'authority231.py').read_text('utf8')+"\nprint(json.dumps(fresh_authority(v['expected'])))"
  put('ROOT231_FRESH227D_AUTHORITY_READONLY_BEFORE_TARGET_ACTUAL.json',d.code(client,d.PY72,auth,dict(expected=expected),timeout=45))
  client.close();client=None;client=d.connect72(secret);secret=None
  create="from pathlib import Path\nimport json\np=Path(v['job']);assert p.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());p.mkdir(parents=True,exist_ok=False)\nprint(json.dumps(dict(passed=True,new_root=str(p))))"
  put('ROOT231_NEW_UNUSED_TARGET_NAMESPACE_ACTUAL.json',d.code(client,d.PY72,create,dict(job=J),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for r in pack['original226']+pack['extras']:
    cur=J
    for bit in r['relative'].split('/')[:-1]:
     cur+='/'+bit
     try:sf.mkdir(cur)
     except OSError:sf.stat(cur)
    sf.put(r['local_path'],J+'/'+r['relative'])
  finally:sf.close()
  put('ROOT231_SOURCE_ASSET_INSTALL_POSTCOPY_ACTUAL.json',d.code(client,d.PY72,POSTCOPY,dict(job=J,files=pack['original226']+pack['extras'],original226=pack['original226']),timeout=180))
  actual=d.code(client,d.PY72,EXEC,dict(job=J,purpose=plan['purpose_id'],python=d.PY72),timeout=2400)
  put('ROOT231_ACTUAL_E2_METADATA_AND_ORIGINAL_MEAN_CASE_RETURNED.json',actual)
  print(json.dumps(dict(passed_execution=actual['passed_execution'],wrapper_error=actual['wrapper_error'],bounded_case=actual['bounded_case'],parent=actual['parent'])),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT231_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT231_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise
'''
ast.parse(caller)
p=N/'run_ROOT231_E2_actual_metadata_and_mean_case_once.py';assert not p.exists();p.write_text(caller,encoding='utf8')
for name in('POSTCOPY','EXEC'):
 tree=ast.parse(caller)
 for node in tree.body:
  if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in node.targets):ast.parse(ast.literal_eval(node.value))
(R/'ROOT231_SELECTED_V2_AND_REMOTE_AST_BEFORE_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),passed=True,selected_metadata_V2_INDEX_SHA=H(idx),remote_AST=2,Root_parent_AST=True,signal_calls=0,model_asset_or_network_access=0),indent=2),encoding='utf8')
print(json.dumps(dict(passed=True,caller=str(p),original_rows=len(rows),extras=len(extras))))
