"""Freeze only new source/review/publication text, no original artifacts revisited."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 p=B/'E2_V5_COMPLETE900_EARLY_COMMAND_INSTANCE_PROFILE_PHASE_TEXT_REVIEW_ACTUAL.json';v=json.loads(p.read_bytes());assert v['passed_saved_text_integrity_and_denominator_accounting'] and v['check_count']==151
 rows=[]
 for q in sorted(B.iterdir()):
  if not q.is_file():continue
  assert q.suffix in ('.py','.json','.md');raw=q.read_bytes()
  if q.suffix=='.py':ast.parse(raw,str(q))
  rows.append(dict(relative=q.name,bytes=len(raw),SHA=H(raw),archival_status='ordinaryGit_PENDING_root'))
 index=dict(status='FROZEN_SAVED_TEXT_REVIEW_ONLY',files_excluding_index=len(rows),saved_files=rows,input_terminal=v['input_terminal'],selected_original_publications=v['selected_exact_small_publications'],checked_small_original_UTF8_bytes_and_SHA=True,metadata_only_artifact_contents_not_opened=True,no_original_model_PT_NPZ_raw_gz_JSONL_SDK_host_or_GPU_access=True,skill_status='PENDING_ORIGINAL_ACCEPTANCE_NOT_GRADUATED',old_E2V4_and_other_original_reports_unchanged=True,no_new_trial_or_tag=True)
 name='FROZEN_E2_V5_COMPLETE900_EARLY_COMMAND_SAVED_TEXT_REVIEW_INDEX_V1.json'
 with (B/name).open('x',encoding='utf8',newline='\n') as f:json.dump(index,f,indent=2)
 print(json.dumps(dict(index=name,SHA=H((B/name).read_bytes()),files=len(rows)+1,report_SHA=H(p.read_bytes()))))
if __name__=='__main__':main()
