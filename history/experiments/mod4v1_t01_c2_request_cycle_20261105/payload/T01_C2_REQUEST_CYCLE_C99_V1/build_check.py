"""New request-cycle mock scenarios; no old QA/robot/driver execution."""
from pathlib import Path
import json,struct,subprocess,time
H=Path(__file__).resolve().parent;R=H.parent;OUT=H/'build001'
def main():
 OUT.mkdir(exist_ok=False)
 protocol=dict(id='C2_REQUEST_CYCLE_MOCK_001',normal_request_calls=3,fault_scenarios=16,precondition_scenarios=2,
  maximum_raw_request_difference=0,arm_objects_expected=2,physics_steps=0,old_cases_read=0,
  oracle='same existing C3->C2 chain direct call; wiring only, not independent algorithm proof',
  fixture='memory-only callbacks; all binding flags synthetic declarations; high feedback velocity boundary not a dynamically consistent robot trace',
  scope='command/feedback/time/profile/one-enqueue/invalidate guards; no physical stop/delivery/atomicity/WCET/BSP claim; original inner actuation order remains external')
 (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
 result=dict(protocol_id=protocol['id'],passed=False,physics_steps=0,old_cases_read=0,full_T01_acceptance=False,arm_objects=[])
 def run(command,stem):
  start=time.perf_counter();p=subprocess.run(command,capture_output=True,text=True)
  for suffix,text in [('.stdout.log',p.stdout),('.stderr.log',p.stderr)]:
   (OUT/(stem+suffix)).write_text(text,encoding='utf8')
  result.setdefault('operations',[]).append(dict(command=list(map(str,command)),exit_code=p.returncode,wall_seconds=time.perf_counter()-start))
  if p.returncode:raise RuntimeError(stem+' failed; output preserved')
  return p.stdout
 try:
  source=H/'pc2_request_cycle.c';old=R/'SPR_AUDIT/portable_control_v3_current';exe=OUT/'request_host.exe'
  dependencies=[R/'T01_C2_SENSOR_CHAIN_C99_V1/pc2_sensor_chain.c',R/'T01_C2_TORQUE_C99_V1/pc2_balance.c',
   R/'T01_C2_REFERENCE_C99_V1/pc2_reference.c',old/'pc3_estimator.c',old/'pc3_controller.c',R/'SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.c']
  command=['C:/MinGW/bin/gcc.exe','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math',str(source),str(H/'host_check.c'),*map(str,dependencies),'-lm','-o',str(exe)]
  run(command,'native_compile');native=json.loads(run([str(exe)],'native_run'));result['native']=native
  if native['normal_request_calls']!=3 or native['fault_scenarios']!=16 or native['precondition_scenarios']!=2 or native['maximum_raw_request_difference']!=0:raise AssertionError('Predeclared counts/tolerance')
  for tag,cpu,fpu in [('m4','cortex-m4','fpv4-sp-d16'),('m7','cortex-m7','fpv5-sp-d16')]:
   output=OUT/('pc2_request_cycle_'+tag+'.o')
   run(['C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe','--target=arm-arm-none-eabi','-mcpu='+cpu,'-mthumb','-mfpu='+fpu,'-mfloat-abi=hard','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-c',str(source),'-o',str(output)],'arm_'+tag)
   with output.open('rb') as f:header=f.read(52)
   if header[:6]!=b'\x7fELF\x01\x01' or struct.unpack_from('<HH',header,16)!=(1,40):raise AssertionError('New ELF32/ET_REL/EM_ARM object header')
   result['arm_objects'].append(dict(target=tag,path=str(output),bytes=output.stat().st_size,sha256=None,elf_class=32,elf_type=1,elf_machine=40))
  result['passed']=len(result['arm_objects'])==2
 except BaseException as error:
  result['error']=repr(error);(OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');raise
 (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
