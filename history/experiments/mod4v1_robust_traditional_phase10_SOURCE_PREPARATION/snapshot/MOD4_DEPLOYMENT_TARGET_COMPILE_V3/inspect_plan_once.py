"""V3 raw project plan only. All native tools deferred; no TU compilation."""
from pathlib import Path
import xml.etree.ElementTree as ET
import json,hashlib,collections
O=Path(__file__).resolve().parent;R=O.parent;S=R/'MOD4_DEPLOYMENT_PORT_V1';B=S/'derived/StandardRobotpp-balance1';P=B/'MDK-ARM/standard_robot.uvprojx'
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(n,v):
 with(O/n).open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def tree(e):
 if e is None:return None
 if len(e)==0:return e.text or ''
 return {c.tag:tree(c)for c in e}
def scalar(e):return None if e is None else {c.tag:(c.text or '')for c in e if len(c)==0}
def opt(e,arm):
 return dict(present=e is not None,common=tree(None if e is None else e.find('CommonProperty')),Cads=tree(None if e is None else e.find(arm+'/Cads')),Aads=tree(None if e is None else e.find(arm+'/Aads')))
parent=load(O/'PARENT_COMPILE_SCOPE.json');assert parent['maximum_each_real_translation_unit_compiles']==1 and parent['target_links']==0
project=rec(P);assert project['SHA']=='8e2f6401395cf571f481732a4549ba513bdde494762e8234ae2e396b34474437'
root=ET.fromstring(P.read_bytes());targets=root.findall('./Targets/Target');assert len(targets)==1;t=targets[0]
closure=load(S/'BUILD_CLOSURE_FINAL.json');patch=load(S/'PATCH_RECEIPT.json');pins={m['member'].casefold():dict(SHA=m.get('raw_SHA'),basis='SAVED_STAGE1_CLOSURE_NOT_FRESH_PAYLOAD_HASH')for m in closure['members']}
for m in patch['changed']:pins[m['member'].casefold()]=dict(SHA=m['after_SHA'],basis='SAVED_STAGE1_NARROW_PATCH_NOT_FRESH_PAYLOAD_HASH')
profiles={'target':dict(xpath='/Project/Targets/Target[1]/TargetOption',raw=tree(t.find('TargetOption')))};rows=[];group_summary=[];counts=collections.Counter();common_values=collections.defaultdict(collections.Counter)
for gi,g in enumerate(t.findall('./Groups/Group')):
 gn=g.findtext('GroupName');gkey='group_%03d'%gi;go=g.find('GroupOption');profiles[gkey]=dict(xpath='/Project/Targets/Target[1]/Groups/Group[%d]/GroupOption'%(gi+1),raw=opt(go,'GroupArmAds'));gs=dict(name=gn,profile=gkey,member_count=0,TU_count=0)
 for fi,f in enumerate(g.findall('./Files/File')):
  typ=int(f.findtext('FileType'));counts[str(typ)]+=1;gs['member_count']+=1;literal=f.findtext('FilePath');p=(P.parent/literal.replace('\\','/')).resolve();assert p.is_relative_to(B.resolve());member=B.name+'/'+p.relative_to(B.resolve()).as_posix();fk='file_%03d_%03d'%(gi,fi);fo=f.find('FileOption')
  if fo is not None:profiles[fk]=dict(xpath='/Project/Targets/Target[1]/Groups/Group[%d]/Files/File[%d]/FileOption'%(gi+1,fi+1),raw=opt(fo,'FileArmAds'))
  if typ not in (1,2):continue
  gs['TU_count']+=1;id=len(rows);st=p.stat()if p.is_file()else None;pin=pins.get(member.casefold(),dict(SHA=None,basis='NO_SAVED_PIN_FOUND'));chain=['target',gkey]+([fk]if fo is not None else [])
  rows.append(dict(id=id,language='C'if typ==1 else'ASM',group=gn,name=f.findtext('FileName'),member=member,project_literal=literal,source=str(p),source_exists=p.is_file(),current_stat=None if st is None else dict(bytes=st.st_size,mtime_ns=st.st_mtime_ns),declared_source_pin=pin,option_chain=chain,raw_group_profile=gkey,raw_file_profile=fk if fo is not None else None,effective_argv=None,effective_flags=None,plan_state='UNRESOLVED_UVISION_OPTION_MAPPING_NO_EXECUTION',output_object_candidate=str(O/'objects'/('%03d_'%id+p.name+'.o')),output_dependency_candidate=str(O/'deps'/('%03d_'%id+p.name+'.d')),state='UNSTARTED'))
 group_summary.append(gs)
assert dict(counts)=={'2':1,'1':162,'5':4,'4':2};assert len(rows)==163
for k,v in profiles.items():
 if k=='target':continue
 raw=v['raw']
 for language in ('Cads','Aads'):
  for field,value in (raw.get(language)or{}).items():
   if isinstance(value,str):common_values[language+'.'+field][value]+=1
