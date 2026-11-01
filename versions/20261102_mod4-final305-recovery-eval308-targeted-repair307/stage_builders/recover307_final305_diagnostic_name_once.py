"""Recover saved final305 after exact diagnostic ERROR-name false classification."""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;O=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101'
N=T/'FINAL305_DIAGNOSTIC_NAME_RECOVERY_V307_20261102';N.mkdir(exist_ok=False);R=N/'reports';R.mkdir()
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,x):
 with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
try:
 complete=json.loads((O/'reports/ROOT305_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());role=complete['roles']['jump_72'];closed=complete['owner_closed'];final=role['final'];task=json.loads((O/'TASK305_FROZEN.json').read_bytes())
 assert closed['passed']and closed['canonical_None']and closed['shared_locks_free']and role['private_EX_free']and role['node_out_or_nonexecuting_original_zombie']and not complete['formals']
 assert role['original_node_terminal']['row']['returncode']==0 and role['original_node_exit']['all_own_children_waited']and role['original_node_exit']['private_EX_released']
 diagnostic=task['job_root']+'/production/ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json'
 assert role['errors']==[diagnostic]
 files={Path(x['path']).name:json.loads(x['UTF8'])for x in role['full_UTF8']if x['path'].endswith('.json')}
 assert files[Path(diagnostic).name]['passed']and files['ENV276_CLOSE_RETURNED.json']['closed']
 assert 'ORIGINAL_ERROR.json'not in files and 'ERROR_SAVE_ORIGINAL_ERROR.json'not in files
 module('p305',O/'teacher_task305.py').validate_final(final,task,final['original_finite_owner_GO'])
 assert 'ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json'in files['NODE_ORIGINAL_ERROR.json']['error']
 patterns='recover307_|collect305_|launch305_|review305_|run306_eval|postround306_finalize|run303_eval|collect300_|run_ROOT|launch297_|collect297_|collect292_'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+patterns+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 4 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['CreationDate']and rows[0]['ExecutablePath'].lower()==sys.executable.lower()
 put('ROOT307_FRESH_EXACT_LOCAL_CIM.json',dict(epoch=time.time(),rows=rows,lease='FREE'))
 put('ROOT307_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),purpose='First transfer exactfinal305 denied by diagnosticfilenameonly; no retrain/normalrerun/accountwrites',source_final=final['final'],original_classification=False,exact_false_positive=diagnostic,originalfee=closed['raw_fee_sum_once']))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 transport=previous=client=secret=None
 try:
  transport,previous=module('t307',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
  secret=module('a307',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import fcntl,hashlib,json,psutil,time
B=Path(v['task']['job_root']);C=B/'control305';O=Path(v['task']['owner_root']);locks=[]
try:
 for path in(v['private_lock'],'/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'):
  f=Path(path).open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
 c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment']is None
 for path in(O/'OWNER_IDENTITY.json',C/'NODE_IDENTITY.json',C/'WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json'):
  row=json.loads(path.read_bytes())
  try:p=psutil.Process(row['pid']);assert p.create_time()!=row['creation']or p.status()==psutil.STATUS_ZOMBIE
  except psutil.NoSuchProcess:pass
 assert json.loads((C/'NODE_EXIT_ACTUAL.json').read_bytes())['all_own_children_waited']
 final=json.loads((B/'production/FINAL.json').read_bytes());assert final==v['final']
 actualerrors=[p.name for p in(B/'production').glob('*ERROR*.json')];assert actualerrors==['ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json']
 assert json.loads((B/'production'/actualerrors[0]).read_bytes())['passed']
 p=Path(final['final']['path']);assert p.stat().st_size==final['final']['bytes']
 with p.open('rb')as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==final['final']['SHA']
 print(json.dumps(dict(epoch=time.time(),passed=True,originalowner_node_workerout_or_nonexecuting=True,canonical_None=True,private_shared_EX=True,filename_false_positive_exact=actualerrors,final=final,bytes=p.stat().st_size,SHA=sha,accountwrites=0,original_classification_preserved=False)))
finally:
 for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
"""
  private=json.loads((O/'reports/ROOT305_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())['specs']['jump_72']['private_lock']
  result=d.code(client,d.PY72,code,dict(task=task,final=final,private_lock=private),timeout=90);put('ROOT307_EXACT_FINAL_OWN_CLOSURE_AND_DIAGNOSTIC_CLASSIFICATION.json',result)
  dest=N/'models/final305_complete.pt';dest.parent.mkdir();sf=client.open_sftp()
  try:sf.get(final['final']['path'],str(dest))
  finally:sf.close()
  assert dest.stat().st_size==final['final']['bytes']and H(dest)==final['final']['SHA']
  put('ROOT307_NEW_FINAL305_SINGLE_TRANSFER.json',dict(epoch=time.time(),passed=True,path=str(dest),source=final['final']['path'],SHA=H(dest),bytes=dest.stat().st_size,transfers=1,twohostSHAequal=True,old_raw_false_unchanged=True,classification='independent recovery of complete final after exact diagnosticfilenamefalsepositive; original305qualifiedfalse retained',original_fee=closed['raw_fee_sum_once']))
  print(json.dumps(dict(passed=True,root=str(N),SHA=final['final']['SHA'],Pi=final['actual_new_Pi_updates'],WM=final['total_WM_updates'],transfer=1)),flush=True)
 finally:
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT307_ALL_SSH_CLOSED_FREE.json',dict(epoch=time.time(),all_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
except BaseException:
 put('ROOT307_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),once_consumed=True));raise
