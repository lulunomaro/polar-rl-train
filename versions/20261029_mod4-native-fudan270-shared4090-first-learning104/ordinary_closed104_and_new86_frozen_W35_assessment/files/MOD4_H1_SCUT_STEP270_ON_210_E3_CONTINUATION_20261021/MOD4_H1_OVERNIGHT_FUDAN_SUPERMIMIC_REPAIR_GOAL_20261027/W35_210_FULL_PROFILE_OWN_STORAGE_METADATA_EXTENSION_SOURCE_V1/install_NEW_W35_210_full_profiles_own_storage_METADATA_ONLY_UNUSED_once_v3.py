"""NEW input namespace; only worker preclose-error receipt changes, no physics."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,sys,threading,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
OLD='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED40050_FROZEN_PROFILES_20261028v1/w35'
NEW='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED92_FULL_PROFILES_OWN_STORAGE_20261029v3/w35'
COPY=r'''
from pathlib import Path
import hashlib,json,os,shutil,time
old=Path(v['old']);new=Path(v['new']);assert new.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013')) and new.is_dir() and not any(new.iterdir())
terminal=json.loads((old/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json').read_bytes());assert terminal['actual_worker_waited'] and terminal['returncode']==0 and not terminal['passed_frozen_execution'] and terminal['private_EX_released']
assert terminal['supervisor']==v['supervisor'] and terminal['worker']==v['worker']
def out(row):
 p=Path('/proc')/str(row['pid'])
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));created=boot+int(a[19])/os.sysconf('SC_CLK_TCK')
 except FileNotFoundError:return True
 return created!=row['creation'] or a[0]=='Z'
assert out(v['supervisor']) and out(v['worker']);assert json.loads((old/'ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json').read_bytes())['passed']
records=[]
for row in v['rows']:
 rel=row['relative']
 if rel in ('evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py','lib/zonglin2_app_launcher.py','detached_W35_frozen_eval_private210_supervisor_once_v1.py'):continue
 p=old/rel;q=new/rel;assert p.resolve().is_relative_to(old) and q.resolve().is_relative_to(new) and not p.is_symlink();before=p.stat();assert before.st_size==row['bytes'];q.parent.mkdir(parents=True,exist_ok=True)
 large=rel.endswith(('.pt','.npz')) or rel=='runtime/assets/source_700N/robot.usd'
 if large:os.link(p,q)
 else:
  raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA'];q.write_bytes(raw)
 after=p.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 records.append(dict(relative=rel,bytes=row['bytes'],producer_SHA=row['SHA'],large_readonly_input_same_inode=os.path.samestat(p.stat(),q.stat()) if large else False,old_bytes_unchanged=True))
print(json.dumps(dict(passed=True,records=records,original_failed_case_input_only_no_outputs_or_Task_copied=True,old_supervisor_worker_out=True,no_model_decode_or_cooking_or_physics_change=True)))
'''
PROOF=r'''
from pathlib import Path
import hashlib,json
old=Path(v['old'])/'evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py';new=Path(v['new'])/old.name;a=old.read_bytes();b=new.read_bytes();assert hashlib.sha256(a).hexdigest()==v['old_SHA'] and hashlib.sha256(b).hexdigest()==v['new_SHA'];needle=v['needle'].encode();replacement=v['replacement'].encode();assert a.count(needle)==1 and b.replace(replacement,needle)==a
print(json.dumps(dict(passed=True,exact_inverse_only_preclose_original_exception_persistence=True,no_physics_actions_task_or_restore_guard_change=True)))
'''
PRE="\nfrom pathlib import Path\nimport json,subprocess,shutil,psutil,time\nJ=Path(v['job']);mount=Path('/mnt/mod4_linux_durable_20261013');assert mount.is_mount() and not J.parent.exists() and J.resolve().is_relative_to(mount.resolve())\nm=json.loads(subprocess.check_output(['findmnt','--json','--target',str(mount),'-o','UUID,OPTIONS'],text=True))['filesystems'][0];assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',')\napps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True)\nline=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')];assert a[0]==v['GPU'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and int(a[3])<=30\nassert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(mount).free>25*1024**3\nJ.mkdir(parents=True,mode=0o700);print(json.dumps(dict(passed=True,epoch=time.time(),GPU_line=line,selected_compute_UUID_rows=apps.splitlines(),user_light_util_le30=True,no_unknown_PID_or_argv_read=True,mount=m,job=str(J))))\n"
AUTH="\nfrom pathlib import Path\nimport hashlib,json,psutil,time\nC=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)\nassert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'\nassert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['remaining_training_seconds']>86412.86069250107\nactive=c['active_segment'];known=v['known_binding'];bound=None\nif active is not None:\n assert known is not None and set(known)=={'owner','run_id','go'}\n expected=known['owner'];assert active['owner_parent_pid']==expected['pid'] and set(active['experts'])==set(known['go'])\n p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'];actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert actual==expected\n assert all(g['run_id']==known['run_id'] and active['experts'][key]['started_epoch']==g['learning_started_epoch'] for key,g in known['go'].items())\n bound=dict(owner=actual,run_id=known['run_id'],genuine_slots=sorted(known['go']))\nprint(json.dumps(dict(passed_readonly_original72_finite_authority=True,epoch=time.time(),canonical_path=str(C),canonical_SHA=hashlib.sha256(raw).hexdigest(),generation=c['authority_generation'],remaining_snapshot=c['remaining_training_seconds'],CNone=active is None,known_active_binding=bound,no_account_lock_copy_write_GO_or_secondwriter=True)))\n"
META={'kind': 'exact_W35_210_launcher_storage_metadata_only_extension_v3', 'source_SHA': 'ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f', 'base_wholeCPU_path': 'C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027\\W35_fixed92_NEW_FINAL_whole_CPU_reviewer_v1\\W35_FIXED92_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V2.json', 'base_wholeCPU_SHA': 'c633a5eb9f091c6d6b2327ae86b3d0b61d25c1b43964b20d875567f97c692442', 'actual_own_storage_N1_path': 'C:\\Users\\lulu\\Desktop\\claude\\mjcf\\MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021\\MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027\\W35_210_N1_OWN_DATASTORE_PATH_ISOLATION_SOURCE_V1\\reports\\N1_OWN_DATASTORE_PATH_ORIGINAL_ASSERTION_OR_ERROR_RETURNED_ACTUAL.json', 'actual_own_storage_N1_SHA': 'c554b5ff7afbc883db4e3cbc2b0e249bb27a5870c69435f492e2c617467d91c1', 'worker_inverse_bytes': True, 'new_model_CPU_load_not_requested': True, 'original_allfullfinite_D1_D7_W35_G3_nearest250_preserved': True, 'actual_new_GPU_fullrestore_native24_profiles_pending': True}

def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--known72-binding-json',type=Path);args=parser.parse_args();known=json.loads(args.known72_binding_json.read_bytes()) if args.known72_binding_json else None
 put('NEW_W35_V2_DIAGNOSTIC_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),new_namespace=NEW,no_old_once_retry_or_model_source_promotion=True));base=L/'W35_210_ADAPTED40050_N20K_BOUNDED_SKILL_REGRESSION_SOURCE_V1';parent_path=base/'install_admit_launch_detached_W35_210_frozen_profiles_UNUSED_once_v1.py';assert hashlib.sha256(parent_path.read_bytes()).hexdigest()=='a1c8bb3377f8e12f14b57eb42d7545da86f008d9a255aea8273f198d36f8468e';parent=module('passed_W35_original_source_interfaces_only_not_main',parent_path)
 manifest=json.loads((B/'W35_210_OWN_STORAGE_COMPLETE_INPUT_MANIFEST_V3.json').read_bytes());original=json.loads((L/'W35_210_FIRST_ORIGINAL_GPU_NATIVE24_READONLY_SOURCE_V1/reports/W35_FIRST_ORIGINAL_GPU_NATIVE24_OR_ERROR_RETURNED_ACTUAL.json').read_bytes());assert original['supervisor_state']['original_out'] and original['worker_state']['original_out'] and not original['passed_original_W35_GPU_fullrestore_and_native24']
 wrapper=module('same_memory_for_NEW_W35_v2_diagnostic',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d;sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sec=module('same72_memory_NEW_W35_v2_readonly',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_FINITE_NEW_W35_V2_EXCEPTION_DIAGNOSTIC',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  client=d.connect72(secret);secret=None;authority=d.code(client,d.PY72,AUTH,dict(known_binding=known),timeout=30);assert authority['passed_readonly_original72_finite_authority'];authority['passed']=True;authority['metadata_extension']=META;put('CURRENT101_AUTHORITY_READONLY_ACTUAL.json',authority);client.close();client=None
  client=route.connect();put('FRESH_NEW_NAMESPACE_UUID_RESOURCE_ACTUAL.json',d.code(client,route.PY,PRE,dict(job=NEW,GPU=parent.GPU),timeout=30));put('VERIFIED_FAILED_V1_INPUT_COPY_ONLY_ACTUAL.json',d.code(client,route.PY,COPY,dict(old=OLD,new=NEW,rows=manifest['files'],supervisor=original['supervisor_state']['expected'],worker=original['worker_state']['expected']),timeout=90))
  worker=B/'evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py';sf=client.open_sftp()
  try:
   try:sf.stat(NEW+'/lib')
   except FileNotFoundError:sf.mkdir(NEW+'/lib',mode=0o700)
   for name,relative in [('evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py','evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py'),('zonglin2_app_launcher.py','lib/zonglin2_app_launcher.py'),('detached_W35_frozen_eval_private210_supervisor_once_v1.py','detached_W35_frozen_eval_private210_supervisor_once_v1.py')]:
    with sf.open(NEW+'/'+relative,'wx') as f:f.write((B/name).read_bytes())
  finally:sf.close()
  result=d.code(client,route.PY,parent.RUN,dict(job=NEW,GPU=parent.GPU,python=route.PY,files=[{k:r[k] for k in ('relative','bytes','SHA')} for r in manifest['files']],RSL_sources=manifest['RSL_sources'],SDK_math_SHA=manifest['SDK_math_SHA'],authority=authority),timeout=120);put('NEW_W35_V2_SOURCE_SDK_AND_FINITE_DIAGNOSTIC_DETACHED_RETURNED_ACTUAL.json',result);print(json.dumps(result))
 finally:
  secret=None;stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('NEW_W35_V2_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_old_namespace_change=True));raise