missing=[x['id']for x in rows if not x['source_exists']];missing_pins=[x['id']for x in rows if x['declared_source_pin']['SHA']is None]
asm=Path('C:/Keil_v5/ARM/ARMCC/bin/armasm.exe');version=dict(allowed_future_argv=[str(asm),'--vsn'],source_input_TUs=[],compile_action=False,executed=False,exit=None,reason='Parent asked to preserve raw plan and wait for authoritative mappings; version-query budget is not consumed.',tool_exists=asm.is_file())
save('ARMASM_QUERY_DEFERRED.json',version)
blockers=[dict(id='UVISION_SELECTOR_AND_INHERITANCE_MAP',observed_example=dict(target=dict(Optim='1',oTime='0',wLevel='2',OneElfS='1'),HAL_group=dict(Optim='2',oTime='1',wLevel='0',EnumInt='2'),HAL_file=dict(Optim='0',oTime='2',wLevel='0',EnumInt='2')),needed='Authoritative/explicitly accepted per-field numeric-selector, inheritance and empty VariousControls rules before literal effective argv; no one-flat-target-flag application.',evidence='Actual XML target312-339,HAL group492-559,first file565-614. Compiler short help describes CLI -O0/-O1/-Otime, not uVision XML encoding.'),dict(id='DIRECT_VARIANT_IMPLICIT_RTE_POLICY',observed='Literal project paths/defines and RTE component declaration are stored separately; no RTE output generated.',needed='Confirm direct literal-only path/macro policy versus any IDE-derived implicit _RTE_/RTE-target include; no injection guessed from component declaration.',evidence='Actual XML339,3716-3727; V2 saved missing new-target RTE directory, existing old empty header.')]
if missing:blockers.append(dict(id='MISSING_REAL_TU_INPUT',TU_ids=missing))
if missing_pins:blockers.append(dict(id='NO_SAVED_SOURCE_PIN',TU_ids=missing_pins))
refs=[rec(O/'PARENT_COMPILE_SCOPE.json'),rec(O/'METHOD.md'),project,rec(S/'BUILD_CLOSURE_FINAL.json'),rec(S/'PATCH_RECEIPT.json'),rec(R/'MOD4_DEPLOYMENT_BUILD_PREP_V2/TOOL_VERSIONS.json'),rec(R/'MOD4_DEPLOYMENT_BUILD_PREP_V2/armcc_help_stdout.log')]
plan=dict(status='RAW_SOURCE_AND_OPTION_CHAIN_LOCK_NOT_EXECUTABLE_EFFECTIVE_ARGV',compiler_variant='ARMCC5.06u6 build750 explicitly approved; not u4.422 reproduction',source_refs=refs,project_target=t.findtext('TargetName'),project_declared_compiler=t.findtext('pCCUsed'),target_debug_browse=tree(t.find('TargetOption/TargetCommonOption')),RTE_declaration=tree(root.find('RTE')),file_type_counts=dict(counts),TU_count=163,groups=group_summary,profiles=profiles,non_target_scalar_value_histograms={k:dict(v)for k,v in common_values.items()},translation_units=rows,missing_TU_inputs=missing,missing_declared_source_pins=missing_pins,unresolved=blockers,effective_argv_frozen=False,source_full423_payload_rehash=False,current_source_SHA_policy='Only project XML is freshly hashed; real TU pins are saved stage1 lineage, current stat/existence checked. No claim of fresh TU payload SHA.',compile_invocations=0)
save('RAW_TU_PLAN_01.json',plan)
result=dict(status='STOPPED_BEFORE_ANY_TU_UNRESOLVED_EFFECTIVE_PLAN',raw_plan=rec(O/'RAW_TU_PLAN_01.json'),armasm_version=rec(O/'ARMASM_QUERY_DEFERRED.json'),unresolved=blockers,TU_total=163,successful_prefix=[],failed_TU=None,failed_compile_diagnostic=None,unstarted_TU_ids=[x['id']for x in rows],real_C_compiles=0,real_ASM_compiles=0,target_links=0,stage1_writes=False,UV_hooks_flash_CAN_SPI_PHY_oldQA_host40_Git_agents=0)
save('PLAN_GATE_01.json',result)
print(json.dumps(dict(status=result['status'],TU_count=len(rows),groups=[g for g in group_summary if profiles[g['profile']]['raw']['present']],profile_count=len(profiles),missing_inputs=missing,missing_pins=missing_pins,armasm_exit=version['exit'],real_C_compiles=0,real_ASM_compiles=0,plan=rec(O/'RAW_TU_PLAN_01.json')),ensure_ascii=False,indent=2))
