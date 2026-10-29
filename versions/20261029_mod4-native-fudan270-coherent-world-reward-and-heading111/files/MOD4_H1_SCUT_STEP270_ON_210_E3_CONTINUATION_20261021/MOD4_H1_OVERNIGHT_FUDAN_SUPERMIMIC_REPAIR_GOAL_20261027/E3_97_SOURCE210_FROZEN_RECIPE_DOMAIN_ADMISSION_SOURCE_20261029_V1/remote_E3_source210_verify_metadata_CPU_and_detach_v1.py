"""Future target only: verified new inputs, CPU metadata/witness, finite frozen eval."""
from pathlib import Path,PurePosixPath
import hashlib,json,os,subprocess,sys,time,traceback
JOB=Path('/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v1/e3')
MODEL='1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8'
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(J,n,x):
 with (J/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def main(v):
 J=Path(v['job']);assert J==JOB and J.resolve()==J;assert v['python']=='/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python3.12'
 manifest=J/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json';assert H(manifest)==v['manifest_SHA'];m=json.loads(manifest.read_bytes());rows=[]
 for r in m['files']:
  rel=PurePosixPath(r['relative']);assert not rel.is_absolute() and '..' not in rel.parts;p=J/rel;assert p.resolve().is_relative_to(J) and not p.is_symlink() and p.stat().st_size==r['bytes'] and H(p)==r['SHA'],str(p);rows.append({k:r[k] for k in ('relative','bytes','SHA')})
 put(J,'E3_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json',dict(actual_postcopy_fullSHA_verified=True,job_root=str(J),manifest_SHA=v['manifest_SHA'],files=rows))
 sys.path.insert(0,str(J));from source210_project_launch_helpers_v1 import environment,own_identity
 assert v['authority']['passed_readonly_original72_finite_authority'];timed=False
 with (J/'E3_SOURCE_CPU_COMPLETE_STDOUT_STDERR.log').open('xb') as f:
  p=subprocess.Popen([v['python'],'-u','-B',str(J/'E3_source210_target_source_SDK_metadata_admission_v1.py'),'--job-root',str(J)],cwd=J,env=environment(J,False),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);initial=own_identity(p.pid)
  try:rc=p.wait(timeout=120)
  except subprocess.TimeoutExpired:
   timed=True
   if p.poll() is None:p.terminate()
   try:rc=p.wait(timeout=20)
   except subprocess.TimeoutExpired:
    if p.poll() is None:p.kill()
    rc=p.wait(timeout=10)
 report=J/'E3_TARGET_SOURCE_SDK_METADATA_ACTUAL.json';identity=J/'E3_CPU_OWN_WORKER_IDENTITY.json';value=json.loads(report.read_bytes()) if report.exists() else None;own=json.loads(identity.read_bytes()) if identity.exists() else None;errors=list(J.glob('E3_SOURCE_SDK_CPU_ORIGINAL_ERROR*.json'))
 cpu=dict(epoch=time.time(),actual_waited=p.poll() is not None,returncode=rc,deadline_terminated=timed,initial_identity=initial,actual_worker_identity=own,report_SHA=H(report) if report.exists() else None,report_value=value,passed=rc==0 and not timed and own is not None and own['pid']==p.pid and not errors and value is not None and value['passed']);put(J,'E3_SOURCE210_CPU_ORIGINAL_WAIT_PROOF.json',cpu);detached=None
 if cpu['passed']:
  task=dict(kind='MOD4_E3_ADAPTED97_SOURCE210_FROZEN_RECIPE_DOMAIN_V1',target_backend='source210',source_SHA=MODEL,num_envs=20000,controls=600,warmup_controls=100,maximum_worker_seconds=1680,no_optimizer_steps=True,actual_source210_SDK_admission_passed=True,actual_private_GPU_EX_held_by_parent=False,canonical72_known_owner_readonly_passed=True,known72_readonly_authority=v['authority'],actual_CPU_report_SHA=H(report),actual_CPU_waited_proof_SHA=H(J/'E3_SOURCE210_CPU_ORIGINAL_WAIT_PROOF.json'),manifest_SHA=v['manifest_SHA'],worker_SHA=v['worker_SHA'],domain_kind='E3_PUBLIC_RECOVERY',original_Adam=866060,original_LR=.0002562890625000001,full_WM_tap_included=False)
  put(J,'FROZEN_CASE_TASK_TEMPLATE.json',task)
  with (J/'FROZEN_E3_SUPERVISOR_COMPLETE_STDOUT_STDERR.log').open('xb') as f:child=subprocess.Popen([v['python'],'-u','-B',str(J/'detached_E3_source210_frozen_recipe_supervisor_once_v1.py'),'--job-root',str(J)],cwd=J,env=environment(J,False),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
  identpath=J/'OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json';limit=time.time()+5
  while not identpath.exists() and child.poll() is None and time.time()<limit:time.sleep(.1)
  ident=json.loads(identpath.read_bytes()) if identpath.exists() else None;assert ident is None or ident['pid']==child.pid
  detached=dict(epoch=time.time(),actual_detached=child.poll() is None and ident is not None,identity=ident,spawn_pid=child.pid,already_exited_returncode=child.poll(),worker_maximum1680=True,actual_child_wait1800=True,no_training_writer_or_GO=True,actual_GPU_restore_native24_and_profiles_pending=True);put(J,'ACTUAL_SOURCE210_E3_FINITE_SUPERVISOR_DETACHED.json',detached)
 texts=[]
 for q in sorted(J.iterdir()):
  if q.is_file() and q.suffix in ('.json','.txt','.log') and q.name not in ('E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json','E3_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json'):
   raw=q.read_bytes();texts.append(dict(path=str(q),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
 return dict(passed_source_CPU_and_detached_only=cpu['passed'] and detached is not None and detached['actual_detached'],epoch=time.time(),job_root=str(J),source_CPU_actual_wait=cpu,detached=detached,complete_original_UTF8=texts,actual_GPU_fullrestore_native24_and_coverage_pending=True,no_PPO_normalizer_or_ledger_write=True,not_skill_graduation_or_complete_WM_dataset=True)
if __name__=='__main__':print(json.dumps(main(v)))
