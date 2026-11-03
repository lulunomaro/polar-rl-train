"""Freeze explicitly parent-selected diagnostic argv from saved raw XML values, no native invocation."""
from pathlib import Path
import json,hashlib,shlex
O=Path(__file__).resolve().parent;R=O.parent;S=R/'MOD4_DEPLOYMENT_PORT_V1';P=S/'derived/StandardRobotpp-balance1/MDK-ARM/standard_robot.uvprojx'
load=lambda p:json.loads(p.read_bytes())
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def save(n,v):
 with(O/n).open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
raw=load(O/'RAW_TU_PLAN_01.json');pre=load(O/'ADDENDUM_PRECHECK_01.json');dec=load(O/'PARENT_AC5_DEFAULTS_DECISION.json');add=load(O/'PARENT_DIAGNOSTIC_RECIPE_ADDENDUM.json')
assert not pre['nonempty_group_file_text']and not pre['unsupported_numeric_values'];assert raw['compile_invocations']==0
assert dec['C_recipe_explicit']==['--cpu=Cortex-M4.fp','-c','--c99','-O1','-Otime','--apcs=interwork','--split_sections','--diag_error=warning']
target=raw['profiles']['target']['raw']['TargetArmAds'];ignored=('v6Lang','v6LangP','vShortEn','vShortWch','v6Lto','v6WtE','v6Rtti','uClangAs')
# Explicit parent recipe, NOT a historical uVision numeric-encoding implementation.
def resolve(row):
 language='Cads'if row['language']=='C'else'Aads';out={k:v for k,v in target[language].items()if isinstance(v,str)};text=dict(target[language]['VariousControls']);chain=[]
 for key in row['option_chain'][1:]:
  b=raw['profiles'][key]['raw'].get(language)
  if b is None:continue
  chain.append(dict(profile=key,raw=b))
  for k,v in b.items():
   if isinstance(v,str)and k not in ('Optim','oTime','wLevel')and k not in ignored:
    assert v in ('0','1','2'),(key,k,v)
    if v!='2':out[k]=v
  for k,v in b.get('VariousControls',{}).items():assert v=='',(key,k,v)
 return language,out,text,chain
items=[];roots=Path('C:/Keil_v5/ARM/ARMCC/bin')
for row in raw['translation_units']:
 language,values,text,chain=resolve(row);isC=row['language']=='C';assert values['interw']=='1'
 for k in ('Ropi','Rwpi','SplitLS','uSurpInc','useXO'):assert values.get(k,'0')=='0',(row['id'],k,values.get(k))
 if isC:
  for k,expected in dict(OneElfS='1',uC99='1',EnumInt='0',PlainCh='0',Strict='0',uThumb='0').items():assert values[k]==expected,(row['id'],k,values[k])
  argv=[str(roots/'armcc.exe')]+dec['C_recipe_explicit']
 else:
  for k in ('thumb','SwStkChk','NoWarn'):assert values[k]=='0',(k,values[k])
  assert not text.get('Define')and not text.get('Undefine')
  argv=[str(roots/'armasm.exe'),'--cpu=Cortex-M4.fp','--apcs=interwork']
 includes=[x for x in text.get('IncludePath','').split(';')if x];defines=[x for x in text.get('Define','').split(',')if x];undefines=[x for x in text.get('Undefine','').split(',')if x]
 for x in includes:argv+=['-I',x]
 for x in defines:argv+=['-D',x]
 for x in undefines:argv+=['-U',x]
 misc=shlex.split(text.get('MiscControls',''),posix=True)
 for x in misc:
  if x=='--diag_error=warning'and x in argv:continue
  argv.append(x)
 obj=O/'objects'/('%03d_'%row['id']+row['name']+'.o');argv+=['-o',str(obj),row['source']]
 assert Path(row['source']).is_file()and row['declared_source_pin']['SHA'];assert all(x!='--no_warn'and not x.startswith('--diag_suppress')for x in argv)
 items.append(dict(id=row['id'],name=row['name'],language=row['language'],source=row['source'],source_pin=row['declared_source_pin'],project_group=row['group'],cwd=str(P.parent),argv=argv,output_object=str(obj),stdout=str(O/'logs'/('%03d_'%row['id']+row['name']+'.stdout.log')),stderr=str(O/'logs'/('%03d_'%row['id']+row['name']+'.stderr.log')),original_option_chain=row['option_chain'],original_chain_profiles=chain,selected_boolean_recipe=values,ignored_AC6_fields={k:v for k,v in values.items()if k in ignored},literal_includes=includes,literal_defines=defines,literal_undefines=undefines,dependency_file_generation='NOT_SELECTED_NO_EXTRA_UNVERIFIED_DEPEND_SWITCH'))
order=[x['id']for x in items if x['language']=='C']+[x['id']for x in items if x['language']=='ASM'];assert len(order)==163 and items[order[0]]['name']=='main.c'
refs=[rec(O/'PARENT_COMPILE_SCOPE.json'),rec(O/'PARENT_DIAGNOSTIC_RECIPE_ADDENDUM.json'),rec(O/'PARENT_AC5_DEFAULTS_DECISION.json'),rec(O/'RAW_TU_PLAN_01.json'),rec(O/'ADDENDUM_PRECHECK_01.json'),rec(R/'MOD4_DEPLOYMENT_BUILD_PREP_V2/TOOL_VERSIONS.json'),rec(R/'MOD4_DEPLOYMENT_BUILD_PREP_V2/STATIC_FACTS.json'),rec(Path(__file__).resolve())]
plan=dict(variant='PARENT_DIAGNOSTIC_V3A',not_original_UVISION_semantics_or_u4_reproduction=True,source_refs=refs,source_metadata_refs_from_raw=raw['source_refs'],source_SHA_rule='stage1 saved lineage; each real TU freshly hash-checked exactly before its single native compile; not a full423 rehash',native_invocations_before_freeze=0,C_recipe=dec['C_recipe_explicit'],ASM_recipe=['--cpu=Cortex-M4.fp','--apcs=interwork'],ASM_note='CPU/interwork explicit same AC5 diagnostic selection; all other false actual Aads flags omitted; literal includes only. Query exact same-bin assembler --vsn once only if ASM reached.',warning_policy='Compiler default warnings; original --diag_error=warning once, no suppression based on XML wLevel',optimization_policy='uniform -O1 -Otime, deliberate override; original values in immutable raw and each chain',RTE_policy=dec['RTE_choices'],defaults_policy=dec['default_choices'],first_object_attribute_gate=dec['first_actual_object_gate'],first_object_expected=dict(ELF_class=1,ELF_data=1,ELF_type=1,ELF_machine=40,CPU_arch=13,CPU_profile=77,THUMB_ISA_use=2,FP_arch=6,ABI_Wchar_t=2,ABI_enum_size=1,ABI_HardFP_use=1,ABI_VFP_args=1,ABI_FP_denormal=[1,2]),maximum_each_TU_native_compile=1,first_error_stop=True,target_links=0,tu_count=163,C_count=162,ASM_count=1,execution_order=order,translation_units=items)
save('LITERAL_ARGV_V3A_01.json',plan)
print(json.dumps(dict(status='EXPLICIT_DIAGNOSTIC_V3A_LITERAL_ARGV_FROZEN_BEFORE_FIRST_TU',plan=rec(O/'LITERAL_ARGV_V3A_01.json'),C_count=162,ASM_count=1,first_name=items[order[0]]['name'],native_invocations=0),ensure_ascii=False,indent=2))
