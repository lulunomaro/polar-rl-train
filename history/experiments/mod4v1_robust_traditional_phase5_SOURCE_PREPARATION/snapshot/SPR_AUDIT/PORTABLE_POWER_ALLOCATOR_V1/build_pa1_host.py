"""Strict native/CPP build and one bounded execution per new source attempt."""
from pathlib import Path
import hashlib,json,shutil,subprocess,traceback
HERE=Path(__file__).resolve().parent;CC=Path('C:/MinGW/bin/gcc.exe');CPP=CC.with_name('g++.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    attempt=1
    while(HERE/f'HOST_BUILD_{attempt:02d}.json').exists():attempt+=1
    if attempt>1:
        old=json.loads((HERE/f'HOST_BUILD_{attempt-1:02d}.json').read_bytes())
        assert 'MISSING_ARTIFACT'not in old.get('error',''),'Stop missing-artifact component, no rebuild workaround'
        assert any(sha(HERE/n)!=v for n,v in old['sources'].items()if n.endswith(('.c','.h','.cpp'))),'No same-source retry'
    rev=HERE/f'host_attempt_{attempt:02d}';rev.mkdir(exist_ok=False)
    names=['pa1_allocator.c','pa1_allocator.h','pa1_test_common.h','pa1_cases_host.c','pa1_native_tests.c','pa1_cpp_smoke.cpp','pa1_cases.h','NUMERICAL_BUDGET.json','MODEL_CONTRACT.json','build_pa1_host.py']
    for n in names:shutil.copy2(HERE/n,rev/n)
    report=dict(scope='NEW_POWER_FIXED6_BINARY64_NATIVE_AND_CPP_ONLY',sources={n:sha(HERE/n)for n in names},commands=[],success=False,physics_steps=0)
    receipt=HERE/f'HOST_BUILD_{attempt:02d}.json'
    def save():receipt.write_text(json.dumps(report,indent=2),encoding='utf-8')
    def run(args,log,artifact=None):
        assert not log.exists();p=subprocess.run([str(x)for x in args],cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
        log.write_text(p.stdout+'\nexit_code='+str(p.returncode)+'\n',encoding='utf-8');r=dict(argv=[str(x)for x in args],exit_code=p.returncode,log=str(log))
        if artifact is not None:
            r.update(artifact=str(artifact),artifact_exists=artifact.is_file())
            if artifact.is_file():r.update(bytes=artifact.stat().st_size,sha256=sha(artifact))
        report['commands'].append(r);save()
        if p.returncode:raise RuntimeError('COMMAND_FAILURE '+str(log))
        if artifact is not None and not artifact.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT')
        return r
    flags=['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
    cppflags=['-std=c++11']+flags[1:]
    try:
        run([CC,'--version'],rev/'gcc_version.log');run([CPP,'--version'],rev/'gpp_version.log')
        for source in ('pa1_allocator.c','pa1_cases_host.c','pa1_native_tests.c'):
            run([CC,*flags,'-c',HERE/source,'-o',rev/(Path(source).stem+'.o')],rev/(Path(source).stem+'_compile.log'),rev/(Path(source).stem+'.o'))
        run([CPP,*cppflags,'-c',HERE/'pa1_cpp_smoke.cpp','-o',rev/'pa1_cpp_smoke.o'],rev/'cpp_compile.log',rev/'pa1_cpp_smoke.o')
        exes=[]
        for name,driver,compiler in [('pa1_cases_host','pa1_cases_host.o',CC),('pa1_native_tests','pa1_native_tests.o',CC),('pa1_cpp_smoke','pa1_cpp_smoke.o',CPP)]:
            exe=rev/(name+'.exe');r=run([compiler,rev/'pa1_allocator.o',rev/driver,'-lm','-o',exe],rev/(name+'_link.log'),exe);exes.append((name,exe,r['sha256']))
        for name,exe,wanted in exes:
            if not exe.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT')
            assert sha(exe)==wanted
            if name=='pa1_cases_host':
                raw=HERE/f'C_RUNS_{attempt:02d}.jsonl';assert not raw.exists()
                with raw.open('xb')as f:p=subprocess.run([str(exe)],cwd=HERE,stdout=f,stderr=subprocess.PIPE)
                report['commands'].append(dict(argv=[str(exe)],exit_code=p.returncode,raw_output=str(raw),raw_sha256=sha(raw),stderr=p.stderr.decode(errors='replace')));save()
                if p.returncode:raise RuntimeError('CASE_DRIVER_FAILURE')
            elif name=='pa1_native_tests':run([exe,HERE/f'NATIVE_CLOCK_CASES_{attempt:02d}.csv'],HERE/f'native_run_{attempt:02d}.log')
            else:run([exe],HERE/f'cpp_run_{attempt:02d}.log')
            if not exe.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT')
            assert sha(exe)==wanted
        report['success']=True;save();print(json.dumps(dict(status='HOST_COMPILED_AND_NATIVE_CPP_EXECUTED_NUMERIC_GRADING_PENDING',attempt=attempt,commands=len(report['commands']),executables=[dict(name=n,path=str(e),sha256=h,bytes=e.stat().st_size)for n,e,h in exes],physics_steps=0),indent=2))
    except BaseException:
        report['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
