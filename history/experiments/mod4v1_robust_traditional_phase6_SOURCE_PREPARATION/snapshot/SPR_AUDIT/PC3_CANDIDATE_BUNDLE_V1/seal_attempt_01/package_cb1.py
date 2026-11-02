"""Final small-scope packaging from saved facts; no executable/compiler/test run.
Argument: host-glob full file list for THIS new directory only. No tree traversal.
"""
from pathlib import Path
import hashlib,json,re,sys,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,v):
 with (HERE/name).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 for n in ('RECEIPT.json','VALIDATION.json','INDEX.json','cb1_source_bundle.zip'):assert not (HERE/n).exists(),n
 ref=json.loads((HERE/'SOURCE_REFERENCES.json').read_bytes());changed=[]
 # ONE final check of 17 explicitly selected references, not an old tree scan.
 for r in ref['references']:
  if sha(ROOT/r['path'])!=r['sha256']:changed.append(r['path'])
 assert not changed
 for n,h in ref['pre_core_contracts'].items():assert sha(HERE/n)==h
 comp=json.loads((HERE/'COMPARISON.json').read_bytes());objects=json.loads((HERE/'OBJECT_FACTS.json').read_bytes())
 h1=json.loads((HERE/'HOST_BUILD_01.json').read_bytes());h2=json.loads((HERE/'HOST_BUILD_02.json').read_bytes());arm=json.loads((HERE/'ARM_BUILD_01.json').read_bytes())
 assert comp['rows']==3200 and not comp['bit_or_discrete_errors']and comp['native_attempt02']['failures']==0 and comp['CPP_actual_pass']and h2['success']and arm['success']
 for n in ('cb1_candidate.c','cb1_candidate.h'):
  assert sha(HERE/n)==h1['sources'][n]==h2['sources'][n]==arm['sources'][n]
 for host in (h1,h2):
  for c in host['commands']:
   if 'artifact'in c:assert Path(c['artifact']).is_file()and sha(Path(c['artifact']))==c['sha256']
 for r in objects['objects']:assert sha(Path(r['object']))==r['sha256']
 runtime=['SPR_AUDIT/PC3_CANDIDATE_BUNDLE_V1/'+n for n in ('cb1_candidate.c','cb1_candidate.h','BUILD.txt')]+['SPR_AUDIT/portable_control_v3_current/'+n for n in ('pc3_control.h','pc3_estimator.c','pc3_controller.c','pc3_p25_data.h')]+['SPR_AUDIT/portable_core_v2_kinematics/'+n for n in ('ct_kinematics.c','ct_kinematics.h')]
 deps={r['path']:r['sha256']for r in ref['references']}
 zipname='cb1_source_bundle.zip';zip_path=HERE/zipname
 with zipfile.ZipFile(zip_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n in runtime:
   b=(ROOT/n).read_bytes()
   if n in deps:assert hashlib.sha256(b).hexdigest()==deps[n]
   info=zipfile.ZipInfo(n,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
 with zipfile.ZipFile(zip_path)as z:
  assert sorted(z.namelist())==sorted(runtime)
  for n in runtime:assert z.read(n)==(ROOT/n).read_bytes()
 # Root-current docs only. Planned metadata targets are created below, no archive relinking.
 planned={HERE/n for n in ('RECEIPT.json','VALIDATION.json','INDEX.json')};links=0
 for n in ('README.md','ERROR_REPORT.md','ARCHITECTURE.md'):
  for target in re.findall(r'\[[^\]]*\]\(<([^>]+)>\)',(HERE/n).read_text()):
   name,_,frag=target.partition('#');p=(HERE/name).resolve();assert p in planned or p.is_file(),(n,target)
   if frag:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',frag);assert m and 1<=int(m[1])<=int(m[2]or m[1])<=len(p.read_bytes().splitlines())
   links+=1
 status='SEALED_NEW_NO_SEND_CANDIDATE_MATH_HOST_CPP_AND_SEPARATE_ARM_OBJECTS'
 receipt=dict(status=status,core={n:sha(HERE/n)for n in ('cb1_candidate.c','cb1_candidate.h')},source_zip=dict(path=zipname,sha256=sha(zip_path),bytes=zip_path.stat().st_size,entries=runtime,old_runtime_dependencies_byte_unchanged=6),selected_old_references_checked=len(ref['references']),changed_old_references=changed,global_old_tree_rehash=False,budget_sha256=sha(HERE/'NUMERICAL_BUDGET.json'),rows=3200,accepted_host_checks=270412,strict_float_bit_mismatches=0,internal_effective_distinct_rows=238,native_first_failure_preserved=dict(checks=1583,failures=1),native_accepted=dict(checks=1583,failures=0),CPP_actual_pass=True,clock_insertions=25,cases_rerun_after_pass=0,core_recompiled_after_first_host=False,new_ARM_objects=len(objects['objects']),ARM_link_or_execution=False,hardware_BSP_WCET_bound=False,send_permission='ALWAYS_FALSE_ON_USABLE_OUTPUTS',aliases='overlapping output is UNUSABLE, not a published candidate',default='UNBOUND_REQUIRE_INIT_AND_DECLARED_MATH_ARM',publication_stage='EXCLUDED_CURRENT_PH5_CUTOFF__PH6_PENDING',old_SDK_or_worker_runs=0,physics=0,GPU=False,Git=False,new_agents=False,parent_goal_changed=False,links_verified=links)
 write('RECEIPT.json',receipt)
 write('VALIDATION.json',dict(validated=True,status=status,new_math_candidate_service_only=True,candidate_math_valid_is_not_send_permission=True,complete_C3_dispatch_or_final_enqueue_qualified=False,FSM_MPC_Power_integration=False,hardware_calibration_BSP_runtime_WCET_qualified=False,source_references_unchanged=not changed,reference_count=len(ref['references']),budget_unchanged=True,all_attempts_preserved=True,first_native_attempt_is_still_failed=True,cases_pass_reused_not_rerun=True,publication_stage=receipt['publication_stage']))
 # Input is the host glob result, NOT os.walk/rglob and never an old workspace scan.
 text=Path(sys.argv[1]).read_text(encoding='utf-8-sig');items=[]
 try:
  data=json.loads(text);items=data if isinstance(data,list)else data['files']
 except (json.JSONDecodeError,KeyError,TypeError):items=[s.strip()for s in text.splitlines()if s.strip()]
 paths=set()
 for raw in items:
  p=Path(raw);p=p if p.is_absolute()else ROOT/p;p=p.resolve()
  assert p.is_relative_to(HERE)and p.is_file(),str(p)
  paths.add(p)
 for n in ('package_cb1.py',zipname,'RECEIPT.json','VALIDATION.json'):paths.add(HERE/n)
 paths.discard(HERE/'INDEX.json');assert len(paths)>=90
 index=dict(status=status,scope='new CB1 files only; INDEX excludes itself',count=len(paths),entries=[dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)])
 write('INDEX.json',index)
 print(json.dumps(dict(status=status,new_index_files=len(paths),source_zip_bytes=zip_path.stat().st_size,selected_old_files_unchanged=len(ref['references']),readme_sha256=sha(HERE/'README.md'),index_sha256=sha(HERE/'INDEX.json'),receipt_sha256=sha(HERE/'RECEIPT.json'),source_zip_sha256=sha(zip_path),no_tests_or_compilers_executed=True),indent=2))
if __name__=='__main__':main()
