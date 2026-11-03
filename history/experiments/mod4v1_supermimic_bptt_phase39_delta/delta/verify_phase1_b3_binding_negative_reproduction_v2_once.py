"""New stdlib-only reproduction of reviewed B3 pre-install binding gaps.
Loads complete pinned SOURCE modules, not project tests, an SDK or a worker.
Temporary function defaults are restored in finally; files stay intact.
"""
from pathlib import Path
import sys,json,hashlib,copy,time,traceback
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;B=R/'source_phase1_passive_sensor_capture_v3';C=R/'source_phase1_typed_capture_codec_v1';out=R/'reports/PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_V2.json';mark=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_V2_STARTED_ONCE.json';assert not out.exists()and not mark.exists();H=lambda x:hashlib.sha256(x).hexdigest()
expected=[(B,3359,'fc7e90950d26ea6f9007777c028574a11b224779d41efa7d7101d5e21b859f28'),(C,1427,'2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219')];observed={}
for root,n,pin in expected:
 b=(root/'SOURCE_SEAL.json').read_bytes();assert(len(b),H(b))==(n,pin);observed[str(root/'SOURCE_SEAL.json')]=H(b)
 for name,item in json.loads(b)['files'].items():
  path=root/name;raw=path.read_bytes();assert len(raw)==item['bytes']and H(raw)==item['sha256'];observed[str(path)]=H(raw)
def audit(event,args):
 if event.startswith(('socket.','subprocess.','ctypes.dlopen'))or event in('os.system','os.fork','os.kill','os.posix_spawn'):raise RuntimeError('Forbidden native/network/process operation')
sys.addaudithook(audit)
with mark.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),purpose='NEW_SOURCE_BINDING_NEGATIVE_REPRODUCTION_NOT_NATIVE_OR_OLD_SUITE',source_files=len(observed),old_source_suites_executed=0),f)
sys.path[:0]=[str(B),str(C)]
import typed_capture_codec as codec_module
import dependency_contract as contract
from field_snapshot import tensor_snapshot_adapter
from fake_tensor import FakeTensor
snapshot=tensor_snapshot_adapter(FakeTensor,FakeTensor(list(range(8)),'torch.int64'),80,witness_env_ids=tuple(range(8)));ledger=codec_module.ControlLedger(snapshot.codec,controls=64,run_id='NEW_PARENT_SOURCE_REPRODUCTION_ONLY');pins=json.loads((B/'CODEC_SOURCE_PINS.json').read_bytes());cases=[];error=None
fn=codec_module._metadata;original_defaults=fn.__defaults__
try:
 q=contract.verify_typed_dependency(snapshot,ledger);assert len(q['checked_functions'])==22 and len(q['classes'])==3;cases.append(dict(case='unchanged_fixed_published_pins',accepted=True,checked_functions=len(q['checked_functions']),checked_classes=len(q['classes'])))
 sparse=copy.deepcopy(pins)
 for key in('codec_constants','codec_classes','codec_functions','field_functions'):sparse[key]={}
 q=contract.verify_typed_dependency(snapshot,ledger,dependency_pins=sparse);assert q['checked_functions']=={}and q['classes']=={};cases.append(dict(case='public_override_empty_check_collections',accepted=True,checked_functions=0,checked_classes=0,source_bytes_and_real_class_bindings_unchanged=True))
 assert original_defaults==(0,)and type(original_defaults[0])is int
 for value in(False,0.0):
  fn.__defaults__=(value,)
  try:
   q=contract.verify_typed_dependency(snapshot,ledger);assert len(q['checked_functions'])==22;cases.append(dict(case='fixed_published_pins_changed_positional_default',old_type='int',old_value=0,new_type=type(value).__name__,new_value=value,accepted=True,observed_signature=q['checked_functions']['_metadata']['signature'],same_published_source_and_bytecode=True))
  finally:fn.__defaults__=original_defaults
 q=contract.verify_typed_dependency(snapshot,ledger);assert len(q['checked_functions'])==22 and fn.__defaults__ is original_defaults;cases.append(dict(case='restored_original_bindings',accepted=True,checked_functions=22))
except BaseException as e:error=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc(limit=8))
finally:
 fn.__defaults__=original_defaults
after={p:H(Path(p).read_bytes())for p in observed};assert after==observed and not any(n in sys.modules for n in('torch','isaaclab','omni','isaacsim'))
v=dict(kind='ACTUAL_STDLIB_SOURCE_BINDING_NEGATIVE_REPRODUCTION_V2',epoch=time.time(),status='OBSERVED_SOURCE_BINDING_CONTRACT_GAPS'if error is None else'REPRODUCTION_ERROR',cases=cases,error=error,source_seals_and_all_members_unchanged=True,temporary_defaults_restored=True,source_member_count=len(observed),old_project_suites_executed=0,actual_SDK_or_worker_or_Torch_or_model_or_raw_or_C_or_resources=0,native_vulnerability_or_physics_cause_claim=False,stage2_go=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2));raise SystemExit(0 if error is None else 1)
