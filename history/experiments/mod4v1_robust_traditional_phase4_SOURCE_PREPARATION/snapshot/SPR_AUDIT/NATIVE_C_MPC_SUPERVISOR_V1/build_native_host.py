"""Only new in-process core/tests. Each expected artifact is mandatory."""
from pathlib import Path
import hashlib,json,subprocess,shutil,traceback
HERE=Path(__file__).resolve().parent;AS=HERE.parent/'ACTIVE_BOX_QP_V3';CC=Path('C:/MinGW/bin/gcc.exe');CXX=CC.parent/'g++.exe'
FLAGS=['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 attempt=1
 while(HERE/f'revisions/host_attempt_{attempt:02d}').exists():attempt+=1
 if attempt>1:
  old=json.loads((HERE/f'HOST_BUILD_{attempt-1:02d}.json').read_text());assert 'MISSING_ARTIFACT'not in old.get('error',''),'Stop missing-artifact line';assert sha(HERE/'nm1_supervisor.c')!=old['sources']['nm1_supervisor.c']or sha(HERE/'nm1_host_tests.c')!=old['sources']['nm1_host_tests.c'],'No same-source retry'
  if old['success']:
   for r in old['commands']:
    p=Path(r['artifact'])
    if p.parent==HERE and p.suffix=='.exe':assert p.is_file()and sha(p)==r['sha256'];shutil.copy2(p,HERE/f'revisions/host_attempt_{attempt-1:02d}'/p.name)
 rev=HERE/f'revisions/host_attempt_{attempt:02d}';rev.mkdir(parents=True,exist_ok=False)
 names=['nm1_supervisor.c','nm1_supervisor.h','nm1_model.c','nm1_model.h','nm1_host_tests.c','nm1_fixtures.h','nm1_cpp_smoke.cpp','NUMERICAL_BUDGET.json','SEMANTIC_MAPPING.md','build_native_host.py']
 for n in names:shutil.copy2(HERE/n,rev/n)
 report=dict(scope='NEW_INPROCESS_NATIVE_ONLY_NO_OLD_IO',sources={n:sha(HERE/n)for n in names},sealed_ASQP_source_sha=sha(AS/'active_box_qp.c'),commands=[],success=False);rp=HERE/f'HOST_BUILD_{attempt:02d}.json'
 def save():rp.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 def run(args,tag,out):
  assert not out.exists()or(out.parent==HERE and attempt>1 and old['success']);p=subprocess.run([str(x)for x in args],cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);log=rev/(tag+'.log');log.write_text(p.stdout,encoding='utf-8');r=dict(argv=[str(x)for x in args],exit_code=p.returncode,log=str(log),artifact=str(out),artifact_exists=out.is_file())
  if out.is_file():r.update(bytes=out.stat().st_size,sha256=sha(out))
  report['commands'].append(r);save();print(json.dumps(r))
  if p.returncode:raise RuntimeError('COMPILER_FAILURE '+tag)
  if not out.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT '+tag)
 try:
  objects=[]
  for name,src in [('nm1_supervisor',HERE/'nm1_supervisor.c'),('nm1_model',HERE/'nm1_model.c'),('sealed_asqp',AS/'active_box_qp.c'),('nm1_host_tests',HERE/'nm1_host_tests.c')]:
   out=rev/(name+'.o');run([CC,*FLAGS,'-I',HERE,'-c',src,'-o',out],name,out);objects.append(out)
  run([CC,*FLAGS,*objects,'-lm','-o',HERE/'nm1_host_tests.exe'],'native_link',HERE/'nm1_host_tests.exe')
  cpp=rev/'nm1_cpp_smoke.o';run([CXX,*[a if a!='-std=c99'else'-std=c++11'for a in FLAGS],'-I',HERE,'-c',HERE/'nm1_cpp_smoke.cpp','-o',cpp],'cpp_compile',cpp)
  run([CXX,cpp,*objects[:3],'-lm','-o',HERE/'nm1_cpp_smoke.exe'],'cpp_link',HERE/'nm1_cpp_smoke.exe');report['success']=True;save()
 except Exception:report['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
