from pathlib import Path
import ast,getpass,hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';W=B.parent;N=W/'MOD4_TWO_LINUX_POLICY50_COHORT_50_20261021';sys.path.insert(0,str(N));import deploy_two50_reconciled_original_writer_once as d
s=importlib.util.spec_from_file_location('memory',B/'run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory)
REMOTE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,signal,subprocess,time
base=Path(v['base']);old=Path(v['old']);owned=Path('/home/lc01/Zonglin Li/zonglin2');uuid='GPU-16828f91-2b45-b646-8dc0-9481138e2842';assert base.resolve().is_relative_to((owned/'tasks').resolve()) and not base.exists();q=json.loads((old/'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').read_bytes());assert q['passed_CPU_only'] and q['source_SHA']==v['source_SHA'];lock=(owned/'state/MOD4_H1_SHARED_FROZEN_EVAL_20261021.lock').open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
with (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if uuid in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
base.mkdir(parents=True);(base/'job0').mkdir();shutil.copytree(old/'lib',base/'lib');shutil.copytree(old/'job0/runtime',base/'job0/runtime');shutil.copytree(old/'job0/assets',base/'job0/assets');shutil.copy2(old/'job0/original_run_manifest.json',base/'job0/original_run_manifest.json');shutil.copy2(old/'job0/source'/v['source_filename'],base/'job0/source.pt');assert hashlib.sha256((base/'job0/source.pt').read_bytes()).hexdigest()==v['source_SHA'];(base/'worker.py').write_text(v['worker'],encoding='utf8');config=dict(source_SHA=v['source_SHA'],source_Adam=v['source_Adam'],explicit_coexist_authority='虽然被占用但是有余量，跑评测不需要太高的性能就能跑。所以可以跑评测',no_training_or_peer_mutation=True);(base/'FROZEN_DIAGNOSTIC_CONFIG.json').write_text(json.dumps(config,indent=2));env=dict(os.environ,CUDA_VISIBLE_DEVICES=uuid,CUDA_DEVICE_ORDER='PCI_BUS_ID',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');start=time.time()
with (base/'WORKER_FULL.log').open('xb') as log:
 p=subprocess.Popen([v['python'],'-u','-B',str(base/'worker.py'),'--steps','60'],cwd=base,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);identity=dict(pid=p.pid,creation=psutil.Process(p.pid).create_time(),argv=psutil.Process(p.pid).cmdline());(base/'PARENT_STARTED_ACTUAL.json').write_text(json.dumps(dict(epoch=time.time(),identity=identity,GPU_line=line,coexist_user_authorized=True,only_own_eval_lease_held=True,original_training_private_locks_untouched=True)))
 try:rc=p.wait(timeout=420)
 except subprocess.TimeoutExpired:
  assert psutil.Process(p.pid).create_time()==identity['creation'];p.send_signal(signal.SIGINT);rc=p.wait(timeout=60)
final=base/'out/FINAL.json';value=json.loads(final.read_bytes()) if final.exists() else None;receipt=dict(epoch=time.time(),root=str(base),identity=identity,actual_child_waited=True,actual_returncode=rc,elapsed=time.time()-start,GPU_line=line,final=value,original_error_paths=[str(p) for p in (base/'out').glob('*ORIGINAL_ERROR*.json')],no_PPO_no_canonical_write=True,eval_GPU_shared_explicitly_authorized=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close();receipt['own_eval_lock_released']=True;(base/'PARENT_RETURNED_ACTUAL.json').write_text(json.dumps(receipt,indent=2));receipt['texts']=[dict(path=str(p),relative=p.relative_to(base).as_posix(),bytes=p.stat().st_size) for p in base.rglob('*') if p.is_file() and p.suffix in ('.json','.log') and '/job0/runtime/' not in str(p)];receipt['raw']=[dict(path=str(p),relative=p.relative_to(base).as_posix(),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (base/'out').glob('*.npz')];print(json.dumps(receipt))
'''
try:
 worker=B/'shared_H1_frozen50_diagnostic_worker_V2.py';tree=ast.parse(worker.read_text('utf8'));assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in ('OnPolicyRunner','PPO','Adam','SGD') for n in ast.walk(tree));q=json.loads((N/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());spec=q['specs']['recovery'];src=q['sources']['recovery'];
 with (R/'SHARED_H1_NATIVE13_V2_SOURCE_AST_AND_AUTHORITY_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_source_AST=True,source_SHA=src['SHA'],source_Adam=src['Adam'],worker_SHA=hashlib.sha256(worker.read_bytes()).hexdigest(),new_human_coexist_authority=True,no_optimizer_constructor_in_source=True,fresh13_diagnostic_only=True,native_steps=60,native_callbacks=480,not_full104_or_skill_admission=True),f,indent=2)
 secret=memory.recover();c=d.connect72(secret);secret=None
 try:
  v=d.code(c,d.PY72,REMOTE,dict(base='/home/lc01/Zonglin Li/zonglin2/tasks/H1shared_eval50_2110v2',old=q['roots']['recovery'],source_filename=spec['source_filename'],source_SHA=src['SHA'],source_Adam=src['Adam'],worker=worker.read_text('utf8'),python=spec['python']),timeout=510)
  local=B/'shared_H1_native13_V2_actual';local.mkdir();sf=c.open_sftp();sf.get_channel().settimeout(90)
  try:
   for row in v['texts']+v['raw']:
    p=local/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes']
    if row.get('SHA'):assert hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
  finally:sf.close()
 finally:c.close()
 with (R/'SHARED_H1_NATIVE13_V2_FINITE_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(actual_finite_returned=True,returncode=v['actual_returncode'],final=v['final'],errors=v['original_error_paths'])))
except BaseException:
 with (R/'SHARED_H1_NATIVE13_V2_DEPLOY_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_automatic_replay=True),f)
 raise
