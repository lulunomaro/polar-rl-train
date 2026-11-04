"""Saved-evidence V7 close only. Does not import or run either attribute reader."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def load(name):return json.loads((HERE/name).read_text(encoding='utf-8'))
def digest(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'SHA256':hashlib.sha256(b).hexdigest()}
def out(name,obj):
 with (HERE/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def main():
 snap=load('INPUT_SNAPSHOT.json');pre=load('QA_PREEXEC.json');fixtures=load('FIXTURE_RESULTS_01.json');result=load('OBJECT_SCOPE_RESULT_01.json')
 old=[]
 for ref in snap['old_read_only_inputs']:
  actual=digest(ROOT/ref['path']);assert actual==ref,ref['path'];old.append(actual)
 assert digest(HERE/'METHOD.md')==snap['method']
 assert digest(HERE/'OFFICIAL_RULES.json')==snap['official_rules']
 for key,name in [('reader_SHA256','scoped_attrs_v7.py'),('runner_SHA256','run_review_once.py'),('input_snapshot_SHA256','INPUT_SNAPSHOT.json'),('fixture_plan_SHA256','FIXTURE_PLAN_01.json')]:
  assert digest(HERE/name)['SHA256']==pre[key],name
 assert fixtures['status']=='PASS' and fixtures['fixture_count']==4 and fixtures['parse_attempts']==4 and fixtures['checks']==19
 assert result['status']=='PASS_STATIC_THIS_OBJECT_ONLY' and result['scope_metadata_checks']==64 and result['real_object_parse_attempts']==1
 assert len(result['code_sections'])==6 and result['code_type_unknown_count']==0 and result['code_type_same_scope_conflict_count']==0
 assert result['original_V6_record']=={'compiler_success_count':1,'post_ABI_accepted_prefix_count':0,'pass_gate':False,'unchanged':True}
 assert result['new_ARM_native_fromelf_compile_probe_link_calls']==0 and result['assessment']['original_file_parser_unknown_resolved_for_this_object'] is True
 assert not result['assessment']['native_continuation_authorized']
 assert not (HERE/'PARTIAL_ERROR_01.json').exists()
 report=(HERE/'REPORT.md').read_text(encoding='utf-8');lines=len(report.splitlines());assert lines<=120
 links=[]
 for target in re.findall(r'\]\(<([^>]+)>\)',report):
  if target.startswith(('https://','http://')):continue
  file=target.split('#',1)[0];p=(HERE/file).resolve();assert p.is_file(),target;links.append(target)
 names=['METHOD.md','OFFICIAL_RULES.json','INPUT_SNAPSHOT.json','prepare_scope_once.py','prepare_scope_01.log','scoped_attrs_v7.py','run_review_once.py','QA_PREEXEC.json','FIXTURE_PLAN_01.json','FIXTURE_RESULTS_01.json','OBJECT_SCOPE_RESULT_01.json','review_01.log','REPORT.md','close_static_v7.py']
 artifacts=[digest(HERE/n) for n in names]
 status='SEALED_STATIC_SCOPE_REVIEW_THIS_OBJECT_ONLY_ORIGINAL_V6_GATE_UNCHANGED_NO_CONTINUATION'
 validation={'status':status,'valid':True,'report_lines':lines,'local_report_links_checked':len(links),'six_old_small_inputs_unchanged':True,'fixtures':4,'fixture_assertions':19,'actual_object_parse_calls':1,'saved_object_metadata_checks':64,'code_sections':6,'unknown':0,'conflict':0,'symbol_scope_actual':0,'synthetic_symbol_test_not_real_SYMTAB_coverage':True,'new_ARM_native_compile_probe_fromelf_link':0,'old_QA_calls':0,'new_robot_or_PHY_calls':0,'full_target_qualified':False,'remaining_TU_continuation_authorized':False,'reader_not_general_ELF_qualification':True}
 out('VALIDATION.json',validation)
 receipt={'status':status,'official_declared_document_version':'2026Q3 / 2026-11-03; main URLs not commit-pinned, exact excerpts hashed','static_assessment':result['assessment'],'original_V6_record_unchanged':result['original_V6_record'],'remaining_unstarted':{'C':161,'ASM':1},'actual_execution':{'Python_stdlib_metadata_runs_before_this_close':2,'new_fixture_blobs_and_parse_calls':4,'new_fixture_checks':19,'existing_object_parse_calls':1,'object_saved_metadata_checks':64,'ARM_native_compile_probe_fromelf_link_calls':0,'old_reader_or_old_QA_calls':0},'old_small_input_hashes_unchanged':old,'new_artifacts':artifacts,'validation':digest(HERE/'VALIDATION.json'),'close_is_saved_only_no_QA_or_reader_rerun':True,'receipt_is_not_self_hashed':True}
 out('RECEIPT.json',receipt)
 print(json.dumps({'status':status,'report':digest(HERE/'REPORT.md'),'receipt':digest(HERE/'RECEIPT.json'),'validation':digest(HERE/'VALIDATION.json'),'old_small_inputs_unchanged':len(old),'report_lines':lines,'ARM_native':0},ensure_ascii=False))
if __name__=='__main__':main()
