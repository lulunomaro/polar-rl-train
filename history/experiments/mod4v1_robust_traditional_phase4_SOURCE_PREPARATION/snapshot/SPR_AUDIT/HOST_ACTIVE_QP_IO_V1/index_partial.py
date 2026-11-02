"""Index BLOCKED evidence only. No compilation, solver run, physics or AV change."""
from pathlib import Path
import hashlib,json,re,struct,traceback
HERE=Path(__file__).resolve().parent
ROOT='''SCOPE.md
freeze_io.py
SOURCE_FREEZE.json
aq_io_build.h
PROTOCOL_SCHEMA.json
clock_vectors.h
CLOCK_VECTORS.json
freeze_01.log
aq_clock.h
aq_clock.c
clock_selftest.c
active_qp_host.c
sdk_fault_fixture.c
compiler_version_01.log
production_01.log
test_clock_only_01.log
clock_selftest.exe
clock_selftest_01.log
sdk_fault_fixture.exe
SDK_lifecycle_fixture_not_solver_01.log
BUILD_RECEIPT_01.json
build_01.log
adapter_diagnostic_01.o
missing_output_diagnostic_01.log
build_io.py
compiler_version_02.log
production_02.log
BUILD_RECEIPT_02.json
build_02.log
missing_output_link_diagnostic_01.log
clock_run_01.log
clock_diagnostic_01.o
core_diagnostic_01.o
link_diagnostic_01.map
explicit_link_diagnostic_01.log
link_probe.c
link_probe_NONE.exe
link_probe_NONE.log
link_probe_PROBE_FENV.exe
link_probe_PROBE_FENV.log
link_probe_PROBE_STRTOF.log
file_events_diagnostic_01.log
active_qp_stdio.py
EVENT_CHECK_01.json
sdk_only_tests.py
PREPARED_UNSENT_186_FRAMES.jsonl
SDK_ONLY_TESTS_01.json
sdk_only_run_01.log
README.md
ERROR_REPORT.md
DIAGNOSTIC_COMMANDS.md
index_partial.py'''.splitlines()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def dump(n,data):
 p=HERE/n
 if p.exists():raise FileExistsError(p)
 p.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def row(p,role):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p),'role':role}
