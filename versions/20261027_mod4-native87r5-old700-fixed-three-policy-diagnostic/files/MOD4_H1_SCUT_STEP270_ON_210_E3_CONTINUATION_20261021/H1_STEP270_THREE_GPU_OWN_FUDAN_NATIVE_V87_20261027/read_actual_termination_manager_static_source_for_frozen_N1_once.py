"""Read exact installed termination manager source for future N1 cached-term capture."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def main():
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('native87R5_future_eval_static_API_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
 try:
  c=d.connect72(secret)
  value=d.code(c,d.PY72,"""from pathlib import Path
import importlib.util,json,hashlib
root=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
p=root/'managers/termination_manager.py';raw=p.read_bytes();assert len(raw)<200000
print(json.dumps(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf8'),no_scene_or_model_or_GPU_or_runtime_process_or_account_query=True)))""",{},timeout=45)
  p=N/'saved_actual_SDK_source/termination_manager_actual_for_future_frozen_N1_87.py.txt'
  with p.open('x',encoding='utf8',newline='') as f:f.write(value.pop('text'))
  assert hashlib.sha256(p.read_bytes()).hexdigest()==value['SHA'];value.update(local_path=str(p),actual_finite_returned=True,epoch=time.time(),source_purpose='Frozen goal acceptance capture existing cached termination terms without guessing API; no live progress watcher')
  with (R/'ACTUAL_TERMINATION_MANAGER_SOURCE_FOR_POST_R5_FROZEN_ACCEPTANCE_RETURNED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
  print(json.dumps(value))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('POST_R5_FROZEN_ACCEPTANCE_STATIC_API_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc()),f,indent=2)
  raise
