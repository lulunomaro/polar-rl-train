from pathlib import Path
import ast,hashlib,json
C=Path(__file__).resolve().parent;L=C.parent
SPECS=[dict(role='E2',base='E2_93_NEW86_TYPED_AST_ENV_GUARD_REPAIR_SOURCE_20261029_V3',dest='E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4',index_old='FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V3.json',index='FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V4.json',manifest='E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',job_old='/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_PROFILE_DOMAIN_20261029v3/e2',job='/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_PROFILE_DOMAIN_20261029v4/e2',cpu='E2_new86_target_source_SDK_metadata_admission_v1.py',component='e2_profile_domain_telemetry_v1.py',entry='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v4_originalHeight.py'),dict(role='E3',base='E3_97_SOURCE210_CANONICAL_PYTHON_ALIAS_REPAIR_SOURCE_20261029_V2',dest='E3_97_SOURCE210_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V3',index_old='FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V2.json',index='FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V3.json',manifest='E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json',job_old='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v2/e3',job='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v3/e3',cpu='E3_source210_target_source_SDK_metadata_admission_v1.py',component='e3_recipe_domain_telemetry_v1.py',entry='install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v3_originalHeight.py')]
def H(b):return hashlib.sha256(b).hexdigest()
def write(D,n,b):
 with (D/n).open('xb') as f:f.write(b)
def put(D,n,v):write(D,n,(json.dumps(v,indent=2)+'\n').encode())
def replace_record(text,a,b,log,required=True):
 count=text.count(a)
 if required:assert count>0,a
 if count:text=text.replace(a,b);log.append(dict(old=a,new=b,count=count))
 return text
