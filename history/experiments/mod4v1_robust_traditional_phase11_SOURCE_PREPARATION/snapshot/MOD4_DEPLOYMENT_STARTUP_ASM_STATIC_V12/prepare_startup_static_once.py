"""One startup source/metadata static review. No ARM calls, parser fixtures or object reads."""
from pathlib import Path
import hashlib,json,re,traceback
O=Path(__file__).resolve().parent;R=O.parent
V3=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V3';V7=R/'MOD4_DEPLOYMENT_ABI_SCOPE_STATIC_V7';V11=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V11'
def rec(p,b=None):
 if b is None:b=p.read_bytes()
 return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(n,v):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 marker=O/'MIN_STATIC_LEDGER_01.json'
 with marker.open('x',encoding='utf-8') as f:f.write('{}\n')
 state=dict(status='STATIC_SOURCE_REVIEW_ENTERED_BEFORE_ANY_TOOL',ARM_native_calls=0,source_files_reviewed=0,old_C_or_library_objects_read=0,parser_fixture_calls=0)
 def checkpoint():
  with marker.open('w',encoding='utf-8',newline='\n') as f:json.dump(state,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush()
 checkpoint()
 try:
  planpath=V11/'LITERAL_ARGV_V11_01.json';rawpath=V3/'RAW_TU_PLAN_01.json';rulespath=V7/'OFFICIAL_RULES.json';deferredpath=V3/'ARMASM_QUERY_DEFERRED.json'
  assert rec(planpath)['SHA']=='58caa3c0129b23014fe348263f84fd10d1d84d2fd003eb2ff2c19fcd3fe08702'
  assert rec(rawpath)['SHA']=='6eade5f9878bde7935f41ee482066717c59392c20ba4907beb63a5e12d387544'
  assert rec(rulespath)['SHA']=='3a354c2e988fcd1822ed6dc19cbad9b889bd43df536ab941ed1964a3ab76b2a5'
  plan=load(planpath);raw=load(rawpath);rules=load(rulespath);deferred=load(deferredpath)
  row=plan['original_ASM_id0_UNSTARTED_frozen_not_authorized'];assert row['id']==0 and row['language']=='ASM'
  src=Path(row['source']);blob=src.read_bytes();source_before=rec(src,blob)
  assert source_before['SHA']==row['source_pin']['SHA']=='7baf21c802efd7aaeace20cfecef16b967d124fcbd5f038088be0eee6138b261' and source_before['bytes']==30149
  refs=[rec(p) for p in [O/'PARENT_SCOPE.json',O/'METHOD.md',Path(__file__).resolve(),planpath,rawpath,rulespath,deferredpath]]+[source_before]
  save('PREEXEC_STATIC_01.json',dict(status='SMALL_SOURCE_AND_METADATA_PINS_BEFORE_STRUCTURED_REVIEW',source_refs=refs,one_source_id=0,tool_invocations_allowed=0,new_object_parses_allowed=0))
  text=blob.decode('utf-8-sig');lines=text.splitlines();code=[(i,s.split(';',1)[0].strip()) for i,s in enumerate(lines,1)]
  constants={};includes=[];imports=[];weak=[];instructions=[];vectors=[];invector=False
  for i,s in code:
   if not s:continue
   m=re.fullmatch(r'(\w+)\s+EQU\s+(0x[0-9a-fA-F]+|[0-9]+)',s)
   if m:constants[m[1]]=dict(value=int(m[2],0),literal=m[2],line=i)
   if re.match(r'^(?:\w+\s+)?(?:INCLUDE|GET|INCBIN)\b',s,re.I):includes.append(dict(line=i,text=s))
   m=re.match(r'^IMPORT\s+(\w+)',s)
   if m:imports.append(dict(name=m[1],line=i))
   m=re.match(r'^EXPORT\s+(\w+)\s+\[WEAK\]',s)
   if m:weak.append(dict(name=m[1],line=i))
   m=re.match(r'^(LDR|BLX|BX|B)\s+(.*)$',s)
   if m:instructions.append(dict(opcode=m[1],operands=m[2],line=i))
   if re.match(r'^__Vectors\s+DCD\b',s):invector=True
   if s=='__Vectors_End':invector=False
   if invector:
    m=re.search(r'\bDCD\s+(\S+)',s)
    if m:vectors.append(dict(word_index=len(vectors),value=m[1],line=i))
  assert constants['Stack_Size']['value']==8192 and constants['Heap_Size']['value']==8192
  assert not includes,'UNEXPECTED_SOURCE_INCLUDE_REQUIRES_NEW_SCOPE_REVIEW'
  assert [v['value'] for v in vectors[:2]]==['__initial_sp','Reset_Handler'] and vectors[-1]['value']=='FPU_IRQHandler'
  ads=raw['profiles']['target']['raw']['TargetArmAds'];aads=ads['Aads'];cads=ads['Cads'];misc=ads['ArmAdsMisc'];group=raw['profiles']['group_000']['raw']
  assert misc['useUlib']=='0' and not group['present'] and group['Aads'] is None
  assert aads['VariousControls']==dict(MiscControls='',Define='',Undefine='',IncludePath='..\\\\Inc;../Inc')
  assert row['literal_defines']==[] and row['literal_undefines']==[] and not any('__MICROLIB' in t for t in row['argv'])
  assert deferred['executed'] is False and deferred['compile_action'] is False
  importnames=[x['name'] for x in imports];assert importnames==['SystemInit','__main','__use_two_region_memory']
  assert {x['opcode'] for x in instructions}=={'LDR','BLX','BX','B'}
  unknown=[dict(item='ARMASM exact installed version',reason='Only named executable existed in prior deferred record; no --vsn was executed.'),dict(item='Runnable first-only argv',reason='Old candidate was frozen without executing ARMASM/help/version; syntax/accepted defaults of --cpu/--apcs/-I/-o not established by ARMCC C-help. Do not infer or guess.'),dict(item='Future output path',reason='Old candidate -o points into sealed V6; never run it. Later first-ASM scope must choose fresh outputs.'),dict(item='Actual assembled conditional branch/metadata/relocations',reason='Source and explicit symbol set predict MICROLIB_OFF ELSE only; assembler has never run.'),dict(item='Precise FP tags10/27/28 and align tags24/25 acceptance values',reason='Previously pinned excerpts cover public omission/inheritance/nodefaults/types/denorm, not full definitions of these tags. No fabricated 0=compatible nor C exact1 gate.'),dict(item='Actual library/startup/memory/IRQ resolution',reason='No object/link/symbol inspection; __main/two-region library and strong ISR replacement unresolved here.')]
  evidence=dict(source=source_before,source_lines=len(lines),integer_constants=constants,source_include_GET_INCBIN=includes,manual_source_review_only_no_full_assembler_parser=True,ISA_source_directives=[dict(line=64,text='PRESERVE8'),dict(line=65,text='THUMB')],stack_heap_AREA=dict(STACK_line48='NOINIT READWRITE ALIGN=3',HEAP_line59='NOINIT READWRITE ALIGN=3',each_alignment_bytes_declared=8,adequacy_measured=False),vector=dict(AREA_RESET_line69='DATA READONLY',exported=['__Vectors','__Vectors_End','__Vectors_Size'],word_declarations=len(vectors),reserved_zero_words=sum(v['value']=='0' for v in vectors),first_two=vectors[:2],last=vectors[-1],source_words_nominal_4B_count=len(vectors)*4,actual_section_bytes_address_and_relocations='UNKNOWN_NO_ASSEMBLY_OR_LINK'),Reset=dict(lines=[183,192],weak_export=True,instruction_sequence=[x for x in instructions if 188<=x['line']<=191],source_call_sequence='SystemInit via BLX then tail BX __main',callee_prototypes_and_actual_resolution='NOT_INSPECTED_SOURCE_IMPORTS_ONLY'),weak_exports_count=len(weak),weak_core_and_reset_sample=weak[:10],peripheral_weak_default_region=[238,406],default_B_forever_line404=True,strong_replacement_not_proven=True,imports=imports,stackheap_MICROLIB_conditional=dict(IF_DEF_line413=True,selected_policy='MICROLIB_OFF_SYMBOL_NOT_DEFINED',visible_ASM_predefines=[],Cdefines_not_auto_ASM=cads['VariousControls']['Define'],actual_branch_not_assembled=True,warning=':DEF: tests existence; defining __MICROLIB=0 is not the same as undefined.',expected_source_ELSE=dict(lines=[419,434],marker_import='__use_two_region_memory',export='__user_initial_stackheap',integer_return_regs=dict(R0='Heap_Mem',R1='Stack_Mem+Stack_Size',R2='Heap_Mem+Heap_Size',R3='Stack_Mem'),return_BX_LR_line430=True)),explicit_project_inputs=dict(useUlib=misc['useUlib'],Aads=aads,group_override_present=group['present'],old_literal_includes=row['literal_includes'],old_literal_defines=row['literal_defines'],old_literal_undefines=row['literal_undefines']))
  state.update(status='STATIC_SOURCE_PINNED_RUNNABLE_ARGV_UNKNOWN_NO_NATIVE',source_files_reviewed=1,source=source_before,source_review=evidence,proposed_first_only_runnable_argv=None,runnable_argv_status='UNKNOWN_DO_NOT_GUESS_DEFERRED_FLAGS',archival_unexecuted_candidate=dict(argv=row['argv'],cwd=row['cwd'],executed=False,contains_historical_readonly_output_path_DO_NOT_RUN=True,not_new_native_grant=True),unknowns=unknown,old_ASM_unstarted=True)
  checkpoint()  # Smallest source/argv/UNKNOWN ledger BEFORE proposal/report.
  addenda=rules['documents'][0];aaelf=rules['documents'][1]
  quotes=[x['quote'] for x in addenda['excerpts'] if 'effect of omitting' in x['quote'] or 'Tag_ABI_PCS_wchar_t' in x['quote'] or 'No defaults tag' in x['quote']]
  proposal=dict(status='ASSEMBLY_SPECIFIC_PROPOSAL_ONLY_NOT_READY_ACCEPTED_GATE',official_previous_pin=rec(rulespath),document_release=addenda['declared_release'],official_URLs=[addenda['official_rendered_URL'],aaelf['official_rendered_URL']],not_commit_pinned=not addenda['commit_pinned'],quoted_rules=quotes,proposal_rows=[dict(topic='Structural object',proposal='Later inspect ELF32LE ARM ET_REL, section/range/format, vector relocations and code/data distinction; actual assembly output and addresses UNKNOWN now. Keep bounded reader checks.'),dict(topic='ISA and stack declaration',proposal='Source THUMB/PRESERVE8 and target Cortex-M4 are declared evidence only, not emitted CPU/FP attributes or runtime SP adequacy.'),dict(topic='Public FILE/SECTION/SYMBOL',proposal='Honor exact public override/default/nodefaults rule. Missing whole carrier/unsupported tags/conflict/unknown are not silently normalized. Private ARM vendor bytes not public AEABI.'),dict(topic='wchar/enum',proposal='Actual public effective 0 with normative/default provenance is UNUSED (prohibited type), not sizeof0. Startup has no C enum/wchar argument setup; do not force C2/1 onto genuine UNUSED. Explicit nonzero/incompatible/unknown declarations need separate documented resolution.'),dict(topic='Floating point',proposal='Reviewed startup instructions only LDR/BLX/BX/B; calls set address registers, not FP arguments. This is call-site source evidence, not checked callee signatures. Do not hard-require C FP6/HardFP1/VFPargs1/denorm1or2 from unused startup. Exact unused/no-FP interface definitions of10/27/28 still UNKNOWN in pinned excerpts; no acceptance rule invented.'),dict(topic='Alignment',proposal='PRESERVE8 promises preservation and AREA ALIGN=3 declares8-byte alignment; emitted24/25 exact meanings/merge rules not in pinned subset, unresolved rather than copied from C.'),dict(topic='Future object assessment',proposal='Only a separate first-one-ASM grant and exact argv may create one object; then record actual attributes/imports/relocations, review assembly-specific applicability without changing C7/V10/C11 gates. No automatic link.')],C_reader_or_gate_changes=0,new_fixtures=0,ASM_object_exists=False,runtime_or_library_or_link_qualified=False)
  save('ABI_ASSESSMENT_PROPOSAL_01.json',proposal)
  after=[rec(Path(x['path'])) for x in refs];assert after==refs
  state.update(source_and_small_metadata_SHA_before_after_unchanged=True,source_refs_before=refs,source_refs_after=after);checkpoint()
  source_link='../MOD4_DEPLOYMENT_PORT_V1/derived/StandardRobotpp-balance1/MDK-ARM/startup_stm32f407xx.s'
  lines_out=['# V12：startup id0源与首ASM命令静态准备（零native）','',f'- 仅一个startup：[源码](<{source_link}>)438行/30149B，fresh SHA7baf21c802efd7aaeace20cfecef16b967d124fcbd5f038088be0eee6138b261与saved id0相同；8小source/metadata before-after SHA一致。', '- [最小ledger](<MIN_STATIC_LEDGER_01.json>)先于本报告/提案；未重读162 C物件或两库，不解析整project。',f'- [向量源码:69–178](<{source_link}#L69-L178>)：RESET DATA READONLY，__initial_sp/Reset_Handler开头，{len(vectors)}个DCD词/{sum(v["value"]=="0" for v in vectors)}个reserved0，3个__Vectors*导出；实际地址/重定位/强ISR覆盖仍UNKNOWN。',f'- [Reset:183–192](<{source_link}#L183-L192>)弱导出；LDR/BLX SystemInit，再LDR/BX __main，无返回路径；imports不是已解析链接。',f'- [默认异常/外设:194–406](<{source_link}#L194-L406>)合计{len(weak)}个weak导出（含Reset），核心异常各B.，外设标签同址落到B.；未证明最终ISR实际绑定。',f'- [Stack/Heap:46–65](<{source_link}#L46-L65>)各0x2000=8192B，NOINIT RW/ALIGN3，PRESERVE8+THUMB；这是声明，不是栈/heap充足或运行证明。',f'- [microLib:413–434](<{source_link}#L413-L434>)检测:DEF:__MICROLIB；target useUlib0、Aads定义/undef空，按选定OFF policy应ELSE，尚未assembly证实；定义为0不等于未定义。', '- ELSE导入__use_two_region_memory/导出__user_initial_stackheap；R0/R1/R2/R3分别heap base/stack top/heap limit/stack base，BX LR；C runtime库匹配和地址仍未链接。', '- 原source无INCLUDE/GET/INCBIN，不需新source/header；C的ARM_MATH_CM4/__FPU_USED等定义不自动流向ASM Aads。', '- Raw Aads interw1/thumb0/其余标志记录原样，group无override；source THUMB是已知，旧数值selector/CLI有效性不是已测事实。', '- 首次可运行argv=UNKNOWN/null：旧V6未执行候选保在ledger（含sealed旧-o，禁止照跑）；ARMASM_QUERY_DEFERRED确未query，ARMCC C-help不证明ARMASM --cpu/--apcs/-I/-o语法/默认。', '- 工具仅可命名C:/Keil_v5/ARM/ARMCC/bin/armasm.exe；版本/完整first-only命令须父另批明确，不运行help/version以偷补预算。', '- [ASM ABI提案](<ABI_ASSESSMENT_PROPOSAL_01.json>)不套C的全浮点/type gate，不改C7/V10/C11 readers/gates，无新fixture/新物件。', '- 已钉[Arm Addenda32](https://github.com/ARM-software/abi-aa/blob/main/addenda32/addenda32.rst)/[AAELF32](https://github.com/ARM-software/abi-aa/blob/main/aaelf32/aaelf32.rst)：公有省略与继承/nodefaults/冲突按原规范；18/26=0是规范UNUSED，不是width0或任意缺失都兼容。', '- 源只见LDR/BLX/BX/B、无FP参数设置；不等同callee原型已核。当前钉excerpts不足定义10/27/28、24/25精确0与合并规则，明确UNKNOWN，不凭未用FPU硬填1/0或宣布兼容。', '- 缺carrier/格式/UNKNOWN/冲突仍STOP；未来新ASM元数据评定规则须单独文档审查，不能静默放宽C gate。', '- 0编译/assembler/fromelf/probe/help/version/link/UV/hooks/flash/realIO/旧QA/FK/PHY/Git/agent/root-goal；source/原project/old records无改动。', '- 原162 C覆盖是三段compile-only记录；startup ASM id0仍未启动，实际固件/库/板BSP/机械映射/ISR/WCET资格仍未形成。', '- 全部PH10 cutoff外；静态准备结束即停，仅后续明确first-one-ASM grant可调用trusted ARMASM，不做链接准备或自动执行。']
  assert len(lines_out)<=30
  with (O/'REPORT.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines_out)+'\n')
  save('RECEIPT.json',dict(status='SEALED_V12_SINGLE_STARTUP_STATIC_PREP_RUNNABLE_ARGV_UNKNOWN_NO_NATIVE',source_and_small_metadata_before=refs,source_and_small_metadata_after=after,source_reviewed_files=1,source_pin_exact=True,raw_option_data_only_no_project_reparse=True,runnable_argv=None,unknowns=unknown,ASM_native_calls=0,all_other_native_calls=0,old_C_or_library_objects_read=0,new_object_parses_or_fixtures=0,PH10_cutoff_excluded=True,artifacts=[rec(O/n) for n in ['METHOD.md','MIN_STATIC_LEDGER_01.json','PREEXEC_STATIC_01.json','ABI_ASSESSMENT_PROPOSAL_01.json','REPORT.md','prepare_startup_static_once.py']],report_lines=len(lines_out)))
  print(json.dumps(dict(status=state['status'],source=source_before,vectors=len(vectors),weak_exports=len(weak),stack=8192,heap=8192,source_includes=0,runnable_argv=None,report=rec(O/'REPORT.md'),ledger=rec(marker),receipt=rec(O/'RECEIPT.json'),native_calls=0),ensure_ascii=False))
 except Exception:
  state.update(status='STOP_FIRST_STATIC_METADATA_ERROR_NO_RETRY',error=traceback.format_exc());checkpoint();print(json.dumps(state,ensure_ascii=False));raise SystemExit(1)
if __name__=='__main__':main()