def main():
 freeze=load('SOURCE_FREEZE.json')
 for record in freeze['old_files']:
  p=Path(record['path']);assert p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],str(p)
 for key in ['core','header','reference_cases','reference_direct_C']:
  r=freeze[key];assert sha(Path(r['path']))==r['sha256']
 revision_files=['build_io.py','active_qp_host.c','aq_clock.c','aq_clock.h','aq_io_build.h','clock_selftest.c','clock_vectors.h','sdk_fault_fixture.c','PROTOCOL_SCHEMA.json','SCOPE.md'];names=list(ROOT)
 for folder in ['build_attempt_01','build_attempt_02']:
  names.extend('revisions/'+folder+'/'+n for n in revision_files)
  for n in ['active_qp_host.c','aq_clock.c','aq_clock.h','aq_io_build.h']:assert sha(HERE/n)==sha(HERE/'revisions'/folder/n)
 names.extend('revisions/build_attempt_01/'+n for n in ['clock_selftest.exe','sdk_fault_fixture.exe'])
 for n in ['active_qp_stdio.py','sdk_only_tests.py','PROTOCOL_SCHEMA.json']:
  names.append('revisions/sdk_only_attempt_01/'+n);assert sha(HERE/n)==sha(HERE/'revisions/sdk_only_attempt_01'/n)
 b1,b2=load('BUILD_RECEIPT_01.json'),load('BUILD_RECEIPT_02.json');assert len(b1['commands'])==5 and all(r['exit_code']==0 for r in b1['commands']) and len(b1['binaries'])==2;assert len(b2['commands'])==2 and b2['commands'][-1]['exit_code']==0 and b2['commands'][-1]['artifact_exists']==False
 for r in b1['binaries']:
  p=Path(r['path']);assert p.is_file() and sha(p)==r['sha256'] and p.stat().st_size==r['bytes'];data=p.read_bytes();off=struct.unpack_from('<I',data,60)[0];assert data[off:off+4]==b'PE\0\0' and struct.unpack_from('<H',data,off+4)[0]==0x14c and struct.unpack_from('<H',data,off+24)[0]==0x10b
 missing=['active_qp_host.exe','active_qp_clock_harness.exe','active_qp_host_diagnostic.exe','explicit_link_diagnostic_01.exe','watch_link_diagnostic_01.exe','link_probe_PROBE_STRTOF.exe'];assert all(not (HERE/n).exists() for n in missing)
 clock=(HERE/'clock_run_01.log').read_text(encoding='utf-8-sig');assert 'checks=2514 failures=0 exact_integer_vectors=254' in clock
 sdk=load('SDK_ONLY_TESTS_01.json');assert sdk['checks']==29154 and not sdk['failures'] and sdk['production_frames_sent']==0 and not sdk['reference_direct_comparison_executed'] and not sdk['logical_earlyabort_worker_test_executed'];assert len((HERE/'PREPARED_UNSENT_186_FRAMES.jsonl').read_text().splitlines())==186
 events=load('EVENT_CHECK_01.json');assert events['read_only'] and events['no_AV_changes'] and all(not r['exact_artifact_hits'] for r in events['logs'])
 closure={'status':'DRAFT_BLOCKED_NOT_RELEASED','production_C':[row(Path(freeze[key]['path']),'unchanged_sealed_'+key) for key in ['core','header']]+[row(HERE/n,'new_adapter_or_clock_source') for n in ['active_qp_host.c','aq_clock.c','aq_clock.h','aq_io_build.h']],'Python_SDK':[row(HERE/n,'draft_SDK_dependency') for n in ['active_qp_stdio.py','PROTOCOL_SCHEMA.json']],'system_dependencies':'C/MinGW runtime + Windows QPC; no ctypes/NumPy/physics in SDK','production_binary':'ABSENT','one_core_solve_per_frame_source_contract':True,'production_runtime_verification':False}
 dump('SOURCE_CLOSURE.json',closure)
 records=[]
 for n in sorted(set(names)):
  p=HERE/n;assert p.is_file(),n;r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p),'role':'preserved_attempt' if n.startswith('revisions/') else 'draft_or_partial_evidence_not_qualified_IO'}
  if p.suffix not in ['.exe','.o']:
   lines=len(p.read_text(encoding='utf-8-sig').splitlines());r['lines']=lines
   if lines:r['citation']=n+f'#L1-L{lines}'
  records.append(r)
 validation={'status':'BLOCKED_NOT_SEALED','old_files_unchanged':len(freeze['old_files']),'sealed_core_unchanged':True,'sealed_header_unchanged':True,'retained_required_production_worker':False,'deletion_actor':'UNKNOWN','exact_artifact_disposition_events':0,'no_AV_settings_changed':True,'same_source_compile_stopped_on_parent_instruction':True,'clock_integer_vectors':254,'clock_component_checks':2514,'clock_component_failures':0,'SDK_only_checks':29154,'SDK_only_failures':0,'prepared_frames':186,'production_frames_sent':0,'direct_C_comparison_executed':False,'raw_production_parser_fault_tests_executed':False,'logical_earlyabort_IO_executed':False,'new_physics_steps':0,'ARM_execution':0,'MCU_3ms_or_parent_cycle_qualified':False,'TRAIN_integration_allowed':False,'missing_artifacts':missing,'pending':['retained production PE32 binary and concrete removal attribution','186 direct numerical cold/warm comparisons','production raw bad-frame/duplicate/nonfinite/integer-limit/fatal-cleanup tests','deterministic I/O earlyabort','successful IO seal'],'files_indexed':len(records)}
 dump('VALIDATION.json',validation);dump('INDEX.json',{'name':'HOST_ACTIVE_QP_IO_V1','status':'BLOCKED_NOT_SEALED','files':records,'validation':validation,'metadata_excluded_from_recursive_hashes':['INDEX.json','VALIDATION.json','MANIFEST.json','SOURCE_CLOSURE.json','index_partial_run_01.log']})
 links=0
 for n in ['README.md','ERROR_REPORT.md','DIAGNOSTIC_COMMANDS.md']:
  for link in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   file,_,fragment=link.partition('#');p=(HERE/file).resolve();assert p.is_file(),link
   if fragment:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),link
   links+=1
 primary=['README.md','ERROR_REPORT.md','active_qp_stdio.py','PROTOCOL_SCHEMA.json','active_qp_host.c','aq_clock.c','SOURCE_FREEZE.json','SOURCE_CLOSURE.json','SDK_ONLY_TESTS_01.json','EVENT_CHECK_01.json','INDEX.json','VALIDATION.json']
 dump('MANIFEST.json',{'status':'BLOCKED_NOT_SEALED_NOT_A_SUCCESS_RECEIPT','deliverables':[row(HERE/n,'blocked_stage_evidence') for n in primary],'markdown_links_checked':links});print(json.dumps({**validation,'markdown_links_checked':links}))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_partial_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
