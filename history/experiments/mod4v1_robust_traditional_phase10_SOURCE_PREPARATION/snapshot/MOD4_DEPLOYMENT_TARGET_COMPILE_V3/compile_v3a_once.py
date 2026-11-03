"""Single bounded diagnostic compile wave. First error/ABI uncertainty stops; NEVER links."""
from pathlib import Path
import json,hashlib,subprocess,time,traceback
from elf_attrs_v3 import inspect
O=Path(__file__).resolve().parent
load=lambda n:json.loads((O/n).read_bytes())
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def save(n,v):
 with(O/n).open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
p=load('LITERAL_ARGV_V3A_01.json');assert p['variant']=='PARENT_DIAGNOSTIC_V3A'and p['maximum_each_TU_native_compile']==1 and p['target_links']==0
for r in p['source_refs']:
 now=rec(Path(r['path']));assert(now['bytes'],now['SHA'])==(r['bytes'],r['SHA'])
for n in ('objects','logs'): (O/n).mkdir(exist_ok=True)
ledger=(O/'EXECUTION_LEDGER_V3A_01.jsonl').open('x',encoding='utf-8');results=[];native=[];first_gate=None;reason=None;failed=None;attempted=[]
def event(x):ledger.write(json.dumps(x,ensure_ascii=False,allow_nan=False)+'\n');ledger.flush()
def call(argv,cwd,stdout,stderr,kind):
 begin=time.monotonic_ns();entry=dict(kind=kind,argv=argv,cwd=str(cwd),stdout=str(stdout),stderr=str(stderr),start_host_monotonic_ns=begin)
 event(dict(event='NATIVE_INVOKE',**entry))
 with stdout.open('xb')as out,stderr.open('xb')as err:cp=subprocess.run(argv,cwd=cwd,stdout=out,stderr=err,check=False)
 entry.update(exit=cp.returncode,elapsed_host_ns_not_WCET=time.monotonic_ns()-begin,stdout_record=rec(stdout),stderr_record=rec(stderr));native.append(entry);event(dict(event='NATIVE_RETURN',**entry));return cp.returncode
