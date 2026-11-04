"""Sole extra query, exactly '--cpu list' explicitly documented by actual help line35."""
from pathlib import Path
import json,subprocess,time,hashlib
O=Path(__file__).resolve().parent
T=Path(r'C:\Keil_v5\ARM\ARMCC\bin\armasm.exe')
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def main():
 h=json.loads((O/'QUERY_MIN_01.json').read_bytes());assert h['rc']==0 and h['actual_native_calls']==1
 text=(O/'armasm_help_stdout.log').read_text(encoding='utf-8');assert '--cpu list' in text and 'Cortex-M4.fp' not in text
 s=dict(status='CPU_LIST_RESERVED_NATIVE2_BEFORE_CALL',native_sequence=2,total_native_maximum=2,argv=[str(T),'--cpu','list'],cwd=str(O),reason='Actual --help line35 explicitly documents --cpu list; exact Cortex-M4.fp spelling is not given in help and remains unknown.',documented_help=rec(O/'armasm_help_stdout.log'),source_refs=[rec(O/'PARENT_SCOPE.json'),rec(O/'METHOD.md'),rec(Path(__file__).resolve())],source_arguments=[],object_output_arguments=[],rc=None)
 with (O/'CPU_QUERY_MIN_01.json').open('x',encoding='utf-8') as f:json.dump(s,f,ensure_ascii=False,indent=2);f.write('\n')
 with (O/'QUERY_LEDGER_01.jsonl').open('a',encoding='utf-8',newline='\n') as log:
  log.write(json.dumps(s,ensure_ascii=False)+'\n');log.flush();start=time.monotonic_ns()
  try:
   with (O/'armasm_cpu_list_stdout.log').open('xb') as out,(O/'armasm_cpu_list_stderr.log').open('xb') as err:
    p=subprocess.run(s['argv'],cwd=str(O),stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False,check=False)
   s.update(status='CPU_LIST_RETURNED_SAVED_BEFORE_INTERPRETATION',rc=p.returncode,exception=None)
  except Exception as e:s.update(status='CPU_LIST_EXCEPTION_STOP_NO_THIRD_QUERY',exception=repr(e))
  s.update(elapsed_ns=time.monotonic_ns()-start,total_native_calls=2,third_native_prohibited=True,assembly_calls=0,stdout_record=rec(O/'armasm_cpu_list_stdout.log') if (O/'armasm_cpu_list_stdout.log').exists() else None,stderr_record=rec(O/'armasm_cpu_list_stderr.log') if (O/'armasm_cpu_list_stderr.log').exists() else None)
  with (O/'CPU_QUERY_MIN_01.json').open('w',encoding='utf-8') as f:json.dump(s,f,ensure_ascii=False,indent=2);f.write('\n');f.flush()
  log.write(json.dumps(s,ensure_ascii=False)+'\n');log.flush();print(json.dumps(s,ensure_ascii=False))
  return 0 if s.get('rc')==0 else 1
if __name__=='__main__':raise SystemExit(main())
