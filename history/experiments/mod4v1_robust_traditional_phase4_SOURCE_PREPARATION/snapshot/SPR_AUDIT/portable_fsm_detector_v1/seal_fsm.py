"""Seal ONLY new native core/API, host facts and separately compile-only objects."""
from pathlib import Path
import json,hashlib,re,struct,zipfile,traceback
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
DISCOVERY=Path(r'C:\Users\lulu\AppData\Local\Temp\dsh-spill-GZhTPR\session-de481967f16c\1aa88acfbf5f-glob-results.txt')
CORE=['fd1_detector.c','fd1_detector.h','fd1_config_fields.inc','fd1_defaults.inc','fd1_reasons.inc','fd1_reason_names.inc']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def dump(n,v):
 p=HERE/n;text=json.dumps(v,indent=2,ensure_ascii=False)+'\n'
 if p.exists():
  before=p.read_bytes()
  if before==text.encode('utf-8'):return
  backup=HERE/'revisions/seal_attempt_01'/n;assert backup.is_file()and backup.read_bytes()==before,'Preserve previous metadata before overwrite'
 p.write_text(text,encoding='utf-8')
def row(p):return {'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
def check_pe(p):
 raw=p.read_bytes();off=struct.unpack_from('<I',raw,60)[0];assert raw[:2]==b'MZ'and raw[off:off+4]==b'PE\0\0'and struct.unpack_from('<H',raw,off+4)[0]==0x14c and struct.unpack_from('<H',raw,off+24)[0]==0x10b
 return 'PE32_i386'
def main():
 freeze=load('SOURCE_FREEZE.json')
 for r in freeze['old_files']+freeze['sources']:
  p=Path(r['path']);assert p.is_file()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],str(p)
 source_names=['fd1_detector.c','fd1_detector.h','fd1_config_fields.inc','fd1_defaults.inc','fd1_reasons.inc','fd1_reason_names.inc']
 for folder,receipt in [('revisions/host_attempt_03','HOST_BUILD_03.json'),('revisions/arm_attempt_02','ARM_BUILD_02.json')]:
  data=load(receipt);assert data['success']
  for n in source_names:assert sha(HERE/n)==data['sources'][n]==sha(HERE/folder/n)
 for attempt in [1,2,3]:
  b=load(f'HOST_BUILD_{attempt:02d}.json');assert b['success']and all(c['exit_code']==0 and c['artifact_exists']for c in b['commands'])
  assert sha(HERE/'NUMERICAL_BUDGET.json')==sha(HERE/f'revisions/host_attempt_{attempt:02d}/NUMERICAL_BUDGET.json')
  for r in b['commands']:
   p=Path(r['artifact'])
   if attempt<3 and p.name in ['fd1_host_tests.exe','fd1_cpp_smoke.exe']:p=HERE/f'revisions/host_attempt_{attempt:02d}'/p.name
   assert p.is_file()and p.stat().st_size==r['bytes']and sha(p)==r['sha256'],str(p)
   if p.suffix=='.exe':check_pe(p)
 assert load('ARM_BUILD_01.json')['success']==False
 arm=load('ARM_BUILD_02.json');assert len(arm['objects'])==2 and all(r['exit_code']==0 for r in arm['commands'])
 for r in arm['objects']:assert sha(Path(r['object']))==r['sha256']
 compare=load('COMPARISON.json');assert compare['reference_rows']==1042 and not compare['mismatches']and compare['all_numeric_fields_binary64_bit_equal']and compare['budgets_unchanged']
 assert compare['native_checks']['3']=={'checks':1993,'failures':0}
 for n in ['host','cpp']:assert 'exit_code=0'in (HERE/(n+'_run_03.log')).read_text()
 host_runs=load('HOST_CPP_RUN_03.json');assert all(r['exit_code']==0 and r['artifact_retained']for r in host_runs)
 registry=load('REASON_REGISTRY.json');assert registry['reason_count']==69 and registry['reason_word_count']==2
 core_receipt={'status':'SEALED_NEW_NATIVE_C99_API_SOURCE_CLOSURE','source':freeze['sources'][1],'native_files':[row(HERE/n)for n in CORE],'semantics_sha256':sha(HERE/'SEMANTIC_MAPPING.md'),'numerical_budget_sha256':sha(HERE/'NUMERICAL_BUDGET.json'),'reason_registry_sha256':sha(HERE/'REASON_REGISTRY.json'),'defaults_unchanged':True,'number_format':'binary64_relative_seconds','C3_float32_promotion_adds_precision':False,'default_actions_disabled_unbound':True,'contact_calibrated_or_truth':False,'C3_online_actuation':False,'old_proposal_ABI_compatible':False,'caller_owned_no_heap':True}
 dump('CORE_RECEIPT.json',core_receipt)
 host={'status':'SEALED_NEW_NATIVE_HOST_INTERFACE_QUALIFICATION','source_scenarios_visited':63,'source_only_zero_step_methods':compare['source_only_methods_with_zero_step'],'new_fixed_contexts':61,'new_C_reference_steps':1042,'replay_checks':46087,'replay_failures':0,'native_checks':1993,'native_failures':0,'numeric_max_absolute_error':0.,'all_numeric_output_bits_equal_in_this_fixture':True,'ordered_reasons_faults_permissions_compared':True,'C_plus_plus_extern_C_executed':True,'host_context_size_bytes':1536,'host_output_size_bytes':392,'host_binary_format':check_pe(HERE/'fd1_host_tests.exe'),'host_executable':row(HERE/'fd1_host_tests.exe'),'CPP_executable':row(HERE/'fd1_cpp_smoke.exe'),'not_63_robot_episodes':True,'old_Python_score_updated':False,'ARM_execution':0,'physical_steps':0,'WCET':False}
 dump('HOST_QUALIFICATION.json',host)
 bundle=HERE/'fd1_source_bundle.zip'
 if not bundle.exists():
  with zipfile.ZipFile(bundle,'x',compression=zipfile.ZIP_DEFLATED)as z:
   for n in CORE+['BUILD.txt']:z.write(HERE/n,'portable_fsm_detector_v1/'+n)
 with zipfile.ZipFile(bundle)as z:
  for n in CORE:assert hashlib.sha256(z.read('portable_fsm_detector_v1/'+n)).hexdigest()==sha(HERE/n)
 discovered=DISCOVERY.read_text(encoding='utf-8-sig');inventory=HERE/'DISCOVERED_FILES.txt'
 if inventory.exists():assert inventory.read_bytes()==(HERE/'revisions/seal_attempt_01/DISCOVERED_FILES.txt').read_bytes()
 inventory.write_text(discovered,encoding='utf-8');paths=[(ROOT/p).resolve()for p in discovered.splitlines()if p.strip()and not ((ROOT/p).resolve().parent==HERE and Path(p).name in ['INDEX.json','VALIDATION.json','MANIFEST.json','seal_run_01.log','seal_run_02.log'])]
 for p in paths:assert p.is_relative_to(HERE)and p.is_file(),str(p)
 paths += [HERE/n for n in ['BUILD.txt','seal_fsm.py','DISCOVERED_FILES.txt','CORE_RECEIPT.json','HOST_QUALIFICATION.json','fd1_source_bundle.zip']]
 records=[]
 for p in sorted(set(paths)):
  r=row(p);r['relative']=p.relative_to(HERE).as_posix();r['role']='preserved_attempt'if 'revisions'in p.parts else 'new_native_core_or_qualification_evidence'
  if p.suffix not in ['.exe','.o','.zip']:
   lines=len(p.read_text(encoding='utf-8-sig').splitlines());r['lines']=lines
   if lines:r['citation']=r['relative']+f'#L1-L{lines}'
  records.append(r)
 validation={'status':'SEALED_NEW_NATIVE_CORE_AND_HOST_INTERFACE_SEPARATE_ARM_OBJECT_FACTS','old_files_unchanged':len(freeze['old_files']),'source_files_verified':len(freeze['sources']),'reference_rows':1042,'contexts':61,'zero_discrete_or_ordered_mismatches':True,'max_numeric_error':0.,'native_checks':1993,'native_failures':0,'C_plus_plus_link_run':True,'new_ARM_objects':2,'ARM_execution':0,'binary64_software_helpers_BSP_linked':False,'WCET_or_stack_measured':False,'new_physics_steps':0,'new_robot_episodes':0,'new_agents':0,'Git_calls':0,'C3_online_actuation':False,'default_force_trusted':False,'default_jump_recovery_autoobstacle':False,'old_Python_score_updated':False,'blocked_ASQP_IO_repaired':False,'scope_does_not_block_other_authorized_work':True,'all_attempts_preserved':True,'files_indexed':len(records)}
 dump('VALIDATION.json',validation);dump('INDEX.json',{'name':'portable_fsm_detector_v1','status':validation['status'],'validation':validation,'files':records,'excluded_recursive_metadata':['INDEX.json','VALIDATION.json','MANIFEST.json','seal_run_01.log','seal_run_02.log']})
 primary=['README.md','ERROR_REPORT.md','fd1_detector.c','fd1_detector.h','fd1_source_bundle.zip','SEMANTIC_MAPPING.md','NUMERICAL_BUDGET.json','SOURCE_FREEZE.json','CORE_RECEIPT.json','HOST_QUALIFICATION.json','COMPARISON.json','OBJECT_SUMMARY.json','ARM_BUILD_02.json','INDEX.json','VALIDATION.json']
 expected_links=sum(len(re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')))for n in ['README.md','ERROR_REPORT.md','SCOPE.md','SEMANTIC_MAPPING.md'])
 dump('MANIFEST.json',{'status':validation['status'],'deliverables':[row(HERE/n)for n in primary],'links_checked':expected_links})
 links=0
 for n in ['README.md','ERROR_REPORT.md','SCOPE.md','SEMANTIC_MAPPING.md']:
  for link in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   file,_,fragment=link.partition('#');p=(HERE/file).resolve();assert p.is_file(),link
   if fragment:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment)
    if m:assert 1<=int(m[1])<=int(m[2]or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),link
   links+=1
 assert links==expected_links
 print(json.dumps({**validation,'markdown_links_checked':links,'README_sha256':sha(HERE/'README.md'),'INDEX_sha256':sha(HERE/'INDEX.json'),'source_bundle_sha256':sha(bundle)}))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'seal_error_02.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
