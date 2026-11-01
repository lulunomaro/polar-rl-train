"""Narrow new reader purpose:delta-clock AST and previously unexecuted tail checks."""
from pathlib import Path
import ast,hashlib,json,time,traceback
N=Path(__file__).resolve().parent;R=N/'reports'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 assert json.loads((R/'CPU_DR064_CLOCK_READER_V2_PURPOSE_FROZEN.json').read_bytes())['executions']==1
 put(R/'CPU_DR064_CLOCK_READER_V2_ONCE_CONSUMED.json',dict(epoch=time.time(),old_case_replays=0))
 original=R/'CPU_DR064_ORIGINAL_ERROR.json';b=original.read_bytes();assert 'line 29' in json.loads(b)['error']
 worker=(N/'probe_dr0_64_worker_ROOT_ONLY.py').read_text(encoding='utf8');wt=ast.parse(worker)
 delta=[]
 for x in ast.walk(wt):
  if isinstance(x,ast.Compare) and isinstance(x.left,ast.BinOp) and isinstance(x.left.op,ast.Sub) and isinstance(x.left.right,ast.Name) and len(x.comparators)==1 and isinstance(x.comparators[0],ast.Constant):
   delta.append((x.left.right.id,x.comparators[0].value))
 assert ('tick',64) in delta and ('fb',16) in delta
 assert 'range(8)' in worker and worker.index("put(N/'DR064_APPCLOSING_BEFORE_CLOSE.json'")<worker.index('app.close()')
 root=(N/'run_ROOT_dr064_once.py').read_text(encoding='utf8');rt=ast.parse(root)
 strings=[x.value.value for x in rt.body if isinstance(x,ast.Assign) and isinstance(x.value,ast.Constant) and isinstance(x.value.value,str) and x.targets[0].id in ('AUTH','SETUP','CASE')]
 for s in [worker,root]+strings:
  for x in ast.walk(ast.parse(s)):
   assert not (isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('kill','terminate','send_signal'))
 assert not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr in ('load','load_state_dict') for x in ast.walk(wt))
 assert 'OnPolicyRunner' not in worker
 c=N.parent/'E0_ALL_RANDOMIZATION_OFF_DR0_SOURCE_CONTRACT_V1_20261101'
 assert all((N/x).read_bytes()==(c/x).read_bytes() for x in ('dr0_contract.py','dr0_actual_readback.py'))
 put(R/'CPU_DR064_NEW_SOURCE_INTERFACE_ACTUAL.json',dict(epoch=time.time(),passed=True,
  original_source_reader_false_preserved=dict(path=str(original),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),reason='substring tick==64 occurs within relative delta;original lexical predicate rejected correct source'),
  original_V1_reached_line29_after_9AST_3embeddedAST_Task_schema_JSON_source_checks=True,
  narrow_V2_delta_clock_AST=[['tick',64],['fb',16]],remaining_no_signal_model_loader_and_core_byte_checks_passed=True,
  earlier_roundtrip_or_off_fixture_replays=0,actual_SDK_readback=False,actual_Target_admission='UNSELECTED_PENDING_ROOT_3060_EVIDENCE_AND_FRESH_AUTHORITY',Torch_model_asset_raw_SDK_network_Git=0))
if __name__=='__main__':
 try:main()
 except BaseException:put(R/'CPU_DR064_CLOCK_READER_V2_ORIGINAL_ERROR.json',dict(error=traceback.format_exc()));raise
