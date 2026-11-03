"""One-header input variant; saved argv transformation only, zero native invocations."""
from pathlib import Path
import json,hashlib,zlib,copy
O=Path(__file__).resolve().parent;R=O.parent;OLD=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V3'
load=lambda p:json.loads(p.read_bytes())
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def save(n,v):
 with(O/n).open('x',encoding='utf-8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
scope=load(O/'PARENT_DEPENDENCY_FIX_SCOPE.json');receipt_path=R/'DEPLOYED_BASELINE_AUDIT_V1/device_header_supplement002/RECEIPT.json';receipt=load(receipt_path)
header=R/scope['exact_new_input'];assert header.resolve()==Path(receipt['compiler_overlay_path']).resolve();data=header.read_bytes();h=dict(path=str(header),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),CRC32='%08x'%(zlib.crc32(data)&0xffffffff));assert h['bytes']==receipt['bytes']==1350860 and h['SHA']==receipt['SHA']==scope['header_SHA']and h['CRC32']==receipt['CRC32']=='9a578ca0'
assert len(data)<=2*1024*1024;del data
old_plan_path=OLD/'LITERAL_ARGV_V3A_01.json';old_result_path=OLD/'COMPILE_RESULT_V3A_01.json';old_plan=load(old_plan_path);old_result=load(old_result_path)
assert rec(old_plan_path)['SHA']=='2cc40fe35e4456f717d0647d189c4839e82d7de9175a2b6dc540c67c4aefdd10';assert old_result['attempted_TU_ids']==[1]and old_result['C_compile_count']==1 and old_result['ASM_compile_count']==0 and old_result['status']=='STOP_FIRST_REAL_COMPILER_ERROR'
variant='PARENT_DIAGNOSTIC_V4_ONE_DEVICE_HEADER_OVERLAY';p=copy.deepcopy(old_plan);p['variant']=variant;deltas=[]
for item,original in zip(p['translation_units'],old_plan['translation_units']):
 assert item['id']==original['id'];oldargv=original['argv'];newargv=list(oldargv);at=newargv.index('-o')+1;oldout=newargv[at];newout=str(O/'objects'/Path(oldout).name);newargv[at]=newout;newargv=[newargv[0],'-I',str(header.parent)]+newargv[1:]
 # Exact inverse proves no other argument changed; no new dependency flag is invented.
 reverse=[newargv[0]]+newargv[3:];reverse[reverse.index('-o')+1]=oldout;assert reverse==oldargv
 item['argv']=newargv;item['output_object']=newout
 for key in ('stdout','stderr'):item[key]=str(O/'logs'/Path(original[key]).name)
 item['new_header_overlay']=h;deltas.append(dict(id=item['id'],name=item['name'],prepended_include=['-I',str(header.parent)],old_object=oldout,new_object=newout,exact_inverse_restores_old_argv=True,old_argv_SHA=hashlib.sha256(json.dumps(oldargv,ensure_ascii=False).encode()).hexdigest(),new_argv_SHA=hashlib.sha256(json.dumps(newargv,ensure_ascii=False).encode()).hexdigest()))
old_exec=OLD/'compile_v3a_once.py';old_attr=OLD/'elf_attrs_v3.py';assert rec(old_exec)['SHA']==old_result['executor']['SHA']and rec(old_attr)['SHA']==old_result['attribute_reader']['SHA']
text=old_exec.read_text(encoding='utf-8');new=text.replace('V3A','V4').replace('PARENT_DIAGNOSTIC_V4','PARENT_DIAGNOSTIC_V4_ONE_DEVICE_HEADER_OVERLAY');assert new.replace('PARENT_DIAGNOSTIC_V4_ONE_DEVICE_HEADER_OVERLAY','PARENT_DIAGNOSTIC_V4').replace('V4','V3A')==text
with(O/'compile_v4_once.py').open('x',encoding='utf-8')as f:f.write(new)
with(O/'elf_attrs_v3.py').open('xb')as f:f.write(old_attr.read_bytes())
assert rec(O/'elf_attrs_v3.py')['SHA']==rec(old_attr)['SHA']
refs=old_plan['source_refs']+[rec(O/'PARENT_DEPENDENCY_FIX_SCOPE.json'),rec(O/'METHOD.md'),rec(receipt_path),dict(path=h['path'],bytes=h['bytes'],SHA=h['SHA']),rec(old_plan_path),rec(old_result_path),rec(OLD/'RECEIPT_V3A_FINAL.json'),rec(O/'compile_v4_once.py'),rec(O/'elf_attrs_v3.py'),rec(Path(__file__).resolve())]
p['source_refs']=refs;p['source_input_variant']=dict(old_variant=old_plan['variant'],old_failure=rec(old_result_path),header=h,receipt=rec(receipt_path),new_scope=rec(O/'PARENT_DEPENDENCY_FIX_SCOPE.json'),only_new_compiler_include=str(header.parent),ABI_gate_and_other_arguments_unchanged=True,no_old_XML_parser_or_version_or_compile_rerun=True)
p['native_invocations_before_freeze']=0;p['warning_policy']=old_plan['warning_policy'];p['first_object_expected']=old_plan['first_object_expected']
assert len(p['translation_units'])==163 and p['execution_order']==old_plan['execution_order']and p['execution_order'][0]==1
save('LITERAL_ARGV_V4_01.json',p);save('ARGV_DELTA_V4_01.json',dict(variant=variant,base=rec(old_plan_path),new=rec(O/'LITERAL_ARGV_V4_01.json'),new_header=h,deltas=deltas,all163_exact_inverse=True,no_old_source_write=True,no_old_project_parser_rerun=True,compiler_version='Reuse exact V2 ARMCC5.06u6 build750 record; no version invocation repeated.',executor_delta='Only V3A record-name token to V4 and variant string; exact reverse restores old executor bytes.',old_executor=rec(old_exec),new_executor=rec(O/'compile_v4_once.py'),attribute_reader_byte_exact=True))
print(json.dumps(dict(status='NEW_INPUT_V4_ALL163_ARGV_FROZEN_NATIVE0',variant=variant,header=h,plan=rec(O/'LITERAL_ARGV_V4_01.json'),delta=rec(O/'ARGV_DELTA_V4_01.json'),C=162,ASM=1,native_invocations=0),ensure_ascii=False,indent=2))
