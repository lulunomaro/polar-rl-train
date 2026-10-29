from pathlib import Path
import hashlib,importlib.util,json,sys,traceback,time
B=Path(__file__).resolve().parent
if __name__=='__main__':
 try:
  index=json.loads((B/'FROZEN_E2_93_NEW86_EARLY_RESAMPLE_COMPLETE_SOURCE_INDEX_V5.json').read_bytes());p=B/'run_E2_new86_readonly_secure_stdin_v4.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==index['readonly_source_SHAs'][p.name]
  s=importlib.util.spec_from_file_location('bound_E2_readonly_first',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);m.main('first')
 except BaseException:
  R=B/'reports';R.mkdir(exist_ok=True)
  with (R/('E2_FIRST_READER_ORIGINAL_LOCAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(traceback=traceback.format_exc(),no_retry=True),f,indent=2)
  raise
