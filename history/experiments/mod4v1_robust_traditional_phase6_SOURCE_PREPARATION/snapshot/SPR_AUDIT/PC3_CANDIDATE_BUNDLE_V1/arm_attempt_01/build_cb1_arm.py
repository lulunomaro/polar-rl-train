"""First scheduled compile-only pass, NEW CB1 source only, no old-core rebuild."""
from pathlib import Path
import hashlib,json,shutil,subprocess,traceback
HERE=Path(__file__).resolve().parent;CC=Path('C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe');FE=CC.with_name('fromelf.exe')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rec=HERE/'ARM_BUILD_01.json';assert not rec.exists();host=json.loads((HERE/'HOST_BUILD_02.json').read_bytes());assert host['success']
 for n in ('cb1_candidate.c','cb1_candidate.h'):assert sha(HERE/n)==host['sources'][n]
 rev=HERE/'arm_attempt_01';rev.mkdir(exist_ok=False)
 for n in ('cb1_candidate.c','cb1_candidate.h','target_cb1_probe.c','build_cb1_arm.py'):shutil.copy2(HERE/n,rev/n)
 r=dict(scope='NEW_CB1_ONLY_M4_M7_OBJECTS_NO_LINK_OR_EXECUTION',sources={n:sha(HERE/n)for n in ('cb1_candidate.c','cb1_candidate.h')},commands=[],objects=[],success=False,old_C3_C2_rebuilt_for_ARM=False,BSP_link=False,ARM_execution=0,WCET=False)
 def save():rec.write_text(json.dumps(r,indent=2),encoding='utf-8')
 def run(args,log,artifact=None):
  with log.open('xb')as f:p=subprocess.run([str(x)for x in args],cwd=HERE,stdout=f,stderr=subprocess.STDOUT)
  c=dict(argv=[str(x)for x in args],exit_code=p.returncode,log=str(log))
  if artifact is not None:
   c.update(artifact=str(artifact),artifact_exists=artifact.is_file())
   if artifact.is_file():c.update(bytes=artifact.stat().st_size,sha256=sha(artifact))
  r['commands'].append(c);save()
  if p.returncode:raise RuntimeError('ARM_COMMAND_FAILURE '+str(log))
  if artifact is not None and not artifact.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT')
  return c
 try:
  run([CC,'--version'],rev/'armclang_version.log')
  for name,cpu,fpu in [('cortex_m4_sp_hard','cortex-m4','fpv4-sp-d16'),('cortex_m7_sp_hard','cortex-m7','fpv5-sp-d16')]:
   folder=HERE/name;folder.mkdir(exist_ok=False)
   flags=['--target=arm-arm-none-eabi','-mthumb','-mcpu='+cpu,'-mfpu='+fpu,'-mfloat-abi=hard','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
   run([CC,*flags,'-dM','-E',HERE/'target_cb1_probe.c'],folder/'target_macros.log')
   obj=folder/'cb1_candidate.o';c=run([CC,*flags,'-c',HERE/'cb1_candidate.c','-o',obj],folder/'compile.log',obj)
   r['objects'].append(dict(target=name,cpu=cpu,fpu=fpu,abi='hard',source_sha=sha(HERE/'cb1_candidate.c'),object=str(obj),bytes=c['bytes'],sha256=c['sha256']));save()
   run([FE,'--text','-v',obj],folder/'fromelf.log')
  r['success']=True;save();print(json.dumps(dict(success=True,new_objects=r['objects'],ARM_execution=0,BSP_link=False,WCET=False),indent=2))
 except BaseException:r['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
