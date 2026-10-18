"""Continue the unrecorded stage after rejecting a stale historical manifest alias."""
from pathlib import Path
import importlib.util,json,time,traceback
B=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('failed_before_any_record_or_note_old_archive_source',B/'archive_H1_8a7c_review_one_hour_continuation_unique_once.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def known_actual(old):
 known={str(Path(r['source_path']).resolve()):dict(bytes=r['bytes'],SHA=r['sha256'],provenance='previous complete Git index') for r in old['entries'] if r.get('sha256') and Path(r['source_path']).suffix.lower() not in m.TEXT}
 skipped=[]
 def accept(path,row,proof):
  if not isinstance(path,str) or not isinstance(row.get('bytes'),int):return
  sha=row.get('SHA') or row.get('sha256');p=Path(path)
  if not isinstance(sha,str) or len(sha)!=64 or not p.is_file() or p.suffix.lower() in m.TEXT:return
  if p.stat().st_size!=row['bytes']:
   skipped.append(dict(path=str(p),proof=str(proof),actual_bytes=p.stat().st_size,declared_bytes=row['bytes'],reason='Historical or unrelated alias is not a current complete artifact index'));return
  known[str(p.resolve())]=dict(bytes=row['bytes'],SHA=sha,provenance=str(proof))
 def visit(v,proof):
  if isinstance(v,list):
   for row in v:visit(row,proof)
  elif isinstance(v,dict):
   for key in ('local_path','path','source_path'):accept(v.get(key),v,proof)
   for row in v.values():
    if isinstance(row,(dict,list)):visit(row,proof)
 for root in (B/'resumed_ce3_original_fp32_v1',B/'hour1_h1_8a7c_v1'):
  for p in root.rglob('*.json'):
   if '__pycache__' in p.parts:continue
   v=json.loads(p.read_bytes())
   if 'reports' in p.parts:visit(v,p)
   if p.name in ('THREE_SLOT_COMPLETE_MANIFEST_V1.json','H1_CR3_FINAL_LINUX4090_MANIFEST_V1.json') and isinstance(v,dict):
    for row in v.get('files',[]):
     if isinstance(row,dict) and isinstance(row.get('relative'),str):accept(str(p.parent/row['relative']),row,p)
 with (B/'reports/H1_ONE_HOUR_ARCHIVE_HISTORICAL_MANIFEST_ALIAS_V1_FALSE_V2_FIX_ACTUAL.json').open('x',encoding='utf8') as f:
  json.dump(dict(epoch=time.time(),original_V1_assertion_retained=True,V1_before_note_DEST_record_commit_tag=True,V2_uses_previous_complete_index_plus_actual_new_root_manifests_and_producer_reports_only=True,skipped_aliases=skipped,no_large_rehash_or_GPU_account_runtime_action=True),f,indent=2)
 return known
if __name__=='__main__':
 try:
  m.getknown=known_actual;m.main()
 except BaseException:
  with (B/'reports'/('H1_ONE_HOUR_UNIQUE_V2_GIT_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),if_committed_only_push_existing_objects_no_repeat_record_tag=True),f,indent=2)
  raise
