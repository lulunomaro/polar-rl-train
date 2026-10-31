"""One human-requested current-status read. Not a watcher or early formal collector."""
from pathlib import Path
import importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'human196_194_one_saved_progress_status_once|collect194_original|start194_literal|install194_literal|install195_literal|start195_literal|collect195_original|run189_W35_saved_cycle|install_capture193_|install_evaluate191_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT196_STATUS_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),self_PID=os.getpid(),self_exe=sys.executable,self_argv=sys.argv,exact_CIM=rows))
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 binding=json.loads((R/'KNOWN_ACTIVE194_AUTHORITY_BINDING_FOR_FUTURE_SERIAL_READONLY.json').read_bytes())
 put('ROOT196_ONE_HUMAN_PROGRESS_READ_PURPOSE_CONSUMED.json',dict(epoch=time.time(),human='现在有成功跳跃的迹象吗',
  scope='One latest saved progress JSON plus existing FINAL/ORIGINAL_ERROR only; exact194 authority check first',
  maximum72_small_JSON_reads=3,maximum210_small_JSON_reads=3,maximum_local_seconds=180,
  model_raw_NPZ_SDK_or_GPU_reads=0,checkpoint_transfer_or_hash=0,normal_collector_calls=0,
  no_watcher_repeat_or_training_change=True,no_account_or_source_write=True))
 wrapper=module('status196_session',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 transport=None;previous=None;client=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('status196_memory_authority',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  auth="""from pathlib import Path
import json,time,hashlib
b=v['binding'];P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=P.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]
O=Path(b['owner']['root']);identity=json.loads((O/'OWNER_IDENTITY.json').read_bytes());current=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert identity['pid']==b['owner']['pid'] and identity['creation']==b['owner']['creation'] and current['go']==b['go']
a=c['active_segment'];matched=a is not None and a['owner_parent_pid']==b['owner']['pid']
assert a is None or matched,'A different current owner cannot use historical194 binding'
print(json.dumps(dict(epoch=time.time(),passed=True,exact194_owner_run_GO_matched=True,canonical_None=a is None,active194_at_this_read=matched,run_id=b['run_id'],canonical_SHA=hashlib.sha256(raw).hexdigest(),canonical_writes=0,small_JSON_reads=3)))"""
  try:authority=d.code(client,d.PY72,auth,dict(binding=binding),timeout=45);put('ROOT196_FRESH72_CURRENT194_AUTHORITY_READONLY.json',authority)
  finally:client.close();client=None
  client=route.connect()
  remote="""from pathlib import Path
import hashlib,json,os,time
B=Path('/mnt/mod4_linux_durable_20261013/MOD4_FUDAN_JUMP_LITERAL_PLANE40050_DR_TWO_HOUR_20261031v194/seed27/production')
rows=[]
for name in ('LATEST_PROGRESS.json','FINAL.json','ORIGINAL_ERROR.json'):
 p=B/name
 if not p.is_file():continue
 assert p.stat().st_size<100000
 with p.open('rb') as f:
  before=os.fstat(f.fileno());raw=f.read();after=os.fstat(f.fileno())
 assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and len(raw)==before.st_size
 rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),value=json.loads(raw),byte_reads=1))
print(json.dumps(dict(epoch=time.time(),files=rows,small_JSON_reads=len(rows),model_raw_NPZ_SDK_GPU_or_account_calls=0,no_remote_write=True)))"""
  current=d.code(client,route.PY,remote,{},timeout=45)
  report=dict(epoch=time.time(),purpose='Human asked now, one necessary current saved-progress read only',authority=authority,source210=current,
   no_watcher_or_early_formal_or_model_read=True,scope='Fudan contact-flight flags and root height are training diagnostics, not verified jump/landing/stable success')
  put('ROOT196_194_ONE_CURRENT_SAVED_PROGRESS_RETURNED_ACTUAL.json',report)
  for row in current['files']:
   print(json.dumps(dict(file=Path(row['path']).name,value=row['value']),ensure_ascii=False))
 finally:
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT196_STATUS_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT196_STATUS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
