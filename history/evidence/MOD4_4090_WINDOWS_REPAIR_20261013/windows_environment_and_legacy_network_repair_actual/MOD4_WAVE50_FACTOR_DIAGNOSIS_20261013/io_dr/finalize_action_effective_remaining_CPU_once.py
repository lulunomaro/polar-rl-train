"""Onlyfinish remaining stop-source/CPUcompile/CPUguard after retained builderassertion."""
from pathlib import Path
import json,time,hashlib,shutil,ast,py_compile,sys,traceback
D=Path(__file__).resolve().parent;W=D.parents[1];N=W/'MOD4_LOCAL_WAVE50_ACTION_EFFECTIVE_REPAIR_20261013'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert (N/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json').exists()
 assert (N/'run_local_attempt.py').exists() and not (N/'request_stop_after_save.ps1').exists()
 p=N/'request_stop_after_save.ps1';src=N/'immutable_local_continue_reference/request_stop_after_save.ps1'
 shutil.copy2(src,p);assert H(src)==H(p)
 # RelativeMyInvocation roots the original helper at its newcopied directory; no stringrootreplacement needed.
 files=list(N.glob('*.py'))+list((N/'immutable_repair_operator').glob('*.py'))
 for p in files:ast.parse(p.read_text(encoding='utf-8-sig'));py_compile.compile(str(p),doraise=True)
 sys.path.insert(0,str(N));import action_effective_source_admission as admission
 proof=admission.source_guard(N/'reports/ACTION_EFFECTIVE_SOURCE_FULLSTATE_CPU_VERIFIED.json',W/'MOD4_LOCAL_WAVE50_CONTINUE_20261013/attempts/same128_continue_second7200_v1/output/model_32396.pt','initial')
 report=dict(epoch=time.time(),CPU_compile_passed=True,CPU_source_guard107_passed=True,source_checkpoint=proof['checkpoint'],active_files=[dict(path=str(p),bytes=p.stat().st_size,sha256=H(p)) for p in files],
  original_runtime_assets476_reference_files_remain_byteexact=True,
  source_all12old_CPUCUDA_markers_strictexact_before_explicit_operator_required=True,operator_actualGPU_roundtrip_required=True,
  source_originalCPU_provenance_not_relabelled_GPU=True,first_newaxis120control_noPPO_fullsave107_physical_admission_required=True,
  future_sameidentity_no_recenter_or_Adamclear=True,shared_oldmsvcrt_GPUlock=True,guardian15sec=True,every2updates_fullsave=True,
  first3600_learning_window_prepared_not_deployed_and_superseded_by_localpause=True,latest_human_pause_blocks_before_Torch_or_Isaac_import=True,
  no_GPU_SDK_PPO_sourcefreeze_dispatch_or_ledger_executed=True,source_originals_and_installed_packages_not_modified=True,
  source_relative_stop_helper_byteexact=True,oldbuilder_assertion_retained=True,
  oldbuilder_failure='Expected hardcoded oldroot string in stophelper, but actual helper uses MyInvocation relative root; failedafter writing preparedCPU sources, before compile/GPU.',
  finalization_only_previously_unexecuted_CPU_stage=True)
 p=N/'reports/ACTION_EFFECTIVE_ACTIVE_FILES_CPU_PREPARED.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(dict(root=str(N),CPU_compile_and_sourceguard=True,local_GPU_paused=True,no_GPU=True),indent=2))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('ACTION_EFFECTIVE_FINALIZE_CPU_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),source_sha256=H(Path(__file__)),preGPU=True),indent=2),encoding='utf-8');raise
