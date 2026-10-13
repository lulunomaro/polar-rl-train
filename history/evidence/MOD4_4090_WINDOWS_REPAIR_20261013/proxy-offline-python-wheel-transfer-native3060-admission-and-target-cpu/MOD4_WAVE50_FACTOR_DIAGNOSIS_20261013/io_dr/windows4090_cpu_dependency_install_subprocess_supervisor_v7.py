"""Demand-task CPU install driver. Direct file FDs avoid PowerShell async-exit wait."""
from pathlib import Path
import os,sys,time,json,subprocess,hashlib,traceback
R=Path(__file__).resolve().parent;P=R/'env/python.exe';Reports=R/'install_reports';Logs=R/'install_logs'
os.environ.update(CUDA_VISIBLE_DEVICES='',PYTHONNOUSERSITE='1',HTTP_PROXY='http://127.0.0.1:7897',HTTPS_PROXY='http://127.0.0.1:7897')
def rec(name,v):
 p=Reports/(name+'.json')
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def stage(name,args,known_original_dependency_conflict=False):
 start=time.time();op=Logs/(name+'.stdout.log');ep=Logs/(name+'.stderr.log')
 with op.open('xb') as o,ep.open('xb') as e:
  child=subprocess.Popen([str(P)]+[str(x) for x in args],stdin=subprocess.DEVNULL,stdout=o,stderr=e,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
  rec(name+'_STARTED',dict(epoch=start,pid=child.pid,parent=os.getpid(),executable=str(P),argv=[str(x) for x in args],direct_file_descriptors=True,no_GPU_Kit_PPO=True))
  code=child.wait(timeout=3600)
  o.flush();e.flush();os.fsync(o.fileno());os.fsync(e.fileno())
 rec(name+'_ENDED',dict(epoch=time.time(),start=start,pid=child.pid,exit_code=code,passed=code==0,stdout=str(op),stderr=str(ep),actual_parent_CPU_seconds=time.time()-start,no_GPU_PPO_budgetwrite=True,original_dependency_false_retained=known_original_dependency_conflict))
 if known_original_dependency_conflict:
  assert code==1,'original known dependency conflict must remain actual false'
  raw=op.read_text(encoding='utf8',errors='replace')+ep.read_text(encoding='utf8',errors='replace');assert 'fastapi' in raw and 'starlette' in raw and 'wheel' in raw and 'packaging' in raw
 elif code:raise RuntimeError(name+' actual failed '+str(code))
try:
 assert sys.version_info[:2]==(3,11) and Path(sys.executable).resolve()==P.resolve()
 assert (Reports/'OFFLINE_PY311_BASE_ACTUAL_COMPLETE.json').exists()
 rec('CPU_SUBPROCESS_DEPENDENCY_SUPERVISOR_STARTED',dict(epoch=time.time(),pid=os.getpid(),python=sys.executable,no_GPU_Kit_PPO_budgetwrite=True,new_env_only=True,original_Powershell_download_parent_wait_unknown_retained=True))
 stage('04A_MISSING4_INDEPENDENT_ARTIFACT_CPU_REVIEW',[R/'windows4090_missing4_independent_artifact_cpu_review_v6.py'])
 stage('04B_NATIVE311_WHEELHOUSE_CPU_EXTRACT_VALIDATE',[R/'extract_native_wheelhouse_independent_artifact_reviewed_cpu_v6.py'])
 stage('04C_EXACT_PINNED_NATIVE311_WHEELHOUSE_INSTALL',['-m','pip','install','--no-deps','--no-index','--require-hashes','--find-links',R/'native311_wheelhouse','--requirement',R/'ACTUAL_NATIVE311_FULL_WHEELHOUSE_PINS.txt'])
 stage('04D_ORIGINAL_CLOSURE_PIPCHECK_FALSE_PRESERVED',['-m','pip','check'],known_original_dependency_conflict=True)
 stage('04E_LABRL_BOUND_COMPATIBILITY_ARTIFACT_CPU_REVIEW',[R/'windows4090_compatibility_artifacts_cpu_review_v6.py'])
 stage('04F_NEWENV_MINIMAL_COMPATIBILITY_WHEELS_INSTALL',['-m','pip','install','--no-deps','--no-index','--require-hashes','--find-links',R/'official_dependency_compatibility_wheels_v6','--requirement',R/'ACTUAL_LABRL_BOUND_COMPATIBILITY_PINS_V6.txt'])
 stage('04G_EXACT_THREE_PACKAGES_CPU_EXTRACT',[R/'extract_three_exact_packages_cpu_v1.py'])
 for n in ('isaaclab','isaaclab_rl','isaaclab_assets','isaaclab_tasks'):stage('04H_EDITABLE_'+n,['-m','pip','install','--no-deps','--no-build-isolation','--editable',R/'sdk_exact/source'/n])
 stage('04I_FULL_ENV_METADATA_CPU_ADMISSION',[R/'metadata_full_environment_cpu_admission_v1.py'])
 stage('04J_NATIVE_LIBRARIES_CPU_ADMISSION',[R/'windows4090_native_libraries_cpu_admission_v5.py'])
 stage('04K_PIP_REQUIREMENTS_CONSISTENCY_CPU',['-m','pip','check'])
 rec('WINDOWS4090_FULL_ENVIRONMENT_CPU_ACTUAL_COMPLETE',dict(epoch=time.time(),pid=os.getpid(),full_environment_CPU_metadata_native_libraries_and_pipcheck_passed=True,GPU_backend_source_fullrestore_probe_still_pending=True,original_dependency_false_and_parent_wait_retained=True,no_GPU_Kit_PPO_or_canonicalwrite=True))
except Exception as e:
 rec('CPU_SUBPROCESS_ORIGINAL_FAILURE_'+str(time.time_ns()),dict(epoch=time.time(),pid=os.getpid(),error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),source_logs_original_false_retained=True,no_GPU_Kit_PPO_or_budgetwrite=True));raise
