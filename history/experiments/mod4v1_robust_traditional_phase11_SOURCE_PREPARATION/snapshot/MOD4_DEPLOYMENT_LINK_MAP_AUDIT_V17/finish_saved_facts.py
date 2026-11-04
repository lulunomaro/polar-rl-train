"""Derive assessment and concise prose only from our persisted selected facts; never reopen V16 map/binary."""
from pathlib import Path
import datetime,hashlib,json,re
D=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def new(n,v):
 with(D/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 assert not(D/'RECEIPT.json').exists(),'No repeated closure'
 x=json.loads((D/'MINIMUM_MAP_FACTS.json').read_text(encoding='utf-8'));counts=json.loads((D/'READ_COUNTS.json').read_text(encoding='utf-8'));b=x['original_saved_metadata']['IMAGE_BASIC_OBSERVATIONS.json']
 totals={}
 for r in x['size_totals']:
  t=r['text'];m=re.search(r'Total\s+(RO|RW|ROM)\s+Size.*?\)\s+(\d+)',t)
  if m:totals[m.group(1)]=int(m.group(2))
 grand=next(z for z in x['size_totals']if 'Grand Totals'in z['text']);numbers=[int(t)for t in re.match(r'^\s*((?:\d+\s+){6})',grand['text']).group(1).split()]
 component=dict(zip(['Code','inc_data_already_in_Code_NOT_added_again','RO_Data','RW_Data_uncompressed','ZI_Data','Debug'],numbers))
 region={}
 for r in x['regions']:
  m=re.search(r'(Load|Execution) Region (\w+) \(Base: (0x[\da-fA-F]+), Size: (0x[\da-fA-F]+), Max: (0x[\da-fA-F]+)',r['text'])
  if m:
   z=dict(kind=m[1],base=int(m[3],16),size=int(m[4],16),max=int(m[5],16),source_line=r['line'],map_text=r['text']);q=re.search(r'COMPRESSED\[(0x[\da-fA-F]+)\]',r['text']);z['compressed_load_bytes_if_shown']=int(q[1],16)if q else None;region[m[2]]=z
 assert totals==dict(RO=118140,RW=66352,ROM=118512)and component['Code']+component['RO_Data']==totals['RO']and component['RW_Data_uncompressed']+component['ZI_Data']==totals['RW']
 assert region['LR_IROM1']['size']==119464 and region['LR_IROM1']['compressed_load_bytes_if_shown']==totals['ROM']and region['ER_IROM1']['size']==totals['RO']and region['RW_IRAM1']['size']==totals['RW']
 defs=x['definitions'];one=lambda k:defs[k][0]
 assert one('__Vectors')['map_value']==b['first_flash_vector_words']['address']==0x08000000 and one('__initial_sp')['map_value']==b['first_flash_vector_words']['initial_SP']==0x20010330 and one('Reset_Handler')['map_value']==b['entry']==b['first_flash_vector_words']['reset_word']==0x080003dd
 groups={}
 for z in x['library_member_rows']:
  if z['section']=='memory':groups.setdefault(z['library'],{}).setdefault(z['member'],dict(first_memory_map_line=z['line'],map_text=z['text']))
 lib_totals={}
 for z in x['component_size_rows']:
  m=re.match(r'^\s*((?:\d+\s+){6})(\S+\.(?:lib|l))\s*$',z['text'])
  if m:lib_totals[m[2]]=dict(zip(['Code','inc_data_in_Code','RO_Data','RW_Data','ZI_Data','Debug'],[int(t)for t in m[1].split()]))
 assert set(groups)==set(lib_totals)=={'AHRS.lib','arm_cortexM4lf_math.lib','c_w.l','g_wm.l','m_wm.l'}
 fullpath=[z for z in x['library_path_and_heading_rows']if re.search(r'[A-Za-z]:[\\/]',z['text'])]
 semis=['__I$use$semihosting','__use_no_semihosting_swi','__semihosting_library_function']
 assessment=dict(status='SAVED_MAP_LAYOUT_SYMBOL_AND_SELECTED_MEMBER_ASSESSMENT_NOT_RUNTIME_OR_FULL_ABI',image_producer_only=b,memory_totals=totals,components=component,regions=region,compression=dict(RW_initializer_uncompressed_bytes=component['RW_Data_uncompressed'],RW_initializer_stored_bytes=region['RW_IRAM1']['compressed_load_bytes_if_shown'],LR_uncompressed_bytes=region['LR_IROM1']['size'],LR_stored_bytes=totals['ROM'],RAM_ZI_not_stored_as_ROM=component['ZI_Data'],RAM_allocation_not_reduced_by_initializer_compression=True),capacity_static_only=dict(Flash_config_bytes=0x100000,Flash_unused_arithmetic_bytes=0x100000-totals['ROM'],SRAM_config_bytes=0x20000,SRAM_unused_arithmetic_bytes=0x20000-totals['RW'],not_dynamic_stack_heap_or_board_map_guarantee=True),vector_SP_Reset_match_saved_parent_basic=True,definitions=defs,definitions_not_new_ELF_symbol_binding_or_vector_relocation_validation=True,library_members_observed_in_allocated_memory_map=groups,library_size_totals=lib_totals,library_full_directory_paths_emitted_in_captured_evidence=fullpath,library_exact_directories_UNKNOWN_if_absent=True,user_libraries_full_input_paths_only_prior_V15_explicit_binding_not_map_emission=True,all_library_members_ABI_or_all163_code_retained=False,semihost=dict(definitions={k:defs[k]for k in semis},special_references={k:x['selected_reference_excerpts'][k]for k in semis},sys_object_references={k:x['selected_reference_excerpts'][k]for k in('sys_command','sys_exit','sys_wrch')},allocated_c_runtime_sys_members=[k for k in groups['c_w.l']if k.startswith('sys_')or k in('use_no_semi.o','indicate_semi.o')],sys_command_reference_is_not_allocated_runtime_reachability=True,reachability_BKPT_retarget_or_standalone_IO='UNKNOWN_NO_DISASSEMBLY_OR_EXECUTION'),own_text_read_counts=x['counts'],PH11pending=True)
 new('ASSESSMENT.json',assessment)
 report=[
 '# V17：一次saved-map语义审查；不是新image/ABI/runtime验证',
 '- Catalog无相应BSP技能，用保存JSON/text分析。先落[MINIMUM_MAP_FACTS](<MINIMUM_MAP_FACTS.json>)再作此报告；本worker stdout打开1次/9989lines、stderr1次；父wrapper/grep先前读过，非全局首次读取。0 image/obj/lib原binary读/hash、native、模型/PHY/QA/Git/agent/Goal。',
 '- V16已存结果rc0/0.2097813s、AXF629048B，producerSHA a70772a2c56bf38c144817b86a27d2ca01d32aa288c17bdcb9b592987ff4f601，165input实际SHA匹配是父原link证据；此处未重核payload。空stderr/无Warning或Error pattern不等于无运行风险。',
 '- Map Code110680B（其中inc.data6886已包含，勿再加）、RO7460、未压缩RW1324、ZI65028；RO合118140/0x1cd7c，实际RAM合66352/0x10330。AXF文件629048B与ELF segment aggregate memory184492均不能当RAM用量。',
 '- LR_IROM1 base0x08000000：未压缩load119464/0x1d2a8，COMPRESSED118512/0x1cef0；RW initializer由1324存成372/0x174，RAM仍66352，不因压缩省RAM；ZI65028不作为ROM存储。',
 '- ER_IROM1 118140 of配置1MiB；RW_IRAM1 base0x20000000、66352 of配置128KiB，纯算术余量Flash930064/SRAM64720B，不保证动态heap/stack或真实板map；未新增CCMregion，非搬数据/改配置。',
 '- Map __Vectors0x08000000、end0x08000188/size392、__initial_sp0x20010330(STACK)、Reset_Handler0x080003dd(.text)均源000_startup_stm32f407xx.s.o；与父已存首vector SP/Reset/headerentry相符。这里只核map标签/地址，未重读vector bytes/relocation或验证实际复位执行。',
 '- SVC_Handler0x0800031d(28B)、PendSV_Handler0x08000379(88B)来自059_port.c.o(.emb_text)；SysTick_Handler0x0800f6bd(14B)来自018_stm32f4xx_it.c.o；SystemInit0x0800f781(64B)来自049_system_stm32f4xx.c.o。不是新ELF bind/ISR优先级/RTOS运行证明。',
 '- Map实际选AHRS.lib(ahrs.o)；DSP的9个member含common_tables、sin/cos_f32及mat_init/add/sub/mult/trans/inverse_f32。RT实际库名c_w.l/g_wm.l/m_wm.l，含CRT/scatter/ZI/heap/printf、软double/FP与math等；完整成员与每项memory-map行见[ASSESSMENT](<ASSESSMENT.json>)，不是全archive成员ABI覆盖或所有163TU代码保留。',
 '- 本次已存分配/库名证据中没有完整库目录，库basename不冒完整目录：两显式AHRS/DSP输入全路径仅有既有V15绑定；RT准确目录仍UNKNOWN，不猜安装默认目录。库size表AHRS Code2718/RO12/RW16、DSP Code2692/RO2052；其余RT细项已存。',
 '- Map semihost定义逐字：'+'; '.join(y['text'].strip()for k in semis for y in defs[k])+'。保留其map类型/来源，不把Number或ABSOLUTE标记冒充可执行函数；cross-ref见sys_command/sys_exit/sys_wrch Special refs，allocated成员列表有sys_exit/sys_wrch/use_no_semi/indicate_semi。',
 '- sys_command special-reference/文件名出现不证明已分配可达指令；semihost-name存在不证明执行BKPT，no_semihosting_swi之名也不证明standalone/retarget IO。真实可达/异常退出/printf行为UNKNOWN，无反汇编或调用实验。',
 '- 只是旧BSP Stage1 UNBOUND映像；旧机械LQR/MF9025接口与新MOD4绑定未解决，无C3＋新startup集成/sole-send。CRT/SystemInit/RTOS一致性、FPSCR/denorm、实时stackheap、pins/CAN/DM3519协议、WCET/HIL/flash与真实站立均未资格化。',
 '- PH11pending，PH10已closed。此任务只交保存文本assessment/receipt，不补link/fromelf/parser/实验/封包/刷写或源码修改，交付后停止。'
 ]
 assert len(report)+1<=25
 for t in report:
  for p in re.findall(r'\]\(<([^>]+)>\)',t):assert(D/p).exists()
 with(D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(report)+'\n')
 artifacts=['MINIMUM_MAP_FACTS.json','READ_COUNTS.json','MAP_READ_INTENT.json','ASSESSMENT.json','audit_saved_map_once.py','finish_saved_facts.py','REPORT.md']
 receipt=dict(status='COMPLETE_V17_ONCE_OWN_SAVED_MAP_ASSESSMENT_ONLY_NOT_BINARY_RUNTIME_OR_HARDWARE_QUALIFIED',created_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),counts=x['counts'],read_counts=counts,original_saved_stdout_not_reopened_after_singlepass=True,report_plus_receipt_lines=len(report)+1,source_parent_scope_SHA=sha(D/'PARENT_SCOPE.json'),artifacts=[dict(path=str(D/p),bytes=(D/p).stat().st_size,SHA=sha(D/p))for p in artifacts],link_execution_by_this_worker=False,V5_and_parallel_C6_candidate_files_touched=False,old_source_binary_score_gate_or_PH10_modified=False,all_dynamics_runtime_ABI_qualification_remain_unproved=True,PH11pending=True)
 with(D/'RECEIPT.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(receipt,f,ensure_ascii=False,allow_nan=False);f.write('\n')
 print(json.dumps(dict(status=receipt['status'],report_lines=len(report),combined_lines=len(report)+1,counts=x['counts'],sizes=totals,member_counts={k:len(v)for k,v in groups.items()},library_directories_UNKNOWN=True,report_SHA=sha(D/'REPORT.md'),receipt_SHA=sha(D/'RECEIPT.json'),assessment_SHA=sha(D/'ASSESSMENT.json')),ensure_ascii=False))
if __name__=='__main__':main()
