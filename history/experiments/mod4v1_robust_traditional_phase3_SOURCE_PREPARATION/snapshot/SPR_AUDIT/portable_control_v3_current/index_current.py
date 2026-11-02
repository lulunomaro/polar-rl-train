"""Seal current V4/P25 component evidence; no unit/physics replay here."""
from pathlib import Path
import hashlib,json,re,csv,traceback
HERE=Path(__file__).resolve().parent
ROOT_NAMES=['SCOPE.md','freeze_inputs.py','pc3_geometry_data.h','pc3_p25_data.h','SOURCE_FREEZE.json','freeze_attempt_01.log',
 'pc3_control.h','pc3_estimator.c','pc3_controller.c','pc3_dispatch.c','edit_attempt_01.txt','host_objects_build_01.log','host_objects_build_02.log','host_objects_build_03.log',
 'pc3_selftest.c','pc3_selftest_host.exe','pc3_selftest_host_02.exe','pc3_selftest_host_03.exe','unit_build_01.log','unit_build_02.log','unit_build_03.log','unit_run_01.log','unit_run_02.log','unit_run_03.log',
 'make_reference_vectors.py','REFERENCE_VECTORS.csv','pc3_vector_layout.h','REFERENCE_LAYOUT.json','reference_generation_01.log','NUMERICAL_BUDGET.json','pc3_replay_host.c','pc3_replay_host.exe','replay_build_01.log','C_REPLAY_01.jsonl','replay_run_01.log','compare_reference.py','NUMERICAL_COMPARISON.json','NUMERICAL_EXCEEDANCES_01.csv','comparison_run_01.log',
 'prepare_arm_current.py','pc3_cpp_smoke.cpp','inspect_objects.py','target_probe.c','arm_current.ps1','ARM_HARNESS_PROVENANCE.json','arm_harness_prepare_01.log','armclang_version_01.log','fromelf_help_01.log',
 'cpp_pc3_estimator_build_01.log','cpp_pc3_controller_build_01.log','cpp_pc3_dispatch_build_01.log','cpp_ctk_build_01.log','pc3_cpp_smoke_host.exe','cpp_link_01.log','cpp_run_01.log',
 'BUILD_RECEIPT.json','arm_build_attempt_01.log','OBJECT_SUMMARY.csv','OBJECT_SUMMARY.json','object_inspection_01.log','README.md','ERROR_REPORT.md','pc3_estimator.o','pc3_controller.o','pc3_dispatch.o','index_current.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 freeze=load('SOURCE_FREEZE.json');old=freeze['old_sealed_snapshot'];sources=freeze['sources'];trains=freeze['fixed_train_inputs']
 for record in old+sources+trains:
  p=Path(record['path']);assert p.stat().st_size==record['bytes'] and sha(p)==record['sha256'],record['path']
 comparison=load('NUMERICAL_COMPARISON.json');assert comparison['rows']==3200 and comparison['all_status_OK'] and comparison['budget_exceedance_points']==0
 refs=load('REFERENCE_LAYOUT.json');assert refs['rows']==3200 and not refs['mujoco_loaded'] and refs['physics_steps']==0 and not refs['H2_feedback_ported']
 for case in refs['cases']:
  if case['name'].startswith('TRAIN_'):assert case['frozen_Python64_vs_logged14_max_abs']==0
 assert 'checks=6509 failures=0' in (HERE/'unit_run_03.log').read_text(encoding='utf-8-sig')
 assert 'pass=1' in (HERE/'cpp_run_01.log').read_text(encoding='utf-8-sig')
 assert 'status_failures=0' in (HERE/'replay_run_01.log').read_text(encoding='utf-8-sig')
 successful_logs=['host_objects_build_02.log','host_objects_build_03.log','unit_build_01.log','unit_build_02.log','unit_build_03.log','unit_run_01.log','unit_run_02.log','unit_run_03.log','replay_build_01.log','replay_run_01.log','comparison_run_01.log','cpp_pc3_estimator_build_01.log','cpp_pc3_controller_build_01.log','cpp_pc3_dispatch_build_01.log','cpp_ctk_build_01.log','cpp_link_01.log','cpp_run_01.log']
 for n in successful_logs:assert 'exit_code=0' in (HERE/n).read_text(encoding='utf-8-sig'),n
 assert 'exit_code=1' in (HERE/'host_objects_build_01.log').read_text(encoding='utf-8-sig')
 names=list(ROOT_NAMES)
 base=['pc3_control.h','pc3_estimator.c','pc3_controller.c','pc3_dispatch.c']
 revision_map={'build_attempt_01':base+['pc3_geometry_data.h','pc3_p25_data.h','pc3_estimator.o','pc3_controller.o'],
               'build_attempt_02':base+['pc3_geometry_data.h','pc3_p25_data.h','pc3_estimator.o','pc3_controller.o','pc3_dispatch.o'],
               'unit_attempt_01':base+['pc3_selftest.c'],'unit_attempt_02':base+['pc3_selftest.c'],'unit_attempt_03':['pc3_selftest.c'],
               'reference_attempt_01':['make_reference_vectors.py'],'replay_attempt_01':base+['pc3_replay_host.c','pc3_vector_layout.h','NUMERICAL_BUDGET.json'],
               'arm_attempt_01':base+['pc3_p25_data.h','arm_current.ps1']}
 for folder,files in revision_map.items():names.extend('revisions/'+folder+'/'+n for n in files)
 names.extend('cpp_objects/'+n+'.o' for n in ['pc3_estimator','pc3_controller','pc3_dispatch','ctk_dependency'])
 receipt=load('BUILD_RECEIPT.json');assert len(receipt['objects'])==6
 for record in receipt['sources']:
  p=Path(record['path']);assert sha(p)==record['sha256'] and p.stat().st_size==record['bytes']
 for event in receipt['commands']:
  assert event['exit_code']==0;names.append(Path(event['log']).relative_to(HERE).as_posix())
  if event['phase']=='object_compile_only':assert '-c' in event['arguments'] and '-mfloat-abi=hard' in event['arguments'] and not any('sse' in a.lower() for a in event['arguments'])
 for record in receipt['objects']:
  p=Path(record['object']);assert record['compile_exit']==0 and record['present'] and p.stat().st_size==record['bytes'] and sha(p)==record['sha256'];names.append(p.relative_to(HERE).as_posix())
 for n in ['pc3_estimator.c','pc3_controller.c','pc3_dispatch.c']:
  text=(HERE/n).read_text(encoding='utf-8');assert not re.search(r'\b(malloc|calloc|realloc|free)\s*\(',text) and not re.search(r'\bdouble\b',text)
 records=[]
 for n in sorted(set(names)):
  p=HERE/n;assert p.is_file(),n;r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p)}
  if p.suffix not in ['.o','.exe']:
   count=len(p.read_text(encoding='utf-8-sig').splitlines());r['line_count']=count
   if count:r['citation']=f'{n}#L1-L{count}'
  r['role']='preserved_attempt' if n.startswith('revisions/') else ('host_or_ARM_build_QA_not_firmware' if p.suffix in ['.o','.exe'] else 'current_source_data_or_log');records.append(r)
 index={'name':'portable_control_v3_current','status':'SEALED_STAGES1_AND2_CURRENT_V4_ESTIMATOR_AND_P25_NUMERICAL_PORT',
  'archive_scope':'postR16/PH3_pending_component; does not enlarge PH2 frozen conclusions','write_scope':str(HERE),'files':records,
  'frozen_sources':sources,'old_snapshot_verified_unchanged':len(old),'TRAIN_inputs':trains,
  'implemented':['100Hz coherent-queue packet validation, no collector','explicit arming + quaternion/lever/pivot/vector gate','Joseph v/b KF + heading unwrap + one-time age view','same-packet lateral proxy diagnostic only','actual P25 K + legPID120/4 + yawPI/FF/shaping/leash1','unchanged effort/signed-DC law + explicit row order','abstract single enqueue, invalid mean/age/time/fault latching and callback late invalidation'],
  'deferred':['H2 nominalK/relative2Dodom/commonwheel tau20 cap1.8 feedback','actual asynchronous/timeweighted acquisition collector','all real hardware/BSP/DM3519 CAN/driver binding','nondefault V4 controller modes, jump/step/contact FSM'],
  'schema':'state14 delta=crank-minus-hip, not passive FK knee; row6 LH LC LW RH RC RW; wheel-first [2,5,0,1,3,4] mathematical only',
  'source_guard_differences':['explicit supported/static arming rather than undeclared bad-IMU upright fallback','changed-payload duplicate hard fault','mandatory positive vector-innovation limit','bounded f32 unwrap domain and exact100Hz controller tick','fault latch/reset/rearm + strict metadata/finiteness/covariance checks'],
  'validation':{'unit_checks':6509,'unit_failures':0,'C_replay_rows':3200,'reference_scenarios':9,'numerical_budget_exceedances':0,'TRAIN_frozen64_log_max':0,'Cpp_externC_pass':True,'ARM_compile_only_objects':6,'ARM_runtime_tests':0,'new_physics_steps':0},
  'no_hardware_binding':True,'no_heap_or_VLA_or_mutable_global_core_state':True,
  'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST/index log excluded from recursive hashes'}
 dump('INDEX.json',index)
 validation={'old_files_unchanged':len(old),'frozen_source_files_unchanged':len(sources),'fixed_TRAIN_files_unchanged':len(trains),'files_indexed':len(records),
 'unit_checks':6509,'unit_failures':0,'C_replay_rows':3200,'numerical_budget_exceedances':0,'TRAIN_reconstructed64_vs_logged14_max':0,'ARM_compile_only_objects':6,'ARM_runtime_tests':0,'new_physics_steps':0,'H2_feedback_ported':False,'hardware_binding':False}
 dump('VALIDATION.json',validation);dump('MANIFEST.json',{});links=0
 for n in ['README.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   fn,_,fragment=target.partition('#');p=(HERE/fn).resolve();assert p.is_file(),target
   if fragment:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 validation['markdown_links_checked']=links;dump('VALIDATION.json',validation)
 primary=['pc3_control.h','pc3_estimator.c','pc3_controller.c','pc3_dispatch.c','pc3_p25_data.h','pc3_geometry_data.h','README.md','SOURCE_FREEZE.json','NUMERICAL_COMPARISON.json','OBJECT_SUMMARY.json','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in primary]})
 print(json.dumps(validation,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
