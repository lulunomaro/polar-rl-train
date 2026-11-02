"""New two-module compile-only objects; old sealed ASQP target objects not rebuilt."""
from pathlib import Path
import json,hashlib,subprocess,shutil,traceback
HERE=Path(__file__).resolve().parent;CC=Path('C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe');FE=CC.parent/'fromelf.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rev=HERE/'revisions/arm_attempt_01';rev.mkdir(parents=True,exist_ok=False);names=['nm1_supervisor.c','nm1_supervisor.h','nm1_model.c','nm1_model.h','target_nm1_probe.c','build_native_arm.py']
 host=json.loads((HERE/'HOST_BUILD_01.json').read_text());assert host['success']
 for n in names:
  if n in host['sources']:assert sha(HERE/n)==host['sources'][n]
  shutil.copy2(HERE/n,rev/n)
 report=dict(scope='NEW_SUPERVISOR_AND_CONST_MODEL_M4_M7_OBJECTS_ONLY',sources={n:sha(HERE/n)for n in names},commands=[],objects=[],success=False);rp=HERE/'ARM_BUILD_01.json';assert not rp.exists()
 def save():rp.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 def run(args,log,out=None):
  assert not log.exists();p=subprocess.run([str(x)for x in args],cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace');log.write_text(p.stdout+'\nexit_code='+str(p.returncode)+'\n',encoding='utf-8');r=dict(argv=[str(x)for x in args],exit_code=p.returncode,log=str(log))
  if out is not None:
   r.update(artifact=str(out),artifact_exists=out.is_file())
   if out.is_file():r.update(bytes=out.stat().st_size,sha256=sha(out))
  report['commands'].append(r);save()
  if p.returncode:raise RuntimeError('ARM_COMMAND_FAILURE '+str(log))
  if out is not None and not out.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT')
  return r
 try:
  run([CC,'--version'],HERE/'armclang_version_01.log')
  for target,cpu,fpu in [('cortex_m4_sp_hard','cortex-m4','fpv4-sp-d16'),('cortex_m7_sp_hard','cortex-m7','fpv5-sp-d16')]:
   d=HERE/target;d.mkdir(exist_ok=False);flags=['--target=arm-arm-none-eabi','-mthumb','-mcpu='+cpu,'-mfpu='+fpu,'-mfloat-abi=hard','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
   run([CC,*flags,'-dM','-E',HERE/'target_nm1_probe.c'],d/'target_macros_01.log')
   for name in ['nm1_supervisor','nm1_model']:
    out=d/(name+'.o');r=run([CC,*flags,'-c',HERE/(name+'.c'),'-o',out],d/(name+'_compile_01.log'),out);report['objects'].append(dict(target=target,cpu=cpu,fpu=fpu,abi='hard',source=str(HERE/(name+'.c')),source_sha256=sha(HERE/(name+'.c')),object=str(out),bytes=r['bytes'],sha256=r['sha256']));save();run([FE,'--text','-v',out],d/(name+'_fromelf_01.log'))
  report['success']=True;save();print(json.dumps(dict(new_objects=len(report['objects']),objects=report['objects'],ARM_execution=0,BSP_link=False,WCET=False)))
 except Exception:report['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
