"""One scheduled new-component native/CPP pass; artifact absence stops this line."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,traceback
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CC=Path('C:/MinGW/bin/gcc.exe');CPP=CC.with_name('g++.exe')
NEW=['cb1_candidate.c','cb1_candidate.h','cb1_cases.h','cb1_cases_host.c','cb1_native_tests.c','cb1_toy.h','cb1_cpp_smoke.cpp','build_cb1_host.py','NUMERICAL_BUDGET.json']
DEPS=[HERE.parent/'portable_control_v3_current'/n for n in ('pc3_estimator.c','pc3_controller.c')]+[HERE.parent/'portable_core_v2_kinematics/ct_kinematics.c']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 attempt=sys.argv[1]if len(sys.argv)>1 else '01';receipt=HERE/('HOST_BUILD_'+attempt+'.json');assert not receipt.exists()
 if attempt!='01':
  prev=json.loads((HERE/('HOST_BUILD_'+str(int(attempt)-1).zfill(2)+'.json')).read_bytes())
  assert not any(c.get('artifact_exists')is False and c['exit_code']==0 for c in prev['commands']),'MISSING_ARTIFACT_STOP_COMPONENT'
  assert any(sha(HERE/n)!=v for n,v in prev['sources'].items()if n.endswith(('.c','.h','.cpp'))),'NO_REBUILD_WITHOUT_GENUINE_SOURCE_CHANGE'
 freeze=json.loads((HERE/'SOURCE_REFERENCES.json').read_bytes());assert sha(HERE/'NUMERICAL_BUDGET.json')==freeze['pre_core_contracts']['NUMERICAL_BUDGET.json']
 rev=HERE/('host_attempt_'+attempt);rev.mkdir(exist_ok=False)
 for n in NEW:shutil.copy2(HERE/n,rev/n)
 r=dict(scope='NEW_IN_PROCESS_CB1_ONLY_NO_OLD_RUNNER_SDK',attempt=attempt,sources={n:sha(HERE/n)for n in NEW},dependencies={p.relative_to(ROOT).as_posix():sha(p)for p in DEPS},commands=[],success=False,physics=0,send_or_enqueue=0)
 def save():receipt.write_text(json.dumps(r,indent=2),encoding='utf-8')
 def run(args,name,artifact=None,outfile=None):
  out=rev/(outfile or name+'.stdout.log');err=rev/(name+'.stderr.log');assert not out.exists()and not err.exists()
  with out.open('xb')as fo,err.open('xb')as fe:p=subprocess.run([str(x)for x in args],cwd=HERE,stdout=fo,stderr=fe)
  c=dict(argv=[str(x)for x in args],exit_code=p.returncode,stdout=str(out),stderr=str(err))
  if artifact is not None:
   c.update(artifact=str(artifact),artifact_exists=artifact.is_file())
   if artifact.is_file():c.update(bytes=artifact.stat().st_size,sha256=sha(artifact))
  r['commands'].append(c);save()
  if p.returncode:raise RuntimeError('COMMAND_FAILURE '+name)
  if artifact is not None and not artifact.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT '+str(artifact))
  return out
 try:
  run([CC,'--version'],'gcc_version')
  common=['-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
  sources=[HERE/'cb1_candidate.c',*DEPS,HERE/'cb1_cases_host.c',HERE/'cb1_native_tests.c']
  objects=[]
  for src in sources:
   obj=rev/(src.stem+'.o');run([CC,'-std=c99',*common,'-c',src,'-o',obj],'compile_'+src.stem,obj);objects.append(obj)
  core=objects[:4]
  for name,obj in [('cb1_cases_host',objects[4]),('cb1_native_tests',objects[5])]:
   exe=rev/(name+'.exe');run([CC,*common,*core,obj,'-lm','-o',exe],'link_'+name,exe)
  cpp_obj=rev/'cb1_cpp_smoke.o';run([CPP,'-std=c++11',*common,'-c',HERE/'cb1_cpp_smoke.cpp','-o',cpp_obj],'compile_cpp',cpp_obj)
  cpp_exe=rev/'cb1_cpp_smoke.exe';run([CPP,*common,*core,cpp_obj,'-lm','-o',cpp_exe],'link_cpp',cpp_exe)
  run([rev/'cb1_cases_host.exe'],'run_cases',outfile='CANDIDATE_RUNS.jsonl')
  run([rev/'cb1_native_tests.exe'],'run_native',outfile='CLOCK_INSERTIONS.csv')
  run([cpp_exe],'run_cpp')
  nm=CC.with_name('nm.exe');run([nm,'-u',core[0]],'new_core_undefined_symbols')
  for obj in core:
   assert obj.is_file()
  r['success']=True;save();print(json.dumps(dict(success=True,attempt=attempt,commands=len(r['commands']),host_folder=str(rev)),indent=2))
 except BaseException:r['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
