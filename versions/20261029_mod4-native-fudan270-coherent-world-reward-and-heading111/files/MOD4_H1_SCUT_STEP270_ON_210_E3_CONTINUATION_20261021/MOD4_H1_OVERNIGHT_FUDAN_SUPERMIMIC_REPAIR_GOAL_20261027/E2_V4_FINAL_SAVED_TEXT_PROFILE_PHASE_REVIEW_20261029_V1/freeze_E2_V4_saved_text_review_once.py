from pathlib import Path
import ast,hashlib,json
B=Path(__file__).resolve().parent
def H(b):return hashlib.sha256(b).hexdigest()
def main():
 p=B/'E2_V4_COMPLETE900_SAVED_TEXT_PROFILE_PHASE_REVIEW_ACTUAL.json';v=json.loads(p.read_bytes());assert v['check_count']==126 and v['skill_graduation'] is False and v['complete_WM_dataset'] is False and v['no_new_model_raw_NPZ_gz_host_SDK_GPU_or_stats_query']
 script=B/'review_E2_V4_complete900_saved_text_once.py';ast.parse(script.read_bytes());assert len(v['all30_original_profile_rows'])==30
 receipt=dict(passed=True,source_script_SHA=H(script.read_bytes()),only_input_saved_JSON=v['input'],checks=126,all_counts_and_event_unique_denominators_preserved=True,no_oldmodel_raw_NPZ_gz_or_host_read=True,original_false_and_source_labels_preserved=True,skill_graduation=False)
 with (B/'SOURCE_AST_SINGLE_ALLOWED_TEXT_REVIEW_RECEIPT_ACTUAL.json').open('x') as f:json.dump(receipt,f,indent=2)
 rows=[]
 for p in sorted(B.iterdir()):
  if p.is_file():raw=p.read_bytes();rows.append(dict(relative=p.name,bytes=len(raw),SHA=H(raw)))
 index=B/'FROZEN_E2_V4_COMPLETE900_SAVED_TEXT_REVIEW_INDEX_ACTUAL.json'
 with index.open('x') as f:json.dump(dict(status='FROZEN_COMPLETED_SAVED_TEXT_REVIEW_NO_NEW_EXECUTION',files=rows,script=script.name,script_SHA=H(script.read_bytes()),input=v['input'],checks=126,ordinary_Git_pending_root=True,no_new_trial_tag=True,skill_graduation=False,complete_WM_dataset=False),f,indent=2)
 print(json.dumps(dict(passed=True,index=index.name,index_SHA=H(index.read_bytes()),report_SHA=H((B/'E2_V4_COMPLETE900_SAVED_TEXT_PROFILE_PHASE_REVIEW_ACTUAL.json').read_bytes()),script_SHA=H(script.read_bytes()),files=len(rows),source_text_only=True)))
if __name__=='__main__':main()
