"""Only this NEW functionality: strict host compile/link with per-artifact guards."""
from pathlib import Path
import hashlib,json,subprocess,shutil,traceback
HERE=Path(__file__).resolve().parent
CC=Path('C:/MinGW/bin/gcc.exe');CXX=Path('C:/MinGW/bin/g++.exe')
FLAGS=['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 attempt=1
 while (HERE/f'revisions/host_attempt_{attempt:02d}').exists():attempt+=1
 rev=HERE/f'revisions/host_attempt_{attempt:02d}';rev.mkdir(parents=True)
 names=['fd1_detector.c','fd1_detector.h','fd1_config_fields.inc','fd1_defaults.inc','fd1_reasons.inc','fd1_reason_names.inc','fd1_replay.c','fd1_native_tests.c','fd1_reference_fixtures.h','fd1_cpp_smoke.cpp','NUMERICAL_BUDGET.json','SEMANTIC_MAPPING.md','build_fsm_host.py']
 for n in names:shutil.copy2(HERE/n,rev/n)
 receipt={'scope':'NEW_NATIVE_FSM_ONLY_NOT_BLOCKED_IO','attempt':attempt,'sources':{n:sha(HERE/n)for n in names},'commands':[],'success':False}
 rp=HERE/f'HOST_BUILD_{attempt:02d}.json'
 def save():rp.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 def run(args,tag,artifact):
  p=Path(artifact);assert not p.exists(),p
  proc=subprocess.run([str(x)for x in args],cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);log=rev/(tag+'.log');log.write_text(proc.stdout,encoding='utf-8');record={'argv':[str(x)for x in args],'exit_code':proc.returncode,'log':str(log),'artifact':str(p),'artifact_exists':p.is_file()}
  if p.is_file():record.update(bytes=p.stat().st_size,sha256=sha(p))
  receipt['commands'].append(record);save()
  if proc.returncode:raise RuntimeError('COMPILER_FAILURE '+tag)
  if not p.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT '+tag)
  print(json.dumps(record))
 try:
  objs=[]
  for n in ['fd1_detector','fd1_replay','fd1_native_tests']:
   out=rev/(n+'.o');run([CC,*FLAGS,'-I',HERE,'-c',HERE/(n+'.c'),'-o',out],n,out);objs.append(out)
  exe=HERE/'fd1_host_tests.exe';run([CC,*FLAGS,*objs,'-lm','-o',exe],'link_native_test',exe)
  cpp=rev/'fd1_cpp_smoke.o';run([CXX,*[x if x!='-std=c99'else'-std=c++11'for x in FLAGS],'-I',HERE,'-c',HERE/'fd1_cpp_smoke.cpp','-o',cpp],'cpp_compile',cpp)
  cpp_exe=HERE/'fd1_cpp_smoke.exe';run([CXX,cpp,objs[0],'-lm','-o',cpp_exe],'cpp_link',cpp_exe)
  receipt['success']=True;save()
 except Exception:
  receipt['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
