"""Freeze one CMSIS raw-header input variant from saved V4 argv; zero native calls."""
from pathlib import Path
import json,hashlib,zlib,copy
O=Path(__file__).resolve().parent;R=O.parent;OLD=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V4'
load=lambda p:json.loads(p.read_bytes())
def rec(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'SHA':hashlib.sha256(b).hexdigest()}
def save(n,x):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
scope=load(O/'PARENT_CMSIS_DEPENDENCY_SCOPE.json');hr=load(O/'HEADER_INPUT_RECEIPT_01.json');review=load(O/'HEADER_REVIEW_01.json')
assert hr['status']=='EXACT_ORIGINAL_RAW_HEADER_VERIFIED_READABLE_READY_FOR_REVIEW'and hr['original_member_payload_read_attempts']==1 and hr['other_member_payload_reads']==0 and not hr['compiler_input_transcoded']
header=Path(hr['raw_compiler_overlay']['path']);b=header.read_bytes();h=rec(header);assert h==hr['raw_compiler_overlay']and h['bytes']==53065 and h['SHA']=='51420495a86c8aea829f63a156c475c225bf9c51429e0bb210eb35db0b1fd1ba'and'%08x'%(zlib.crc32(b)&0xffffffff)==hr['actual_payload_CRC32']=='61803e9e';del b
assert review['raw_input']['SHA']==h['SHA']and review['native_invocations_so_far']==hr['native_invocations']==0
assert rec(Path(hr['readable_only_never_compiler_input']['path']))==hr['readable_only_never_compiler_input']
old_plan_path=OLD/'LITERAL_ARGV_V4_01.json';old_result_path=OLD/'COMPILE_RESULT_V4_01.json';old=load(old_plan_path);old_result=load(old_result_path)
assert rec(old_plan_path)['SHA']=='163cfb3326d48b2612bda4bfe8e5d17345ab2e53ae2f89301b2fd5c373814fa4'and old_result['attempted_TU_ids']==[1]and old_result['C_compile_count']==1 and old_result['ASM_compile_count']==0 and old_result['status']=='STOP_FIRST_REAL_COMPILER_ERROR'
variant='PARENT_DIAGNOSTIC_V6_CMSIS_RTOS_HEADER_OVERLAY';p=copy.deepcopy(old);p['variant']=variant;deltas=[]
for item,original in zip(p['translation_units'],old['translation_units']):
 assert item['id']==original['id'];a=list(original['argv']);at=a.index('-o')+1;oldout=a[at];newout=str(O/'objects'/Path(oldout).name);a[at]=newout;a=[a[0],'-I',str(header.parent)]+a[1:]
 reverse=[a[0]]+a[3:];reverse[reverse.index('-o')+1]=oldout;assert reverse==original['argv']
 assert original['argv'][1:3]==['-I',str(Path(original['new_header_overlay']['path']).parent)]and a[3:5]==original['argv'][1:3]
 item['argv']=a;item['output_object']=newout
 for key in ('stdout','stderr'):item[key]=str(O/'logs'/Path(original[key]).name)
 item['new_CMSIS_header_overlay']={**h,'CRC32':'61803e9e'}
 deltas.append({'id':item['id'],'name':item['name'],'prepended_I':['-I',str(header.parent)],'retained_old_device_I':a[3:5],'old_object':oldout,'new_object':newout,'all_other_tokens_reverse_exact':True,'old_argv_SHA':hashlib.sha256(json.dumps(original['argv'],ensure_ascii=False).encode()).hexdigest(),'new_argv_SHA':hashlib.sha256(json.dumps(a,ensure_ascii=False).encode()).hexdigest()})
old_executor=OLD/'compile_v4_once.py';old_attr=OLD/'elf_attrs_v3.py';assert rec(old_executor)==old_result['executor']and rec(old_attr)==old_result['attribute_reader']
original=old_executor.read_bytes();new=original.replace(b'V4',b'V6').replace(b'PARENT_DIAGNOSTIC_V6_ONE_DEVICE_HEADER_OVERLAY',variant.encode());assert new.replace(variant.encode(),b'PARENT_DIAGNOSTIC_V6_ONE_DEVICE_HEADER_OVERLAY').replace(b'V6',b'V4')==original
with(O/'compile_v6_once.py').open('xb')as f:f.write(new)
with(O/'elf_attrs_v3.py').open('xb')as f:f.write(old_attr.read_bytes())
assert rec(O/'elf_attrs_v3.py')['SHA']==rec(old_attr)['SHA']
refs=old['source_refs']+[rec(O/'PARENT_CMSIS_DEPENDENCY_SCOPE.json'),rec(O/'METHOD.md'),rec(O/'HEADER_INPUT_RECEIPT_01.json'),rec(O/'HEADER_REVIEW_01.json'),h,rec(old_plan_path),rec(old_result_path),rec(OLD/'RECEIPT_V4_FINAL.json'),rec(R/'MOD4_DEPLOYMENT_DEPENDENCY_STATIC_V5/RECEIPT_V5_FINAL.json'),rec(O/'compile_v6_once.py'),rec(O/'elf_attrs_v3.py'),rec(Path(__file__).resolve())]
p['source_refs']=refs;p['previous_source_input_variant']=old['source_input_variant'];p['source_input_variant']={'old_variant':old['variant'],'old_failure':rec(old_result_path),'added_CMSIS_header':h,'CRC32':'61803e9e','input_receipt':rec(O/'HEADER_INPUT_RECEIPT_01.json'),'header_review':rec(O/'HEADER_REVIEW_01.json'),'new_scope':rec(O/'PARENT_CMSIS_DEPENDENCY_SCOPE.json'),'only_new_compiler_I':str(header.parent),'old_device_I_retained':True,'all_other_argv_and_ABI_gate_unchanged':True,'no_old_XML_parser_version_or_compile_rerun':True};p['native_invocations_before_freeze']=0
assert len(p['translation_units'])==163 and p['execution_order']==old['execution_order']and p['execution_order'][0]==1 and p['maximum_each_TU_native_compile']==1 and p['target_links']==0
save('LITERAL_ARGV_V6_01.json',p)
save('ARGV_DELTA_V6_01.json',{'variant':variant,'base_V4':rec(old_plan_path),'new':rec(O/'LITERAL_ARGV_V6_01.json'),'new_CMSIS_raw_header':h,'old_device_overlay_retained':True,'deltas':deltas,'all163_exact_argv_inverse':True,'executor_delta':'Only record-name V4 to V6 tokens and variant string; original byte line endings preserved.','old_executor':rec(old_executor),'new_executor':rec(O/'compile_v6_once.py'),'executor_raw_byte_inverse_actually_checked':True,'attribute_reader_byte_exact':True,'no_old_source_write_or_parser_version_compile_rerun':True,'native_invocations':0})
print(json.dumps({'status':'V6_ALL163_ACTUAL_ARGV_FROZEN_REVERSE_EXACT_NATIVE0','header':h,'plan':rec(O/'LITERAL_ARGV_V6_01.json'),'delta':rec(O/'ARGV_DELTA_V6_01.json'),'C':162,'ASM':1,'native':0},ensure_ascii=False,indent=2))
