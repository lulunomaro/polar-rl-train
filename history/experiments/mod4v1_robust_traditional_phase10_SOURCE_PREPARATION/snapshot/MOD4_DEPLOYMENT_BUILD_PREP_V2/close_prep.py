"""Saved-evidence static-prep receipt. No compiler/link/archive/algorithm/target action."""
from pathlib import Path
import json,hashlib,re
O=Path(__file__).resolve().parent
load=lambda n:json.loads((O/n).read_bytes())
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def check(r):
 p=Path(r['path']);p=p if p.is_absolute()else O/p
 q=rec(p);assert(q['bytes'],q['SHA'])==(r['bytes'],r['SHA'])
V=load('TOOL_VERSIONS.json');H=load('TOOL_HELP.json');P=load('PATHS_AND_PROJECT.json');M=load('LIBRARY_MEMBERS.json');A=load('LIBRARY_ATTRIBUTE_COMMANDS.json');S=load('STATIC_FACTS.json')
assert len(V['tools'])==4 and all(x['exit']==0 and '5.06 update 6 (build 750)'in x['stdout']for x in V['tools'])
assert all('ARMCC' in x['path']and 'ARMCLANG'not in x['path']for x in V['tools'])
assert P['pCCUsed']=='5060422::V5.06 update 4 (build 422)::ARMCC'
assert len(H)==3 and len(M)==2 and len(A['commands'])==5
commands=V['tools']+H+M+A['commands'];assert len(commands)==14 and all(x['exit']==0 for x in commands)
for x in commands:
 for k in ('stdout_file','stderr_file','stdout','stderr'):
  r=x.get(k)
  if isinstance(r,dict):check(r)
for x in V['tools']:
 st=Path(x['path']).stat();assert(st.st_size,st.st_mtime_ns)==(x['bytes'],x['mtime_ns'])
for r in S['source_refs']:check(r)
assert S['source_refs'][:4]==P['source_refs']
for lr in A['libraries']:
 for obj in lr['objects']:check(obj)
for lr in P['libraries']:
 st=Path(lr['path']).stat();assert(st.st_size,st.st_mtime_ns)==(lr['bytes'],lr['mtime_ns'])
assert len(M[0]['members'])==1 and len(M[1]['members'])==272
assert A['libraries'][0]['complete_archive_attribute_coverage']and not A['libraries'][1]['complete_archive_attribute_coverage']
assert len(S['library_objects'])==3 and all(x['ELF32']and x['EABI5']and x['little_endian']and x['relocatable']and x['machine_ARM']for x in S['library_objects'])
assert len(P['unique_include_directories'])==34 and len(P['literal_include_checks'])==36
missing=[x for x in P['unique_include_directories']if not x['is_directory']];assert len(missing)==1 and missing[0]['literal']=='../application/protocol'
assert len(P['tool_standard_headers'])==13 and all(x['is_file']for x in P['tool_standard_headers'])
K=Path('C:/Keil_v5/ARM/PACK/Keil/STM32F4xx_DFP/2.17.1')
pack_checks=[dict(role=role,path=str(K/name),is_file=(K/name).is_file())for role,name in [('PDSC_declared_F407_debug_SVD','CMSIS/SVD/STM32F407.svd'),('PDSC_declared_compile_header','Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f4xx.h')]]
report=O/'REPORT.md';text=report.read_text(encoding='utf-8');lines=len(text.splitlines());assert lines<=120
links=re.findall(r'\]\(<([^>]+)>\)',text)
for link in links:
 p=(O/link.split('#')[0]).resolve();assert p.is_file()or p==O/'RECEIPT.json'
inputs=['METHOD.md','inspect_versions.py','inspect_help.py','inspect_paths.py','list_libraries.py','inspect_library_attributes.py','summarize_static.py','close_prep.py']
v=dict(status='SEALED_STATIC_BUILD_PREP_WITH_EXACT_TOOL_VERSION_DELTA_AND_OPEN_DEPENDENCIES_NOT_BUILD_APPROVAL',report=rec(report),report_lines=lines,report_live_links=len(links),source_metadata_refs_checked=len(S['source_refs']),source_metadata_refs=S['source_refs'],method_and_helpers=[rec(O/n)for n in inputs],evidence=[rec(O/n)for n in ('TOOL_VERSIONS.json','TOOL_HELP.json','PATHS_AND_PROJECT.json','LIBRARY_MEMBERS.json','LIBRARY_ATTRIBUTE_COMMANDS.json','STATIC_FACTS.json')],trusted_metadata_commands=14,trusted_metadata_command_failures=0,installed_compiler='5.06 update 6 build 750',requested_compiler='5.06 update 4 build 422',compiler_version_exact_match=False,Pack_DFP_2_17_1_PDSC_exists=True,CMSIS5_8_default_Keil_PDSC_exists=False,alternate_pack_caches='UNKNOWN_NOT_SEARCHED',exact_additional_PDSC_paths=pack_checks,project_unique_include_directories=34,missing_include_directories=missing,active_dependency_need_of_missing_paths='UNKNOWN_NO_PREPROCESS',AHRS_member_attribute_coverage='1/1',DSP_member_attribute_coverage='2/272_REPRESENTATIVE_ONLY',DSP_member_listing_coverage='272/272',library_input_hashes='STAGE1_VERIFIED_LINEAGE_ONLY_NOT_REHASHED_V2; CURRENT_SIZE_MTIME_STABLE',target_object_ABI_compatibility='UNKNOWN_NOT_COMPILED_OR_LINKED',target_compile_link_actions=0,UV_hook_flash=0,library_algorithm_target_execution=0,host40_oldQA_PHY_FK_Git_agents=0,stage1_files_written=False,whole423_rehash=False,raw_ZIP_access=False,packages_installed_or_replaced=False,ARMCLANG_migration=False,ready_for_full_target_build=False)
with(O/'RECEIPT.json').open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
for link in links:assert(O/link.split('#')[0]).resolve().is_file()
print(json.dumps(dict(status=v['status'],report=rec(report),report_lines=lines,receipt=rec(O/'RECEIPT.json'),metadata_commands=14,source_refs_checked=len(S['source_refs']),exact_pack_paths=pack_checks,compile_link=0),indent=2))
