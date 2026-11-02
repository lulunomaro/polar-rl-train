"""Final saved-evidence metadata/source ZIP only. No tree scan or binary run."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_bytes())
def write(n,obj):
 with(HERE/n).open('x',encoding='utf-8')as f:json.dump(obj,f,indent=2,allow_nan=False)
def main():
 for n in('INDEX.json','RECEIPT.json','VALIDATION.json','control_cores_source_bundle.zip'):assert not(HERE/n).exists(),n
 bom=load('SOURCE_BOM.json');audit=load('COMBINATION_AUDIT.json');host=load('HOST_BUILD.json');arm=load('ARM_BUILD.json')
 assert audit['status']=='PASS_BUILD_COHABITATION_DEFAULT_ONLY_NOT_SEND_CHAIN'and host['success']and arm['success']
 # Narrow FINAL old SHA check: exactly22 actual runtime/header files, no old tree.
 changed=[r['path']for r in bom['files']if sha(ROOT/r['path'])!=r['sha256']];assert len(bom['files'])==22 and not changed
 assert sha(HERE/'ARCHITECTURE.md')==bom['prebuild']['ARCHITECTURE']and sha(HERE/'BUDGET.json')==bom['prebuild']['BUDGET']
 for b in(host,arm):
  for n,h in b['new_inputs'].items():assert sha(HERE/n)==h,n
  for c in b['commands']:
   if'artifact'in c:assert c['exit_code']==0 and sha(HERE/c['artifact'])==c['sha256']
 # Reverse only the documented exact classifier alias edit; no runtime edits.
 s=(HERE/'audit_co1.py').read_text(encoding='utf-8')
 old=s.replace('# Installed ARM math.h:740-741 declares _fabsf (old ARM name), fabsf calls it.\n','').replace("MATH={'_fabsf','acos'","MATH={'acos'")
 assert old.encode('utf-8')==(HERE/'audit_attempt_01/audit_co1.py').read_bytes()
 newfiles=['co1_abi.h','co1_abi_probe.c','co1_smoke_body.h','co1_smoke_c.c','co1_smoke_cpp.cpp','build_co1.py','prepare_co1.py','audit_co1.py','SOURCE_BOM.json','BUDGET.json','ARCHITECTURE.md','BUILD.txt','armlink_help.log','TOOLCHAIN_ALIAS_EVIDENCE.json']
 entries=[r['path']for r in bom['files']]+['SPR_AUDIT/CONTROL_CORES_LINK_V1/'+n for n in newfiles];assert len(entries)==len(set(entries))==36
 zpath=HERE/'control_cores_source_bundle.zip'
 with zipfile.ZipFile(zpath,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n in entries:
   info=zipfile.ZipInfo(n,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,(ROOT/n).read_bytes())
 with zipfile.ZipFile(zpath)as z:
  assert sorted(z.namelist())==sorted(entries)
  for n in entries:assert z.read(n)==(ROOT/n).read_bytes()
 planned={HERE/n for n in('INDEX.json','RECEIPT.json','VALIDATION.json')};links=0
 for name in('README.md','ERROR_REPORT.md','ARCHITECTURE.md'):
  for target in re.findall(r'\[[^\]]*\]\(<([^>]+)>\)',(HERE/name).read_text(encoding='utf-8')):
   fn,_,anchor=target.partition('#');p=Path(fn);p=(p if p.is_absolute()else HERE/p).resolve();assert p.is_file()or p in planned,(name,target)
   if anchor:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',anchor);assert m and 1<=int(m[1])<=int(m[2]or m[1])<=len(p.read_bytes().splitlines())
   links+=1
 status='SEALED_BUILD_COMBINATION_DEFAULT_ONLY_C_CPP_AND_ARM_PARTIAL_NOT_SEND_CHAIN'
 targets=[dict(cpu=t['cpu'],**{k:t['partial'][k]for k in('path','bytes','sha256','format')},remaining_system_undefined=len(t['partial']['undefined']),unexpected=0,firmware_executable=False)for t in audit['ARM']]
 receipt=dict(status=status,BOM_sha256=sha(HERE/'SOURCE_BOM.json'),runtime_translation_units=9,old_source_header_count=22,old_sources_unchanged=not changed,old_tree_rehash=False,per_runtime_compiles_per_platform=1,host_build_commands=len(host['commands']),ARM_build_commands=len(arm['commands']),host_default_smokes={k:dict(checks=v['checks'],failures=v['failures'])for k,v in audit['host']['smokes'].items()},host_executables=audit['host']['executables'],host_runtime_strong_symbols=45,duplicate_strong_symbols=0,unexpected_dependencies=0,dispatch_send_dependencies=0,CPP_matches_C_layout_fields=29,ARM_partial=targets,ARM_partial_attempts_per_target=1,ARM_system_libraries_BSP_linked=False,host_CRT_libm_linked=True,actual_ARM_execution=False,hardware_stack_ISR_FPSCR_WCET_qualified=False,audit_attempt01='FAILED_CLASSIFIER_MISSING_VERIFIED_OLD_ARM_FABSF_ALIAS__PRESERVED',audit_attempt02='SAVED_EVIDENCE_ONLY_PASS__NO_BUILD_OR_SMOKE_RERUN',source_zip=dict(path=zpath.name,bytes=zpath.stat().st_size,sha256=sha(zpath),entries=len(entries),runtime_C_entries=9,old_source_entries=22,new_build_smoke_entries=len(newfiles)),default_only_no_valid_control_transaction=True,full_send_chain_qualified=False,old_QA_runs=0,physics=0,GPU=False,Git=False,new_agents=False,blockedIO=False,parent_goal_changed=False,publication='PH6_PENDING',live_MD_links=links)
 write('RECEIPT.json',receipt)
 write('VALIDATION.json',dict(validated=True,status=status,source_BOM_unchanged=True,source_scope22_only=True,budget_unchanged=True,all_runtime_sources_compiled_once_per_platform=True,actual_C_and_CPP_new_smokes_only=True,ARM_two_actual_relocatable_partials=True,duplicate_strong_or_unexpected_or_send_dependencies=0,system_RT_libm_remain_unresolved=True,default_unbound_inhibit_behavior_preserved=True,new_control_transaction_implemented=False,hardware_or_final_enqueue_or_WCET_qualified=False,old_tests_or_physics_executed=False,publication='PH6_PENDING'))
 paths=set()
 for line in Path(sys.argv[1]).read_text(encoding='utf-8-sig').splitlines():
  if not line.strip():continue
  p=Path(line.strip());p=(p if p.is_absolute()else ROOT/p).resolve();assert p.is_relative_to(HERE)and p.is_file();paths.add(p)
 for n in('RECEIPT.json','VALIDATION.json',zpath.name):paths.add(HERE/n)
 paths.discard(HERE/'INDEX.json');assert len(paths)>100
 write('INDEX.json',dict(status=status,scope='new component files only; excludes INDEX itself',count=len(paths),entries=[dict(path=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]))
 print(json.dumps(dict(status=status,index_files=len(paths),live_MD_links=links,old_22_unchanged=True,source_zip_bytes=zpath.stat().st_size,source_zip_entries=36,README_sha256=sha(HERE/'README.md'),INDEX_sha256=sha(HERE/'INDEX.json'),RECEIPT_sha256=sha(HERE/'RECEIPT.json'),ZIP_sha256=sha(zpath),no_binary_compiler_linker_runs=True),indent=2))
if __name__=='__main__':main()
