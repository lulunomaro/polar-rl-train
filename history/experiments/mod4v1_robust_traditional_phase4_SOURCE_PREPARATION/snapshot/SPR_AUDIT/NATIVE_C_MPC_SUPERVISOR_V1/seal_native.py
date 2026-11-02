"""Final read-only revalidation of saved facts; no tests/compiler/physics rerun."""
from pathlib import Path
import json,hashlib,re,traceback,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
META=['INDEX.json','VALIDATION.json','MANIFEST.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(p):return dict(path=str(p.resolve()),relative=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 for n in META:
  if(HERE/n).exists():
   assert json.loads((HERE/n).read_text())['status']=='PENDING_FINAL_LINK_CHECK_NOT_A_SEAL','No completed seal overwrite'
   assert sha(HERE/n)==sha(HERE/'revisions/seal_attempt_01'/n),'Previous provisional metadata must be preserved byte-for-byte'
 fr=json.loads((HERE/'SOURCE_FREEZE.json').read_text())
 for r in fr['old_files']+fr['sources']:assert Path(r['path']).is_file()and sha(Path(r['path']))==r['sha256'],r['path']
 host=json.loads((HERE/'HOST_BUILD_01.json').read_text());assert host['success']and len(host['commands'])==7
 for n in ['nm1_supervisor.c','nm1_supervisor.h','nm1_model.c','nm1_model.h','nm1_host_tests.c','nm1_fixtures.h','nm1_cpp_smoke.cpp','NUMERICAL_BUDGET.json','build_native_host.py']:
  assert sha(HERE/n)==host['sources'][n]and sha(HERE/n)==sha(HERE/'revisions/host_attempt_01'/n)
 for r in host['commands']:assert r['exit_code']==0 and r['artifact_exists']and Path(r['artifact']).is_file()and sha(Path(r['artifact']))==r['sha256']
 run=json.loads((HERE/'HOST_RUN_01.json').read_text());assert len(run)==2 and all(r['exit_code']==0 and sha(Path(r['executable']))==r['sha256']for r in run)
 arm=json.loads((HERE/'ARM_BUILD_01.json').read_text());assert arm['success']and len(arm['objects'])==4
 for r in arm['objects']:assert sha(Path(r['source']))==r['source_sha256']and sha(Path(r['object']))==r['sha256']
 for n in ['nm1_supervisor.c','nm1_supervisor.h','nm1_model.c','nm1_model.h']:assert sha(HERE/n)==sha(HERE/'revisions/arm_attempt_01'/n)
 comp=json.loads((HERE/'COMPARISON.json').read_text());assert comp['error_count']==0 and comp['rows']==3717 and not comp['f_bit_different_rows']and comp['native_contract']['failures']==0 and sha(HERE/'NUMERICAL_BUDGET.json')==comp['budget_sha'];assert comp['maximum_errors']['tau']==comp['maximum_errors']['warm']==comp['maximum_errors']['last_u']==0
 data=json.loads((HERE/'COMPILED_DATA_PROOF.json').read_text());assert data['ARM_compiled_model_H_and_all_maps_bits_equal']
 non=json.loads((HERE/'ALL_NONCONVERGED.json').read_text());assert non['count']==334 and non['all_z_outputs_zero']and all(not r['accepted']and not r['qvalid']for r in non['records'])
 closure=json.loads((HERE/'SOURCE_CLOSURE.json').read_text());assert sha(Path(closure['bundle']['path']))==closure['bundle']['sha256']
 with zipfile.ZipFile(HERE/'nm1_source_bundle.zip')as z:
  for r in closure['entries']:assert z.read(r['archive_path'])==Path(r['path']).read_bytes()and sha(Path(r['path']))==r['sha256']
 paths=[]
 for line in(HERE/'DISCOVERED_FILES_02.txt').read_text().splitlines():
  p=Path(line.strip());p=p if p.is_absolute()else (ROOT/p if p.parts[0]=='SPR_AUDIT'else HERE/p)
  assert p.is_file()and p.is_relative_to(HERE),str(p)
  if p.parent==HERE and p.name in META+['seal_01.log','seal_02.log']:continue
  paths.append(p)
 paths+= [HERE/'DISCOVERED_FILES_02.txt'];paths=sorted(set(paths));assert HERE/'seal_native.py'in paths
 for n in META:dump(n,dict(status='PENDING_FINAL_LINK_CHECK_NOT_A_SEAL'))
 links=[]
 for p in paths:
  # Archived snapshots preserve original bytes/relative paths, not live docs.
  if p.suffix=='.md'and p.parent==HERE:
   for dest in re.findall(r'\[[^\]]*\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
    if dest.startswith(('https://','http://')):continue
    target=(p.parent/dest.split('#')[0]).resolve();assert target.is_file(),str(p)+' -> '+dest;links.append(dict(source=p.name,target=str(target)))
 val=dict(status='SEALED_NEW_NATIVE_INPROCESS_CORE_HOST_CPP_AND_SEPARATE_ARM_OBJECTS_NOT_HARDWARE',old_files_unchanged=len(fr['old_files']),source_references_verified=len(fr['sources']),rows=3717,total_native_host_checks=84531,failures=0,raw_H15_cold_warm=36,all_original_parent_problem_bits_equal_in_cohort=True,max_torque_warm_last_u_error=0.,max_caller_KKT_error=comp['maximum_errors']['caller_KKT'],accepted=1510,ordinary_nonconverged_fallback=334,all_nonconverged_preserved=True,CPP_link_run=True,new_ARM_objects=4,ARM_execution=0,soft_double_libm_BSP_linked=False,clock_insertions=45,complete_cycle_driver_or_WCET_qualified=False,ground_flight_permission_inferred_from_pitch=False,caller_must_disable_jump_flight_non_normal_unbound_contact=True,COM_FSM_caps_raised=False,R39_GT_read=False,blocked_IO_repaired=False,new_physics_steps=0,GPU_Git_newagents_parentgoal_changes=0,all_attempts_preserved=True,markdown_links_checked=len(links),files_indexed=len(paths))
 dump('INDEX.json',dict(name='NATIVE_C_MPC_SUPERVISOR_V1',status=val['status'],validation=val,files=[row(p)for p in paths],metadata_excluded_from_self_hash=META+['seal_01.log','seal_02.log'],links=links));dump('VALIDATION.json',val)
 primary=['README.md','SEMANTIC_MAPPING.md','nm1_supervisor.c','nm1_supervisor.h','nm1_model.c','nm1_model.h','NUMERICAL_BUDGET.json','MODEL_EXPORT.json','COMPILED_DATA_PROOF.json','COMPARISON.json','CORE_RECEIPT.json','HOST_QUALIFICATION.json','OBJECT_SUMMARY.json','SOURCE_CLOSURE.json','nm1_source_bundle.zip']
 dump('MANIFEST.json',dict(status=val['status'],primary=[row(HERE/n)for n in primary],old_files_unchanged=len(fr['old_files']),scope='new in-process source+host proof; separate objects, no hardware/IO qualification'))
 print(json.dumps({**val,'README_sha256':sha(HERE/'README.md'),'INDEX_sha256':sha(HERE/'INDEX.json'),'bundle_sha256':sha(HERE/'nm1_source_bundle.zip'),'core_sha256':sha(HERE/'nm1_supervisor.c'),'header_sha256':sha(HERE/'nm1_supervisor.h')}))
if __name__=='__main__':
 try:main()
 except Exception:(HERE/'seal_error_02.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
