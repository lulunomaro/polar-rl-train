from pathlib import Path
import copy,hashlib,importlib.util,json,shutil,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
A=L/'TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1';B=L/'TWO103_FUDAN270_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V2';OLD=L/'TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 assert not B.exists();B.mkdir();(B/'reports').mkdir()
 public=copy.deepcopy(json.loads((A/'reports/TWO103_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes()))
 public['run_id']='TWO103_FUDAN270_SIGNED_GO_NATIVE_'+str(time.time_ns())
 public['owner_root']=public['owner_root'].replace('2610v103/','2610v103V2/')
 public['owner_source']=str(B/'owner')
 prepared=json.loads((N/'reports/TWO103_BANK_READER_V4_PAYLOADS_PREPARED_ACTUAL.json').read_bytes())
 for role in ['owner','node_h1','node_h1_seed28']:
  d=B/role;d.mkdir()
  for p in (A/role).glob('*.py'):shutil.copy2(p,d/p.name)
  for name,key in [('h1_next72_protocol_actual95_v2.py','h1'),('h1_seed28_next72_protocol_v100.py','h1_seed28')]:
   p=d/name;s=p.read_text('utf8');needle="'fudan_step_task','input_start_mode'";assert s.count(needle)==2;s=s.replace(needle,"'fudan_step_task','goal_conditioning','input_start_mode'")
   needle="def validate_spec(s):\n";assert s.count(needle)==1;s=s.replace(needle,needle+" require(s.get('goal_conditioning')=="+repr(public['experts'][key]['goal_conditioning'])+",'literal preserved mask-aware goal encoding')\n")
   p.write_text(s,encoding='utf8')
 for key,spec in public['experts'].items():
  spec['run_id']=public['run_id'];public['node_sources'][key]=str(B/('node_'+key));public['node_roots'][key]=public['node_roots'][key].replace('2610v103/','2610v103V2/')
  d=B/('node_'+key)
  put(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',dict(key=key,source_SHA=spec['source_SHA'],worker_SHA=spec['worker_SHA'],source_CPU_SHA=spec['source_CPU_SHA'],files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(d.iterdir()) if p.is_file()]));spec['manifest_SHA']=H(d/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
 public['task_templates']=copy.deepcopy(public['experts'])
 activation=(OLD/'activate_two101_producer_fixed_native20_original_single_writer_once.py').read_text('utf8').replace('TWO101','TWO103')
 with (B/'activate_TWO103_fudan270_original_single_writer_UNUSED_once.py').open('x',encoding='utf8') as f:f.write(activation)
 # Use the actual protocol-generated GO fields, not a hand-filled fake GO.
 sys.path.insert(0,str(B/'owner'));import mixed72_next_protocol_v1 as dispatch;assert dispatch.validate_schedule(public)
 checked=[]
 for mode,p in prepared['payloads'].items():
  key=p['logical_slot'];spec=public['experts'][key];protocol=dispatch.module_for(spec)
  source=Path(p['payload']);sys.path[:0]=[str(source),str(source/'source')]
  for module in ('native88C_to_flat_migration_v1','native103_fudan270_pins_v1'):sys.modules.pop(module,None)
  import native88C_to_flat_migration_v1 as migration
  go=dict(protocol.flat_go_fields(spec),source_SHA=spec['source_SHA'],max_parent_seconds=3900,exit_headroom_seconds=300)
  migration.assert_declared_admission('h1',p['task'],go)
  wrong=copy.deepcopy(go);wrong['goal_conditioning']={}
  try:migration.assert_declared_admission('h1',p['task'],wrong)
  except ValueError:pass
  else:raise AssertionError('unsigned/wrong goal encoding admitted')
  checked.append(key)
 for name in ('two95_finite_owner_authority72_v1.py','three_slot_common_v1.py','forwarded_original_owner_control_v1.py'):
  assert (B/'owner'/name).read_bytes()==(OLD/'owner'/name).read_bytes()
 put(B/'reports/TWO103_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public)
 put(B/'reports/TWO103_PROTOCOL_GENERATED_GO_FIELD_CLOSURE_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),roles=checked,original_UNUSED_V1_preserved=True,V1_source_only_missing_GO_goal_conditioning_caught_before_any_launch=True,correction_only_signed_goal_metadata_fields_and_validation=True,original_owner_common_forward_bytes_exact=True,no_model_read_remote_or_GPU=True,actual_GPU_admission_and_GO_pending=True))
 put(B/'FROZEN_UNUSED_TWO103_FUDAN270_CONTROLLER_INDEX_V2.json',dict(frozen=True,unused=True,files=[dict(relative=p.relative_to(B).as_posix(),bytes=p.stat().st_size,SHA=H(p)) for p in sorted(B.rglob('*')) if p.is_file()]))
 print(json.dumps(dict(passed_actual_generated_GO_CPU=True,roles=checked,controller_and_activation_frozen_UNUSED=True,no_GPU_or_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  if (B/'reports').exists():put(B/'reports/CONTROLLER103_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_remote_or_GPU=True))
  raise
