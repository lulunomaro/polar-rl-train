"""One TU40 owned-snapshot ELF/section-header diagnosis only. No attribute/symbol payload."""
from pathlib import Path
import ast,hashlib,json,struct,traceback
O=Path(__file__).resolve().parent
R=O.parent
V8=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V8'
V7=R/'MOD4_DEPLOYMENT_ABI_SCOPE_STATIC_V7'

def record(p,b=None):
 if b is None:b=p.read_bytes()
 return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(name,obj):
 with (O/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def stat(p):s=p.stat();return {'bytes':s.st_size,'mtime_ns':s.st_mtime_ns}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def main():
 small=[O/'PARENT_HEADER_ONLY_SCOPE.json',O/'METHOD.md',Path(__file__).resolve(),V8/'FACTS_V8_01.json',V8/'attributes'/'040_scope.json',V8/'RECEIPT_V8_FINAL.json',V7/'scoped_attrs_v7.py']
 before=[record(p) for p in small]
 facts=load(V8/'FACTS_V8_01.json');stop=load(V8/'attributes'/'040_scope.json')
 expected=facts['failed_TU']['object'];obj=Path(expected['path'])
 need(facts['C_attempts']==39 and facts['new_scope_accepted_prefix']==38 and facts['unstarted_C']==122,'wrong V8 history')
 need(facts['failed_TU']['id']==40 and stop['classification']=='READER_CAPACITY_STOP','wrong stopped object')
 need(expected['bytes']==58720 and expected['SHA']=='8e01341b4c39ce543c2c114a1bddcba11371731ec87bcb4865f6285263a0e1a0','wrong producer pin')
 reader_bytes=(V7/'scoped_attrs_v7.py').read_bytes()
 need(hashlib.sha256(reader_bytes).hexdigest()=='0d4784fc36059a49fc434da44f93f354b9d786e8e65c184f4a0246798ed7d1e3','sealed reader drift')
 caps={}
 for node in ast.parse(reader_bytes.decode('utf-8')).body:
  if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id.startswith('MAX_'):
   caps[node.targets[0].id]=ast.literal_eval(node.value)
 need(caps=={'MAX_OBJECT':65536,'MAX_SECTIONS':256,'MAX_VENDORS':32,'MAX_BLOCKS':128,'MAX_PAIRS':2048,'MAX_IDS':256},'sealed caps drift')
 save('PREEXEC_HEADER_01.json',{'small_inputs_before':before,'expected_object':expected,'object_read_max':1,'header_diagnoses_max':1,'sealed_reader_import_parse_calls':0,'attribute_symbol_string_code_data_payload_interpretation':0,'ARM_native_calls':0,'existing_caps':caps})
 diag={'status':'HEADER_DIAG_STARTED','producer_object_pin':expected,'object_payload_open_reads':0,'attribute_payload_interpreted':False,'symbol_entries_decoded':0,'string_contents_decoded':0,'code_data_interpreted':False,'full_object_bytes_only_opaque_snapshot_and_hash':True,'sealed_V7_reader_import_or_parse_calls':0,'other_38_objects_read':0,'ARM_native_calls':0,'old_V8_history_unchanged':True,'ABI_TU40_still_unknown':True}
 try:
  st_before=stat(obj);data=obj.read_bytes();diag['object_payload_open_reads']=1
  diag['unique_owned_snapshot_record']=record(obj,data);need(diag['unique_owned_snapshot_record']==expected,'snapshot producer SHA/size mismatch')
  need(len(data)>=52 and data[:6]==b'\x7fELF\x01\x01','not ELF32LE')
  h=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
  diag['ELF_header']={'ELF_class':data[4],'ELF_data':data[5],'e_type':h[1],'e_machine':h[2],'e_version':h[3],'e_entry':h[4],'e_phoff':h[5],'e_shoff':h[6],'e_flags':h[7],'e_ehsize':h[8],'e_phentsize':h[9],'e_phnum':h[10],'e_shentsize':h[11],'e_shnum':h[12],'e_shstrndx':h[13],'file_bytes':len(data)}
  need(h[1:4]==(1,40,1) and h[8]==52 and h[11]==40,'unexpected class/header/entry/type/machine')
  need(h[6]>=52 and h[6]+40<=len(data),'no complete first section header')
  ext={'section_count':h[12]==0,'shstr_index':h[13]==65535,'program_count':h[10]==65535}
  first=struct.unpack_from('<10I',data,h[6]) if ext['section_count'] or ext['shstr_index'] or ext['program_count'] else None
  count=first[5] if ext['section_count'] else h[12]
  shstr=first[6] if ext['shstr_index'] else h[13]
  end=h[6]+40*count
  diag.update(extended_encoding=ext,effective_section_count=count,effective_shstr_index=shstr,section_table_end=end,section_table_end_within_file=end<=len(data),section_table_bytes=40*count,header_loop_bound_from_file=(len(data)-h[6])//40)
  need(count>0 and end<=len(data),'section table exceeds actual file')
  need(0<shstr<count,'invalid effective shstr index')
  rows=[first if i==0 and first is not None else struct.unpack_from('<10I',data,h[6]+40*i) for i in range(count)]
  need(rows[0][1]==0 and rows[shstr][1]==3,'not NULL section0/STRtab shstr header')
  bad=[];bad_names=[];symbols=[];attributes=[];nobits=0
  for i,s in enumerate(rows):
   bounded=s[4]<=len(data) and s[4]+s[5]<=len(data)
   if s[1]==8:nobits+=1
   if s[1] not in (0,8) and not bounded:bad.append({'id':i,'type':s[1],'offset':s[4],'size':s[5],'end':s[4]+s[5]})
   if s[0]>=rows[shstr][5]:bad_names.append({'id':i,'name_offset':s[0]})
   if s[1] in (2,11):
    aligned=s[9]>0 and s[5]%s[9]==0
    symbols.append({'id':i,'type':s[1],'offset':s[4],'bytes':s[5],'sh_entsize':s[9],'entries_including_null':s[5]//s[9] if aligned else None,'expected_ELF32_entry_size16':s[9]==16,'integer_entry_count':aligned,'payload_range_valid':bounded,'linked_string_table_index':s[6],'linked_index_valid':0<s[6]<count,'entries_payload_read':False})
   if s[1]==0x70000003:attributes.append({'id':i,'type':s[1],'offset':s[4],'bytes':s[5],'end':s[4]+s[5],'payload_range_valid':bounded,'payload_interpreted':False})
  diag.update(section_header_records_decoded=count,non_NOBITS_payload_bound_error_count=len(bad),bound_errors=bad[:16],name_offset_error_count=len(bad_names),name_offset_errors=bad_names[:16],NOBITS_sections_excluded_from_file_payload_bounds=nobits,shstr_table_header={'id':shstr,'offset':rows[shstr][4],'bytes':rows[shstr][5],'end':rows[shstr][4]+rows[shstr][5],'contents_read':False},symbol_table_headers=symbols,attribute_section_headers=attributes,attribute_total_bytes=sum(x['bytes'] for x in attributes))
  need(not bad and not bad_names,'header range/name-offset error')
  need(all(x['integer_entry_count'] and x['expected_ELF32_entry_size16'] and x['linked_index_valid'] for x in symbols),'bad symbol table header shape')
  diag['ordinary_valid_count_exceeds_old256_not_extended']=not any(ext.values()) and count>256
  diag['status']='HEADER_ONLY_VALID_STRUCTURE_NO_ATTRIBUTE_QUALIFICATION'
 except Exception:diag.update(status='STOP_HEADER_DIAG_ERROR_NO_RETRY',error=traceback.format_exc())
 finally:
  if 'data' in locals():diag['same_owned_snapshot_after_SHA']=hashlib.sha256(data).hexdigest()
  if 'st_before' in locals():diag.update(object_stat_before=st_before,object_stat_after=stat(obj),object_stat_stable=st_before==stat(obj),independent_post_file_SHA=None,post_SHA_evidence='Same owned snapshot rehashed; size/mtime checked. No second payload file read.')
  after=[record(p) for p in small];diag['small_inputs_after']=after;diag['small_input_source_SHA_before_after_unchanged']=before==after
  save('HEADER_DIAG_01.json',diag)  # Minimum result precedes every proposal/report.
 if diag['status']!='HEADER_ONLY_VALID_STRUCTURE_NO_ATTRIBUTE_QUALIFICATION':
  print(json.dumps({'status':diag['status'],'result':record(O/'HEADER_DIAG_01.json'),'payload_reads':diag['object_payload_open_reads']}));raise SystemExit(1)
 proposed=caps['MAX_SECTIONS'] if count<=caps['MAX_SECTIONS'] else count
 proposal={'status':'PROPOSAL_ONLY_NOT_APPLIED_NEW_READER_STUDY_SEPARATE','old_reader_SHA':hashlib.sha256(reader_bytes).hexdigest(),'actual_header_section_count':count,'old_MAX_SECTIONS':caps['MAX_SECTIONS'],'smallest_sufficient_MAX_SECTIONS_for_this_object':proposed,'candidate_source_delta':f'MAX_SECTIONS={caps["MAX_SECTIONS"]} -> MAX_SECTIONS={proposed}','only_section_cap_change_proposed':True,'all_other_MAX_constants_unchanged':{k:v for k,v in caps.items() if k!='MAX_SECTIONS'},'conditional_SYMBOL_entry_cap_unchanged':1024,'actual_symbol_table_entry_counts':[x['entries_including_null'] for x in symbols],'public_SYMBOL_scope_presence':'UNKNOWN_ATTRIBUTE_PAYLOAD_NOT_READ','public_block_pair_id_caps_sufficiency':'UNKNOWN_ATTRIBUTE_PAYLOAD_NOT_READ','semantic_gates_unchanged':{'ELF_class':1,'ELF_data':1,'ELF_type':1,'ELF_machine':40,'FILE_CPU_arch':13,'FILE_CPU_profile':77,'FILE_THUMB_ISA_use':2,'FILE_FP_arch':6,'FILE_ABI_HardFP_use':1,'FILE_ABI_VFP_args':1,'FILE_ABI_FP_denormal':[1,2],'each_code_and_SYMBOL_tag18':'2 or normative0 UNUSED with exact provenance','each_code_and_SYMBOL_tag26':'1 or normative0 UNUSED with exact provenance','unknown_conflict_reserved_malformed':'STOP'},'attribute_payload_interpreted':False,'old_limits_raised':False,'TU40_ABI_accepted':False,'native_or_suffix_continuation_authorized':False}
 save('CAPACITY_PROPOSAL_01.json',proposal)
 lines=['# V9：TU40一次结构header诊断（非属性重试）','',f'- 当前物件{len(data)}B；一次payload open/read，snapshot SHA与V8 producer pin相同。ELF32LE、ET_REL={h[1]}、EM_ARM={h[2]}。',f'- e_shnum={h[12]}，e_shoff={h[6]}，e_shentsize={h[11]}，e_shstrndx={h[13]}；table_end={end} ≤ file_size={len(data)}。',f'- extended flags={ext}；有效section count={count}，shstr header类型STRTAB；这一区分普通有效N>256与原reader合并报错中的extended/invalid。',f'- 全{count}个section header已核；非NOBITS payload边界错{len(bad)}，name offset边界错{len(bad_names)}。整物件仅opaque取数/hash，未遍历或解释string/symbol entry/attribute/code payload。',f'- symbol-table header计数（含NULL entry）={[x["entries_including_null"] for x in symbols]}；attribute section数={len(attributes)}，总大小={diag["attribute_total_bytes"]}B。详见[最小JSON](<HEADER_DIAG_01.json>)。',f'- 最小有界提案仅MAX_SECTIONS：256→{proposed}；64KiB与其余caps、conditional1024symbol、全部type/non-type gates原封不动。仅提案，未写新reader/改旧reader/解释属性；其他payload limits足够与否仍UNKNOWN。', '- [提案](<CAPACITY_PROPOSAL_01.json>)必须由父另批new reader study；该TU40 ABI仍UNKNOWN，122C+ASM1原样未启动。', '- 旧V8仍39成功编译/38scope认可/容量停止；失败prep与唯一suffix修订原件不变，无重新计账。', '- 小source/metadata before-after SHA一致；对象post SHA为同一owned snapshot再hash，file侧只核size/mtime，不冒充第二次独立file-side hash。', '- sealed V7 reader无import/调用，38个已认可物件无读取；ARM/compile/ASM/fromelf/probe/link/version/IO/oldQA/PHY/Git/agent/root-goal均0。', '- 全部V9在PH10 cutoff外；structural validity不是ABI/link/固件/runtime/板级资格。']
 need(len(lines)<=20,'report cap')
 with (O/'REPORT.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines)+'\n')
 save('RECEIPT.json',{'status':'SEALED_ONE_HEADER_ONLY_DIAGNOSIS_NOT_ABI_OR_CONTINUATION','object_payload_reads':diag['object_payload_open_reads'],'structural_header_diagnoses':1,'old_reader_parse_calls':0,'attribute_payload_interpretations':0,'source_small_pins_before':before,'source_small_pins_after':after,'object_unique_snapshot':diag['unique_owned_snapshot_record'],'post_file_hash_limit':diag['post_SHA_evidence'],'object_stat_stable':diag['object_stat_stable'],'report_lines':len(lines),'artifacts':[record(O/n) for n in ['PREEXEC_HEADER_01.json','HEADER_DIAG_01.json','CAPACITY_PROPOSAL_01.json','REPORT.md','diagnose_header_once.py']],'ARM_native_suffix_calls':0,'TU40_ABI_unknown':True})
 print(json.dumps({'status':diag['status'],'result':record(O/'HEADER_DIAG_01.json'),'report':record(O/'REPORT.md'),'receipt':record(O/'RECEIPT.json'),'actual_section_count':count,'actual_symbol_counts':proposal['actual_symbol_table_entry_counts'],'attribute_bytes':diag['attribute_total_bytes'],'payload_reads':diag['object_payload_open_reads']},ensure_ascii=False))
if __name__=='__main__':main()
