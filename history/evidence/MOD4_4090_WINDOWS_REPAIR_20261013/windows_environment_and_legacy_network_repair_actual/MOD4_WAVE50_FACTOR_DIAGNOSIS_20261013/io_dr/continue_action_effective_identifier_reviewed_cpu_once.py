"""Retain original pre-executionSyntaxError; execute only unstartedCPUbuilder under localpause."""
from pathlib import Path
import hashlib,json,time,py_compile,runpy,traceback
D=Path(__file__).resolve().parent;W=D.parents[1];N=W/'MOD4_LOCAL_WAVE50_ACTION_EFFECTIVE_REPAIR_20261013'
old=D/'complete_action_effective_cpu_files_once.py';new=D/'complete_action_effective_identifier_reviewed_cpu_once.py'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (N/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json').exists() and not (N/'local_scope_worker.py').exists()
 try:compile(old.read_text(encoding='utf-8'),'originalCPUbuilder','exec')
 except SyntaxError as error:
  p=D/'ACTION_EFFECTIVE_ORIGINAL_CPU_IDENTIFIER_ERROR_RETAINED.json';assert not p.exists()
  p.write_text(json.dumps(dict(epoch=time.time(),original_source=str(old),original_SHA256=H(old),error_type='SyntaxError',message=error.msg,line=error.lineno,column=error.offset,
   original_traceback_text='SyntaxError: invalid decimal literal',no_CPUbuilder_statement_executed=True,no_activeworker_files_created=True,no_GPU_SDK_PPO=True),indent=2),encoding='utf-8')
 else:raise AssertionError('Expected retained originalSyntaxError')
 text=old.read_text(encoding='utf-8');needle='3060_assessment_requires_independent_ownbaseline_and_root_actuallease';assert text.count(needle)==1;text=text.replace(needle,'assessment3060_requires_independent_ownbaseline_and_root_actuallease')
 # ReversibleCPUprepared dispatch is blocked before importingTorch/Isaac, not justbeforeAppLauncher.
 needle="worker=replace(worker,\"type=int,default=1800\",\"type=int,default=3600\")"
 assert text.count(needle)==1
 extra="\n worker=replace(worker,\"D=Path(__file__).resolve().parent;C=D/'runtime/isaac/mod4';sys.path[:0]=[str(C),str(D)]\",\"D=Path(__file__).resolve().parent;C=D/'runtime/isaac/mod4';sys.path[:0]=[str(C),str(D)]\\nassert not (D/'reports/HUMAN_PAUSE_LOCAL_GPU_ACTUAL.json').exists(),'LocalGPU paused; CPUprepared only'\")"
 text=text.replace(needle,needle+extra);assert not new.exists();new.write_text(text,encoding='utf-8');py_compile.compile(str(new),doraise=True)
 runpy.run_path(str(new),run_name='__main__')
if __name__=='__main__':
 try:main()
 except BaseException:
  p=D/('ACTION_EFFECTIVE_IDENTIFIER_REVIEWED_CPU_ERROR_'+str(time.time_ns())+'.json');p.write_text(json.dumps(dict(epoch=time.time(),error=traceback.format_exc(),preGPU=True,source_sha256=H(Path(__file__))),indent=2),encoding='utf-8');raise
