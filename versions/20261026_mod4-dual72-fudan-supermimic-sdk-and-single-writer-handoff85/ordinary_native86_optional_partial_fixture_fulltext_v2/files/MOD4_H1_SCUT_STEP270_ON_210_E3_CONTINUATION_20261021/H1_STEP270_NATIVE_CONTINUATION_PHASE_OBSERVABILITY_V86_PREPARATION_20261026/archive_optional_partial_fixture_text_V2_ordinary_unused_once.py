from pathlib import Path
import importlib.util,json,time,traceback
F=Path(__file__).resolve().parent;R=F/'reports';T=F.parent;G=T.parent/'polar-rl-train'
p=F/'archive_optional_partial_fixture_text_ordinary_once.py';sp=importlib.util.spec_from_file_location('original_partial_archive_defs_only',p);old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
s=old.s
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch('ordinary_native86_optional_partial_fixture_fulltext','ordinary_native86_optional_partial_fixture_fulltext_v2')
patch('ACTUAL_ORDINARY_NATIVE86_SOURCE_PHASE_COVERAGE_GIT_NOTE','ACTUAL_ORDINARY_NATIVE86_PARTIAL_V2_GIT_NOTE')
patch('ORDINARY_NATIVE86_SOURCE_PHASE_COVERAGE_ARCHIVE_STARTED','ORDINARY_NATIVE86_PARTIAL_V2_ARCHIVE_STARTED')
ns={'__name__':'exact_partial_fulltext_V2_only','__file__':str(old.previous.base.m.m.engine)};exec(compile(s,str(old.previous.base.m.m.engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='c5620292ca8ef676643e3edc44c434031940c649' and len(git('tag','--list').splitlines())==1456 and not git('status','--porcelain')
 classification=json.loads((R/'EXACT_SYNTHETIC_OPTIONAL_IO_PARTIAL_FULLTEXT_CLASSIFICATION_ACTUAL.json').read_bytes());assert classification['bytes']==829 and classification['new_capture_full_UTF8_text']
 with (R/'PARTIAL_ARCHIVER_V1_LOCAL_NOTE_NAME_COLLISION_CLASSIFIED_ACTUAL.json').open('x',encoding='utf8') as out:json.dump(dict(epoch=time.time(),classification='LOCAL_ARCHIVER_PRECOMMIT_EXCLUSIVE_NOTE_FILENAME_COLLISION',original_V1_failed_before_Git_commit_or_push=True,current_HEAD=git('rev-parse','HEAD'),source86_first_ordinary_stays_committed=True,new_V2_only_unique_note_started_and_capture_namespace=True,no_experiment_or_runtime_change=True),out,indent=2)
 prior=G/'versions/20261026_mod4-dual72-fudan-supermimic-sdk-and-single-writer-handoff85'
 for rel in ('COMPLETE_FILE_CAPTURE_INDEX.json','ordinary_closed85_native_Fudan_E3_and_continuation_prep/ORDINARY_CAPTURE_INDEX.json','ordinary_native86_bound_phase_coverage_source_preparation/ORDINARY_CAPTURE_INDEX.json'):ns['prior'](prior/rel)
 note='''Ordinary fulltext completion for exact829byte synthetic optional-I/O JSON .partial, not binarymodel/raw. Prior unknownSHA metadata unchanged; originalclassification pins JSONbytes/SHA. Original attempted archiver failed precommit at exclusive existingnote filename; originalsource/trace/error retained, newV2 changes only unique note/started/capture namespace, no replay of oldonce and no experiment/model/remote/account effects. Capture source86CPUfixture partial fully, V1error/classification and V2source. No newtrial/tag, sourcecandidate still uninstalled/noTask/noGO. Existing1456tags/peels protected; postGit onlyconversation.'''
 ns['run_stage']('fudan',[F],[Path(__file__)],note,'Complete exact source fixture partial fulltext with unique archive namespace')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('PARTIAL_V2_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as out:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_second_record_or_tag=True),out,indent=2)
  raise
