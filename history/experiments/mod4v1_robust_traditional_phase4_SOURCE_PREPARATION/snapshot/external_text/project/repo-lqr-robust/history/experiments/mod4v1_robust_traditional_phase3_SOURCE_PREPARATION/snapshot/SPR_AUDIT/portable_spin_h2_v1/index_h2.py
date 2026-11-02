"""Seal fixed-H2 math component, not an actuator/physical qualification."""
from pathlib import Path
import json,hashlib,re,traceback
HERE=Path(__file__).resolve().parent
ROOT=['SCOPE.md','NUMERICAL_BUDGET.json','freeze_h2.py','sh2_nominal_data.h','sh2_geometry_fixture.h','SOURCE_FREEZE.json','freeze_01.log','sh2_control.h','sh2_controller.c','sh2_pipeline.c','sh2_controller.o','sh2_pipeline.o','host_build_01.log','make_h2_reference.py','REFERENCE_H2.csv','sh2_vector_layout.h','REFERENCE_LAYOUT.json','reference_01.log','sh2_selftest.c','sh2_selftest_host.exe','unit_build_01.log','unit_run_01.log','sh2_replay_host.c','sh2_replay_host.exe','replay_build_01.log','C_H2_REPLAY_01.jsonl','replay_run_01.log','compare_h2.py','NUMERICAL_COMPARISON.json','NUMERICAL_EXCEEDANCES_01.csv','comparison_01.log','prepare_arm_h2.py','sh2_cpp_smoke.cpp','arm_h2.ps1','inspect_h2_objects.py','target_probe.c','ARM_HARNESS_PROVENANCE.json','arm_prepare_01.log','armclang_version_01.log','fromelf_help_01.log','cpp_sh2_controller_01.log','cpp_sh2_pipeline_01.log','cpp_estimator_01.log','cpp_ctk_01.log','sh2_cpp_smoke_host.exe','cpp_link_01.log','cpp_run_01.log','host_defined_symbols_01.log','BUILD_RECEIPT.json','arm_build_01.log','OBJECT_SUMMARY.csv','OBJECT_SUMMARY.json','object_inspection_01.log','README.md','ERROR_REPORT.md','index_h2.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 freeze=load('SOURCE_FREEZE.json')
 for r in freeze['old_files']+freeze['sources']+freeze['TRAIN']:
  p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
 ref=load('REFERENCE_LAYOUT.json');numeric=load('NUMERICAL_COMPARISON.json');assert ref['rows']==numeric['rows']==5400 and ref['physics_steps']==0
 assert all(ref['cases'][0][key]==0 for key in ['logged14_max_abs','logged_tau_max_abs','logged_center_max_abs'])
 assert ref['source_nominalK_max_difference']<1e-9 and ref['source_velocity_center_cap']==0 and freeze['nominal_K_vs_P25_max_abs_difference']>1
 assert not numeric['status_failures'] and not numeric['flag_mismatches'] and numeric['budget_exceedance_points']==0 and not numeric['actuation_qualified']
 assert 'checks=5418 failures=0' in (HERE/'unit_run_01.log').read_text(encoding='utf-8-sig')
 assert 'pass=1' in (HERE/'cpp_run_01.log').read_text(encoding='utf-8-sig')
 symbols=(HERE/'host_defined_symbols_01.log').read_text(encoding='utf-8-sig');assert 'sh2_controller_step' in symbols and 'pc3_estimator_update' in symbols and not re.search(r'pc3_p25|pc3_cycle',symbols)
 for n in ['host_build_01.log','unit_build_01.log','unit_run_01.log','reference_01.log','replay_build_01.log','replay_run_01.log','comparison_01.log','cpp_sh2_controller_01.log','cpp_sh2_pipeline_01.log','cpp_estimator_01.log','cpp_ctk_01.log','cpp_link_01.log','cpp_run_01.log','host_defined_symbols_01.log']:
  assert 'exit_code=0' in (HERE/n).read_text(encoding='utf-8-sig'),n
 for n in ['sh2_controller.c','sh2_pipeline.c']:
  text=(HERE/n).read_text();assert not re.search(r'\b(malloc|calloc|realloc|free)\s*\(|\bdouble\b|pc3_p25|pc3_cycle',text)
  assert sha(HERE/n)==sha(HERE/'revisions/build_attempt_01'/n)==sha(HERE/'revisions/replay_attempt_01'/n)==sha(HERE/'revisions/arm_attempt_01'/n)
 assert sha(HERE/'NUMERICAL_BUDGET.json')==sha(HERE/'revisions/reference_attempt_01/NUMERICAL_BUDGET.json')
 names=list(ROOT);base=['sh2_control.h','sh2_controller.c','sh2_pipeline.c'];revisions={'build_attempt_01':base+['sh2_nominal_data.h','sh2_geometry_fixture.h'],'unit_attempt_01':base+['sh2_selftest.c'],'reference_attempt_01':['make_h2_reference.py','NUMERICAL_BUDGET.json'],'replay_attempt_01':base+['sh2_replay_host.c','sh2_vector_layout.h','NUMERICAL_BUDGET.json'],'arm_attempt_01':base+['sh2_nominal_data.h','arm_h2.ps1']}
 for folder,files in revisions.items():names.extend('revisions/'+folder+'/'+n for n in files)
 names.extend('cpp_objects/'+n+'.o' for n in ['sh2_controller','sh2_pipeline','pc3_estimator','ctk'])
 receipt=load('BUILD_RECEIPT.json');assert len(receipt['objects'])==4
 for r in receipt['sources']:assert sha(Path(r['path']))==r['sha256']
 for event in receipt['commands']:
  assert event['exit_code']==0;names.append(Path(event['log']).relative_to(HERE).as_posix())
  if event['phase']=='object_compile_only':assert '-c' in event['arguments'] and '-mfloat-abi=hard' in event['arguments'] and not any('sse' in arg.lower() for arg in event['arguments'])
 for r in receipt['objects']:
  p=Path(r['object']);assert r['compile_exit']==0 and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'];names.append(p.relative_to(HERE).as_posix())
 records=[]
 for n in sorted(set(names)):
  p=HERE/n;assert p.is_file(),n;r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p),'role':'preserved_attempt' if n.startswith('revisions/') else ('host_or_ARM_build_QA_not_firmware' if p.suffix in ['.exe','.o'] else 'source_numerical_data_or_log')}
  if p.suffix not in ['.exe','.o']:
   lines=len(p.read_text(encoding='utf-8-sig').splitlines());r['line_count']=lines
   if lines:r['citation']=f'{n}#L1-L{lines}'
  records.append(r)
 flags=['math valid only; actuation_qualified always0','full failsafe dispatcher and H2 IO loop deferred; no P25 linkage','relative2D/no-side-slip proxy not world measurement; unknown slip unobserved','explicit supported-upright gyro-only prior, not arbitrary initial attitude','source age-view legFK with held gyro differs from raw-epoch proxy','source positive4pi physical scope unchanged; synthetic stop/reverse not physical qualification','f32 gauge/ref precision at20m/long duration not covered; sealed C3 unchanged']
 host_flags=['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse']
 index={'name':'portable_spin_h2_v1','status':'SEALED_FROZEN_H2_PURE_MATH_NOT_ACTUATION_QUALIFIED','archive':'postR16/PH3_pending_no_PH2_expansion','files':records,'old_files_verified_unchanged':len(freeze['old_files']),'sources_verified_unchanged':len(freeze['sources']),'TRAIN_files_verified_unchanged':len(freeze['TRAIN']),'nominal_K_vs_P25_max_abs_difference':freeze['nominal_K_vs_P25_max_abs_difference'],'source_controller':freeze['H2_controller'],'source_base_defaults':freeze['base_defaults'],'limits':flags,
 'validation':{'unit_checks':5418,'unit_failures':0,'replay_rows':5400,'budget_exceedances':0,'original_R11_Python64_vs_logged14_tau_center_max':0,'Cpp_externC_pass':True,'ARM_compile_only_objects':4,'ARM_execution':0,'new_physics_steps':0,'actuation_qualified':False},
 'source_identity':'nominal K row6 LH LC LW RH RC RW; delta=crank-minus-hip; wheel-first [2,5,0,1,3,4]; output load-side Nm, real hardware bindings unqualified',
 'host_build':{'compiler':r'C:\MinGW\bin\gcc.exe','flags':host_flags,'math_link_sources':['sh2_controller.c','sh2_pipeline.c','../portable_control_v3_current/pc3_estimator.c','../portable_core_v2_kinematics/ct_kinematics.c'],'unit_main':'sh2_selftest.c','replay_main':'sh2_replay_host.c','libraries':['-lm'],'no_P25_controller_or_dispatcher':True},'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST/index stdout excluded from recursive hashes'}
 dump('INDEX.json',index)
 validation={'files_indexed':len(records),'old_files_unchanged':len(freeze['old_files']),'frozen_sources_unchanged':len(freeze['sources']),'TRAIN_files_unchanged':len(freeze['TRAIN']),'unit_checks':5418,'unit_failures':0,'replay_rows':5400,'budget_exceedances':0,'active_target_flag_mismatches':0,'original_R11_Python64_log_max':0,'no_P25_or_dispatcher_defined_symbols':True,'ARM_compile_only_objects':4,'ARM_execution':0,'new_physics_steps':0,'actuation_qualified':False,'full_dispatch':'deferred','PH3':'pending'}
 dump('VALIDATION.json',validation);dump('MANIFEST.json',{});links=0
 for n in ['README.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   fn,_,fragment=target.partition('#');p=(HERE/fn).resolve();assert p.is_file(),target
   if fragment:
    match=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment)
    if match:assert 1<=int(match[1])<=int(match[2] or match[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 validation['markdown_links_checked']=links;dump('VALIDATION.json',validation)
 primary=['sh2_control.h','sh2_controller.c','sh2_pipeline.c','sh2_nominal_data.h','SOURCE_FREEZE.json','README.md','NUMERICAL_COMPARISON.json','OBJECT_SUMMARY.json','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in primary]})
 print(json.dumps(validation))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
