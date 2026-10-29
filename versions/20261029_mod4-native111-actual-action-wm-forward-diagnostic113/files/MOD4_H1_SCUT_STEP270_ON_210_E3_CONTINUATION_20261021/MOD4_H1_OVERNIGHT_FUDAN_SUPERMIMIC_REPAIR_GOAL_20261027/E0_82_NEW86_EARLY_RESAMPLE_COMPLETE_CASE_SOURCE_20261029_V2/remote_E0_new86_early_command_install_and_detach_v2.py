"""Project-owned deployment/CPU actual wait/detached regression; no training GO."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,shutil,subprocess,sys,time,traceback
ROOT=Path('/data/robemo/polar-rl-train')
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(J,n,x):
 with (J/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def paths(v):
 J=Path(v['stage']);assert str(J)=='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_EARLY_RESAMPLE_20261029v2/e0';D=Path(v['copy']);assert J.resolve()==J and J.is_relative_to(ROOT/'evaluation_runs') and D.resolve()==D and D.is_relative_to(ROOT/'runtime_migrations');return J,D
def pre(v):
 J,D=paths(v);assert ROOT.resolve()==ROOT and not J.exists();marker=json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert marker['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and marker['authorized_root']==str(ROOT)
 clone=ROOT/'runtime_migrations/proven72_20261028_v1/extract_relocate_stage_v1/VERIFIED_NEW_COPY_EXTRACT_AND_NARROW_RELOCATION_COMPLETE_ACTUAL.json';assert json.loads(clone.read_bytes())==v['clone_complete'] and v['clone_complete']['destination']==str(D)
 prior=ROOT/'validation_runs/NORMAL_H1_PPO86B40050_WHOLECPU_NATIVE24_20261029v2/NORMAL_H1_ADMISSION_COMPLETE_ORIGINAL_TERMINAL.json';proof=json.loads(prior.read_bytes());assert proof==v['normal_whole_result'] and proof['passed_actual_wholeCPU_CUDA_fullrestore_native24_only'] and proof['private_EX_released'] and all(r['passed'] and r['actual_waited'] and r['returncode']==0 for r in proof['actual_phase_waits'])
 O=Path('/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_LONG_COMMAND_20261029v1/e0');assert O.resolve()==O and O.is_relative_to(ROOT/'evaluation_runs') and H(O/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V1.json')==v['old_manifest_SHA']
 old_wait=json.loads((O/'FROZEN_E0_ORIGINAL_WAITED_TERMINAL_ACTUAL.json').read_bytes());assert old_wait==v['samehost_previous_terminal'] and old_wait['passed_frozen_execution'] and old_wait['actual_worker_waited'] and old_wait['returncode']==0 and old_wait['private_EX_released'] and old_wait['result']['controls']==1000
 assert shutil.disk_usage(ROOT).free>25*1024**3;J.mkdir(parents=True,mode=0o700)
 for name in ('home','tmp','cache','config','data','state','state/runtime','cache/nv','cache/torch','cache/pip','cache/conda','cache/triton','cache/warp','cache/numba','cache/matplotlib','cache/gl'):(J/name).mkdir(parents=True,exist_ok=True,mode=0o700)
 put(J,'OWN_NEW86_E0_FROZEN_PROFILE_SCOPE.json',dict(root=str(J),source='qualified E0 adapted89D final82',no_training_GO_or_C_write=True))
 copied=[]
 for row in v['samehost_reuse_rows']:
  rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts;src=O/rel;dst=J/rel
  assert src.resolve().is_relative_to(O) and not src.is_symlink() and src.stat().st_size==row['bytes'] and not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True,mode=0o700);shutil.copyfile(src,dst);copied.append(row['relative'])
 put(J,'SAMEHOST_PRIOR_VERIFIED_INPUTS_COPY_ACTUAL.json',dict(passed=True,old_job=str(O),old_manifest_SHA=v['old_manifest_SHA'],copied=sorted(copied),no_old_outputs_Task_GO_or_log_copy=True,postcopy_all_new_target_input_fullSHA_still_required=True))
 return dict(passed=True,epoch=time.time(),job_root=str(J),normal_robot_native24_prior_actual_proof=True,no_current_GPU_idle_claim=True,samehost_copied_relative=sorted(copied))
def verify(v):
 J,D=paths(v);mf=J/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json';assert H(mf)==v['manifest_SHA'];m=json.loads(mf.read_bytes());rows=[]
 for r in m['files']:
  rel=PurePosixPath(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts;p=J/rel;assert p.resolve().is_relative_to(J) and not p.is_symlink() and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],str(p);rows.append({k:r[k] for k in ('relative','bytes','SHA')})
 receipt=dict(actual_postcopy_fullSHA_verified=True,job_root=str(J),manifest_SHA=v['manifest_SHA'],files=rows);put(J,'E0_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json',receipt);return dict(passed=True,files=len(rows),manifest_SHA=v['manifest_SHA'],actual_postcopy_all_fullSHA=True)
def run(v):
 J,D=paths(v);sys.path.insert(0,str(J));from project_clone_launch_helpers_v1 import environment,argv,own_identity
 cpuenv=environment(J,D,False);cpuenv['MOD4_PROVEN_CLONE_ROOT']=str(D);command=argv(D,J/'E0_new86_target_source_SDK_metadata_admission_v2_early.py',['--job-root',str(J)]);timed=False
 with (J/'E0_SOURCE_CPU_COMPLETE_STDOUT_STDERR.log').open('xb') as f:
  p=subprocess.Popen(command,cwd=J,env=cpuenv,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);initial=own_identity(p.pid)
  try:rc=p.wait(timeout=120)
  except subprocess.TimeoutExpired:
   timed=True
   if p.poll() is None:p.terminate()
   try:rc=p.wait(timeout=20)
   except subprocess.TimeoutExpired:
    if p.poll() is None:p.kill()
    rc=p.wait(timeout=10)
 report=J/'E0_TARGET_SOURCE_SDK_METADATA_ACTUAL.json';own=J/'E0_CPU_OWN_WORKER_IDENTITY.json';value=json.loads(report.read_bytes()) if report.exists() else None;identity=json.loads(own.read_bytes()) if own.exists() else None;errs=list(J.glob('E0_SOURCE_SDK_CPU_ORIGINAL_ERROR*.json'))
 cpu=dict(epoch=time.time(),actual_waited=p.poll() is not None,returncode=rc,deadline_terminated=timed,initial_identity=initial,actual_worker_identity=identity,report_SHA=H(report) if report.exists() else None,report_value=value,passed=rc==0 and not timed and identity is not None and identity['pid']==p.pid and not errs and value is not None and value['passed']);put(J,'E0_NEW86_CPU_ORIGINAL_WAIT_PROOF.json',cpu)
 detached=None
 if cpu['passed']:
  assert v['authority']['passed_readonly_original72_finite_authority']
  task=dict(kind='MOD4_E0_ADAPTED82_NEW86_EARLY_RESAMPLE_FROZEN_PROFILE_DOMAIN_V2',target_backend='new86',source_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',num_envs=20000,controls=1000,warmup_controls=100,maximum_worker_seconds=1680,no_optimizer_steps=True,actual_target86_SDK_admission_passed=True,actual_private_GPU_EX_held_by_parent=False,canonical72_known_owner_readonly_passed=True,known72_readonly_authority=v['authority'],actual_CPU_report_SHA=H(report),actual_CPU_waited_proof_SHA=H(J/'E0_NEW86_CPU_ORIGINAL_WAIT_PROOF.json'),manifest_SHA=v['manifest_SHA'],worker_SHA=v['worker_SHA'],domain_kind='E0_DIRECTIONAL_SPIN_V1',original_Adam=641200,original_LR=.00038443359375000017,ground_provider_contract=json.loads((J/'GROUND_PROVIDER_SOURCE_CONTRACT.json').read_bytes()),ground_provider_contract_SHA=H(J/'GROUND_PROVIDER_SOURCE_CONTRACT.json'),telemetry_component_SHA=H(J/'e0_long_command_domain_telemetry_v1.py'),first_native24_read_wait_maximum_seconds=360,full_WM_tap_included=False,early_observer_SHA=H(J/'e0_early_original_resample_passthrough_observer_v1.py'),actual_target_CommandTerm_method_AST_passed=True,typed_JSONL_collection='producer_metadata_only_no_contents',population_contract='original20k_D1_D7_fullrestore_no_projection',initial_command_instance_start_unknown=True,requested_simulated_seconds=20,original_episode_seconds=20,complete_command_exposure_may_be_missing=True)
  put(J,'FROZEN_CASE_TASK_TEMPLATE.json',task);command=argv(D,J/'detached_E0_new86_frozen_profile_supervisor_once_v2_early.py',['--job-root',str(J),'--clone-root',str(D)])
  with (J/'FROZEN_E0_SUPERVISOR_COMPLETE_STDOUT_STDERR.log').open('xb') as f:child=subprocess.Popen(command,cwd=J,env=environment(J,D,False),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
  identpath=J/'OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json';limit=time.time()+5
  while not identpath.exists() and child.poll() is None and time.time()<limit:time.sleep(.1)
  identity=json.loads(identpath.read_bytes()) if identpath.exists() else None;assert identity is None or identity['pid']==child.pid
  detached=dict(epoch=time.time(),actual_detached=child.poll() is None and identity is not None,identity=identity,spawn_pid=child.pid,already_exited_returncode=child.poll(),worker_maximum1680=True,actual_child_wait1800=True,no_training_writer_or_GO=True,actual_GPU_restore_native24_and_profiles_pending=True);put(J,'ACTUAL_NEW86_E0_FINITE_SUPERVISOR_DETACHED.json',detached)
 texts=[]
 for q in sorted(J.iterdir()):
  if q.is_file() and q.suffix in ('.json','.txt','.log') and q.name not in ('E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json','E0_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json'):
   raw=q.read_bytes();texts.append(dict(path=str(q),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
 return dict(passed_source_CPU_and_detached_only=cpu['passed'] and detached is not None and detached['actual_detached'],epoch=time.time(),source_CPU_actual_wait=cpu,detached=detached,complete_original_UTF8=texts,actual_GPU_fullrestore_native24_and_coverage_pending=True,no_PPO_normalizer_or_ledger_write=True,not_skill_graduation_or_complete_WM_dataset=True)
if __name__=='__main__':
 assert hashlib.sha256(v['code'].encode()).hexdigest()==v['remote_code_SHA'];print(json.dumps({'pre':pre,'verify':verify,'run':run}[v['action']](v)))
