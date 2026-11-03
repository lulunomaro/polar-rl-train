"""NEW preflight caller for the independently validated flat20 packaging fix.
No prior caller/remote package is edited or replayed; no native parent operations.
"""
from pathlib import Path
import ast,hashlib,json,time
R=Path(__file__).resolve().parent;old=R/'upload_preflight_good_holdout_v3_seed20260929_once.py';new=R/'upload_preflight_good_holdout_v3_flat20_fix_seed20260929_once.py';out=R/'reports/GOOD_HOLDOUT_FLAT20_PREFLIGHT_CALLER_SOURCE_V1.json';assert not new.exists()and not out.exists();b=old.read_bytes();t=b.decode();H=lambda b:hashlib.sha256(b).hexdigest()
changes=[('GOOD_HOLDOUT_V3_SEED20260929_ACTUAL_PREFLIGHT_V1.json','GOOD_HOLDOUT_V3_SEED20260929_FLAT20_FIX_ACTUAL_PREFLIGHT_V1.json'),('GOOD_HOLDOUT_V3_SEED20260929_PREFLIGHT_STARTED_ONCE.json','GOOD_HOLDOUT_V3_SEED20260929_FLAT20_FIX_PREFLIGHT_STARTED_ONCE.json'),('GOOD_HOLDOUT_SOURCE_PAYLOAD_V3.json','GOOD_HOLDOUT_SOURCE_PAYLOAD_V3_FLAT20_FIX_V1.json'),("assert pay['unique_files']==103 and pay['mirror_declared_and_current_full_files']==79 and pay['actual_remote_preflight_stage_parent_SDK_model_C_or_resource_operations']==0","assert pay['unique_files']==123 and pay['source_mapping_count']==20 and pay['whole_original_source_mappings_local_passed']and pay['old_stager_source_unchanged']and pay['actual_remote_stage_parent_SDK_model_C_or_resource_operations']==0"),("'MOD4V1_GOOD_TEACHER_HOLDOUT_20260929_V3_'","'MOD4V1_GOOD_TEACHER_HOLDOUT_20260929_V3_FLAT20_FIX_V1_'"),("'--source-dir',project+'/source_good_expert_holdout_subset_v1'","'--source-dir',project+'/good_holdout_complete_flat20_v1'"),('NEW_GOOD_HOLDOUT_V3_SEED20260929_SOURCE_PREFLIGHT_NOT_NATIVE','NEW_GOOD_HOLDOUT_V3_SEED20260929_FLAT20_FIXED_SOURCE_PREFLIGHT_NOT_NATIVE')]
for before,after in changes:
 assert t.count(before)==1,(before,t.count(before));t=t.replace(before,after,1)
anchor="review_path=R/'source_good_holdout_lifecycle_parent_review_v2/SOURCE_REVIEW.json'";assert t.count(anchor)==1;t=t.replace(anchor,"prior=json.loads((R/'reports/GOOD_HOLDOUT_V3_SEED20260929_ACTUAL_PREFLIGHT_V1.json').read_bytes());assert prior['returncode']==1 and '/source_good_expert_holdout_subset_v1/a1_frozen_eval_runtime_v2.py'in prior['stderr']and 'FileNotFoundError'in prior['stderr']\n"+anchor,1);ast.parse(t)
with new.open('x',encoding='utf8',newline='\n')as f:f.write(t)
z=new.read_bytes();v=dict(kind='GOOD_HOLDOUT_FLAT20_NEW_PREFLIGHT_CALLER_SOURCE_NOT_EXECUTED',epoch=time.time(),source_template=str(old),source_template_SHA256=H(b),path=str(new),bytes=len(z),SHA256=H(z),original_D3_stager_runtime_parent_or_predicate_changed=False,actual_remote_or_native_or_model_operations=0)
with out.open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
print(json.dumps(v,indent=2))
