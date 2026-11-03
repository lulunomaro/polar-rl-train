"""Derive NEW PH7 bounded archive implementation; do not edit or run PH6 helper."""
from pathlib import Path
import ast,hashlib,traceback
P=Path(__file__).resolve().parent;WT=P.parents[2]
old=WT/'history/experiments/mod4v1_robust_traditional_phase6_SOURCE_PREPARATION/prepare_source.py';dest=P/'prepare_source.py'
assert not dest.exists();original=old.read_bytes();text=original.decode('utf-8');changes=[]
def change(a,b):
    global text
    assert text.count(a)==1,(a,text.count(a));text=text.replace(a,b);changes.append(a)
def main():
    global text
    change('PH6 bounded source snapshot only.','PH7 bounded source snapshot only.')
    change("('mod4v1_robust_traditional_phase5_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','0a21cdc6445268c05389103afea071836424b470')]","('mod4v1_robust_traditional_phase5_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','0a21cdc6445268c05389103afea071836424b470'),('mod4v1_robust_traditional_phase6_SOURCE_PREPARATION/FINAL_SOURCE_MANIFEST.json','4e7a3fb9855657b5b501de08785f875b1e0bedfd')]")
    change("if any(int(x)>=54 for x in ROUND.findall(low)):return 'R54plus_future_excluded'","if any(int(x)>=62 for x in ROUND.findall(low)):return 'R62plus_future_excluded'")
    change("if any(x in low for x in ('takeoff_window005','launch_manual_profile_train_v1','spin_stop_causal_v1','phase7_pending')):return 'explicit_active_PH7_excluded'","if any(x in low for x in ('air_pitch_ref','prepare_r62','phase8_pending')):return 'active_AIR_PITCH_REF_or_PH8_excluded'")
    change("authority_path=S/'PH6_ARCHIVE_CUTOFF_R53.json';authority=load(authority_path);authority_sha=sh(authority_path.read_bytes());assert authority['kind']=='PH6_SOURCE_PREPARATION_AUTHORITY_ONLY_NOT_GIT_COMMIT_APPROVAL'","authority_path=S/'PH7_ARCHIVE_CUTOFF_R61.json';authority=load(authority_path);authority_sha=sh(authority_path.read_bytes());assert authority['action']=='SOURCE_PREPARATION_ONLY_NO_RECORD_COMMIT_TAG_OR_PUSH'")
    change("re.match(r'^r(?:48|49|50|51|52|53)(?:[^0-9]|$)',b.name,re.I)","re.match(r'^r(?:54|55|56|57|58|59|60|61)(?:[^0-9]|$)',b.name,re.I)")
    change("manual=[(S/x).resolve()for x in authority['manual_first_bar_allowlist_only']];modules=[(S/x).resolve()for x in authority['include_new_module_roots']]+[x for x in manual if x.is_dir()];root_names=set(authority['root_script_name_allowlist'])|{authority_path.name}","modules=[(S/x).resolve()for x in authority['root_trees_explicit']];root_names=set(authority['root_scripts_explicit'])|set(authority['handoffs'])|{authority_path.name}")
    change("not_actual_closed_R48_R53_PROTOCOL_case_no_result_sweep","not_actual_closed_R54_R61_PROTOCOL_case_no_result_sweep")
    change(next(line for line in text.splitlines(keepends=True) if "if p.is_relative_to(S/'MANUAL_FIRST_BAR_V1')" in line),"")
    change(" for x in manual:\n  if x.is_file():add(x,'written_MANUAL_FIRST_BAR_file_allowlist',explicit=True)\n for rel in authority['include_completed_reports']:add(S/rel,'written_completed_report',explicit=True)"," for report in sorted((S/'reports').iterdir()):\n  if report.is_file() and re.match(r'^R(?:54|55|57|59|60|61)(?:[^0-9]|$)',report.name,re.I) and report.suffix.lower()in('.json','.md'):add(report,'written_closed_report_family_actual_file',explicit=True)")
    change("authority['include_prior_postcommit_receipt']","authority['prior_postcommit_receipt']")
    change("kind='existing_repository_reference',prior_commit='0a21cdc6445268c05389103afea071836424b470'","kind='existing_repository_reference',prior_commit='4e7a3fb9855657b5b501de08785f875b1e0bedfd',observed_source_SHA_before=h")
    change("prior_PH1_to_PH4_saved_SHA","prior_PH1_to_PH6_saved_SHA")
    change("expected13_results_182040_steps_are_crosschecks_not_source_evidence","expected51_results_46200controls_924000steps_are_sanity_only_not_evidence")
    change("postcut_phase7_pending","postcut_phase8_pending")
    change("LOCAL_PH6_SOURCE_PREPARED_ONLY_WAIT_PARENT_REVIEW","LOCAL_PH7_SOURCE_PREPARED_ONLY_WAIT_PARENT_REVIEW")
    ast.parse(text);dest.write_text(text,encoding='utf-8');print({'old_template_SHA':hashlib.sha256(original).hexdigest(),'new_capture_SHA':hashlib.sha256(dest.read_bytes()).hexdigest(),'asserted_substitutions':len(changes)})
if __name__=='__main__':
    try:main()
    except BaseException:
        i=1
        while(P/f'GENERATOR_FAILURE_{i:03d}.txt').exists():i+=1
        (P/f'GENERATOR_FAILURE_{i:03d}.txt').write_text(traceback.format_exc(),encoding='utf-8');(P/f'GENERATOR_FAILURE_SOURCE_{i:03d}.py').write_bytes(Path(__file__).read_bytes());raise
