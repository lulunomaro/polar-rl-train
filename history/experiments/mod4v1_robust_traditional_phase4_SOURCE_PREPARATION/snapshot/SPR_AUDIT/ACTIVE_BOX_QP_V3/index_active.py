"""Read-only evidence recheck + seal; does not rerun QP/clock/robot tests."""
from pathlib import Path
import hashlib,json,re,traceback
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=['SCOPE.md','NUMERICAL_BUDGET.json','freeze_active.py','SOURCE_FREEZE.json','freeze_01.log','python_proof.py','PROBLEMS.json','PYTHON_PROOF.json','ab3_cases.h','python_proof_01.log','active_box_qp.h','active_driver.c','active_driver_host.exe','build_01.log','C_RUNS_01.jsonl','runs_01.log','analysis_01.log','diagnose_warm01.c','diagnose_warm01.exe','diagnose_build_01.log','WARM01_TRACE.csv','diagnose_run_01.log','active_box_qp.c','analyse_active.py','active_driver_host_02.exe','build_02.log','C_RUNS_02.jsonl','runs_02.log','COMPARISON.json','ALL_NONCONVERGED.json','RUN_COMPARISON.csv','analysis_02.log','active_selftest.c','active_selftest_host.exe','unit_build_01.log','EARLY_ABORT_CASES_01.csv','unit_run_01.log','active_cpp_smoke.cpp','prepare_arm_ab3.py','active_cpp_link.o','cpp_c_build_01.log','active_cpp_smoke.exe','cpp_link_01.log','cpp_run_01.log','arm_active.ps1','ARM_HARNESS_PROVENANCE.json','inspect_active_objects.py','target_probe.c','arm_prepare_01.log','armclang_version_01.log','fromelf_help_01.log','BUILD_RECEIPT.json','arm_build_01.log','OBJECT_SUMMARY.json','OBJECT_SUMMARY.csv','object_inspection_01.log','ALGORITHM_REVISION_02.md','README.md','ERROR_REPORT.md','index_active.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def count_primary(runs,budget,mode):return sum(r['valid'] for r in runs if r['real_H15'] and r['budget']==budget and r['mode']==mode)
def main():
 freeze=load('SOURCE_FREEZE.json')
 for r in freeze['old_files']+freeze['real_MPC_references']:
  p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
 assert sha(HERE/'NUMERICAL_BUDGET.json')==freeze['budget_sha256']
 for revision in ['python_attempt_01','build_attempt_01','build_attempt_02']:assert sha(HERE/'NUMERICAL_BUDGET.json')==sha(HERE/'revisions'/revision/'NUMERICAL_BUDGET.json')
 for revision in ['build_attempt_02','unit_attempt_01','cpp_attempt_01','arm_attempt_01']:
  for name in ['active_box_qp.h','active_box_qp.c']:assert sha(HERE/name)==sha(HERE/'revisions'/revision/name)
 assert sha(HERE/'active_box_qp.c')!=sha(HERE/'revisions/build_attempt_01/active_box_qp.c')
 core=(HERE/'active_box_qp.c').read_text();assert not re.search(r'\b(malloc|calloc|realloc|free)\s*\(|\bdouble\b',core)
 problems=load('PROBLEMS.json')['cases'];proof=load('PYTHON_PROOF.json');assert len(problems)==93 and len(proof['runs'])==186 and not proof['failures'] and all(r['status']=='CONVERGED' for r in proof['runs'])
 # Verify generated C literals exactly roundtrip every declared input as f32.
 lines=[s for s in (HERE/'ab3_cases.h').read_text().splitlines() if s.startswith('{')];assert len(lines)==93
 pattern=r'^\{(\d+)u,([01])u,"([^"]+)",\{([^}]*)\},\{([^}]*)\},\{([^}]*)\},\{([^}]*)\},\{([^}]*)\}\},$'
 original=json.loads((HERE.parent/'C_MPC8_NUMERIC_V1/actual_model_vectors.json').read_text())
 for cid,(q,line) in enumerate(zip(problems,lines)):
  match=re.fullmatch(pattern,line);assert match,q['name'];assert int(match[1])==q['n'] and match[3]==q['name'];n=q['n'];padded=np.zeros((16,16),dtype=np.float32);padded[:n,:n]=np.asarray(q['H'],dtype=np.float32);expected=[padded.ravel()]
  for key in ['f','lo','hi','warm']:
   a=np.zeros(16,dtype=np.float32);a[:n]=np.asarray(q[key],dtype=np.float32);expected.append(a)
  for numbers,want in zip(match.groups()[3:],expected):
   got=np.asarray([float(x.rstrip('f')) for x in numbers.split(',')],dtype=np.float32);assert np.array_equal(got.view(np.uint32),want.view(np.uint32)),q['name']
  assert q['oracle_checked_kkt']<=1e-8 and q['eigen_min']>0
  if cid<18:
   assert np.array_equal(np.asarray(q['H']),original['H32'])
   for key,oldkey in [('f','f32'),('lo','lo32'),('hi','hi32'),('warm','warm32')]:assert np.array_equal(np.asarray(q[key]),original['cases'][cid][oldkey])
 runs1=[json.loads(s) for s in (HERE/'C_RUNS_01.jsonl').read_text().splitlines()];runs2=[json.loads(s) for s in (HERE/'C_RUNS_02.jsonl').read_text().splitlines()];assert len(runs1)==len(runs2)==1302
 assert sum(not r['valid'] for r in runs1)==402 and sum(not r['valid'] for r in runs2)==392
 assert count_primary(runs1,64,0)==18 and count_primary(runs1,64,1)==14 and count_primary(runs1,256,1)==16
 assert count_primary(runs2,64,0)==count_primary(runs2,64,1)==18
 compare=load('COMPARISON.json');assert not compare['certificate_failures'] and not compare['actual_accuracy_budget_failures']
 for mode in [0,1]:assert compare['table'][f'independent_stress_b64_m{mode}']['converged']==75
 assert len(load('revisions/run_attempt_01/ALL_NONCONVERGED.json'))==402 and len(load('ALL_NONCONVERGED.json'))==392
 assert 'checks=531 failures=0' in (HERE/'unit_run_01.log').read_text() and 'pass=1' in (HERE/'cpp_run_01.log').read_text()
 for name in ['freeze_01.log','python_proof_01.log','build_01.log','runs_01.log','analysis_01.log','diagnose_build_01.log','diagnose_run_01.log','build_02.log','runs_02.log','analysis_02.log','unit_build_01.log','unit_run_01.log','cpp_c_build_01.log','cpp_link_01.log','cpp_run_01.log','arm_prepare_01.log','object_inspection_01.log']:assert 'exit_code=0' in (HERE/name).read_text(encoding='utf-8-sig'),name
 names=list(ROOT);revision_files={'python_attempt_01':['python_proof.py','NUMERICAL_BUDGET.json'],'build_attempt_01':['active_box_qp.h','active_box_qp.c','active_driver.c','NUMERICAL_BUDGET.json'],'run_attempt_01':['analyse_active.py','COMPARISON.json','ALL_NONCONVERGED.json','RUN_COMPARISON.csv'],'build_attempt_02':['active_box_qp.h','active_box_qp.c','active_driver.c','NUMERICAL_BUDGET.json','analyse_active.py'],'unit_attempt_01':['active_box_qp.h','active_box_qp.c','active_selftest.c'],'cpp_attempt_01':['active_box_qp.h','active_box_qp.c','active_cpp_smoke.cpp'],'arm_attempt_01':['active_box_qp.h','active_box_qp.c','arm_active.ps1']}
 for folder,files in revision_files.items():names.extend('revisions/'+folder+'/'+n for n in files)
 receipt=load('BUILD_RECEIPT.json');assert len(receipt['objects'])==2
 for r in receipt['sources']:assert sha(Path(r['path']))==r['sha256']
 for event in receipt['commands']:
  assert event['exit_code']==0;names.append(Path(event['log']).relative_to(HERE).as_posix())
  if event['phase']=='object_compile_only':assert '-c' in event['arguments'] and '-mfloat-abi=hard' in event['arguments'] and not any('sse' in a.lower() for a in event['arguments'])
 for r in receipt['objects']:
  p=Path(r['object']);assert r['compile_exit']==0 and p.stat().st_size==r['bytes'] and sha(p)==r['sha256'];names.append(p.relative_to(HERE).as_posix())
 records=[]
 for n in sorted(set(names)):
  p=HERE/n;assert p.is_file(),n;r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p),'role':'preserved_attempt' if n.startswith('revisions/') else 'source_inputs_evidence_or_build_not_firmware'}
  if p.suffix not in ['.exe','.o']:
   count=len(p.read_text(encoding='utf-8-sig').splitlines());r['lines']=count
   if count:r['citation']=f'{n}#L1-L{count}'
  records.append(r)
 validation={'files_indexed':len(records),'old_files_unchanged':len(freeze['old_files']),'real_MPC_references_unchanged':len(freeze['real_MPC_references']),'C_fixture_inputs_exact_f32':93,'Python_proof_runs':186,'attempt01':{'runs':1302,'nonconverged':402,'real_cold64':18,'real_warm64':14,'real_warm256':16},'attempt02':{'runs':1302,'nonconverged':392,'real_cold64':18,'real_warm64':18,'active_cold64':8,'active_warm64':8,'active_max_pivots_cold':25,'active_max_pivots_warm':54,'independent_cold64':75,'independent_warm64':75,'certificate_or_actual_accuracy_failures':0},'unit_checks':531,'unit_failures':0,'cpp_pass':True,'new_ARM_compile_only_objects':2,'ARM_execution':0,'new_physics_steps':0,'host_timing_benchmark_added':False,'algorithm_budget_changed':False,'complete_robot_MPC_or_3ms_qualified':False,'archive':'postR16/PH3_pending_no_PH2_expansion'}
 index={'name':'ACTIVE_BOX_QP_V3','status':'SEALED_NUMERICAL_ACTIVE_SET_NOT_DEPLOYED_MPC','files':records,'validation':validation,'objective':'.5*z^T H z + f^T z subject to finite box; n<=16','method':'feasible primal active-set, full/free SPD factors, first-bound blocking, sign release, same global pivot and clock state, no restart/regularization/free-only fallback','acceptance':'conservative f32 projected-KKT upper <= unchanged absolute .002; no widening by roundoff allowance','failure_output':'all nonCONVERGED valid0/n,z,cost,KKT0; private workspace iterate diagnostic only','clock':'caller monotonic uint64/context relative START budget, internal phase polls + exit; excludes setup before first START sample and is not preemption/WCET','host_build':{'compiler':r'C:\MinGW\bin\gcc.exe','flags':['-std=c99','-O2','-Wall','-Wextra','-Werror','-pedantic','-Wvla','-fno-fast-math','-ffp-contract=off','-msse2','-mfpmath=sse'],'core':'active_box_qp.c','driver':'active_driver.c','unit':'active_selftest.c','library':'-lm'},'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST/index stdout omitted to avoid self recursion'}
 dump('INDEX.json',index);dump('VALIDATION.json',validation);dump('MANIFEST.json',{})
 links=0
 for n in ['README.md','ERROR_REPORT.md','ALGORITHM_REVISION_02.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   file,_,fragment=target.partition('#');p=(HERE/file).resolve();assert p.is_file(),target
   if fragment:
    match=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment)
    if match:assert 1<=int(match[1])<=int(match[2] or match[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 validation['markdown_links_checked']=links;dump('VALIDATION.json',validation)
 primary=['active_box_qp.h','active_box_qp.c','NUMERICAL_BUDGET.json','SOURCE_FREEZE.json','README.md','ALGORITHM_REVISION_02.md','COMPARISON.json','EARLY_ABORT_CASES_01.csv','OBJECT_SUMMARY.json','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in primary]})
 print(json.dumps(validation))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
