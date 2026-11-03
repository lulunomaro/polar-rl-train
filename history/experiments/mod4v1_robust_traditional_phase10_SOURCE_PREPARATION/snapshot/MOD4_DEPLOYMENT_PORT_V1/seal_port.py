"""Saved-evidence/source-byte seal and new source ZIP. No build/test/target run."""
from pathlib import Path,PurePosixPath
import hashlib,json,re,zipfile,xml.etree.ElementTree as ET,struct
O=Path(__file__).resolve().parent;ROOT=O.parent;B=ROOT/'DEPLOYED_BASELINE_AUDIT_V1';D=O/'derived'
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):
 b=p.read_bytes();return dict(path=p.relative_to(O).as_posix(),bytes=len(b),SHA=sha(b))
def save(n,v):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
L=json.loads((O/'SOURCE.json').read_bytes());P=json.loads((O/'PATCH_RECEIPT.json').read_bytes());H=json.loads((O/'HOST_BUILD_01.json').read_bytes());S=json.loads((O/'SUPPLEMENT_RECEIPT.json').read_bytes());F=json.loads((O/'BUILD_CLOSURE_FINAL.json').read_bytes())
assert H['success']and H['smoke_assertions']==40 and H['smoke_failures']==0 and len(H['commands'])==6
assert all(r['exit']==0 for r in H['commands'])and not H['missing_exit0_artifact']
for r in H['inputs']:assert rec(O/r['path'])==r
for row in H['commands']:
 for key in ('log','artifact'):
  r=row.get(key)
  if r is not None:assert rec(O/r['path'])==r
host=O/'attempts/host_01/mod4_port_host_smoke.exe';hb=host.read_bytes();pe=struct.unpack_from('<I',hb,0x3c)[0];assert hb[:2]==b'MZ'and hb[pe:pe+4]==b'PE\0\0'and struct.unpack_from('<H',hb,pe+4)[0]==0x14c
assert b'checks=40 failures=0'in(O/'attempts/host_01/smoke.log').read_bytes()
changed={x['member']:x for x in P['changed']};payloads={};old_verified=0
for r in L['selected']:
 m=r['member'];orig=B/'source_original'/Path(*PurePosixPath(m).parts);assert sha(orig.read_bytes())==r['raw_SHA'];old_verified+=1
 dp=D/m;b=dp.read_bytes();expected=changed[m]['after_SHA']if m in changed else r['raw_SHA'];assert sha(b)==expected;payloads['derived/'+m]=b
 if m in changed:
  before=O/'before'/m;assert sha(before.read_bytes())==r['raw_SHA'];payloads['before/'+m]=before.read_bytes()
mp=B/'build_supplement001/MANIFEST.json';assert sha(mp.read_bytes())=='524b8dd11524fece9ac7faf5f9bd842e4d06e9f020d76f64ea47378e26bdcc7c'
SM=json.loads(mp.read_bytes())
for r in SM['files']:
 m=r['member'];orig=B/'build_supplement001/source_original'/Path(*PurePosixPath(m).parts);assert sha(orig.read_bytes())==r['raw_SHA'];old_verified+=1
 b=(D/m).read_bytes();assert sha(b)==r['raw_SHA'];payloads['derived/'+m]=b
for r in L['selection'],L['central']:
 assert sha((ROOT/r['path']).read_bytes())==r['SHA']
for n in ('mod4_port_gate.c','mod4_port_gate.h','mod4_port_bridge.c','mod4_port_bridge.h'):
 b=(O/'new_code'/n).read_bytes();m='StandardRobotpp-balance1/application/mod4_port/'+n;assert (D/m).read_bytes()==b;payloads['derived/'+m]=b;payloads['new_code/'+n]=b
assert len([p for p in payloads if p.startswith('derived/')])==427 and old_verified==423
project=D/'StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx';E=ET.fromstring(project.read_bytes());T=E.find('./Targets/Target');assert T is not None and len(T.findall('./Groups/Group/Files/File'))==169
assert T.findtext('./TargetOption/Utilities/Flash1/UpdateFlashBeforeDebugging')=='0'and T.findtext('./TargetOption/Utilities/Flash1/UseTargetDll')=='0'
assert F['all_original_165_members_provided']and not F['active_members_missing_provided']and not F['conditional_preprocessor_evaluated']and not F['full_target_link']
assert all(all(v['fields'].get(k)=='0'for k in('RunUserProg1','RunUserProg2'))for v in F['original_hooks'])
assert all(all(not v['fields'].get(k)for k in('UserProg1Name','UserProg2Name'))for v in F['original_hooks'])
for x in P['changed']:
 b=(D/x['member']).read_bytes();assert sha(b)==x['after_SHA'];txt=b.decode('utf-8-sig'if x['UTF8_BOM']else x['encoding'])
 for old,new in reversed([(x['old'],x['new'])for x in x['operations']]):assert txt.count(new)==1;txt=txt.replace(new,old,1)
 restored=(b'\xef\xbb\xbf'if x['UTF8_BOM']else b'')+txt.encode(x['encoding']);assert sha(restored)==x['before_SHA']
