"""New attempt resumes only actual missing/wrong artifacts after external OS reboot."""
from pathlib import Path
import sys,os,json,time,subprocess,hashlib
R=Path(__file__).resolve().parent;P=R/'env/python.exe';Reports=R/'install_reports';Logs=R/'install_logs'
os.environ.update(CUDA_VISIBLE_DEVICES='',PYTHONNOUSERSITE='1',HTTP_PROXY='http://127.0.0.1:7897',HTTPS_PROXY='http://127.0.0.1:7897')
audit=Reports/'PREFIX_INSTALLED_ARTIFACT_RECORD_CPU_ACTUAL_1791873373499568100.json'
proof=json.loads(audit.read_bytes());assert proof['no_Torch_Isaac_CUDA_GPU_import_or_install'] and len(proof['missing_or_wrong'])==180 and not proof['fully_exact']
assert (Reports/'04A_MISSING4_INDEPENDENT_ARTIFACT_CPU_REVIEW_ENDED.json').exists() and (Reports/'04B_NATIVE311_WHEELHOUSE_CPU_EXTRACT_VALIDATE_ENDED.json').exists()
def rec(name,v):
 with (Reports/(name+'.json')).open('x',encoding='utf8') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def stage(name,args,known_original_dependency_conflict=False):
 start=time.time();op=Logs/(name+'.stdout.log');ep=Logs/(name+'.stderr.log')
 with op.open('xb') as o,ep.open('xb') as e:
  c=subprocess.Popen([str(P)]+[str(x) for x in args],stdin=subprocess.DEVNULL,stdout=o,stderr=e,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
  rec(name+'_STARTED',dict(epoch=start,pid=c.pid,parent=os.getpid(),executable=str(P),argv=[str(x) for x in args],direct_file_descriptors=True,no_GPU_Kit_PPO_budgetwrite=True))
  code=c.wait(timeout=3600);o.flush();e.flush();os.fsync(o.fileno());os.fsync(e.fileno())
 rec(name+'_ENDED',dict(epoch=time.time(),start=start,pid=c.pid,exit_code=code,passed=code==0,stdout=str(op),stderr=str(ep),actual_stage_wall_seconds=time.time()-start,no_GPU_PPO_budgetwrite=True,original_dependency_false_retained=known_original_dependency_conflict))
 if known_original_dependency_conflict:
  assert code==1
  raw=op.read_text(encoding='utf8',errors='replace')+ep.read_text(encoding='utf8',errors='replace');assert 'fastapi' in raw and 'starlette' in raw and 'wheel' in raw and 'packaging' in raw
 elif code:raise RuntimeError(name+' actual failed '+str(code))
try:
 assert Path(sys.executable).resolve()==P.resolve() and sys.version_info[:2]==(3,11)
 rec('POSTBOOT_MISSING_ARTIFACT_SUPERVISOR_STARTED',dict(epoch=time.time(),pid=os.getpid(),python=sys.executable,actual_prefix_audit=str(audit),actual_prefix_audit_sha256=hashlib.sha256(audit.read_bytes()).hexdigest(),source_of_missing_set='actual version + full hashed RECORD audit',old_task_not_restarted=True,old04A04B_not_reexecuted=True,old04C_OS_reboot_exit_unknown_retained=True,no_GPU_Kit_PPO_or_canonicalwrite=True))
 lines=(R/'ACTUAL_NATIVE311_FULL_WHEELHOUSE_PINS.txt').read_text(encoding='utf8').splitlines();selected=[]
 for line in lines:
  name=line.split('==')[0]
  if name in proof['missing_or_wrong']:selected.append(line)
 assert len(selected)==180
 req=R/'ACTUAL_POSTBOOT_MISSING_OR_WRONG_NATIVE_PINS_V14.txt';assert not req.exists();req.write_text('\n'.join(selected)+'\n',encoding='utf8')
 stage('05A_POSTBOOT_ACTUAL_MISSING_OR_WRONG_NATIVE_INSTALL',['-m','pip','install','--no-deps','--no-index','--require-hashes','--find-links',R/'native311_wheelhouse','--requirement',req])
 stage('05B_ORIGINAL_CLOSURE_PIPCHECK_FALSE_PRESERVED',['-m','pip','check'],known_original_dependency_conflict=True)
 stage('05C_LABRL_BOUND_COMPATIBILITY_ARTIFACT_CPU_REVIEW',[R/'windows4090_compatibility_artifacts_cpu_review_v6.py'])
 stage('05D_NEWENV_MINIMAL_COMPATIBILITY_WHEELS_INSTALL',['-m','pip','install','--no-deps','--no-index','--require-hashes','--find-links',R/'official_dependency_compatibility_wheels_v6','--requirement',R/'ACTUAL_LABRL_BOUND_COMPATIBILITY_PINS_V6.txt'])
 stage('05E_EXACT_THREE_PACKAGES_CPU_EXTRACT',[R/'extract_three_exact_packages_cpu_v1.py'])
 for n in ('isaaclab','isaaclab_rl','isaaclab_assets','isaaclab_tasks'):stage('05F_EDITABLE_'+n,['-m','pip','install','--no-deps','--no-build-isolation','--editable',R/'sdk_exact/source'/n])
 stage('05G_FULL_ENV_METADATA_CPU_ADMISSION',[R/'metadata_full_environment_cpu_admission_v1.py'])
 stage('05H_NATIVE_LIBRARIES_CPU_ADMISSION',[R/'windows4090_native_libraries_cpu_admission_v5.py'])
 stage('05I_PIP_REQUIREMENTS_CONSISTENCY_CPU',['-m','pip','check'])
 rec('WINDOWS4090_FULL_ENVIRONMENT_CPU_ACTUAL_COMPLETE',dict(epoch=time.time(),pid=os.getpid(),full_environment_CPU_metadata_native_libraries_and_pipcheck_passed=True,GPU_backend_source_fullrestore_probe_still_pending=True,old_external_reboot_interruption_and_dependency_false_retained=True,no_GPU_Kit_PPO_or_canonicalwrite=True))
except Exception as e:
 import traceback
 rec('POSTBOOT_MISSING_ARTIFACT_ORIGINAL_FAILURE_'+str(time.time_ns()),dict(epoch=time.time(),pid=os.getpid(),error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(),source_logs_original_false_retained=True,no_GPU_Kit_PPO_or_budgetwrite=True));raise
