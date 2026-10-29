from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent;OLD=L/'E3_97_SOURCE210_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V3'
OLDJOB='/mnt/mod4_linux_durable_20261013/MOD4_E3_ADAPTED97_RECIPE_DOMAIN_20261029v3/e3';JOB=OLDJOB.replace('20261029v3','20261029v4');INDEX='FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V4.json'
ENTRY='install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v4_exactEntryReceipt.py';REMOTE='remote_E3_source210_verify_metadata_CPU_and_detach_v4_exactEntryReceipt.py';CODE='E3_source210_actual_receipts_readonly_CODE_v4.py'
RENAMES={'install_E3_source210_frozen_recipe_metadata_detach_UNUSED_once_v3_originalHeight.py':ENTRY,'remote_E3_source210_verify_metadata_CPU_and_detach_v3_originalHeight.py':REMOTE,'E3_source210_actual_receipts_readonly_CODE_v3.py':CODE,'run_E3_source210_readonly_v3.py':'run_E3_source210_readonly_v4.py','read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v3.py':'read_E3_source210_FIRST_native24_recipe_queue_UNUSED_once_v4.py','collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v3.py':'collect_E3_source210_TERMINAL_recipe_fulltext_UNUSED_once_v4.py'}
def H(b):return hashlib.sha256(b).hexdigest()
def write(n,b):
 with (B/n).open('xb') as f:f.write(b)
