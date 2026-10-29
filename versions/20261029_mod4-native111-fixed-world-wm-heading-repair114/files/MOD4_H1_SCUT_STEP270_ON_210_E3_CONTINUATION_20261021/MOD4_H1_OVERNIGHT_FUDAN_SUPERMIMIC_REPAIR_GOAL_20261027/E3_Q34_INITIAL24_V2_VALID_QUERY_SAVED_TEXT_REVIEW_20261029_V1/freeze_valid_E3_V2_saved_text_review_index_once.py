"""Freeze only newly extracted report/source text; no original artifact revisit."""
from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 report=json.loads((B/'E3_V2_VALID95_ORIGINAL_RESET_WRITE_QUERY_CHAIN_SAVED_TEXT_REVIEW_ACTUAL.json').read_bytes());assert report['passed_text_chain_checks'] and report['check_count']==174
 rows=[]
 for p in sorted(B.iterdir()):
  if not p.is_file():continue
  assert p.suffix in ('.py','.json','.md');raw=p.read_bytes()
  if p.suffix=='.py':ast.parse(raw,str(p))
  rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw),archival_status='ordinaryGit_PENDING_root'))
 index=dict(status='FROZEN_SAVED_TEXT_REVIEW_ONLY_NOT_NEW_GPU_OR_MODEL_PURPOSE',files_excluding_index=len(rows),saved_files=rows,exact_original_first_read_once=report['source_extraction']['input_path'],exact_original_first_SHA=report['source_extraction']['input_SHA'],selected_producer_paths_bytes_SHAs=report['source_extraction']['selected_exact_original_UTF8_evidence'],original_first_and_normal_once_not_replayed=True,no_original_model_NPZ_raw_gz_SDK_host_GPU_access=True,no_unique_root_cause_or_new_physics_repair_or_skill_promotion=True)
 name='FROZEN_E3_V2_VALID95_SAVED_TEXT_CHAIN_REVIEW_INDEX_V1.json'
 with (B/name).open('x',encoding='utf8',newline='\n') as f:json.dump(index,f,indent=2)
 print(json.dumps(dict(index=name,index_SHA=H((B/name).read_bytes()),files=len(rows)+1,report_SHA=H((B/'E3_V2_VALID95_ORIGINAL_RESET_WRITE_QUERY_CHAIN_SAVED_TEXT_REVIEW_ACTUAL.json').read_bytes()))))
if __name__=='__main__':main()
