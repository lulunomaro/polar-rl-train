"""Seal the fast prototype with read-only cross-version and artifact checks."""
from pathlib import Path
import json,re,hashlib,traceback,csv
HERE=Path(__file__).resolve().parent
NAMES=['boxqp_fast.h','derive_fast_source.py','boxqp_fast.c','DERIVATION.json','source_derivation_01.log',
 'base_regression_host.exe','base_build_attempt_01.log','base_selftest_attempt_01.log','fast_selftest.c','fast_selftest_host.exe','fast_build_attempt_01.log','fast_selftest_attempt_01.log',
 'derive_actual_harness.py','compare_results.py','fast_actual_driver.c','ACTUAL_HARNESS_PROVENANCE.json','harness_derivation_01.log','fast_actual_host.exe','actual_build_attempt_01.log',
 'C_RUNS_01.jsonl','sweep_checkpoints_01.csv','actual_selftest_attempt_01.log','COMPARISON.json','BUDGET_SUMMARY.csv','RUN_COMPARISON.csv','comparison_attempt_01.log',
 'cross_version_check.py','CROSS_VERSION.json','cross_version_attempt_01.log','host_benchmark.c','fast_cpp_smoke.cpp','host_benchmark.exe','benchmark_build_01.log',
 'boxqp_fast_host.o','cpp_c_object_build_01.log','fast_cpp_smoke_host.exe','cpp_link_01.log','HOST_TIMING_01.csv','host_timing_attempt_01.log','cpp_smoke_01.log',
 'summarize_host.py','HOST_TIMING_SUMMARY.json','host_summary_01.log','README.md','ERROR_REPORT.md','index_fast.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 d=load(HERE/'DERIVATION.json');assert sha(Path(d['base']))==d['base_sha256'] and sha(Path(d['new']))==d['new_sha256']
 inputs=[]
 for item in load(HERE/'ACTUAL_HARNESS_PROVENANCE.json').values():
  if isinstance(item,dict):assert sha(Path(item['path']))==item['sha256'];inputs.append(item)
 for n in ['bqp_fixtures.h','bqp_selftest.c','boxqp.h']:
  p=HERE.parent/'portable_mpc_qp_v1'/n;record=next(x for x in load(HERE.parent/'portable_mpc_qp_v1/INDEX.json')['files'] if x['path']==n)
  assert sha(p)==record['sha256'];inputs.append({'path':str(p),'sha256':sha(p)})
 old=[]
 for p,key in [(HERE.parent/'deliverable_manifest.json','files'),(HERE.parent/'portable_core_v1/MANIFEST.json','deliverables'),
               (HERE.parent/'portable_core_v2_kinematics/MANIFEST.json','deliverables'),(HERE.parent/'portable_mpc_qp_v1/MANIFEST.json','deliverables'),
               (HERE.parent/'ODOM2D_DIAGNOSTIC/MANIFEST.json','deliverables'),(HERE.parent/'C_MPC8_NUMERIC_V1/MANIFEST.json','deliverables')]:
  for item in load(p)[key]:
   q=p.parent/item['path'];assert q.stat().st_size==item['bytes'] and sha(q)==item['sha256'];old.append(str(q))
 cross=load(HERE/'CROSS_VERSION.json');assert cross['all_80_free_runs_selected_zero_sweep']==80 and cross['all_64_active_runs_bit_equal_z_sweeps_cost_KKT_status_to_C1']==64
 results=load(HERE/'COMPARISON.json')['runs'];assert len(results)==144 and sum(r['converged'] for r in results)==123
 logs=['base_build_attempt_01.log','base_selftest_attempt_01.log','fast_build_attempt_01.log','fast_selftest_attempt_01.log',
       'actual_build_attempt_01.log','actual_selftest_attempt_01.log','benchmark_build_01.log','host_timing_attempt_01.log','cpp_c_object_build_01.log','cpp_link_01.log','cpp_smoke_01.log']
 for n in logs:assert 'exit_code=0' in (HERE/n).read_text(encoding='utf-8-sig')
 for n in ['base_selftest_attempt_01.log','fast_selftest_attempt_01.log','actual_selftest_attempt_01.log']:assert 'failures=0' in (HERE/n).read_text(encoding='utf-8-sig')
 assert 'pass=1' in (HERE/'cpp_smoke_01.log').read_text(encoding='utf-8-sig')
 files=[]
 for n in NAMES:
  p=HERE/n;assert p.is_file();r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p)}
  if p.suffix not in ('.exe','.o'):
   count=len(p.read_text(encoding='utf-8-sig').splitlines());r['line_count']=count;r['citation']=f'{n}#L1-L{count}'
  files.append(r)
 core=(HERE/'boxqp_fast.c').read_text(encoding='utf-8');assert not re.search(r'\b(malloc|calloc|realloc|free)\s*\(',core) and not re.search(r'\bdouble\b',core)
 index={'name':'portable_mpc_qp_v2_fast','status':'SEALED_OPTIONAL_FREE_SHORTCUT_WITH_UNCHANGED_ACTIVE_FALLBACK','write_scope':str(HERE),
  'files':files,'derivation':d,'shared_inputs_hash_checked':inputs,'old_primary_files_unchanged':old,
  'API':'old structs/base CCD ABI unchanged; new bqp_solve_fast(enable_free,optional_info); compile new core INSTEAD OF old, not both',
  'workspace_host_bytes':2448,'heap_or_VLA_or_shared_cache':False,
  'tests':{'base_original_fixtures_checks':4166,'enabled_checks':1110,'actual_H_driver_checks':196951,'assertion_failures':0,
           'actual_runs':144,'converged':123,'honest_active_MAX_SWEEPS':21,'free_zero_sweep_runs':80,'active_runs_bit_identical_to_C1':64,'cpp_fast_ABI_pass':True},
  'deadline':'check before/after free, every sweep and after callback; absolute sampled deadline, not preemption/WCET; final result authoritative',
  'host_timing':'QPC in separate host-only Windows file, cold numerical starts, callbacks off, repeated cache-warm calls; NOT ARM WCET',
  'unresolved':'64/256 active-bound budget failures remain unchanged; no state/power coupling or robot/BSP qualification',
  'scope_exclusions':['parent import/edits','old package edits','MjData/physics/step/HIL/board/CAN/SSH/Git','new package/agent'],
  'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST/index log excluded to avoid recursion'}
 dump('INDEX.json',index)
 val={'old_primary_files_unchanged':len(old),'files_indexed':len(files),'shared_input_hashes_checked':len(inputs),
      'all_base_and_enabled_assertion_failures':0,'actual_H_converged':123,'actual_H_honest_budget_failures':21,'free_zero_sweep_runs':80,
      'active_runs_bit_identical_to_C1':64,'new_physics_steps':0,'ARM_runtime_tested':False}
 dump('VALIDATION.json',val);dump('MANIFEST.json',{});links=0
 for n in ['README.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   fn,_,frag=target.partition('#');p=(HERE/fn).resolve();assert p.is_file(),target
   if frag:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',frag)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 val['markdown_links_checked']=links;dump('VALIDATION.json',val)
 primary=['boxqp_fast.h','boxqp_fast.c','README.md','CROSS_VERSION.json','BUDGET_SUMMARY.csv','HOST_TIMING_SUMMARY.json','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in primary]})
 print(json.dumps(val,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
