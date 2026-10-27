"""UNUSED pin-bound entry. Original collector owns both unchanged900 assertions."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
D=Path(__file__).resolve().parent
BINDING_SHA='6f73a2fb97230286b65a8d89726705025f1a905ba146a576305fa56d96063a5d'
def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def validate_bound_files():
 p=D/'ACTUAL_SIGNED_GO_AND_CLOSING_GATE_BOUND_SOURCE_ACTUAL.json'
 assert H(p)==BINDING_SHA
 b=json.loads(p.read_bytes());assert b['passed'] is True
 for row in [*b['inputs'].values(),*b['frozen_closing_sources'].values()]:
  path=Path(row['path']);assert path.is_file() and not path.is_symlink() and H(path)==row['SHA']
 return b
def main():
 b=validate_bound_files();entry=Path(b['frozen_closing_sources']['collect_H1_native87R5_finals_actual_cost_unused_once.py']['path'])
 sys.path.insert(0,str(entry.parent))
 sp=importlib.util.spec_from_file_location('actual_R5_frozen_collector_once',entry);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 sys.argv=[str(entry),'--stage',b['stage'],'--detached-report',b['inputs']['detached']['path'],'--go-report',b['inputs']['go']['path']]
 # No sleeping/early SSH/extra owner. Original main rejects before credential
 # recovery or transport whenever max(actual nominal end)-now exceeds900.
 return m.main()
if __name__=='__main__':
 try:main()
 except BaseException:
  b=json.loads((D/'ACTUAL_SIGNED_GO_AND_CLOSING_GATE_BOUND_SOURCE_ACTUAL.json').read_bytes());R=Path(b['stage'])/'reports'
  with (R/('H1_NATIVE87R5_BOUND_CLOSING_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
   json.dump(dict(epoch=time.time(),error=traceback.format_exc(),original_900_gate_not_relaxed=True,no_retry_model_read_refund_or_extra_GO=True),f,indent=2)
  raise
