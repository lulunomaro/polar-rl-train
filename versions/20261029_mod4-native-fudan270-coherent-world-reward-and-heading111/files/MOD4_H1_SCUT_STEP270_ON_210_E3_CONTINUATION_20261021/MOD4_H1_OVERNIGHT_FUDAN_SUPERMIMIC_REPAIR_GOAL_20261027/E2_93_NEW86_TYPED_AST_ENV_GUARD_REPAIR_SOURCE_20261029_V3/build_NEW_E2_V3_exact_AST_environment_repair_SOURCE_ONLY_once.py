"""NEW namespace: CPU AST guard repair only; worker/model/runtime bytes untouched."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent;L=B.parent;OLD=L/'E2_93_NEW86_FROZEN_PROFILE_DOMAIN_PATH_REPAIR_SOURCE_20261029_V2'
OLD_STAGE='/data/robemo/polar-rl-train/evaluation_runs/E2_ADAPTED93_PROFILE_DOMAIN_20261029v2/e2';STAGE=OLD_STAGE.replace('20261029v2','20261029v3')
OLD_ENTRY='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v2_exactE2root.py';ENTRY='upload_admit_detach_NEW86_E2_final93_profiles_secure_stdin_UNUSED_once_v3_typedASTenv.py'
OLD_REMOTE='remote_E2_new86_profile_install_and_detach_v2_exactE2root.py';REMOTE='remote_E2_new86_profile_install_and_detach_v3_typedASTenv.py'
INDEX='FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V3.json';CPU='E2_new86_target_source_SDK_metadata_admission_v1.py'
READER_NAMES={'E2_frozen_actual_receipts_readonly_CODE_v1.py':'E2_frozen_actual_receipts_readonly_CODE_v3.py','run_E2_new86_readonly_secure_stdin_v1.py':'run_E2_new86_readonly_secure_stdin_v3.py','read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v1.py':'read_E2_new86_FIRST_native24_queue_secure_stdin_UNUSED_once_v3.py','collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v1.py':'collect_E2_new86_TERMINAL_fulltext_secure_stdin_UNUSED_once_v3.py'}
def H(raw):return hashlib.sha256(raw).hexdigest()
def write(name,raw):
 with (B/name).open('xb') as f:f.write(raw)
def put(name,v):write(name,(json.dumps(v,indent=2)+'\n').encode())
def changed(name,newname,replacements):
 raw=(OLD/name).read_bytes();text=raw.decode();proof=[]
 for a,b in replacements:
  count=text.count(a);assert count>0,(name,a);text=text.replace(a,b);proof.append(dict(old=a,new=b,count=count))
 inverse=text
 for row in reversed(proof):inverse=inverse.replace(row['new'],row['old'])
 assert inverse.encode()==raw,name;ast.parse(text);write(newname,text.encode());return dict(old_file=str(OLD/name),old_SHA=H(raw),new_file=newname,new_SHA=H(text.encode()),inverse_bytes_exact=True,replacements=proof)
def main():
 (B/'reports').mkdir(exist_ok=True);old=json.loads((OLD/'FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V2.json').read_bytes());m=json.loads((OLD/old['manifest_local_filename']).read_bytes());proof=[];kept=[]
 for name,sha in old['executable_source_SHAs'].items():
  if name in (OLD_ENTRY,OLD_REMOTE,CPU):continue
  raw=(OLD/name).read_bytes();assert H(raw)==sha;write(name,raw);kept.append(name)
 name='E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json';write(name,(OLD/name).read_bytes())
 oldguard="assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('learn','backward','update') for n in ast.walk(tree))"
 newguard="from e2_frozen_worker_call_guard_v3 import validate_frozen_worker_calls\n guard=validate_frozen_worker_calls(tree)"
 proof.append(changed(CPU,CPU,[(oldguard,newguard),("worker_SHA=H(worker),versions=versions","worker_SHA=H(worker),frozen_worker_AST_call_guard=guard,versions=versions")]))
 proof.append(changed(OLD_REMOTE,REMOTE,[(OLD_STAGE,STAGE)]))
 proof.append(changed(OLD_ENTRY,ENTRY,[(OLD_STAGE,STAGE),(OLD_REMOTE,REMOTE),('FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V2.json',INDEX)]))
 for oldname,newname in READER_NAMES.items():
  text=(OLD/oldname).read_text();replacements=[]
  for a,b in [(OLD_STAGE,STAGE),('FROZEN_E2_93_NEW86_PROFILE_DOMAIN_SOURCE_INDEX_V2.json',INDEX),('E2_V2_','E2_V3_')]+list(READER_NAMES.items()):
   if a in text:replacements.append((a,b));text=text.replace(a,b)
  proof.append(changed(oldname,newname,replacements))
 rows=[]
 for r in m['files']:
  name=r['relative'];x=dict(r)
  if name==OLD_ENTRY:name=ENTRY
  if name==OLD_REMOTE:name=REMOTE
  if name in kept+[ENTRY,REMOTE,CPU,'E2_93_QUALIFIED_FORMAL_CPU_WITNESS.json']:
   raw=(B/name).read_bytes();x.update(relative=name,local_path=str(B/name),bytes=len(raw),SHA=H(raw))
  rows.append(x)
 guard='e2_frozen_worker_call_guard_v3.py';raw=(B/guard).read_bytes();rows.append(dict(relative=guard,local_path=str(B/guard),bytes=len(raw),SHA=H(raw)))
 m.update(files=rows,target_stage=STAGE,source_version='V3_typed_AST_environment_declaration_only_guard_repair',old_V2_actual_CPU_failure_preserved=True,worker_model_metric_physics_queue_unchanged=True)
 write('E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',(json.dumps(m,indent=2)+'\n').encode())
 actual=OLD/'reports/NEW86_E2_METADATA_WITNESS_AND_DETACHED_RETURNED_ACTUAL.json';raw=actual.read_bytes();v=json.loads(raw);assert not v['passed_source_CPU_and_detached_only'] and v['detached'] is None and v['source_CPU_actual_wait']['returncode']==1
 put('V2_ACTUAL_CPU_FALSE_ORIGINAL_ERROR_RETAINED_REFERENCE.json',dict(actual_report=str(actual),actual_full_SHA=H(raw),actual_returncode=1,detached=None,no_App_PT_GPU_or_GO=True,classification='metadata CPU blanket .update AST guard rejected declared environment update',old_source_and_once_untouched=True))
 put('V3_SOURCE_EXACT_INVERSE_AND_UNCHANGED_INPUT_PROOF.json',dict(passed=True,changes=proof,unchanged_sources=kept,model_runtime_asset_bank_rows_reused_metadata_only=True,no_binary_PT_raw_NPZ_USD_stat_or_read=True,no_remote_SDK_GPU_or_modelcall=True))
 selected=dict(status='V3_SOURCE_PENDING_SYNTHETIC_GUARD_AND_FINAL_FREEZE',entry=ENTRY,remote=REMOTE,index=INDEX,target_stage=STAGE,manifest_local_filename='E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json',manifest_SHA=H((B/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes()),executable_source_SHAs={n:H((B/n).read_bytes()) for n in kept+[ENTRY,REMOTE,CPU,guard]},readonly_source_SHAs={n:H((B/n).read_bytes()) for n in READER_NAMES.values()},first_reader=READER_NAMES[old['first_reader']],terminal_reader=READER_NAMES[old['terminal_reader']],source_model_SHA=old['source_model_SHA'],clone_receipt_SHA=old['clone_receipt_SHA'],actual_clone_CUDA_SDK_receipt_SHA=old['actual_clone_CUDA_SDK_receipt_SHA'])
 put('V3_SELECTION_PENDING_FINAL_FREEZE.json',selected);print(json.dumps(dict(passed=True,source_only=True,input_rows=len(rows),unchanged_worker=True,target=STAGE)))
if __name__=='__main__':main()
