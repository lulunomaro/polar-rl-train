"""Complete exact known synthetic JSON partial capture; never reopen binary models."""
from pathlib import Path
import importlib.util,json,hashlib,time,traceback
F=Path(__file__).resolve().parent;R=F/'reports';T=F.parent;G=T.parent/'polar-rl-train'
p=F/'archive_source86_phase_coverage_ordinary_unused_once.py';sp=importlib.util.spec_from_file_location('source86_archive_defs_only',p);previous=importlib.util.module_from_spec(sp);sp.loader.exec_module(previous)
s=previous.s
def patch(a,b):
 global s
 assert s.count(a)==1,a;s=s.replace(a,b,1)
patch('ordinary_native86_bound_phase_coverage_source_preparation','ordinary_native86_optional_partial_fixture_fulltext')
needle="and not (suffix=='.partial' and p.name.startswith('SYNTHETIC_ORIGINAL_ACCOUNT_FIXTURE') and 'agent_retire_old210_authority_cpu' in p.parts):"
replacement="and not (suffix=='.partial' and p.name.startswith('SYNTHETIC_ORIGINAL_ACCOUNT_FIXTURE') and 'agent_retire_old210_authority_cpu' in p.parts) and not (p.name=='occupied_directory.json.partial' and p.parent.name=='cpu_phase_attempt_1793019412219594400' and p.parent.parent.name=='H1_STEP270_NATIVE_CONTINUATION_PHASE_OBSERVABILITY_V86_PREPARATION_20261026'):"
patch(needle,replacement)
ns={'__name__':'exact_source86_optional_fixture_fulltext_capture','__file__':str(previous.base.m.m.engine)};exec(compile(s,str(previous.base.m.m.engine),'exec'),ns);git=ns['git']
def main():
 assert git('rev-parse','HEAD')=='c5620292ca8ef676643e3edc44c434031940c649' and len(git('tag','--list').splitlines())==1456 and not git('status','--porcelain')
 fixture=F/'cpu_phase_attempt_1793019412219594400/occupied_directory.json.partial';raw=fixture.read_bytes();j=json.loads(raw)
 assert len(raw)==829 and j['schema']=='mod4.native.sampled_policy_phase_coverage.v1' and j['sampled_starts']==1 and j['not_a_training_or_model_or_skill_gate']
 report=dict(epoch=time.time(),classification='INTENTIONAL_OPTIONAL_IO_FAILURE_CPU_SYNTHETIC_SMALL_JSON_PARTIAL',path=str(fixture),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),
             prior_archive_metadata_only_unknown_SHA_remains_original=True,new_capture_full_UTF8_text=True,
             exact_fixture_path_exception_only=True,no_general_partial_or_binary_model_reads=True,no_experiment_or_runtime_change=True)
 with (R/'EXACT_SYNTHETIC_OPTIONAL_IO_PARTIAL_FULLTEXT_CLASSIFICATION_ACTUAL.json').open('x',encoding='utf8') as out:json.dump(report,out,indent=2)
 prior=G/'versions/20261026_mod4-dual72-fudan-supermimic-sdk-and-single-writer-handoff85'
 for rel in ('COMPLETE_FILE_CAPTURE_INDEX.json','ordinary_closed85_native_Fudan_E3_and_continuation_prep/ORDINARY_CAPTURE_INDEX.json','ordinary_native86_bound_phase_coverage_source_preparation/ORDINARY_CAPTURE_INDEX.json'):ns['prior'](prior/rel)
 note='''Ordinary completion of exact829byte synthetic optional-I/O JSON partial. The prior source86 archive used generic large/binary metadata policy for the .partial suffix, retaining unknownSHA without readingcontent; that original record remains unchanged. New classification verifies this exact source-only CPU fixture as UTF8 JSON, pins actualbytes/SHA, and captures fulltext. No general partial allowlist, model/raw read, experiment retry, remote/GPU/budget or source modification. Source-only continuation/optionaldiagnostic remains uninstalled/noTask/noGO. Preserve1456tags/peels; no record/tag. PostGit onlyconversation.'''
 ns['run_stage']('fudan',[F],[Path(__file__)],note,'Capture exact synthetic optional-I-O partial JSON as full text')
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('EXACT_PARTIAL_ARCHIVE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as out:json.dump(dict(error=traceback.format_exc(),actual_HEAD=git('rev-parse','HEAD'),no_second_record_or_tag=True),out,indent=2)
  raise