def put(n,x):write(n,(json.dumps(x,indent=2)+'\n').encode())
def main():
 (B/'reports').mkdir(exist_ok=True);old=json.loads((OLD/'FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V3.json').read_bytes());mf=json.loads((OLD/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());names={Path(r['local_path']).name for r in mf['files'] if Path(r['local_path']).parent==OLD};names.update(RENAMES);names.update(('AUTH72_CURRENT_KNOWN_OWNER_READONLY_CODE_v1.py','PRE210_UNUSED_MOUNT_LIGHT_RESOURCE_CODE_v1.py'));changes=[]
 for n in sorted(names):
  raw=(OLD/n).read_bytes();name=RENAMES.get(n,n);text=raw.decode();edits=[]
  for a,b in [(OLDJOB,JOB),('FROZEN_E3_97_SOURCE210_RECIPE_DOMAIN_SOURCE_INDEX_V3.json',INDEX)]+list(RENAMES.items()):
   if a in text:edits.append(dict(old=a,new=b,count=text.count(a)));text=text.replace(a,b)
  if n=='evaluate_E3_adapted97_source210_frozen600_once_v1.py':
   for a,b in [('train_E3_full_resume_v1.py','train_E3_fullstate_v1.py'),('ACTUAL_NATIVE34_E3_40050_CLOCK_QUEUE.json','ACTUAL_NATIVE24_E3_40050_CLOCK_QUEUE.json')]:assert text.count(a)==1;text=text.replace(a,b);edits.append(dict(old=a,new=b,count=1))
  if n=='E3_source210_actual_receipts_readonly_CODE_v3.py':
   for a,b in [('ACTUAL_NATIVE34_E3_40050_CLOCK_QUEUE.json','ACTUAL_NATIVE24_E3_40050_CLOCK_QUEUE.json'),('ACTUAL_E3_93_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json','ACTUAL_E3_97_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json')]:assert text.count(a)==1;text=text.replace(a,b);edits.append(dict(old=a,new=b,count=1))
  if n=='run_E3_source210_readonly_v3.py':
   a='from pathlib import Path';b='from pathlib import Path,PurePosixPath';assert text.count(a)==1;text=text.replace(a,b);edits.append(dict(old=a,new=b,count=1))
   a="str(Path(JOB)/'detached_E3_source210_frozen_recipe_supervisor_once_v1.py')";b="str(PurePosixPath(JOB)/'detached_E3_source210_frozen_recipe_supervisor_once_v1.py')";assert text.count(a)==1;text=text.replace(a,b);edits.append(dict(old=a,new=b,count=1))
  if n=='E3_source210_target_source_SDK_metadata_admission_v1.py':
   a=" result=dict(passed=True,kind=";b=" from e3_declared_entry_receipt_cli_contract_v1 import validate_installed_entry_contract\n entry_closure=validate_installed_entry_contract(J,m,Path(modules['isaaclab']).parent/'app/app_launcher.py')\n"+a;assert text.count(a)==1;text=text.replace(a,b);edits.append(dict(old=a,new=b,count=1))
   a='worker_SHA=H(worker),ground_provider_source_contract=';b='worker_SHA=H(worker),declared_entry_dependency_CLI_hook_receipt_contract=entry_closure,ground_provider_source_contract=';assert text.count(a)==1;text=text.replace(a,b);edits.append(dict(old=a,new=b,count=1))
  inverse=text
  for r in reversed(edits):inverse=inverse.replace(r['new'],r['old'])
  assert inverse.encode()==raw,(name,'exact inverse');ast.parse(text) if name.endswith('.py') else None;write(name,text.encode());changes.append(dict(base=str(OLD/n),base_SHA=H(raw),selected=name,selected_SHA=H(text.encode()),changes=edits,inverse_bytes_exact=True))
 # Contract facts come from original production file table and actual command source.
 production=L/'E3_97_GAS400_COMPLETE_RUNTIME_SOURCE_CPU_PREPARATION_V1/E3_COMPLETE_INSTALL_MANIFEST_V1.json';prod=json.loads(production.read_bytes());entry=next(r for r in prod['files'] if r['relative']=='runtime/isaac/mod4/train_E3_fullstate_v1.py');assert entry['SHA']=='9799d3485f23f3947d28d64160e3ec68323eafe56b1e822f531ee36fd8441260';source=Path(entry['local_path']);assert H(source.read_bytes())==entry['SHA']
 command=L/'E3_PPO50_gas400_source_preparation_20261028/E3_PPO50_gas400_finite_worker_v1.py';tree=ast.parse(command.read_bytes());value=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='entry' for t in n.targets));assert ast.unparse(value)=="mod / 'train_E3_fullstate_v1.py'"
 put('ORIGINAL_E3_PRODUCTION_ENTRY_COMMAND_AND_DECLARED_CLOSURE_CONTRACT.json',dict(kind='original_E3_fullstate_entry_CLI_learn_hook_receipt_v1',production_input_manifest=str(production),production_manifest_SHA=H(production.read_bytes()),original_entry_row=entry,production_command_source=str(command),production_command_source_SHA=H(command.read_bytes()),actual_production_entry_assignment=ast.unparse(value),selected_entry_relative=entry['relative'],native24_receipt='ACTUAL_NATIVE24_E3_40050_CLOCK_QUEUE.json',fullrestore_receipt='ACTUAL_E3_97_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json',no_model_PT_raw_read=True))
 rows=[]
 for r in mf['files']:
  x=dict(r)
  if Path(r['local_path']).parent==OLD:
   name=RENAMES.get(Path(r['local_path']).name,Path(r['local_path']).name);data=(B/name).read_bytes();x.update(local_path=str(B/name),bytes=len(data),SHA=H(data))
   if '/' not in x['relative']:x['relative']=name
  rows.append(x)
 for n in ('e3_declared_entry_receipt_cli_contract_v1.py',CODE,'ORIGINAL_E3_PRODUCTION_ENTRY_COMMAND_AND_DECLARED_CLOSURE_CONTRACT.json'):
  data=(B/n).read_bytes();rows.append(dict(relative=n,local_path=str(B/n),bytes=len(data),SHA=H(data)))
 mf.update(files=rows,target_root=JOB,target_stage=JOB,selected_original_E3_production_entry=entry['relative'],entry_dependency_CLI_hook_receipt_static_contract_required=True,first_native24_read_wait_maximum_seconds=360)
 put('E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json',mf);put('NEW_V4_EXACT_ENTRY_NATIVE24_RESTORE_POSIX_SOURCE_INVERSE_PROOF.json',dict(passed=True,records=changes,production_entry_bound_from_actual_command_and_file_table=True,numerical24_192_48_model_physics_metrics_unchanged=True,source_only=True))
 put('V4_SELECTED_SOURCE_PENDING_FINAL_FREEZE.json',dict(entry=ENTRY,remote=REMOTE,index=INDEX,target_root=JOB,manifest_SHA=H((B/'E3_SOURCE210_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes()),model_SHA=old['model_SHA'],first_reader=RENAMES[old['first_reader']],terminal_reader=RENAMES[old['terminal_reader']],source_only=True))
 print(json.dumps(dict(passed=True,source_only=True,input_rows=len(rows),production_entry=entry['relative'],new_root=JOB)))
if __name__=='__main__':main()
