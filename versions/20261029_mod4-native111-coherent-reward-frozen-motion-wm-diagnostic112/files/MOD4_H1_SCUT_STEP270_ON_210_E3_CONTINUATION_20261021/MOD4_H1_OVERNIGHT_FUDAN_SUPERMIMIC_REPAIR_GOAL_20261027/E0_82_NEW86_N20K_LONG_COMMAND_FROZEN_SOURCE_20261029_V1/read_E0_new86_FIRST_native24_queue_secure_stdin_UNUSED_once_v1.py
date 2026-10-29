from pathlib import Path
import hashlib,importlib.util,json,sys,traceback,time
B=Path(__file__).resolve().parent
if __name__=='__main__':
 try:
  index=json.loads((B/'FROZEN_E0_82_NEW86_LONG_COMMAND_SOURCE_INDEX_V1.json').read_bytes());p=B/'run_E0_new86_readonly_secure_stdin_v1.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==index['readonly_source_SHAs'][p.name]
  s=importlib.util.spec_from_file_location('bound_E0_readonly_first',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);m.main('first')
 except BaseException:
  R=B/'reports';R.mkdir(exist_ok=True)
  with (R/('E0_FIRST_READER_ORIGINAL_LOCAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(traceback=traceback.format_exc(),no_retry=True),f,indent=2)
  raise
