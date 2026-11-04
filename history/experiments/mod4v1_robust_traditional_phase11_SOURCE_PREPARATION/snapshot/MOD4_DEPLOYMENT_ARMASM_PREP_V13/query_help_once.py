"""Exactly one approved trusted ARMASM --help call; never takes source/output arguments."""
from pathlib import Path
import json,hashlib,subprocess,time
O=Path(__file__).resolve().parent
TOOL=Path(r'C:\Keil_v5\ARM\ARMCC\bin\armasm.exe')
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def dump(p,x):
 with p.open('w',encoding='utf-8',newline='\n') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n');f.flush()
def main():
 ledger=O/'QUERY_LEDGER_01.jsonl'
 with ledger.open('x',encoding='utf-8',newline='\n') as log:
  status=dict(status='HELP_RESERVED_BEFORE_NATIVE',native_sequence=1,max_native=2,argv=[str(TOOL),'--help'],cwd=str(O),source_arguments=[],output_object_arguments=[],source_refs=[rec(O/'PARENT_SCOPE.json'),rec(O/'METHOD.md'),rec(Path(__file__).resolve())],stdout=str(O/'armasm_help_stdout.log'),stderr=str(O/'armasm_help_stderr.log'),rc=None)
  dump(O/'QUERY_MIN_01.json',status);log.write(json.dumps(status,ensure_ascii=False)+'\n');log.flush()
  assert TOOL.is_file()
  start=time.monotonic_ns()
  try:
   with (O/'armasm_help_stdout.log').open('xb') as stdout,(O/'armasm_help_stderr.log').open('xb') as stderr:
    cp=subprocess.run(status['argv'],cwd=str(O),stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,shell=False,check=False)
   status.update(status='HELP_RETURNED_SAVED_BEFORE_INTERPRETATION',rc=cp.returncode,exception=None)
  except Exception as e:status.update(status='HELP_NATIVE_EXCEPTION_STOP',exception=repr(e))
  status.update(elapsed_ns=time.monotonic_ns()-start,actual_native_calls=1,stdout_record=rec(O/'armasm_help_stdout.log') if (O/'armasm_help_stdout.log').is_file() else None,stderr_record=rec(O/'armasm_help_stderr.log') if (O/'armasm_help_stderr.log').is_file() else None,extra_native_not_authorized_by_this_helper=True,assembly_calls=0)
  dump(O/'QUERY_MIN_01.json',status);log.write(json.dumps(status,ensure_ascii=False)+'\n');log.flush()
  print(json.dumps(status,ensure_ascii=False));return 0 if status.get('rc')==0 else 1
if __name__=='__main__':raise SystemExit(main())
