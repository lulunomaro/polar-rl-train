"""Derive NEW PH8 source-only capture from immutable PH7, no model/Git/rawread."""
from pathlib import Path
import ast,hashlib,traceback
P=Path(__file__).resolve().parent;WT=P.parents[2]
def main():
 base=WT/'history/experiments/mod4v1_robust_traditional_phase7_SOURCE_PREPARATION/prepare_source.py';text=base.read_text(encoding='utf-8');changes=[]
 def change(a,b):
  nonlocal text
  assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b);changes.append(a)
 change('"""PH7 bounded source snapshot only.','"""PH8 bounded source snapshot only.')
 change("'.macros','.in'","'.macros','.in','.m'")
 change("('mod4v1_robust_traditional_phase6_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','4e7a3fb9855657b5b501de08785f875b1e0bedfd')]","('mod4v1_robust_traditional_phase6_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','4e7a3fb9855657b5b501de08785f875b1e0bedfd'),('mod4v1_robust_traditional_phase7_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','223577994e0f750e0ae062ce9ffee204273c90a2')]")
 a=text.index('def forbidden(p):');b=text.index('\ndef main():',a)
 text=text[:a]+'''def forbidden(p):
  low=str(p).replace('\\\\','/').lower()
  if any(t in p.parts for t in ('__pycache__','.git','.venv','node_modules'))or any(t.startswith('.dsh-office-')for t in p.parts):return 'runtime_or_private_preview_cache'
  if p.is_relative_to(PROJECT/'repo-lqr'):return 'other_expert_worktree_not_read'
  if p.name.lower().startswith(('.env','id_rsa','id_ed25519'))or p.suffix.lower()in('.pem','.key','.kdbx'):return 'credential_path'
  if any(int(x)>=63 for x in ROUND.findall(low)):return 'R63plus_active_postcut_excluded'
  if any(x in low for x in ('spring_push_release_v1','r63_phase_source_review_v1','candidate_case_evidence_v1.py','launch_manual_profile_train_v5.py','derive_candidate_nominal_launcher_v5.py','preflight_candidate_binding_v1.py','parent_r63_binding_preflight_v1','phase9_pending')):return 'explicit_active_R63_workflow_excluded'
  if p.name.startswith(('~$','.tmp'))or p.suffix.lower()in('.tmp','.temp','.lock'):return 'temporary'
  return None
''' +text[b:];changes.append('full PH8 forbidden function')
 change("authority_path=S/'PH7_ARCHIVE_CUTOFF_R61.json'","authority_path=S/'PH8_ARCHIVE_CUTOFF_R62_INSIGHT.json'")
 change("assert authority['action']=='SOURCE_PREPARATION_ONLY_NO_RECORD_COMMIT_TAG_OR_PUSH'","assert authority['status']=='PARENT_EXPLICIT_CLOSED_SOURCE_SNAPSHOT_ONLY_NOT_GIT_APPROVAL' and authority['git_commit_tag_push_authorized_by_this_cutoff']is False")
 change("re.match(r'^r(?:54|55|56|57|58|59|60|61)(?:[^0-9]|$)',b.name,re.I)","re.match(r'^r62(?:[^0-9]|$)',b.name,re.I)")
 change("modules=[(S/x).resolve()for x in authority['root_trees_explicit']];root_names=set(authority['root_scripts_explicit'])|set(authority['handoffs'])|{authority_path.name}","modules=[(S/x).resolve()for x in authority['included_closed_root_dirs']];root_names={p.name for pattern in authority['included_root_filename_families_if_actual_files_exist']for p in S.glob(pattern)if p.is_file()}|{authority_path.name}")
 change('not_actual_closed_R54_R61_PROTOCOL_case_no_result_sweep','not_actual_closed_R62_PROTOCOL_case_no_result_sweep')
 change("'producer_SHA','output_sha256'","'producer_SHA','output_sha256','selected_bytes_SHA256','selected_PDF_bytes_SHA256'")
 change("'path','file','source_path','source','source_file','artifact','output','original_path','npz_path','raw_path'","'path','file','extracted_path','source_path','source','source_file','artifact','output','original_path','npz_path','raw_path'")
 report_line=next(line for line in text.splitlines(keepends=True)if line.lstrip().startswith("for report in sorted((S/'reports').iterdir()):"));a=text.index(report_line);indent=report_line[:len(report_line)-len(report_line.lstrip())]
 end_line=next(line for line in text[a:].splitlines(keepends=True)if line.lstrip().startswith('for b in closed_batches:'));b=text.index(end_line,a)
 text=text[:a]+indent+"for name in authority['included_result_reports']:\n"+indent+" add(S/name,'written_closed_report_actual_name',explicit=True)\n"+text[b:];changes.append('exact PH8 reports')
 change("prior_receipt=WT/authority['prior_postcommit_receipt']","prior_receipt=WT/'history/experiments/mod4v1_robust_traditional_phase8_PENDING/ARCHIVE_PHASE7_RECEIPT.json'")
 change("prior_commit='4e7a3fb9855657b5b501de08785f875b1e0bedfd'","prior_commit='223577994e0f750e0ae062ce9ffee204273c90a2'")
 change('prior_PH1_to_PH6_saved_SHA','prior_PH1_to_PH7_saved_SHA')
 change('expected51_results_46200controls_924000steps_are_sanity_only_not_evidence','expected6_results_4800controls_96000steps_are_sanity_only_not_evidence')
 change("'postcut_phase8_pending':True","'postcut_phase9_pending':True")
 change('LOCAL_PH7_SOURCE_PREPARED_ONLY_WAIT_PARENT_REVIEW','LOCAL_PH8_SOURCE_PREPARED_ONLY_WAIT_PARENT_REVIEW')
 dest=P/'prepare_source.py';assert not dest.exists();ast.parse(text);dest.write_text(text,encoding='utf-8');print('PH8_NEW_GENERATOR_AST_OK',hashlib.sha256(base.read_bytes()).hexdigest(),hashlib.sha256(dest.read_bytes()).hexdigest(),len(changes))
if __name__=='__main__':
 try:main()
 except BaseException:
  n=1
  while(P/f'GENERATOR_FAILURE_{n:03d}.txt').exists():n+=1
  (P/f'GENERATOR_FAILURE_{n:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(P/f'GENERATOR_FAILURE_SOURCE_{n:03d}.py').write_bytes(Path(__file__).read_bytes());raise
