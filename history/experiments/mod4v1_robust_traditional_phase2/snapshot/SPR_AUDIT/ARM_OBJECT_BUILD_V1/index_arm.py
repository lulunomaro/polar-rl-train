"""Final read-only compile artifact/source/ABI/link validation, no execution."""
from pathlib import Path
import hashlib,json,re,traceback
HERE=Path(__file__).resolve().parent
STATIC=['SCOPE.md','target_probe.c','armclang_version_01.log','fromelf_help_01.log','arm_build.ps1','BUILD_RECEIPT.json',
        'arm_build_attempt_01.log','inspect_objects.py','OBJECT_SUMMARY.json','OBJECT_SUMMARY.csv','object_inspection_01.log','README.md','ERROR_REPORT.md','index_arm.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(n,v):(HERE/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 receipt=load(HERE/'BUILD_RECEIPT.json');summary=load(HERE/'OBJECT_SUMMARY.json');assert len(receipt['objects'])==6 and len(summary['objects'])==6
 assert receipt['no_armcc_or_link_or_bin_or_runtime_or_license_change']
 sources=[]
 for item in receipt['sources']:
  p=Path(item['path']);assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'];sources.append(item)
 headers=['portable_core_v1/ct_core.h','portable_core_v2_kinematics/ct_kinematics.h','portable_mpc_qp_v2_fast/boxqp_fast.h','portable_mpc_qp_v1/boxqp.h','portable_hal_proposal.h']
 for n in headers:
  p=HERE.parent/n;sources.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'role':'read-only local header'})
 files=[HERE/n for n in STATIC]
 for event in receipt['commands']:
  assert event['exit_code']==0,event
  p=Path(event['log']);assert p.resolve().is_relative_to(HERE.resolve()) and 'exit_code=0' in p.read_text(encoding='utf-8-sig');files.append(p)
  if event['phase']=='object_compile_only':
   a=event['arguments'];assert '-c' in a and '-mfloat-abi=hard' in a and '-fno-fast-math' in a and '-ffp-contract=off' in a
   assert '--target=arm-arm-none-eabi' in a and '-std=c99' in a and '-O2' in a
   assert '-Wall' in a and '-Wextra' in a and '-Werror' in a and not any('sse' in x.lower() for x in a)
  elif event['phase']=='fromelf_text_verbose_headers':assert event['arguments'][:2]==['--text','-v']
 for item in receipt['objects']:
  p=Path(item['object']);assert p.resolve().is_relative_to(HERE.resolve()) and item['compile_exit']==0 and item['present']
  assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'];files.append(p)
 old=[]
 pairs=[(HERE.parent/'deliverable_manifest.json','files'),(HERE.parent/'portable_core_v1/MANIFEST.json','deliverables'),
        (HERE.parent/'portable_core_v2_kinematics/MANIFEST.json','deliverables'),(HERE.parent/'portable_mpc_qp_v1/MANIFEST.json','deliverables'),
        (HERE.parent/'ODOM2D_DIAGNOSTIC/MANIFEST.json','deliverables'),(HERE.parent/'C_MPC8_NUMERIC_V1/MANIFEST.json','deliverables'),
        (HERE.parent/'portable_mpc_qp_v2_fast/MANIFEST.json','deliverables')]
 for p,key in pairs:
  for item in load(p)[key]:
   q=p.parent/item['path'];assert q.stat().st_size==item['bytes'] and sha(q)==item['sha256'];old.append(str(q))
 records=[]
 for p in sorted(set(files),key=lambda p:str(p)):
  r={'path':p.relative_to(HERE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
  if p.suffix!='.o':
   count=len(p.read_text(encoding='utf-8-sig').splitlines());r['line_count']=count
   if count:r['citation']=f'{r["path"]}#L1-L{count}'
  r['role']='ARM_relocatable_object_QA_not_firmware' if p.suffix=='.o' else 'source_command_log_or_metadata';records.append(r)
 phases={name:sum(x['phase']==name for x in receipt['commands']) for name in ['preprocessor_target_macros','object_compile_only','fromelf_text_verbose_headers']}
 assert phases=={'preprocessor_target_macros':2,'object_compile_only':6,'fromelf_text_verbose_headers':6}
 index={'name':'ARM_OBJECT_BUILD_V1','status':'SEALED_6_OF_6_COMPILE_ONLY_SUCCESS_NO_ARM_RUNTIME_OR_BSP_LINK',
  'write_scope':str(HERE),'files':records,'read_only_inputs':sources,'commands':receipt['commands'],
  'compiler_version_log':'armclang_version_01.log','fromelf_help_log':'fromelf_help_01.log','targets':receipt['targets'],
  'macros':summary['macros'],'objects':summary['objects'],'old_primary_files_unchanged':old,
  'claims':'C99 objects parse/codegen for explicit M4/M7 SP-hard candidates; headers and VFP ABI metadata checked',
  'not_claimed':['board binding DJIC/DM02/MOD4v1','BSP/stdlib link','firmware BIN','ARM runtime numerical identity','FPU enable/FPSCR/RTOS setup','HIL/flash','WCET/latency','robot/control qualification'],
  'never_performed':['armcc/armlink invocation','license workaround/environment change','toolchain install','parent/sealed edits','new physics/step/plant/controller replay','board/CAN/SSH/Git/new agents'],
  'metadata_self_hash_policy':'INDEX/VALIDATION/MANIFEST/index stdout excluded from recursive file hashes'}
 dump('INDEX.json',index)
 validation={'object_compile_success':6,'object_compile_total':6,'macro_probe_success':2,'fromelf_header_success':6,'failed_command_events':0,
             'source_files_hash_unchanged':3,'local_headers_hashed':len(headers),'old_primary_files_unchanged':len(old),'files_indexed':len(records),
             'linked_images':0,'BIN_files':0,'ARM_runtime_runs':0,'flash_operations':0,'ARM_WCET_measured':False}
 dump('VALIDATION.json',validation);dump('MANIFEST.json',{});links=0
 for n in ['README.md','ERROR_REPORT.md']:
  for target in re.findall(r'\]\(<([^>]+)>\)',(HERE/n).read_text(encoding='utf-8')):
   fn,_,frag=target.partition('#');p=(HERE/fn).resolve();assert p.is_file(),target
   if frag:
    m=re.fullmatch(r'L(\d+)(?:-L(\d+))?',frag)
    if m:assert 1<=int(m[1])<=int(m[2] or m[1])<=len(p.read_text(encoding='utf-8-sig').splitlines()),target
   links+=1
 validation['markdown_links_checked']=links;dump('VALIDATION.json',validation)
 primary=['README.md','BUILD_RECEIPT.json','OBJECT_SUMMARY.json','OBJECT_SUMMARY.csv','INDEX.json','VALIDATION.json','ERROR_REPORT.md']
 dump('MANIFEST.json',{'deliverables':[{'path':n,'bytes':(HERE/n).stat().st_size,'sha256':sha(HERE/n)} for n in primary]})
 print(json.dumps(validation,ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception:
  (HERE/'index_error_01.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
