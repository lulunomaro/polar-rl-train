"""Post-call receipt from the exact recorded host build invocation; no rebuild."""
from pathlib import Path
import json,hashlib,struct
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (HERE/'BUILD_RECEIPT.json').exists()
 args=['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse','p25_host_adapter.c','..\\portable_control_v3_current\\pc3_estimator.c','..\\portable_control_v3_current\\pc3_controller.c','..\\portable_control_v3_current\\pc3_dispatch.c','..\\portable_core_v2_kinematics\\ct_kinematics.c','-lm','-o','p25_host_adapter.exe']
 sources=[]
 for name in ['p25_host_adapter.c','io_protocol.h','p25_stdio.py','PROTOCOL_SCHEMA.json','DEFAULT_INIT_P25.json','../portable_control_v3_current/pc3_control.h','../portable_control_v3_current/pc3_estimator.c','../portable_control_v3_current/pc3_controller.c','../portable_control_v3_current/pc3_dispatch.c','../portable_control_v3_current/pc3_p25_data.h','../portable_core_v2_kinematics/ct_kinematics.c','../portable_core_v2_kinematics/ct_kinematics.h']:
  p=(HERE/name).resolve();sources.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
 exe=HERE/'p25_host_adapter.exe';data=exe.read_bytes();pe=struct.unpack_from('<I',data,0x3c)[0]
 receipt={'mode':'LOCAL_STDIO_RESIDENT_HOST_P25_NOT_BSP_FIRMWARE','compiler':r'C:\MinGW\bin\gcc.exe','compiler_version_log':'gcc_version_01.log','compiler_target_log':'gcc_target_01.log','working_directory':str(HERE),'exact_arguments':args,'raw_build_log':'build_01.log','exit_code':0,
          'capture':'recorded after the call from exact tool invocation; this program did not rebuild','read_only_sources_and_protocol':sources,
          'executable':{'path':str(exe),'bytes':exe.stat().st_size,'sha256':sha(exe),'PE_machine_hex':hex(struct.unpack_from('<H',data,pe+4)[0]),'optional_magic_hex':hex(struct.unpack_from('<H',data,pe+24)[0])},
          'transport':'ASCII stdin/stdout, no binary struct layout','hardware_binding':False,'ARM_execution':False,'physics_steps':0,'PH3':'pending'}
 (HERE/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt['executable']))
if __name__=='__main__':main()
