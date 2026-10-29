"""Index only new saved source/review text. No external artifacts or rerun."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 result=json.loads((B/'E0_V2_FULL1000_EARLY_COMMAND_INSTANCE_SAVED_TEXT_ACCEPTANCE_REVIEW_ACTUAL.json').read_bytes());assert result['passed_text_integrity_and_accounting'] and result['check_count']==251
 rows=[]
 for p in sorted(B.iterdir()):
  if not p.is_file():continue
  assert p.suffix in ('.py','.json','.md');raw=p.read_bytes()
  if p.suffix=='.py':ast.parse(raw,filename=str(p))
  rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw),archive_status='ordinaryGit_PENDING_root'))
 name='FROZEN_E0V2_FULL1000_EARLY_COMMAND_SAVED_TEXT_REVIEW_INDEX_V1.json'
 index=dict(status='FROZEN_SAVED_TEXT_REVIEW_ONLY',files_excluding_index=len(rows),saved_files=rows,input_terminal=result['input_terminal'],checked_saved_text_rows65=True,integrity_accounting_checks251=True,original_case_or_model_source_not_modified=True,raw_JSONL_NPZ_PT_gz_SDK_host_GPU_access=False,original_skill_acceptance_pending=True,no_learning_writer_or_new_trial_tag=True)
 with (B/name).open('x',encoding='utf8',newline='\n') as f:json.dump(index,f,indent=2)
 print(json.dumps(dict(index=name,SHA=H((B/name).read_bytes()),files=len(rows)+1,report_SHA=H((B/'E0_V2_FULL1000_EARLY_COMMAND_INSTANCE_SAVED_TEXT_ACCEPTANCE_REVIEW_ACTUAL.json').read_bytes()))))
if __name__=='__main__':main()
