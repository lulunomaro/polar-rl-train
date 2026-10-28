"""Missing-only source fixture. No owner, worker, model, account or network IO."""
from pathlib import Path
import ast,copy,hashlib,importlib,json,sys,time
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent
OLD=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028/controller_three93_source_v3'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def functions(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(Path(p).read_bytes())) if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def main():
 v=json.loads((B/'reports/TWO95_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes())
 sys.path.insert(0,str(B/'owner'));import mixed72_next_protocol_v1 as mp
 assert mp.validate_schedule(v)
 h=json.loads((T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028/reports/NATIVE95_ACTUAL_SOURCE_SDK_CPU_AND_RESOURCE_RETURNED_ACTUAL.json').read_bytes())
 ev=json.loads((L/'E3_PPO50_gas400_source_preparation_20261028/reports/E3_SOURCE_SDK_CPU_ADMISSION_ACTUAL_V1.json').read_bytes())
 result={}
 for key,value in [('h1',h['value']),('e3',ev)]:
  spec=v['experts'][key];m=mp.module_for(spec);assert m.validate_cpu_value(value,spec)
  e=dict(value=value,SHA=spec['source_CPU_SHA'],actual_CPU_waited_EXIT0=True)
  if key=='h1':
   e.update(raw_report_UTF8=json.dumps(value,ensure_ascii=False,indent=2),value_digest=m.digest(value),actual_waited_proof=h['proof'],actual_waited_proof_SHA=h['proof_SHA'],raw_waited_proof_UTF8=json.dumps(h['proof'],ensure_ascii=False,indent=2))
   assert hashlib.sha256(e['raw_report_UTF8'].encode()).hexdigest()==spec['source_CPU_SHA']
   assert hashlib.sha256(e['raw_waited_proof_UTF8'].encode()).hexdigest()==spec['CPU_waited_proof_SHA']
  ready=dict(key=key,phase='ready',manifest_SHA=spec['manifest_SHA'],closed_source_CPU=e,actual_validation_fcntl_held=True)
  assert mp.nativeflat_valid_ready(ready,spec)
  bad=copy.deepcopy(ready);bad['actual_validation_fcntl_held']=False;assert not mp.nativeflat_valid_ready(bad,spec)
  go=mp.flat_go_fields(spec);assert go['GPU_UUID']==spec['GPU_UUID'] and go['worker_SHA']==spec['worker_SHA']
  if key=='h1':assert go['native_learning_seed']==27 and go['task_focused_real_replay']==spec['task_focused_real_replay']
  result[key]=dict(actual_CPU_JSON_and_external_wait_used=True,exact_CPU_SHA=spec['source_CPU_SHA'],original_protocol_positive_and_missing_lock_negative=True,actual_node_acquire_not_claimed_by_fixture=True)
 protected={}
 for name,newfile,oldfile,items in [('owner',B/'owner/two95_finite_owner_authority72_v1.py',OLD/'three93_finite_owner_authority72_v1.py',['account','Handler']),('common',B/'owner/three_slot_common_v1.py',OLD/'three_slot_common_v1.py',['charge_values','authenticated_row','terminal']),('authority',B/'owner/single_writer72_authority_V85M_source.py',OLD/'single_writer72_authority_V85M_source.py',[])]:
  a=functions(newfile);c=functions(oldfile)
  for item in items:assert a[item]==c[item],item
  if name=='authority':assert newfile.read_bytes()==oldfile.read_bytes()
  protected[name]=dict(functions=items,passed=True,original_SHA=H(oldfile),selected_SHA=H(newfile))
 for p in B.rglob('*.py'):ast.parse(p.read_bytes())
 out=dict(passed=True,epoch=time.time(),actual_CPU_ready_GO=result,protected_AST=protected,old_fixture_false_preserved=True,no_models_SDK_GPU_network_owner_worker_spawn_or_ledger_IO=True)
 with (B/'reports/TWO95_ACTUAL_CPU_READY_GO_AND_ORIGINAL_ACCOUNT_AST_ACTUAL_V2.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2)
 print(json.dumps(out))
if __name__=='__main__':main()
