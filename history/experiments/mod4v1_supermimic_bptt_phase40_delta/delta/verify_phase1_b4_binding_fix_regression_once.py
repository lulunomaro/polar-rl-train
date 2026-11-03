"""NEW independent stdlib control/negative comparison for the sealed B4 guard.
Not an execution of author11/old30, Tensor behavior or an installed capture.
"""
from pathlib import Path
import sys,json,hashlib,copy,time,traceback
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;B=R/'source_phase1_passive_sensor_capture_v4';C=R/'source_phase1_typed_capture_codec_v1';out=R/'reports/PHASE1_B4_PARENT_MATCHED_BINDING_REGRESSION_V1.json';marker=R/'PAPER_ALIGNED_REBUILD_20261103/PHASE1_B4_PARENT_MATCHED_BINDING_REGRESSION_STARTED_ONCE.json';assert not out.exists()and not marker.exists();H=lambda b:hashlib.sha256(b).hexdigest();files={}
for root,n,pin in[(B,3824,'81fe69c8c2f2ffde98b2a5e4b03d6921207d60156dcb180ab0097aa7397813b3'),(C,1427,'2cc26eaee058d30c9ac5b17ca8fb37541beb7c1e5ddbb738963ddef08c199219')]:
 raw=(root/'SOURCE_SEAL.json').read_bytes();assert(len(raw),H(raw))==(n,pin);files[str(root/'SOURCE_SEAL.json')]=H(raw)
 for name,p in json.loads(raw)['files'].items():
  path=root/name;b=path.read_bytes();assert(len(b),H(b))==(p['bytes'],p['sha256']);files[str(path)]=H(b)
def audit(event,args):
 if event.startswith(('socket.','subprocess.','ctypes.dlopen'))or event in('os.system','os.fork','os.kill','os.posix_spawn'):raise RuntimeError('Forbidden process/network/native operation')
sys.addaudithook(audit)
with marker.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),purpose='NEW_MATCHED_SOURCE_FIX_REGRESSION_NO_AUTHOR_SUITE_OR_CAPTURE',source_file_count=len(files)),f)
sys.path[:0]=[str(B),str(C)]
import typed_capture_codec as codec
import dependency_contract as guard
from field_snapshot import tensor_snapshot_adapter
from fake_tensor import FakeTensor
snapshot=tensor_snapshot_adapter(FakeTensor,FakeTensor(list(range(8)),'torch.int64'),80,witness_env_ids=tuple(range(8)));ledger=codec.ControlLedger(snapshot.codec,controls=64,run_id='PARENT_B4_MATCHED_SOURCE_FIX_ONLY');fixed=json.loads((B/'CODEC_SOURCE_PINS.json').read_bytes());cases=[];error=None;olddefaults=codec._metadata.__defaults__;oldkw=codec.CaptureCodec.__init__.__kwdefaults__
def positive(name,**kw):
 q=guard.verify_typed_dependency(snapshot,ledger,**kw);assert len(q['checked_functions'])==22 and len(q['classes'])==3 and q['expected_pins_sha256']=='5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452';cases.append(dict(case=name,outcome='ACCEPTED_FIXED_COMPLETE',checked_functions=22,checked_classes=3))
def negative(name,**kw):
 try:guard.verify_typed_dependency(snapshot,ledger,**kw)
 except (ValueError,TypeError)as e:cases.append(dict(case=name,outcome='REJECTED_AS_EXPECTED',error_type=type(e).__name__,message=str(e)))
 else:raise AssertionError('Bad source metadata accepted: '+name)
try:
 positive('fixed_default_control');positive('identical_override_control',dependency_pins=copy.deepcopy(fixed))
 sparse=copy.deepcopy(fixed)
 for key in('codec_constants','codec_classes','codec_functions','field_functions'):sparse[key]={}
 negative('empty_check_collections_matched_to_B3_counterexample',dependency_pins=sparse)
 partial=copy.deepcopy(fixed);partial['codec_functions'].pop('_metadata');negative('omitted_one_published_function',dependency_pins=partial)
 for value in(False,0.0):
  codec._metadata.__defaults__=(value,)
  try:negative('changed_default_int0_to_'+type(value).__name__)
  finally:codec._metadata.__defaults__=olddefaults
 codec.CaptureCodec.__init__.__kwdefaults__=dict(oldkw,n=80.0)
 try:negative('changed_keyword_default_int80_to_float80')
 finally:codec.CaptureCodec.__init__.__kwdefaults__=oldkw
 positive('restored_default_control');assert len(cases)==8
except BaseException as e:error=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc(limit=8))
finally:codec._metadata.__defaults__=olddefaults;codec.CaptureCodec.__init__.__kwdefaults__=oldkw
assert {p:H(Path(p).read_bytes())for p in files}==files and codec._metadata.__defaults__ is olddefaults and codec.CaptureCodec.__init__.__kwdefaults__ is oldkw and not FakeTensor.operations and not any(x in sys.modules for x in('torch','passive_capture','isaaclab','omni','isaacsim'))
v=dict(kind='PARENT_B4_MATCHED_SOURCE_BINDING_FIX_REGRESSION_V1',epoch=time.time(),status='PASS_SOURCE_BINDING_FIX_ONLY'if error is None else'FAILED',cases=cases,error=error,source_member_count=len(files),all_source_members_and_seals_unchanged=True,all_live_defaults_restored=True,fake_tensor_operations=dict(FakeTensor.operations),author11_or_old30_suites_executed=0,capture_ledger_control_or_sensor_Torch_SDK_model_raw_C_resource_operations=0,Gate1='UNKNOWN',stage2_go=False)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2));raise SystemExit(0 if error is None else 1)