validation=dict(status='PASS_STAGE1_BYTE_CLOSURE_DERIVED_PATCH_AND_NEW_C99_HOST_ONLY',old_423_payload_SHA_unchanged=True,original_source_391=391,parent_supplement32=32,derived_payload_files=427,modified_inherited_files=2,other_inherited_byte_exact=421,reverse_patch_byte_exact=True,original_project_members_provided=165,new_project_members=4,all_169_files_present=True,Windows_case_aliases=len(F['Windows_case_aliases']),reachable_lexical_text_nodes=F['reachable_lexical_text_nodes'],actual_preprocess=False,opaque_library_ABI_checked=False,target_compiler_executed=False,full_target_builds=0,target_link=False,auto_flash_before_debug=False,host_program_PE32_i386=True,host_smoke_runs=1,host_checks=40,host_failures=0,new_C99_source_TU=3,CPP_or_ARM_runs=0,real_CAN_SPI=0,PHY_FK_oldQA=0,git_agents=0,physical_MOD4_binding=False,send_or_flash_qualification=False,default_unbound_gate=True,selected_original_ZIP_written_or_opened=False)
save('VALIDATION.json',validation)
extras=['METHOD.md','SOURCE.json','PATCH_PLAN.md','SUPPLEMENT_APPENDIX.md','COPIED_ORIGINALS.json','BUILD_CLOSURE.json','NEEDED_MEMBERS.json','BUILD_CLOSURE_FINAL.json','PATCH_RECEIPT.json','SUPPLEMENT_RECEIPT.json','HOST_BUILD_01.json','VALIDATION.json','NEXT_TARGET_BUILD_PLAN.md','ERROR_REPORT.md','PACKAGE_README.md','PORT_NARROW.patch','host_smoke.c','build_host_once.py','prepare_closure.py','apply_narrow_patch.py','append_supplement_and_close_graph.py','seal_port.py','attempts/host_01/smoke.log']
for n in extras:payloads[n]=(O/n).read_bytes()
assert len({n.casefold()for n in payloads})==len(payloads)
zpath=O/'mod4_deployment_port_stage1.zip'
with zipfile.ZipFile(zpath,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for name in sorted(payloads):
  q=PurePosixPath(name);assert not q.is_absolute()and '..'not in q.parts and '.git'not in q.parts
  zi=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));zi.create_system=0;zi.external_attr=0x20;zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,payloads[name],compresslevel=6)
with zipfile.ZipFile(zpath)as z:
 assert len(z.infolist())==len(payloads)and z.testzip()is None
 for n,b in payloads.items():assert sha(z.read(n))==sha(b)
# Live workspace document links only; no old directory walk or raw archive scan.
for md in ('README.md','METHOD.md','PATCH_PLAN.md','SUPPLEMENT_APPENDIX.md','NEXT_TARGET_BUILD_PLAN.md','ERROR_REPORT.md'):
 for target in re.findall(r'\]\(<([^>]+)>\)',(O/md).read_text(encoding='utf-8')):
  p=(O/target.split('#')[0]).resolve();assert p.exists()or p==O/'RECEIPT.json'
save('RECEIPT.json',dict(status='SEALED_STAGE1_DERIVED_KEIL_FILES_AND_NEW_HOST_GATE_NOT_TARGET_FIRMWARE',README=rec(O/'README.md'),METHOD=rec(O/'METHOD.md'),SOURCE=rec(O/'SOURCE.json'),initial_closure=rec(O/'BUILD_CLOSURE.json'),final_closure=rec(O/'BUILD_CLOSURE_FINAL.json'),patch=rec(O/'PORT_NARROW.patch'),patch_receipt=rec(O/'PATCH_RECEIPT.json'),supplement_receipt=rec(O/'SUPPLEMENT_RECEIPT.json'),host=rec(O/'HOST_BUILD_01.json'),host_executable=rec(host),validation=rec(O/'VALIDATION.json'),source_ZIP=rec(zpath),ZIP_entry_count=len(payloads),ZIP_uncompressed_bytes=sum(map(len,payloads.values())),ZIP_contains_host_or_target_executables=False,old_payloads_checked=old_verified,full_target_builds=0,target_program_executions=0,real_CAN_SPI=0,old_sources_written=False,library_ABI='UNVERIFIED_OPAQUE_COPY_ONLY',conditional_include_and_builtin_Pack='NOT_ACTUALLY_PREPROCESSED',next_build_plan=rec(O/'NEXT_TARGET_BUILD_PLAN.md')))
print(json.dumps(dict(status='STAGE1_SEALED_NO_TARGET_BUILD',README=rec(O/'README.md'),final_closure=rec(O/'BUILD_CLOSURE_FINAL.json'),source_ZIP=rec(zpath),ZIP_entries=len(payloads),receipt=rec(O/'RECEIPT.json'),old_unchanged=old_verified,host_checks=40,host_failures=0),indent=2))
