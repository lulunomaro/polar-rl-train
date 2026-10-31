"""One serial finite for two NEW zero-yaw evaluations. No learning/ledger writes."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,posixpath,subprocess,sys,time,traceback
B=Path(__file__).resolve().parent;T=B.parent;W=T.parent;R=B/'reports'
ROOT='/mnt/mod4_linux_durable_20261013/MOD4_PRIMARY_E0_EVAL_ONLY_ZERO_YAW_20261031v207'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'run207_zero_yaw_two_qualified_models_once|inspect206_original_training_unread_log_ranges_once|install_evaluate201_E0_final32066_same_plane_once|install_capture200_final197_literal_jump_plane_once|collect197_original_two_role_formals|launch197_unified_194_remaining' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 x=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(x.stdout) if x.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[r for r in rows if r['ProcessId']==os.getpid()];others=[r for r in rows if r['ProcessId']!=os.getpid()]
 put('ROOT207_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,exact_CIM=rows))
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 manifest=json.loads((B/'FROZEN207_TWO_QUALIFIED_MODELS_ZERO_YAW_MANIFEST.json').read_bytes())
 for row in manifest['files']:
  raw=(B/row['local_relative']).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
 post=(B/'remote207_two_zero_yaw_cases.txt').read_text('utf8');ast.parse(post)
 put('ROOT207_TWO_ZERO_YAW_PURPOSE_CONSUMED.json',dict(epoch=time.time(),roles=list(manifest['roles']),model_GPU_reads=2,model_GPU_decodes=2,old_input_models_raw_NPZ_reads=0,source_POST_SHA=hashlib.sha256(post.encode('utf8')).hexdigest(),no_training_or_account_write=True,no_replay_or_auto_retry=True))
 wrapper=module('eval207_session',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('eval207_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  auth="""from pathlib import Path
import hashlib,json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment'] is None
print(json.dumps(dict(epoch=time.time(),CNone=True,SHA=hashlib.sha256(raw).hexdigest(),readonly=True)))"""
  try:put('ROOT207_FRESH72_CNONE_READONLY.json',d.code(client,d.PY72,auth,{},timeout=45))
  finally:client.close();client=None
  client=route.connect()
  pre="""from pathlib import Path
import json,subprocess
b=Path(v['root']);assert str(b)=='/mnt/mod4_linux_durable_20261013/MOD4_PRIMARY_E0_EVAL_ONLY_ZERO_YAW_20261031v207'
m=json.loads(subprocess.check_output(['findmnt','--json','--target','/mnt/mod4_linux_durable_20261013','-o','UUID,OPTIONS'],text=True))['filesystems'][0]
assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',');b.mkdir(parents=True,exist_ok=False)
print(json.dumps(dict(passed=True,root=str(b),UUID_rw=m)))"""
  put('ROOT207_NEW_DURABLE_UUID_RW_NAMESPACE.json',d.code(client,route.PY,pre,dict(root=ROOT),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   made=set()
   for row in manifest['files']:
    cur=ROOT
    for bit in posixpath.dirname(row['relative']).split('/'):
     if not bit:continue
     cur+='/'+bit
     if cur not in made:
      try:sf.mkdir(cur)
      except OSError:sf.stat(cur)
      made.add(cur)
    sf.put(str(B/row['local_relative']),ROOT+'/'+row['relative'])
  finally:sf.close()
  actual=d.code(client,route.PY,post,dict(root=ROOT,files=manifest['files']),timeout=1930)
  put('ROOT207_TWO_ORIGINAL_ZERO_YAW_CASES_RETURNED_ACTUAL.json',actual)
  print(json.dumps(dict(passed_execution=actual['passed_execution'],cases={k:dict(passed=v['passed'],controls=(v.get('case') or {}).get('controls'),metrics=(v.get('case') or {}).get('eval_only_zero_yaw'),terminal_flags=(v.get('case') or {}).get('terminal_flags')) for k,v in actual['cases'].items()},parent_error=actual['parent_error'])),flush=True)
 finally:
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT207_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT207_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
