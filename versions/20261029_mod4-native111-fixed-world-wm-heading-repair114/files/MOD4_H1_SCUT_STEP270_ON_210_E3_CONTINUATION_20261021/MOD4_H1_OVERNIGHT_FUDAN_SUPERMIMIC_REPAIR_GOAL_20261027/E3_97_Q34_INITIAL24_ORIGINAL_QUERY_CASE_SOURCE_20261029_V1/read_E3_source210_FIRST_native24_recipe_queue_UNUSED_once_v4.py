from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent
if __name__=='__main__':
 try:
  index=json.loads((B/'FROZEN_E3_Q34_INITIAL24_COMPLETE_SOURCE_INDEX_V1.json').read_bytes());p=B/'run_E3_source210_readonly_v4.py';assert hashlib.sha256(p.read_bytes()).hexdigest()==index['local_source_SHAs'][p.name];s=importlib.util.spec_from_file_location('bound_E3_source210_first',p);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);m.main('first')
 except BaseException:
  R=B/'reports';R.mkdir(exist_ok=True)
  with (R/('E3_FIRST_ORIGINAL_LOCAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_retry=True),f,indent=2)
  raise
