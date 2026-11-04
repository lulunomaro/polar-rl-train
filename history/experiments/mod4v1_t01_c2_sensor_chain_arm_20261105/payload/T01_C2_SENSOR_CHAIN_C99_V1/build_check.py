"""Fresh C3->C2 interface smoke plus new-source ARM object compilation only."""
from pathlib import Path
import json,struct,subprocess,time
H=Path(__file__).resolve().parent;R=H.parent;OUT=H/'build001'
ARM=Path('C:/Keil_v5/ARM/ARMCLANG/bin/armclang.exe')
def main():
 OUT.mkdir(exist_ok=False)
 protocol=dict(id='C2_SENSOR_CHAIN_AND_ARM_OBJECTS_001',physics_steps=0,old_cases_read=0,
  fresh_synthetic_packet_windows=256,held_packet_views=2,normal_control_calls=258,heading_modes=[0,1],
  expected_state_and_torque_wiring_difference=0.,failure_scope='5 new glue propagation/latch scenarios plus alias/NULL/invalid explicit prior',
  counts_note='20 declared means per synthetic window are metadata, not 5120 physically collected innovations',
  arm_objects_expected=6,targets=['cortex-m4 fpv4-sp-d16 hard','cortex-m7 fpv5-sp-d16 hard'],
  boundary='No driver callbacks/frames/motor IO, no inner PD/D4/DC extra preclip; object compile is not linking/execution/WCET/BSP/HIL')
 (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2),encoding='utf8')
 result=dict(protocol_id=protocol['id'],passed=False,physics_steps=0,old_cases_read=0,full_T01_acceptance=False,arm_objects=[])
 def run(command,stem):
  start=time.perf_counter();p=subprocess.run(command,capture_output=True,text=True)
  (OUT/(stem+'.stdout.log')).write_text(p.stdout,encoding='utf8');(OUT/(stem+'.stderr.log')).write_text(p.stderr,encoding='utf8')
  receipt=dict(command=[str(s) for s in command],exit_code=p.returncode,wall_seconds=time.perf_counter()-start)
  result.setdefault('operations',[]).append(receipt)
  if p.returncode:raise RuntimeError(stem+' failed; original output preserved')
  return p.stdout
 try:
  old=R/'SPR_AUDIT/portable_control_v3_current';exe=OUT/'chain_host.exe'
  sources=[H/'pc2_sensor_chain.c',R/'T01_C2_TORQUE_C99_V1/pc2_balance.c',R/'T01_C2_REFERENCE_C99_V1/pc2_reference.c']
  command=['C:/MinGW/bin/gcc.exe','-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math',
   *map(str,sources),str(H/'host_check.c'),str(old/'pc3_estimator.c'),str(old/'pc3_controller.c'),
   str(R/'SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.c'),'-lm','-o',str(exe)]
  run(command,'native_compile');native=json.loads(run([str(exe)],'native_run'));result['native']=native
  if native['fresh_packet_windows']!=256 or native['held_packet_views']!=2 or native['control_calls']!=258 or native['max_state_difference']!=0 or native['max_torque_difference']!=0:raise AssertionError('Predeclared wiring checks')
  if not ARM.is_file():raise RuntimeError('Known ARM compiler path absent; no install/fallback attempted')
  for tag,cpu,fpu in [('m4','cortex-m4','fpv4-sp-d16'),('m7','cortex-m7','fpv5-sp-d16')]:
   target=OUT/('arm_'+tag);target.mkdir()
   for source in sources:
    output=target/(source.stem+'.o');stem=tag+'_'+source.stem
    command=[str(ARM),'--target=arm-arm-none-eabi','-mcpu='+cpu,'-mthumb','-mfpu='+fpu,'-mfloat-abi=hard',
     '-std=c99','-O2','-Wall','-Wextra','-Werror','-fno-fast-math','-c',str(source),'-o',str(output)]
    run(command,stem)
    with output.open('rb') as f:header=f.read(52)
    if header[:6]!=b'\x7fELF\x01\x01':raise AssertionError('Expected ELF32 little-endian new object')
    typ,machine=struct.unpack_from('<HH',header,16)
    if typ!=1 or machine!=40:raise AssertionError('Expected ET_REL/EM_ARM')
    result['arm_objects'].append(dict(target=tag,source=str(source),path=str(output),bytes=output.stat().st_size,
     elf_class=32,elf_type=typ,elf_machine=machine,sha256=None,note='Only 52-byte new-object header inspected; no final link/runtime/WCET assertion'))
  result['passed']=len(result['arm_objects'])==6
 except BaseException as error:
  result['error']=repr(error);(OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');raise
 (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
