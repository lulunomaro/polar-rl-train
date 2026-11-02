"""Seal software adapter, with every V3/old dependency read-only checked."""
from pathlib import Path
import json,hashlib,re,traceback
HERE=Path(__file__).resolve().parent
ROOT=['SCOPE.md','prepare_io.py','DEPENDENCY_FREEZE.json','io_protocol.h','PROTOCOL_SCHEMA.json','DEFAULT_INIT_P25.json','prepare_01.log','p25_host_adapter.c','p25_host_adapter.exe','build_01.log','p25_stdio.py','TEST_CRITERIA.json','selftest_io.py','ROUNDTRIP_01.jsonl','SELFTEST_RESULTS.json','selftest_01.log','PROTOCOL.md','README.md','gcc_version_01.log','gcc_target_01.log','capture_build.py','BUILD_RECEIPT.json','build_capture_01.log','ERROR_REPORT.md','index_io.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((HERE/n).read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 dependency=load('DEPENDENCY_FREEZE.json')
 for r in dependency['read_only_files']:
  p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],r['path']
 result=load('SELFTEST_RESULTS.json');criteria=load('TEST_CRITERIA.json');receipt=load('BUILD_RECEIPT.json');schema=load('PROTOCOL_SCHEMA.json')
 assert result['checks']==41632 and result['failures']==0 and result['fixture_rows_roundtripped']==3200
 assert result['math_state_float32_bit_mismatches']==0 and result['math_tau_float32_bit_mismatches']==0
 assert result['max_guarded_vs_original_DC64_Nm']<=criteria['guarded_torque_vs_independent_original_signed_DC_double_abs_Nm']
 assert {x['case'] for x in result['negative_cases']}==set(criteria['required_negative_cases']) and all(x['all_payload_zero'] for x in result['negative_cases'])
 assert result['large_uint64_exact'] and result['python_pointer_bits']==64 and result['executable_machine']=='0x14c' and result['executable_optional_magic']=='0x10b'
 assert not result['ctypes_used'] and not result['network_or_CAN'] and result['new_physics_steps']==0 and not result['hardware_binding']
 assert sha(Path(receipt['executable']['path']))==receipt['executable']['sha256']
 for r in receipt['read_only_sources_and_protocol']:
  p=Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256']
 for n in ['prepare_01.log','build_01.log','selftest_01.log','gcc_version_01.log','gcc_target_01.log','build_capture_01.log']:assert 'exit_code=0' in (HERE/n).read_text(encoding='utf-8-sig'),n
 assert len(schema['INIT_fields'])==51 and len(schema['STEP_fields'])==51 and len(schema['REPLY_fields'])==71
 names=list(ROOT)+[f'case_{i}_stderr_01.log' for i in range(9)]
 names +=[n+'_stderr_01.log' for n in ['bad_wire_sequence','reinitialization','step_before_init','invalid_mean','unknown_operation','wrong_field_count','nonfinite_token','logical_clock_rollback','large_u64','truncated_EOF']]
 names+=['revisions/build_attempt_01/p25_host_adapter.c','revisions/build_attempt_01/io_protocol.h','revisions/selftest_attempt_01/p25_stdio.py','revisions/selftest_attempt_01/selftest_io.py','revisions/selftest_attempt_01/TEST_CRITERIA.json']
 records=[]
 for n in sorted(set(names)):
  p=HERE/n;assert p.is_file(),n;r={'path':n,'bytes':p.stat().st_size,'sha256':sha(p),'role':'local_host_executable_not_firmware' if p.suffix=='.exe' else ('preserved_attempt' if n.startswith('revisions/') else 'source_protocol_test_or_log')}
  if p.suffix!='.exe':
   lines=len(p.read_text(encoding='utf-8-sig').splitlines());r['line_count']=lines
   if lines:r['citation']=f'{n}#L1-L{lines}'
  records.append(r)
 index={'name':'HOST_CLOSED_LOOP_IO_V1','status':'SEALED_LOCAL_RESIDENT_P25_STDIO_ADAPTER_SOFTWARE_ONLY','archive_scope':'postR16_PH3_pending; does not enlarge PH2 cutoff',
        'files':records,'dependency_files_verified_unchanged':len(dependency['read_only_files']),'executable':receipt['executable'],
        'protocol':{'magic':'PC3IO','version':1,'request':'ASCII one line + field count + wireseq','INIT':51,'STEP':51,'REPLY':71,'profile':'P25 only','fault':'zero entire payload + latch until new process','clock':'explicit external logical simulation before/after, not CPU elapsed'},
        'validation':result,'output_semantics':'MATH_TAU pre-pointDC; GUARDED_TAU finalpointDC; two distinct parent driver-chain cohorts, never silently interchangeable',
        'no_physics_or_network_or_CAN_or_BSP_or_ARM_execution':True,'V3_changed':False,'PH3_physics_pending_in_parent':True,'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST/index stdout excluded'}
 dump('INDEX.json',index)
 validation={'files_indexed':len(records),'dependencies_unchanged':len(dependency['read_only_files']),'software_checks':41632,'failures':0,'roundtrip_rows':3200,'math_state_bit_mismatches':0,'math_tau_bit_mismatches':0,'negative_cases':9,'truncated_EOF_exit':2,'large_u64_exact':True,'Python_pointer_bits':64,'host_PE32':True,'V3_changed':False,'new_physics_steps':0,'hardware_binding':False,'PH3':'pending'}
 dump('VALIDATION.json',validation);dump('MANIFEST.json',{});links=0
 for n in ['README.md','PROTOCOL.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   fn,_,fragment=target.partition('#');p=(HERE/fn).resolve();assert p.is_file(),target
   if fragment:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',fragment)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 validation['markdown_links_checked']=links;dump('VALIDATION.json',validation)
 primary=['p25_host_adapter.exe','p25_host_adapter.c','p25_stdio.py','PROTOCOL_SCHEMA.json','DEFAULT_INIT_P25.json','PROTOCOL.md','README.md','BUILD_RECEIPT.json','SELFTEST_RESULTS.json','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in primary]})
 print(json.dumps(validation))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