def main():
 for s in SPECS:
  D=L/s['dest'];D.mkdir();(D/'reports').mkdir();B=L/s['base'];old=json.loads((B/s['index_old']).read_bytes());mf=json.loads((B/s['manifest']).read_bytes())
  old_entry=old['entry'];old_remote=old['remote'] if 'remote' in old else 'remote_E3_source210_verify_metadata_CPU_and_detach_v2.py';new_remote=old_remote.replace('_v3_typedASTenv','_v4_originalHeight').replace('_v2.py','_v3_originalHeight.py')
  old_first=old['first_reader'];old_term=old['terminal_reader'];renames={old_entry:s['entry'],old_remote:new_remote}
  if s['role']=='E2':renames.update({'E2_frozen_actual_receipts_readonly_CODE_v3.py':'E2_frozen_actual_receipts_readonly_CODE_v4.py','run_E2_new86_readonly_secure_stdin_v3.py':'run_E2_new86_readonly_secure_stdin_v4.py',old_first:old_first.replace('_v3.py','_v4.py'),old_term:old_term.replace('_v3.py','_v4.py')})
  else:renames.update({'E3_source210_actual_receipts_readonly_CODE_v2.py':'E3_source210_actual_receipts_readonly_CODE_v3.py','run_E3_source210_readonly_v2.py':'run_E3_source210_readonly_v3.py',old_first:old_first.replace('_v2.py','_v3.py'),old_term:old_term.replace('_v2.py','_v3.py')})
  names={Path(r['local_path']).name for r in mf['files'] if Path(r['local_path']).parent==B};names.update(renames)
  if s['role']=='E3':names.update(('AUTH72_CURRENT_KNOWN_OWNER_READONLY_CODE_v1.py','PRE210_UNUSED_MOUNT_LIGHT_RESOURCE_CODE_v1.py'))
  proofs=[]
  for n in sorted(names):
   raw=(B/n).read_bytes();name=renames.get(n,n);text=raw.decode();log=[]
   for a,b in [(s['job_old'],s['job']),(s['index_old'],s['index'])]+list(renames.items()):text=replace_record(text,a,b,log,False)
   if n==s['component']:
    text=replace_record(text,'from pathlib import Path','from pathlib import Path\nfrom original_flat_height_provider_v1 import OriginalFlatHeightProvider',log)
    text=replace_record(text,'def __init__(self,e,t,out,task):','def __init__(self,e,t,out,task,ground_module=None):',log)
    if s['role']=='E2':text=replace_record(text,"assert hasattr(e,'_mod4_ground_z') and not e._own_native_capture","assert not e._own_native_capture\n        self.ground=OriginalFlatHeightProvider(e,t,task['ground_provider_contract'],ground_module)",log)
    else:text=replace_record(text,'self.book=E3Book(t,e.num_envs,e.device,e.termination_manager.active_terms);self.episode=',"self.ground=OriginalFlatHeightProvider(e,t,task['ground_provider_contract'],ground_module)\n  self.book=E3Book(t,e.num_envs,e.device,e.termination_manager.active_terms);self.episode=",log)
    text=replace_record(text,'cached_ground_z=self._snapshot(e._mod4_ground_z)','original_source_ground_world_z=self._snapshot(self.ground.ground_z())',log)
    if s['role']=='E2':text=replace_record(text,"tensor(r.data.root_pos_w)[:,2]-e._mod4_ground_z-.25","self.ground.height()-.25",log)
    else:text=replace_record(text,"root[:,2]-e._mod4_ground_z-.25","self.ground.height()-.25",log)
    assert '_mod4_ground_z' not in text,'Every selected telemetry ground reference must use typed original getter'
   if n==s['cpu']:
    needle=' result=dict(passed=True,kind=';prefix=" from original_flat_height_provider_v1 import validate_flat_height_source\n from selected_telemetry_constructor_API_fixture_v1 import run_selected_constructor_fixture\n ground_contract=json.loads((J/'GROUND_PROVIDER_SOURCE_CONTRACT.json').read_bytes());ground_proof=validate_flat_height_source(J/'runtime/isaac/mod4/mod4_task.py',ground_contract)\n constructor_proof=run_selected_constructor_fixture(J,"+repr(s['role'])+",torch)\n"+needle
    text=replace_record(text,needle,prefix,log)
    text=replace_record(text,'worker_SHA=H(worker),frozen_worker_AST_call_guard=guard','worker_SHA=H(worker),ground_provider_source_contract=ground_proof,selected_constructor_fresh_CPU_API_fixture=constructor_proof,first_native24_read_wait_maximum_seconds=360,frozen_worker_AST_call_guard=guard',log)
   if n==old_remote:
    text=replace_record(text,'full_WM_tap_included=False',"ground_provider_contract=json.loads((J/'GROUND_PROVIDER_SOURCE_CONTRACT.json').read_bytes()),ground_provider_contract_SHA=H(J/'GROUND_PROVIDER_SOURCE_CONTRACT.json'),telemetry_component_SHA=H(J/"+repr(s['component'])+"),first_native24_read_wait_maximum_seconds=360,full_WM_tap_included=False",log)
   # First-only wait is NEW360. Keep normal850/sup1800/worker1680/remaining900.
   for a,b in [("110 if mode=='first' else 850","360 if mode=='first' else 850"),("110 if mode=='first' else 850","360 if mode=='first' else 850"),("150 if mode=='first' else 900","420 if mode=='first' else 900"),("180 if mode=='first' else 960","450 if mode=='first' else 960")]:text=replace_record(text,a,b,log,False)
   if n.endswith('.py'):ast.parse(text)
   write(D,name,text.encode());proofs.append(dict(base=str(B/n),base_SHA=H(raw),selected=name,selected_SHA=H(text.encode()),changes=log))
  for n in ('original_flat_height_provider_v1.py','selected_telemetry_constructor_API_fixture_v1.py'):write(D,n,(C/n).read_bytes())
  contract=dict(kind='original_mod4_task_flat_root_height_readonly_v1',task_source_SHA='30ce41126a1a9b78a1c2b446281b28f4555c28052bfaa7c0e9a76079cf561fc5',API='mod4_task.root_height_above_ground',flat_only=True,original_missing_cache_fallback_legal=True,no_ground_cache_injection_or_SDK_raycast_RNG=True,first_native24_read_wait_maximum_seconds=360)
  put(D,'GROUND_PROVIDER_SOURCE_CONTRACT.json',contract)
  rows=[]
  for r in mf['files']:
   x=dict(r)
   if Path(r['local_path']).parent==B:
    name=renames.get(Path(r['local_path']).name,Path(r['local_path']).name);data=(D/name).read_bytes();x.update(local_path=str(D/name),bytes=len(data),SHA=H(data))
   rows.append(x)
  for n in ('original_flat_height_provider_v1.py','selected_telemetry_constructor_API_fixture_v1.py','GROUND_PROVIDER_SOURCE_CONTRACT.json'):
   data=(D/n).read_bytes();rows.append(dict(relative=n,local_path=str(D/n),bytes=len(data),SHA=H(data)))
  mf.update(files=rows,target_root=s['job'],target_stage=s['job'],original_flat_height_getter_source_contract=contract,first_native24_read_wait_maximum_seconds=360)
  put(D,s['manifest'],mf);selection=dict(role=s['role'],entry=s['entry'],remote=new_remote,index=s['index'],target_root=s['job'],target_stage=s['job'],manifest_filename=s['manifest'],manifest_SHA=H((D/s['manifest']).read_bytes()),first_reader=renames[old_first],terminal_reader=renames[old_term],model_SHA=old.get('source_model_SHA',old.get('model_SHA')),base_index=str(B/s['index_old']),base_index_SHA=H((B/s['index_old']).read_bytes()),source_only=True)
  if s['role']=='E2':selection.update(clone_receipt_SHA=old['clone_receipt_SHA'],actual_clone_CUDA_SDK_receipt_SHA=old['actual_clone_CUDA_SDK_receipt_SHA'],manifest_local_filename=s['manifest'])
  put(D,'GROUND_REPAIR_SELECTION_PENDING_FINAL_FREEZE.json',selection);put(D,'GROUND_REPAIR_SOURCE_CHANGES_EXACT_RECORD.json',dict(passed=True,records=proofs,old_source_errors_once_immutable=True,all_selected_ground_references_audited=True,no_binary_PT_raw_SDK_remote=True))
  print(json.dumps(dict(source_only=True,role=s['role'],dest=str(D),rows=len(rows))))
if __name__=='__main__':main()
