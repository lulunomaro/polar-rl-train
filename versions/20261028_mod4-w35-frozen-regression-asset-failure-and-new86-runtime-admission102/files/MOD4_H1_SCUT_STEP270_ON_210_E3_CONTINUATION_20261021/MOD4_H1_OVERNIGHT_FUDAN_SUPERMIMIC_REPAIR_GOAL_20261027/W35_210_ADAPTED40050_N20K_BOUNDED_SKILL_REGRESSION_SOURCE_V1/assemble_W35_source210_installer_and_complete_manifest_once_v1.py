"""Local text-source assembly only; PT/USD/NPZ use existing producer metadata."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent
E0=L/'E0_210_N20K_MEAN_FROZEN_REGRESSION_SOURCE_V1'

def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p,raw):
 with p.open('xb') as f:f.write(raw)

def main():
 witness=json.loads((B/'ORIGINAL_E0_PASSED_OWNER_PRE_CPU_INTERFACE_TEXT_WITNESS.json').read_bytes());old=(E0/'install_admit_run_collect_E0_210_bounded_frozen_case_once_v2_complete_dependency.py').read_text();tree=ast.parse(old)
 cpu=witness['RUN'].split("lock=lockpath.open('rb+')")[0].replace('existing E0 formal wholeCPU reused','existing W35 final78 wholeCPU reused');cpu=cpu.replace("J=Path(v['job']);lockpath=", "os.environ['CUDA_VISIBLE_DEVICES']='';J=Path(v['job']);lockpath=")
 start=r'''
task=dict(kind='MOD4_W35_ADAPTED92_ORIGINAL_N20K_FROZEN_PROFILES_V1',source_SHA='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f',num_envs=20000,controls=1200,warmup_controls=100,maximum_worker_seconds=1680,no_optimizer_steps=True,actual_source210_SDK_admission_passed=True,actual_private_GPU_EX_held_by_parent=False,canonical72_known_owner_readonly_passed=v['authority']['passed'],known72_readonly_authority=v['authority'],actual_source210_python=v['python'],full_WM_tap_included=False)
put('FROZEN_CASE_TASK_TEMPLATE.json',task)
env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1');argv=[v['python'],'-u','-B',str(J/'detached_W35_frozen_eval_private210_supervisor_once_v1.py'),'--job-root',str(J)]
with (J/'FROZEN_W35_SUPERVISOR_COMPLETE_STDOUT_STDERR.log').open('xb') as log:p=subprocess.Popen(argv,env=env,cwd=J,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
q=psutil.Process(p.pid);identity=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd());assert p.poll() is None
put('ACTUAL_FROZEN_W35_FINITE_SUPERVISOR_DETACHED.json',dict(epoch=time.time(),identity=identity,actual_detached=True,worker_maximum_seconds=1680,original_child_wait_seconds=1800,source_SDK_CPU_passed=True,actual_GPU_fullrestore_native24_and_profiles_pending=True,no_optimizer_budget_or_new_GO=True))
print(json.dumps(dict(passed_source_admission_and_detached_only=True,epoch=time.time(),identity=identity,job_root=str(J),source_SDK_CPU=cpu,actual_GPU_fullrestore_native24_and_profile_coverage_pending=True,no_policy_training_or_skill_graduation_claim=True)))
'''
 functions=[]
 for name in ['put','module','read_json']:
  fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);functions.append(ast.get_source_segment(old,fn))
 mainold=ast.get_source_segment(old,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main'))
 prefix=mainold.split("  target=R/'complete_original_UTF8_texts'")[0]
 prefix=prefix.replace('E0_210_FROZEN_CASE_CONSUMED_BEFORE_NETWORK_ACTUAL.json','W35_210_FROZEN_PROFILES_CONSUMED_BEFORE_NETWORK_ACTUAL.json').replace('E0_FROZEN_CASE_COMPLETE_INPUT_MANIFEST_V2.json','W35_FROZEN_PROFILES_COMPLETE_INPUT_MANIFEST_V1.json').replace('TWO97_H1_E3_NEW_FULL_CPU_OWNER_SOURCE_V1/reports/TWO97_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json','TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1/reports/TWO101_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').replace('TWO97_H1_E3_COMBINED_FIRST_INLINE_SOURCE_V1/reports/TWO97_ACTUAL_TWO_GO_OWNER_METADATA_RETURNED.json','TWO101_PRODUCER_FIXED_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1/reports/TWO101_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json').replace('E0_CURRENT97_CANONICAL72_KNOWN_OWNER_READONLY_ADMISSION_ACTUAL.json','W35_CURRENT101_CANONICAL72_KNOWN_OWNER_READONLY_ADMISSION_ACTUAL.json').replace('E0_210_FRESH_UUID_MOUNT_RESOURCE_ACTUAL.json','W35_210_FRESH_UUID_MOUNT_RESOURCE_ACTUAL.json').replace('timeout=630','timeout=120').replace('SAME_FINITE_E0_FROZEN_REGRESSION','SAME_FINITE_W35_SOURCE_ADMISSION_AND_DETACHED_EVAL')
 tail="  put('W35_210_SOURCE_SDK_AND_FINITE_SUPERVISOR_DETACHED_RETURNED_ACTUAL.json',value);print(json.dumps(value))\n finally:\n  secret=None;stop.set();thread.join(1)\n  if client:client.close()\n  transport.SESSION=previous\n"
 header='''"""NEW W35 source210 install+actual SDK CPU+detached finite frozen regression."""\nfrom pathlib import Path,PurePosixPath\nimport argparse,base64,hashlib,importlib.util,json,os,sys,threading,time,traceback\nB=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'\nJOB='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED40050_FROZEN_PROFILES_20261028v1/w35'\nGPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'\n'''
 entry=header+'OWNER='+repr(witness['OWNER'])+'\nPRE='+repr(witness['PRE'])+'\nRUN='+repr(cpu+start)+'\n\n'+'\n\n'.join(functions)+'\n\n'+prefix+tail+"\nif __name__=='__main__':\n try:main()\n except BaseException:put('W35_210_FROZEN_PROFILES_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_newwriter_or_oldsource_promotion=True));raise\n"
 ast.parse(entry);installer=B/'install_admit_launch_detached_W35_210_frozen_profiles_UNUSED_once_v1.py';write(installer,entry.encode())
 base=json.loads((L/'W35_retention_fixed_next92_source_extension_candidate_v2/W35_RETENTION_BASELINE_V2_COMPLETE_INSTALL_MANIFEST.json').read_bytes());files=[];launcher_delta=None
 for row in base['small_source_files']:
  rel=row['installed_relative']
  if not (rel.startswith('runtime/') or rel=='original_run_manifest.json'):continue
  p=Path(row['local_path']);raw=p.read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
  if rel=='runtime/isaac/mod4/train_e1_retention_named_owned_resume_ppo.py':
   needle=b'from isaaclab.app import AppLauncher';replacement=b'from zonglin2_app_launcher import Zonglin2AppLauncher as AppLauncher';assert raw.count(needle)==1;new=raw.replace(needle,replacement);assert new.replace(replacement,needle)==raw;local=B/'source210_headless_train_e1_retention_named_owned_resume_ppo.py';write(local,new);launcher_delta=dict(original_SHA=row['SHA'],new_SHA=hashlib.sha256(new).hexdigest(),inverse_single_import_bytes_equal=True,headless_launcher_same_as_actual_E0_210=True,physics_reward_commands_restore_code_unchanged=True);p=local;raw=new
  files.append(dict(relative=rel,local_path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),index_kind='actual_small_source_bytes'))
 e0=json.loads((E0/'E0_FROZEN_CASE_COMPLETE_INPUT_MANIFEST_V2.json').read_bytes())
 for row in e0['files']:
  if row['relative'].startswith('lib/'):files.append(dict(row))
 for row in base['binary_dependencies']:files.append(dict(relative=row['installed_relative'],local_path=row['local_path'],bytes=row['bytes'],SHA=row['SHA'],index_kind='existing_binary_producer_metadata_not_reread'))
 proof=L/'W35_fixed92_NEW_FINAL_whole_CPU_reviewer_v1/W35_FIXED92_NEW_FORMAL_INITIAL_WHOLE_CPU_ACTUAL_V2.json';cpu=json.loads(proof.read_bytes());assert cpu['passed'] and cpu['review']['Adam_step']==648360 and cpu['review']['stored_RSL_iteration']==32336
 model=cpu['model'];assert model['SHA']=='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f';files.append(dict(relative='source/W35_ADAPTED92_FINAL78.pt',local_path=model['local_path'],bytes=model['bytes'],SHA=model['SHA'],index_kind='existing_qualified_final78_producer_and_CPU_metadata_not_reread'))
 files.append(dict(relative='W35_EXISTING_FORMAL_WHOLE_CPU_WITNESS.json',local_path=str(proof),bytes=len(proof.read_bytes()),SHA=H(proof),index_kind='existing_wholeCPU_text_witness'))
 for name in ['evaluate_W35_adapted92_originalN20K_frozen_profiles_once_v1.py','detached_W35_frozen_eval_private210_supervisor_once_v1.py']:
  p=B/name;files.append(dict(relative=name,local_path=str(p),bytes=len(p.read_bytes()),SHA=H(p),index_kind='new_frozen_evaluation_source'))
 assert launcher_delta and len({r['relative'] for r in files})==len(files)
 manifest=dict(kind='MOD4_W35_FROZEN40050_N20K_SOURCE210_PROFILE_INPUT_V1',files=files,RSL_sources=e0['RSL_sources'],SDK_math_SHA=e0['SDK_math_SHA'],headless_only_entry_source_delta=launcher_delta,original_model_and_bank_and_USD_bytes_not_reread_during_assembly=True,original_fixed92_retention_checkpoint_SHA='8d3a49766a076f508118b5f84c4a1e9557d6e8a84369b9502516827336604894',model_SHA=model['SHA'],expected_frozen_Adam648360=True,coverage=dict(controls=1200,policy_dt=.02,warmup_controls=100,steady_controls=1100,natural_original_G3_and_retained_commands=True,skill_graduation=False),no_training_writer_or_GO=True)
 write(B/'W35_FROZEN_PROFILES_COMPLETE_INPUT_MANIFEST_V1.json',json.dumps(manifest,indent=2).encode());print(json.dumps(dict(installer=str(installer),installer_SHA=H(installer),files=len(files),payload_bytes=sum(r['bytes'] for r in files),no_model_or_binary_read=True)))

if __name__=='__main__':main()
