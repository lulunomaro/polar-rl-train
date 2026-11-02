"""First compile-only build of this NEW native FSM module on M4/M7 candidates."""
from pathlib import Path
import hashlib,json,subprocess,shutil,traceback
HERE=Path(__file__).resolve().parent;CC=Path('C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe');FE=CC.parent/'fromelf.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 attempt=1
 while (HERE/f'revisions/arm_attempt_{attempt:02d}').exists():attempt+=1
 if attempt>1:
  old=json.loads((HERE/f'ARM_BUILD_{attempt-1:02d}.json').read_text());assert 'MISSING_ARTIFACT'not in old.get('error',''),'Stop missing-artifact component';assert sha(HERE/'fd1_detector.c')!=old['sources']['fd1_detector.c'],'No same-source retry'
 rev=HERE/f'revisions/arm_attempt_{attempt:02d}';rev.mkdir(parents=True,exist_ok=False)
 names=['fd1_detector.c','fd1_detector.h','fd1_config_fields.inc','fd1_defaults.inc','fd1_reasons.inc','fd1_reason_names.inc','target_fd1_probe.c','build_fsm_arm.py']
 host=json.loads((HERE/'HOST_BUILD_03.json').read_text());assert host['success'];assert sha(HERE/'fd1_detector.c')==host['sources']['fd1_detector.c']
 for n in names:shutil.copy2(HERE/n,rev/n)
 report={'scope':'NEW_FSM_BINARY64_M4_M7_SP_HARD_ABI_OBJECT_ONLY_NOT_SP_ARITHMETIC_OR_RUNTIME','sources':{n:sha(HERE/n)for n in names},'commands':[],'objects':[],'success':False};receipt=HERE/f'ARM_BUILD_{attempt:02d}.json';assert not receipt.exists()
 def save():receipt.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 def run(args,log,artifact=None):
  assert not log.exists();p=subprocess.run([str(x)for x in args],cwd=HERE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace');log.write_text(p.stdout+'\nexit_code='+str(p.returncode)+'\n',encoding='utf-8');r={'argv':[str(x)for x in args],'exit_code':p.returncode,'log':str(log)}
  if artifact is not None:
   r.update(artifact=str(artifact),artifact_exists=artifact.is_file())
   if artifact.is_file():r.update(bytes=artifact.stat().st_size,sha256=sha(artifact))
  report['commands'].append(r);save()
  if p.returncode:raise RuntimeError('ARM_COMMAND_FAILURE '+str(log))
  if artifact is not None and not artifact.is_file():raise RuntimeError('MISSING_ARTIFACT_STOP_COMPONENT')
  return r
 try:
  run([CC,'--version'],HERE/f'armclang_version_{attempt:02d}.log')
  for target,cpu,fpu in [('cortex_m4_sp_hard','cortex-m4','fpv4-sp-d16'),('cortex_m7_sp_hard','cortex-m7','fpv5-sp-d16')]:
   folder=HERE/target;folder.mkdir(exist_ok=True);flags=['--target=arm-arm-none-eabi','-mthumb','-mcpu='+cpu,'-mfpu='+fpu,'-mfloat-abi=hard','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
   run([CC,*flags,'-dM','-E',HERE/'target_fd1_probe.c'],folder/f'target_macros_{attempt:02d}.log')
   out=folder/'fd1_detector.o';assert not out.exists(),'Preserve existing object';r=run([CC,*flags,'-c',HERE/'fd1_detector.c','-o',out],folder/f'compile_{attempt:02d}.log',out);report['objects'].append({'target':target,'cpu':cpu,'fpu':fpu,'abi':'hard','source':str(HERE/'fd1_detector.c'),'source_sha256':sha(HERE/'fd1_detector.c'),'object':str(out),'bytes':r['bytes'],'sha256':r['sha256']});save()
   run([FE,'--text','-v',out],folder/f'fromelf_{attempt:02d}.log')
  report['success']=True;save();print(json.dumps({'compiled_new_objects':len(report['objects']),'objects':report['objects'],'ARM_execution':0,'BSP_link':False,'WCET':False}))
 except Exception:
  report['error']=traceback.format_exc();save();raise
if __name__=='__main__':main()
