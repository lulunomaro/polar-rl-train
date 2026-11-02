"""One scheduled M4/M7 compile-only pass for current new power source."""
from pathlib import Path
import hashlib,json,shutil,subprocess,traceback
HERE=Path(__file__).resolve().parent;CC=Path('C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe');FE=CC.with_name('fromelf.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    receipt=HERE/'ARM_BUILD_01.json';assert not receipt.exists()
    host=json.loads((HERE/'HOST_BUILD_02.json').read_bytes());comparison=json.loads((HERE/'COMPARISON_02.json').read_bytes())
    assert host['success']and comparison['numerical_failures']==comparison['native_failures']==0 and comparison['CPP_pass']
    for n in ('pa1_allocator.c','pa1_allocator.h'):assert sha(HERE/n)==host['sources'][n]
    rev=HERE/'arm_attempt_01';rev.mkdir(exist_ok=False)
    names=['pa1_allocator.c','pa1_allocator.h','target_pa1_probe.c','build_pa1_arm.py']
    for n in names:shutil.copy2(HERE/n,rev/n)
    report=dict(scope='NEW_POWER_BINARY64_M4_M7_SP_HARD_ABI_COMPILE_ONLY',sources={n:sha(HERE/n)for n in names},commands=[],objects=[],success=False,ARM_execution=0,BSP_link=False,WCET=False)
    def save():receipt.write_text(json.dumps(report,indent=2),encoding='utf-8')
    def run(args,log,artifact=None):
        assert not log.exists();p=subprocess.run([str(x)for x in args],cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace')
        log.write_text(p.stdout+'\nexit_code='+str(p.returncode)+'\n',encoding='utf-8');r=dict(argv=[str(x)for x in args],exit_code=p.returncode,log=str(log))
        if artifact is not None:
            r.update(artifact=str(artifact),artifact_exists=artifact.is_file())
            if artifact.is_file():r.update(bytes=artifact.stat().st_size,sha256=sha(artifact))
        report['commands'].append(r);save()
        if p.returncode:raise RuntimeError('ARM_COMMAND_FAILURE '+str(log))
        if artifact is not None and not artifact.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT')
        return r
    try:
        run([CC,'--version'],rev/'armclang_version.log')
        for name,cpu,fpu in [('cortex_m4_sp_hard','cortex-m4','fpv4-sp-d16'),('cortex_m7_sp_hard','cortex-m7','fpv5-sp-d16')]:
            folder=HERE/name;folder.mkdir(exist_ok=False)
            flags=['--target=arm-arm-none-eabi','-mthumb','-mcpu='+cpu,'-mfpu='+fpu,'-mfloat-abi=hard','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
            run([CC,*flags,'-dM','-E',HERE/'target_pa1_probe.c'],folder/'target_macros.log')
            obj=folder/'pa1_allocator.o';r=run([CC,*flags,'-c',HERE/'pa1_allocator.c','-o',obj],folder/'compile.log',obj)
            report['objects'].append(dict(target=name,cpu=cpu,fpu=fpu,abi='hard',source_SHA=sha(HERE/'pa1_allocator.c'),object=str(obj),bytes=r['bytes'],sha256=r['sha256']));save()
            run([FE,'--text','-v',obj],folder/'fromelf.log')
        report['success']=True;save();print(json.dumps(dict(new_objects=len(report['objects']),objects=report['objects'],ARM_execution=0,BSP_link=False,WCET=False),indent=2))
    except BaseException:report['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