try:
 for id in p['execution_order']:
  row=p['translation_units'][id];src=Path(row['source']);obj=Path(row['output_object']);assert not obj.exists(),('OBJECT_ALREADY_EXISTS_NO_RETRY',id)
  actual=rec(src)
  if actual['SHA']!=row['source_pin']['SHA']:
   reason='STOP_SOURCE_PIN_MISMATCH_BEFORE_TU';failed=dict(id=id,name=row['name'],not_compiled=True,actual=actual,expected=row['source_pin']);break
  if row['language']=='ASM':
   argv=['C:/Keil_v5/ARM/ARMCC/bin/armasm.exe','--vsn'];rc=call(argv,O,O/'logs/armasm_vsn.stdout.log',O/'logs/armasm_vsn.stderr.log','ARMASM_VERSION_ONLY')
   if rc!=0:reason='STOP_ASSEMBLER_VERSION_QUERY_FAILED_BEFORE_ASM';failed=dict(id=id,name=row['name'],not_compiled=True);break
  attempted.append(id);event(dict(event='TU_ATTEMPT',id=id,name=row['name'],language=row['language'],source_now=actual,plan=rec(O/'LITERAL_ARGV_V3A_01.json')))
  rc=call(row['argv'],row['cwd'],Path(row['stdout']),Path(row['stderr']),'REAL_'+row['language']+'_TU_COMPILE')
  item=dict(id=id,name=row['name'],language=row['language'],source_now=actual,exit=rc,object_exists=obj.is_file(),argv=row['argv'],stdout=rec(Path(row['stdout'])),stderr=rec(Path(row['stderr'])))
  if obj.is_file():item['object']=rec(obj)
  results.append(item)
  if rc!=0:reason='STOP_FIRST_REAL_COMPILER_ERROR';failed=item;break
  if not obj.is_file()or obj.stat().st_size==0:reason='STOP_COMPILER_EXIT0_MISSING_OR_EMPTY_OBJECT';failed=item;break
  if first_gate is None:
   rc=call(['C:/Keil_v5/ARM/ARMCC/bin/fromelf.exe','--text','-v',str(obj)],O,O/'logs/first_object.fromelf.stdout.log',O/'logs/first_object.fromelf.stderr.log','FIRST_REAL_OBJECT_ATTRIBUTES_ONLY')
   first_gate=dict(id=id,name=row['name'],fromelf_exit=rc,expected=p['first_object_expected'],source_reference='Target intent plus V2 saved AHRS1/DSP2 object metadata. Only sampled old library attributes, not whole-library proof.')
   if rc!=0:
    first_gate.update(pass_gate=False,reason='FROMELF_NONZERO');save('FIRST_OBJECT_GATE_V3A_01.json',first_gate);reason='STOP_FIRST_OBJECT_ATTRIBUTE_TOOL_ERROR';break
   try:attrs=inspect(obj)
   except Exception:
    first_gate.update(pass_gate=False,reason='ELF_ATTRIBUTE_PARSE_UNKNOWN',error=traceback.format_exc());save('FIRST_OBJECT_GATE_V3A_01.json',first_gate);reason='STOP_FIRST_OBJECT_ATTRIBUTE_UNKNOWN';break
   tags=attrs['merged_tags'];expect=p['first_object_expected'];checks=[]
   for key in ('ELF_class','ELF_data','ELF_type','ELF_machine'):checks.append(dict(field=key,actual=attrs[key],expected=expect[key],pass_gate=attrs[key]==expect[key]))
   mapping={6:'CPU_arch',7:'CPU_profile',9:'THUMB_ISA_use',10:'FP_arch',18:'ABI_Wchar_t',26:'ABI_enum_size',27:'ABI_HardFP_use',28:'ABI_VFP_args',20:'ABI_FP_denormal'}
   for tag,key in mapping.items():
    actual_tag=tags.get(str(tag),'UNKNOWN');wanted=expect[key];ok=actual_tag in wanted if isinstance(wanted,list)else actual_tag==wanted;checks.append(dict(field=key,tag=tag,actual=actual_tag,expected=wanted,pass_gate=ok))
   first_gate.update(attributes=attrs,checks=checks,pass_gate=all(x['pass_gate']for x in checks),ABI_is_not_runtime_or_FPSCR_qualification=True);save('FIRST_OBJECT_GATE_V3A_01.json',first_gate)
   if not first_gate['pass_gate']:reason='STOP_FIRST_REAL_OBJECT_UNEXPECTED_OR_UNKNOWN_ABI';break
  event(dict(event='TU_ACCEPTED_COMPILE_ONLY',id=id,name=row['name']))
 else:reason='ALL163_DIAGNOSTIC_OBJECTS_COMPILED_NOT_LINKED_PENDING_REVIEW'
except Exception:
 reason='STOP_EXECUTOR_EXCEPTION_NO_AUTOMATIC_RETRY';event(dict(event='EXECUTOR_EXCEPTION',error=traceback.format_exc()));failed=dict(exception=traceback.format_exc())
finally:
 ledger.close()
unstarted=[x for x in p['execution_order']if x not in attempted];successful=[x for x in results if x['exit']==0 and x['object_exists']]
r=dict(status=reason,variant=p['variant'],plan=rec(O/'LITERAL_ARGV_V3A_01.json'),executor=rec(Path(__file__).resolve()),attribute_reader=rec(O/'elf_attrs_v3.py'),native_invocations=native,TU_results=results,successful_compile_prefix=successful,failed_TU=failed,first_object_gate=first_gate,attempted_TU_ids=attempted,unstarted_TU_ids=unstarted,C_compile_count=sum(p['translation_units'][i]['language']=='C'for i in attempted),ASM_compile_count=sum(p['translation_units'][i]['language']=='ASM'for i in attempted),each_TU_at_most_once=len(set(attempted))==len(attempted),target_links=0,old_source_edits=0,no_UV_hook_flash_CAN_SPI_PHY_oldQA_host40_Git_agents=True)
save('COMPILE_RESULT_V3A_01.json',r)
print(json.dumps(dict(status=reason,result=rec(O/'COMPILE_RESULT_V3A_01.json'),C_compile_count=r['C_compile_count'],ASM_compile_count=r['ASM_compile_count'],successful_compile_prefix=len(successful),failed_name=failed.get('name')if failed else None,unstarted_count=len(unstarted),first_object_gate=None if first_gate is None else first_gate.get('pass_gate')),ensure_ascii=False,indent=2))
raise SystemExit(0 if reason=='ALL163_DIAGNOSTIC_OBJECTS_COMPILED_NOT_LINKED_PENDING_REVIEW'else 1)
