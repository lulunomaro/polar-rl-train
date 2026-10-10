"""Retain immutable existing collection; new name for new actual evidence."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';old=D/'sync_curb133_partial_schema_actual_once.py';new=D/'sync_curb133_partial_schema_unique_name_once.py'
assert not new.exists() and (R/'CURB133_PARTIAL_SCHEMA_SYNC_ERROR.json').exists()
src=old.read_text(encoding='utf8').replace('CURB133_PARTIAL_SCHEMA_SYNC_STARTED','CURB133_PARTIAL_SCHEMA_UNIQUE_SYNC_STARTED').replace('CURB133_PARTIAL_ACTUAL_SCHEMA_METADATA_SYNCED','CURB133_PARTIAL_UNIQUE_ACTUAL_SCHEMA_METADATA_SYNCED').replace('CURB133_PARTIAL_SCHEMA_SYNC_ERROR','CURB133_PARTIAL_SCHEMA_UNIQUE_SYNC_ERROR').replace('E1_CURB20_133_CURRENT_COLLECTION.json','E1_CURB20_133_ACTUAL_COLLECTION_SCHEMA_REVIEWED.json')
src=src.replace("scope.update(actual_133_partial_review=", "scope.update(actual_133_collection=str(R/'E1_CURB20_133_ACTUAL_COLLECTION_SCHEMA_REVIEWED.json'),actual_133_partial_review=")
guard="""  with n.open_sftp() as check:
   existing=json.loads(check.open(E+'/reports/E1_CURB20_133_CURRENT_COLLECTION.json').read())
   assert not existing['cases'] and len(existing['pending'])==4
   current=json.loads(check.open(E+'/reports/MOE_PLAN_EXECUTION_CURRENT.json').read())
   assert 'actual_133_schema_reader_review' not in current['terrain_subexpert_revision004']['curb20_formal_reviewed_scope']
   for name in reports:assert name not in check.listdir(E+'/reports')
"""
src=src.replace('  with n.open_sftp() as f:\n   for name,raw in reports.items():',guard+'  with n.open_sftp() as f:\n   for name,raw in reports.items():')
compile(src,str(new),'exec');new.write_bytes(src.encode())
v=dict(epoch=time.time(),trial_id='CURB133-PARTIAL-SYNC-IMMUTABLE-EXISTING-NAME-01',original_exclusive_SFTP_existing_collection_rejected_before_any_new_file_or_CAS=True,existing_current_collection_original_retained=True,new_unique_snapshot_name='E1_CURB20_133_ACTUAL_COLLECTION_SCHEMA_REVIEWED.json',old_source_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),new_source_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),no_GPU_budget_or_old_once_replay=True)
(R/'CURB133_PARTIAL_SYNC_UNIQUE_NAME_REPAIR_REVIEW.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
