"""Exact failed-test-oracle revision only. Reuse first3200 pass, do not rerun it.
Compile only the changed new native test, link its unchanged four C objects;
first actual CPP execution then undefined-symbol inventory. No old code run.
"""
from pathlib import Path
import hashlib,json,shutil,subprocess,traceback
HERE=Path(__file__).resolve().parent;CC=Path('C:/MinGW/bin/gcc.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rec=HERE/'HOST_BUILD_02.json';assert not rec.exists();old=json.loads((HERE/'HOST_BUILD_01.json').read_bytes());first=HERE/'host_attempt_01'
 for n,h in old['sources'].items():
  if n!='cb1_native_tests.c':assert sha(HERE/n)==h,(n,'UNCHANGED_CORE_CASES_BUDGET_COMPILER')
 assert sha(HERE/'cb1_native_tests.c')!=old['sources']['cb1_native_tests.c']
 for c in old['commands']:
  if 'artifact'in c:
   assert c['exit_code']==0 and c['artifact_exists']and Path(c['artifact']).is_file(),'MISSING_ARTIFACT_STOP_COMPONENT'
   assert sha(Path(c['artifact']))==c['sha256'],'CHANGED_ARTIFACT_STOP_COMPONENT'
 case=next(c for c in old['commands']if Path(c['stdout']).name=='CANDIDATE_RUNS.jsonl');assert case['exit_code']==0
 rev=HERE/'host_attempt_02';rev.mkdir(exist_ok=False)
 for n in ('cb1_native_tests.c','retest_cb1_native.py'):shutil.copy2(HERE/n,rev/n)
 core=[first/(n+'.o')for n in ('cb1_candidate','pc3_estimator','pc3_controller','ct_kinematics')]
 report=dict(scope='FAILED_NEW_NATIVE_ORACLE_ONLY_RETEST_AND_FIRST_CPP_EXECUTION',sources={n:sha(HERE/n)for n in old['sources']},retest_script_sha=sha(Path(__file__)),unchanged_core_objects={str(p):sha(p)for p in core},reused_case_output=str(first/'CANDIDATE_RUNS.jsonl'),reused_case_sha=sha(first/'CANDIDATE_RUNS.jsonl'),cases_rerun=0,commands=[],success=False)
 def save():rec.write_text(json.dumps(report,indent=2),encoding='utf-8')
 def run(args,name,artifact=None,stdout=None):
  fo=rev/(stdout or name+'.stdout.log');fe=rev/(name+'.stderr.log')
  with fo.open('xb')as out,fe.open('xb')as err:p=subprocess.run([str(x)for x in args],cwd=HERE,stdout=out,stderr=err)
  c=dict(argv=[str(x)for x in args],exit_code=p.returncode,stdout=str(fo),stderr=str(fe))
  if artifact is not None:
   c.update(artifact=str(artifact),artifact_exists=artifact.is_file())
   if artifact.is_file():c.update(bytes=artifact.stat().st_size,sha256=sha(artifact))
  report['commands'].append(c);save()
  if p.returncode:raise RuntimeError('COMMAND_FAILURE '+name)
  if artifact is not None and not artifact.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT')
 try:
  flags=['-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
  obj=rev/'cb1_native_tests.o';exe=rev/'cb1_native_tests.exe'
  run([CC,'-std=c99',*flags,'-c',HERE/'cb1_native_tests.c','-o',obj],'compile_native',obj)
  run([CC,*flags,*core,obj,'-lm','-o',exe],'link_native',exe)
  run([exe],'run_native',stdout='CLOCK_INSERTIONS.csv')
  run([first/'cb1_cpp_smoke.exe'],'run_cpp')
  run([CC.with_name('nm.exe'),'-u',core[0]],'new_core_undefined_symbols')
  report['success']=True;save();print(json.dumps(dict(success=True,commands=len(report['commands']),cases_rerun=0,core_recompiled=False,CPP_first_actual_run=True),indent=2))
 except BaseException:report['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
