"""Archive hashes and existing-output validation; no solver or physical replay."""
from pathlib import Path
import json,re,hashlib,traceback
HERE=Path(__file__).resolve().parent
NAMES=['SCOPE.md','host_cwd_denial_01.txt','environment_probe_02.log','environment_probe_03.log','build_condensed.py','HESSIAN_BASELINE.json','hessian_build_01.log',
 'make_fixtures.py','actual_model_vectors.json','actual_fixtures.h','provenance.json','fixture_generation_01.log',
 'actual_hessian_driver.c','actual_hessian_host.exe','build_attempt_01.log','C_RUNS_01.jsonl','sweep_checkpoints_01.csv','selftest_attempt_01.log',
 'revisions/compare_results_attempt_01.py','comparison_error_01.txt','comparison_attempt_01.log','compare_results.py','COMPARISON.json',
 'BUDGET_SUMMARY.csv','RUN_COMPARISON.csv','comparison_attempt_02.log','README.md','ERROR_REPORT.md','index_numeric.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 provenance=load(HERE/'provenance.json')
 for key in ['source','model','generator']:
  item=provenance[key];p=Path(item['path']);assert sha(p)==item['sha256']
 assert provenance['max_oracle_quantized_KKT']<1e-8 and not provenance['parent_imported'] and not provenance['mujoco_loaded']
 comparison=load(HERE/'COMPARISON.json');assert len(comparison['runs'])==144
 assert sum(r['converged'] for r in comparison['runs'])==89
 assert sum(not r['converged'] for r in comparison['runs'])==55
 for r in comparison['runs']:
  assert r['feasible'] and r['has_candidate']
  assert r['status_name']==('CONVERGED' if r['converged'] else 'MAX_SWEEPS')
 for n in ['build_attempt_01.log','selftest_attempt_01.log']:assert 'exit_code=0' in (HERE/n).read_text(encoding='utf-8-sig')
 assert 'failures=0' in (HERE/'selftest_attempt_01.log').read_text(encoding='utf-8-sig')
 old=[]
 for p,key in [(HERE.parent/'deliverable_manifest.json','files'),(HERE.parent/'portable_core_v1/MANIFEST.json','deliverables'),
               (HERE.parent/'portable_core_v2_kinematics/MANIFEST.json','deliverables'),(HERE.parent/'portable_mpc_qp_v1/MANIFEST.json','deliverables'),
               (HERE.parent/'ODOM2D_DIAGNOSTIC/MANIFEST.json','deliverables')]:
  for item in load(p)[key]:
   target=p.parent/item['path'];assert target.stat().st_size==item['bytes'] and sha(target)==item['sha256'];old.append(str(target))
 files=[]
 for n in NAMES:
  p=HERE/n;assert p.is_file();r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p)}
  if p.suffix!='.exe':
   count=len(p.read_text(encoding='utf-8-sig').splitlines());r['line_count']=count;r['citation']=f'{n}#L1-L{count}'
  files.append(r)
 index={'name':'C_MPC8_NUMERIC_V1','status':'SEALED_ACTUAL_H_NUMERICAL_QUALIFICATION_WITH_HONEST_BUDGET_FAILURES','files':files,
  'write_scope':str(HERE),'source_provenance':provenance,'old_primary_hashes_unchanged':old,
  'kernel_source':{'path':str(HERE.parent/'portable_mpc_qp_v1/boxqp.c'),'sha256':sha(HERE.parent/'portable_mpc_qp_v1/boxqp.c'),'modified':False},
  'runs':{'total':144,'converged':89,'honest_MAX_SWEEPS':55,'driver_contract_checks':541983,'driver_contract_failures':0},
  'fairness':'C pure CCD vs independent double oracle; parent Python free shortcut is absent in C1. Synthetic prior-oracle warm is not closed-loop data.',
  'preserved_issues':['missing cwd blocked before command','bundled runtime missing SciPy, reused existing Python314 instead','NumPy float32 report serialization fixed with original source/log retained','one unique warm KKT threshold roundoff boundary in two extended-budget runs'],
  'scope':'numpy/scipy/stdlib matrix algebra + host GCC only, no parent import/physics/MjData/step/board/ARM deadline/Git',
  'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST/index stdout log excluded from own file hashes'}
 dump('INDEX.json',index)
 validation={'old_primary_files_unchanged':len(old),'files_indexed':len(files),'original_parent_source_and_model_hashes_match':True,
             'C_runs':144,'C_feasible_runs':144,'C_converged_runs':89,'C_budget_failure_runs':55,'driver_assertion_failures':0,'physics_steps':0}
 dump('VALIDATION.json',validation);dump('MANIFEST.json',{});links=0
 for n in ['README.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   filename,_,frag=target.partition('#');p=(HERE/filename).resolve();assert p.is_file(),target
   if frag:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',frag)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 validation['markdown_links_checked']=links;dump('VALIDATION.json',validation)
 names=['README.md','COMPARISON.json','BUDGET_SUMMARY.csv','provenance.json','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in names]})
 print(json.dumps(validation,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
