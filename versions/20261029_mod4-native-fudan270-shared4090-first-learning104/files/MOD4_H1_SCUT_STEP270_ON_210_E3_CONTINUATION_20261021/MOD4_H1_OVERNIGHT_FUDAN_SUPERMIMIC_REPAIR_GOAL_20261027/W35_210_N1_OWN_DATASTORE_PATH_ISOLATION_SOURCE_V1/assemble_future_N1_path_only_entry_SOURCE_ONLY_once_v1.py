"""Generate a future N1 finite from frozen interfaces; metadata/source reads only."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent
def H(x):return hashlib.sha256(x).hexdigest()
def literal(path,name):
 tree=ast.parse(path.read_bytes())
 return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
TEMPLATE=r'''"""UNUSED path-only N1; original asset/physics/assertions, no policy/model."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,sys,threading,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
OLD='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED40050_FROZEN_PROFILES_20261028v2/w35'
NEW='/mnt/mod4_linux_durable_20261013/MOD4_W35_N1_OWN_DATASTORE_PATH_20261029v1/w35'
GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
__SOURCE_CODE_CONSTANTS__
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,v):
 R.mkdir(exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--known72-binding-json',type=Path);a=p.parse_args();index=json.loads((B/'FROZEN_W35_OWN_DATASTORE_PATH_N1_SOURCE_INDEX_V1.json').read_bytes())
 for name,want in index['executable_source_SHAs'].items():assert H(B/name)==want,name
 known=json.loads(a.known72_binding_json.read_bytes()) if a.known72_binding_json else None
 if known is not None:assert set(known)=={'owner','run_id','go'}
 put('OWN_DATASTORE_N1_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),scope='one N1 candidate, no cooking boolean toggle',maximum_local_control_seconds=420,no_model_actor_optimizer_or_GO=True));deadline=time.monotonic()+420
 manifest=json.loads((L/'W35_210_V2_PRECLOSE_EXCEPTION_DIAGNOSTIC_SOURCE_V1/W35_V2_PRECLOSE_COMPLETE_INPUT_MANIFEST.json').read_bytes());actual=json.loads((L/'W35_210_V2_PRECLOSE_EXCEPTION_DIAGNOSTIC_SOURCE_V1/reports/NEW_W35_V2_SOURCE_SDK_AND_FINITE_DIAGNOSTIC_DETACHED_RETURNED_ACTUAL.json').read_bytes())
 wrapper=module('N1_owned_storage_same_compressed_memory_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sec=module('N1_owned_storage_same72_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;sf=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_FINITE_W35_N1_OWN_DATASTORE_PATH',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 def run(py,code,args,seconds):
  remaining=deadline-time.monotonic();assert remaining>0;return d.code(client,py,code,args,timeout=min(seconds,remaining))
 try:
  client=d.connect72(secret);secret=None;put('KNOWN_ORIGINAL72_AUTHORITY_READONLY_ACTUAL.json',run(d.PY72,AUTH,dict(known_binding=known),30));client.close();client=None
  client=route.connect();put('FRESH_PREVIOUS_V2_KNOWN_OWNOUT_ACTUAL.json',run(route.PY,PRE_OWN,dict(old=OLD,supervisor=actual['identity']),20));put('FRESH_USER_LIGHT_RESOURCE_MOUNT_ACTUAL.json',run(route.PY,PRE,dict(job=NEW,GPU=GPU),30))
  rows=[r for r in manifest['files'] if (r['relative'].startswith(('runtime/','lib/')) or r['relative']=='original_run_manifest.json') and r['relative']!='lib/zonglin2_app_launcher.py'];put('EXACT_ORIGINAL_RUNTIME_COPY_EXCEPT_NEW_STORAGE_LAUNCHER_ACTUAL.json',run(route.PY,COPY,dict(old=OLD,new=NEW,rows=rows),60))
  sf=client.open_sftp();sf.get_channel().settimeout(30)
  try:sf.stat(NEW+'/lib')
  except FileNotFoundError:sf.mkdir(NEW+'/lib',mode=0o700)
  for name,relative in [('diagnose_original_W35_N1_asset_colliders_once.py','diagnose_original_W35_N1_asset_colliders_once.py'),('zonglin2_app_launcher.py','lib/zonglin2_app_launcher.py')]:
   with sf.open(NEW+'/'+relative,'wx') as f:f.write((B/name).read_bytes())
  sf.close();sf=None
  assert deadline-time.monotonic()>245,'Do not start GPU N1 without original own-worker wait reserve'
  value=run(route.PY,RUN,dict(new=NEW,GPU=GPU,python=route.PY,worker_SHA=H(B/'diagnose_original_W35_N1_asset_colliders_once.py')),245);put('N1_OWN_DATASTORE_PATH_ORIGINAL_ASSERTION_OR_ERROR_RETURNED_ACTUAL.json',value);print(json.dumps({k:v for k,v in value.items() if k!='complete_original_UTF8'}))
 finally:
  secret=None;stop.set();thread.join(1)
  if sf:sf.close()
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('N1_OWN_DATASTORE_PATH_ORIGINAL_LOCAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_retry=True));raise
'''
def main():
 old=L/'W35_210_N1_ASSET_COLLIDER_DIAGNOSTIC_SOURCE_V1/run_NEW_W35_210_N1_asset_only_original_assertion_UNUSED_once.py';assert H(old.read_bytes())=='9911b574d9677119a066a844df3e6f62d4db47fc8a6ee5217c7fc39f4eda34ff'
 parent=L/'W35_210_ADAPTED40050_N20K_BOUNDED_SKILL_REGRESSION_SOURCE_V1/install_admit_launch_detached_W35_210_frozen_profiles_UNUSED_once_v1.py'
 auth=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/upload_and_admit_NEW86_normal_H1_wholeCPU_native24_secure_stdin_UNUSED_once_v2_user_light_GPU.py';assert H(auth.read_bytes())=='4e9bc93f9433a6da245e40bbfd3f84326d08e831b27ec9f9de4c71c334c4e14b'
 constants={k:literal(old,k) for k in ('PRE_OWN','COPY','RUN')};constants['AUTH']=literal(auth,'AUTH');pre=literal(parent,'PRE');run=constants['RUN']
 a=";assert v['GPU'] not in apps,'selected GPU compute busy: left untouched'";assert pre.count(a)==1;pre=pre.replace(a,'')
 a="int(a[2])>15669";b="int(a[2])>15669 and int(a[3])<=30";assert pre.count(a)==1;pre=pre.replace(a,b)
 # Metadata must say actual observed UUID rows, not the old zero-compute claim.
 assert pre.count('selected_compute_UUID_rows=0')==1;pre=pre.replace('selected_compute_UUID_rows=0','selected_compute_UUID_rows=apps.splitlines(),user_light_occupancy_util_at_most30=True')
 a="assert GPU not in apps and row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669";b="assert row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669 and int(row[3])<=30";assert run.count(a)==1;run=run.replace(a,b);constants['PRE']=pre;constants['RUN']=run
 for code in constants.values():ast.parse(code)
 text=TEMPLATE.replace('__SOURCE_CODE_CONSTANTS__','\n'.join(k+'='+repr(v) for k,v in constants.items()));ast.parse(text);entry=B/'run_NEW_W35_210_N1_owned_datastore_path_candidate_UNUSED_once_v1.py';assert not entry.exists();entry.write_text(text,encoding='utf8');(B/'reports').mkdir(exist_ok=True)
 # No source/manifold/cache content is inspected beyond existing saved text.
 launcher=ast.parse((B/'zonglin2_app_launcher.py').read_bytes());extra=next(n.value for n in ast.walk(launcher) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Subscript) and isinstance(t.slice,ast.Constant) and t.slice.value=='extra_args' for t in n.targets));strings=[n.value for n in ast.walk(extra) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
 assert '--portable-root' in strings and not any(x.startswith(('--clear','--reset','--/physics/','--/UJITSO/forceBuilds')) for x in strings)
 names=('run_NEW_W35_210_N1_owned_datastore_path_candidate_UNUSED_once_v1.py','diagnose_original_W35_N1_asset_colliders_once.py','zonglin2_app_launcher.py');shas={name:H((B/name).read_bytes()) for name in names}
 proof=dict(epoch=time.time(),source_AST_and_embedded_remote_AST_passed=True,original_N1_and_original_MildDR_mesh_force_solver_assertions_retained=True,own_new_paths_only=True,old_cache_not_read_copied_cleared_or_deleted=True,no_cooking_boolean_or_forceBuilds_toggle=True,official_portable_root_userConfigPath_and_localCachePath_only=True,user_light_free15669_util30_bound=True,original_globalCanonical_not_written=True,all_execution_pending=True,no_model_RAW_USD_NPZ_or_remote_reads=True)
 (B/'N1_OWN_STORAGE_SOURCE_AST_AND_SCOPE_ONLY_ACTUAL.json').write_text(json.dumps(proof,indent=2)+'\n')
 index=dict(status='FROZEN_UNUSED_SOURCE_ONLY_N1_STORAGE_PATH_CANDIDATE',epoch=time.time(),entry=str(entry),entry_SHA=shas[entry.name],executable_source_SHAs=shas,previous_actual_N1_source_SHA=H(old.read_bytes()),new_namespace='/mnt/mod4_linux_durable_20261013/MOD4_W35_N1_OWN_DATASTORE_PATH_20261029v1/w35',original_worker_max180s_cleanup30plus15=True,maximum_local_control_seconds=420,source_proof=proof,no_actual_candidate_validation_or_skill_claim=True,Git='root ordinary pending, no trial/tag by child')
 out=B/'FROZEN_W35_OWN_DATASTORE_PATH_N1_SOURCE_INDEX_V1.json';out.write_text(json.dumps(index,indent=2)+'\n');print(json.dumps(dict(entry=str(entry),entry_SHA=index['entry_SHA'],index=str(out),index_SHA=H(out.read_bytes()),source_only=True)))
if __name__=='__main__':main()
