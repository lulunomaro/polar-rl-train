"""One six-NEW-fixture capacity study, then at most one existing TU40 scoped parse."""
from pathlib import Path
import ast,hashlib,importlib.util,json,traceback
O=Path(__file__).resolve().parent

def record(p,b=None):
 if b is None:b=p.read_bytes()
 return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(name,obj):
 with (O/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def stat(p):s=p.stat();return dict(bytes=s.st_size,mtime_ns=s.st_mtime_ns)
def main():
 minimum=O/'STUDY_RESULT_MIN_01.json'
 with minimum.open('x',encoding='utf-8') as f:f.write('{}\n')  # Exclusive one-study marker.
 state=dict(status='STARTED_BEFORE_PARSE',fixtures=[],fixture_pass_prefix=[],fixture_parse_calls=0,fixture_assertions=0,actual_object_parse_calls=0,actual_object_payload_reads=0,TU40_gate=None,ARM_native_calls=0,old_V7_fixture_or_main_parses=0,old_38_objects_read=0,suffix_C_or_ASM_compiles=0,PH10_cutoff_excluded=True,old_V8_history=dict(compiler_success39=39,scope_accepted38=38,capacity_stop_TU40=True,unstarted_C=122,unstarted_ASM=1))
 def checkpoint():
  with minimum.open('w',encoding='utf-8',newline='\n') as f:json.dump(state,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush()
 def check(ok,message):
  state['fixture_assertions']+=1
  if not ok:raise AssertionError(message)
 checkpoint();q=None;data=None;real_stat_before=None;current='PRE_PARSE_SOURCE_CHECKS';scope_result=None
 try:
  q=load(O/'QA_PREEXEC_01.json')
  for r in q['source_refs']:
   if record(Path(r['path']))!=r:raise RuntimeError('PRE_PARSE_SOURCE_PIN_DRIFT '+r['path'])
  rp=Path(q['reader']['path']);spec=importlib.util.spec_from_file_location('independent_scoped_reader_v10',rp);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
  check(reader.MAX_OBJECT==1048576 and reader.MAX_SECTIONS==4096,'new parent capacity constants')
  check((reader.MAX_VENDORS,reader.MAX_BLOCKS,reader.MAX_PAIRS,reader.MAX_IDS)==(32,128,2048,256),'other caps unchanged')
  for item in q['fixture_plan']:
   current=item['name'];blob_path=Path(item['blob']['path']);blob=blob_path.read_bytes();blob_before=record(blob_path,blob)
   if blob_before!=item['blob']:raise RuntimeError('FIXTURE_PIN_DRIFT '+current)
   row=dict(name=current,expected_positive=item['expected_positive'],input=blob_before,construction=item['construction'],parse_calls=0,passed=False)
   state['fixtures'].append(row);state['status']='FIXTURE_PARSE_ENTERED';row['parse_calls']=1;state['fixture_parse_calls']+=1;checkpoint()
   try:
    parsed=reader.inspect_elf(blob)
   except reader.ParseError as exc:
    row['actual_exception_type']=type(exc).__name__;row['actual_message']=str(exc)
    check(not item['expected_positive'],'positive boundary raised '+str(exc))
    check(type(exc) is reader.ParseError and str(exc)==item['expected_error'],'negative boundary wrong failure')
    if item['construction']['public_SYMBOL_scope_present']:row['conditional_SYMBOL_path_evidence']='Expected symbol-table bounds stop after explicit public SYMBOL scope'
   else:
    check(item['expected_positive'],'negative boundary unexpectedly parsed')
    check(parsed['section_count']==item['construction']['section_count'],'fixture section count')
    check(len(parsed['code_sections'])==1,'fixture executable section count')
    check(parsed['symbol_table_index_metadata_read']==item['construction']['public_SYMBOL_scope_present'],'conditional symbol path')
    if item['construction']['public_SYMBOL_scope_present']:
     check(parsed['attributes'].symbol_ids=={item['construction']['symbol_count_including_null']-1},'last boundary symbol validated')
    row['parsed_summary']=dict(section_count=parsed['section_count'],code_sections=len(parsed['code_sections']),public_SYMBOL_ids=sorted(parsed['attributes'].symbol_ids),symbol_index_metadata_read=parsed['symbol_table_index_metadata_read'],not_ABI_gate=True)
   row['passed']=True;row['same_owned_snapshot_after_SHA']=hashlib.sha256(blob).hexdigest();state['fixture_pass_prefix'].append(current);state['status']='FIXTURE_PASSED';checkpoint()
  check(len(state['fixture_pass_prefix'])==6 and state['fixture_parse_calls']==6,'six fixtures exactly once')
  # Extract ONLY the unchanged trusted gate definition. No executor module/import/native code.
  gp=Path(q['gate_definition_source']['path']);gbytes=gp.read_bytes()
  if record(gp,gbytes)!=q['gate_definition_source']:raise RuntimeError('PURE_GATE_SOURCE_DRIFT')
  nodes=[n for n in ast.parse(gbytes.decode('utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='gate']
  if len(nodes)!=1 or hashlib.sha256(ast.dump(nodes[0]).encode()).hexdigest()!=q['gate_AST_SHA']:raise RuntimeError('PURE_GATE_AST_DRIFT')
  namespace={};exec(compile(ast.Module(body=nodes,type_ignores=[]),'sealed_V8_gate_definition_only','exec'),namespace)
  current='ACTUAL_TU40';path=Path(q['actual_object_pin']['path']);real_stat_before=stat(path);data=path.read_bytes();state['actual_object_payload_reads']=1;state['actual_object_input']=record(path,data)
  if state['actual_object_input']!=q['actual_object_pin']:raise RuntimeError('TU40_PRODUCER_PIN_DRIFT')
  state['status']='TU40_NEW_SCOPED_PARSE_ENTERED';state['actual_object_parse_calls']=1;checkpoint()
  scope_result=namespace['gate'](data,reader,q['expected_non_type_gate_unchanged'])  # ONE inspect_elf call inside exact old gate.
  state['TU40_gate']=scope_result['pass_gate'];meta=scope_result['metadata'];types=scope_result['type_checks']
  hist={}
  for x in types:
   key='tag%s/%s/%s'%(x['tag'],x['effective']['classification'],x['effective']['value']);hist[key]=hist.get(key,0)+1
  state['TU40_summary']=dict(section_count=meta['section_count'],code_sections=len(meta['code_sections']),public_symbol_ids=meta['public_symbol_ids'],symbol_index_metadata_read=meta['symbol_table_index_metadata_read'],public_blocks=len(meta['raw_public_blocks']),type_checks=len(types),non_type_checks=len(scope_result['non_type_checks']),unknown_type_cells=sum(x['effective']['classification']=='UNKNOWN' for x in types),failed_type_cells=sum(not x['pass_gate'] for x in types),failed_non_type_checks=sum(not x['pass_gate'] for x in scope_result['non_type_checks']),type_histogram=hist)
  state['status']='STATIC_STUDY_PASS_TU40_NEW_GATE_PASS_NOT_COMPILE_CONTINUATION' if scope_result['pass_gate'] else 'STOP_TU40_SEMANTIC_GATE_FAILED_NO_RETRY'
  checkpoint()  # Minimum numeric outcome BEFORE full metadata/report.
  save('TU40_SCOPE_RESULT_01.json',scope_result)
 except Exception:
  state['status']='STOP_FIRST_STUDY_ERROR_NO_RETRY';state['failed_at']=current;state['error']=traceback.format_exc();checkpoint()
 finally:
  if q is not None:
   state['source_refs_after']=[record(Path(r['path'])) for r in q['source_refs']]
   state['source_SHA_before_after_unchanged']=state['source_refs_after']==q['source_refs']
   if not state['source_SHA_before_after_unchanged']:state['status']='STOP_SOURCE_AFTER_SHA_DRIFT_NO_RETRY'
  if data is not None:
   state['actual_object_same_owned_snapshot_after_SHA']=hashlib.sha256(data).hexdigest();state['actual_object_stat_before']=real_stat_before;state['actual_object_stat_after']=stat(Path(q['actual_object_pin']['path']));state['actual_object_stat_stable']=real_stat_before==state['actual_object_stat_after'];state['actual_object_independent_post_file_SHA']=None
   if not state['actual_object_stat_stable']:state['status']='STOP_OBJECT_POST_STAT_DRIFT_NO_RETRY'
  checkpoint()
 save('FIXTURE_RESULTS_01.json',dict(status='PASS' if len(state['fixture_pass_prefix'])==6 else 'PARTIAL_FIRST_STOP',parse_calls=state['fixture_parse_calls'],assertions=state['fixture_assertions'],rows=state['fixtures'],not_old_V7_QA_replay=True,no_ARM_execution=True))
 success=state['status']=='STATIC_STUDY_PASS_TU40_NEW_GATE_PASS_NOT_COMPILE_CONTINUATION'
 summary=state.get('TU40_summary',{})
 lines=['# V10：新有界容量版本静态study（非ABI放宽/非后缀编译）','',f'- 状态：{state["status"]}。最小数字先保存在[结果](<STUDY_RESULT_MIN_01.json>)；任何首错保prefix且无修订重跑。','- 父另选HOST结构预算16×：MAX_OBJECT=1048576B、MAX_SECTIONS=4096、条件SYMTAB entries=16384；不是V9仅需304的最小提案推断。','- [独立派生](<DERIVATION_01.json>)仅3个literal；字节inverse与AST inverse精确还原sealed V7，其他caps与全部范围/语义检查不变。',f'- 六个NEW fixture每cap正/负边界、完整backing，实际{state["fixture_parse_calls"]} parse、已过{len(state["fixture_pass_prefix"])}/6、{state["fixture_assertions"]} assertions；public SYMBOL路径显式测试16384/16385，未重放旧19/64QA。',f'- 只有fixture全部通过后读TU40：open/read={state["actual_object_payload_reads"]}，新完整parse={state["actual_object_parse_calls"]}；58720B producer pin及同snapshot post SHA，file侧只核size/mtime。',f'- TU40新gate={state["TU40_gate"]}；summary={summary}。完整[scope与provenance](<TU40_SCOPE_RESULT_01.json>)仅在实际返回后保存。','- Non-type gate仍ELF1/1/1/40、FILE CPU13/profile77/Thumb2/FP6/HardFP1/VFPargs1/denorm1或2；纯gate定义AST与V8原件一致，未import executor。','- 每EXEC/SYMBOL 18=2或规范UNUSED0，26=1或规范UNUSED0；继承/override/nodefaults/冲突/UNKNOWN STOP全部原样，不把0解释为width0或强填2/1。','- 旧V8仍39成功编译/38scope认可/TU40容量停止；旧V6 gate历史不变。新TU40静态认可若PASS也不是旧账重写或新增C编译。','- 122C+ASM1仍未启动；ARM/ASM/fromelf/probe/link/version/UV/hooks/IO/flash/oldQA/FK/PHY/Git/agent/root-goal均0，38accepted/main读取0。',f'- source小输入before-after SHA一致={state.get("source_SHA_before_after_unchanged")}; reader/resource limits仅HOST预算，不是库/固件/MCU/FPSCR/gradual/WCET或实机资格。','- 全部PH10 cutoff外；父actual read后另批C-only scope才可继续122C，ASM仍排除。']
 if not (O/'TU40_SCOPE_RESULT_01.json').exists():lines[7]='- TU40未获得可返回的完整scope JSON；见最小结果首错/prefix，ABI不作新认可。'
 with (O/'REPORT.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines)+'\n')
 assert len(lines)<=30
 artifacts=['QA_PREEXEC_01.json','DERIVATION_01.json','CAPACITY_ONLY.patch','scoped_attrs_v10.py','new_boundary_fixtures.py','prepare_study_once.py','run_study_once.py','STUDY_RESULT_MIN_01.json','FIXTURE_RESULTS_01.json','REPORT.md']
 if (O/'TU40_SCOPE_RESULT_01.json').exists():artifacts.append('TU40_SCOPE_RESULT_01.json')
 save('RECEIPT.json',dict(status='SEALED_STATIC_V10_STUDY_PASS_NO_NATIVE_CONTINUATION' if success else 'PARTIAL_FIRST_STOP_STATIC_STUDY_NOT_AUTO_RETRIED',success=success,old_V8_history_unchanged=state['old_V8_history'],fixtures_parse_calls=state['fixture_parse_calls'],fixture_assertions=state['fixture_assertions'],actual_object_new_parse_calls=state['actual_object_parse_calls'],actual_TU40_gate=state['TU40_gate'],source_refs_before=q['source_refs'] if q else None,source_refs_after=state.get('source_refs_after'),source_pins_unchanged=state.get('source_SHA_before_after_unchanged'),actual_object=state.get('actual_object_input'),post_object_hash_evidence='Same owned snapshot rehash plus size/mtime; not independent second payload file hash.',artifacts=[record(O/n) for n in artifacts],report_lines=len(lines),ARM_native_calls=0,old_38_objects_or_main_read=0,suffix_compile_calls=0,library_firmware_runtime_WCET_qualified=False,PH10_cutoff_excluded=True))
 print(json.dumps(dict(status=state['status'],fixture_parse_calls=state['fixture_parse_calls'],fixtures_pass=len(state['fixture_pass_prefix']),assertions=state['fixture_assertions'],TU40=state.get('TU40_summary'),gate=state['TU40_gate'],report=record(O/'REPORT.md'),minimum=record(minimum),receipt=record(O/'RECEIPT.json')),ensure_ascii=False))
 if not success:raise SystemExit(1)
if __name__=='__main__':main()
