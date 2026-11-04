"""Saved-only V11 evidence closure. No object reader/compiler/native/import executor."""
from pathlib import Path
import ast,copy,hashlib,json,traceback
O=Path(__file__).resolve().parent;R=O.parent

def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(n,v):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def exact(x):
 a=rec(Path(x['path']));assert a==x,('PIN_DRIFT',x['path']);return a

def main():
 marker=O/'CLOSE_MIN_01.json'
 with marker.open('x',encoding='utf-8') as f:f.write('{}\n')
 state=dict(status='SAVED_ONLY_CLOSE_ENTERED_NO_NATIVE_OR_READER',native_calls=0,object_metadata_reader_calls=0,old_object_reads=0)
 def checkpoint():
  with marker.open('w',encoding='utf-8',newline='\n') as f:json.dump(state,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush()
 checkpoint()
 try:
  pre=load(O/'PREEXEC_V11_01.json');plan=load(O/'LITERAL_ARGV_V11_01.json');out=load(O/'COMPILE_RESULT_V11_01.json');der=load(O/'EXECUTOR_DERIVATION_01.json');delta=load(O/'ARGV_DELTA_V11_01.json')
  for k in ('plan','delta','executor','preparer','sealed_reader'):exact(pre[k])
  for x in plan['source_refs']+plan['existing_raw_overlay_header_pins']+plan['selected_C_fresh_pins']:exact(x)
  assert out['end_small_refs_and_two_headers_unchanged'] is True and out['each_C_at_most_once'] is True
  assert plan['execution_order']==list(range(41,163)) and len(plan['translation_units'])==122
  order=plan['execution_order'];by={x['id']:x for x in plan['translation_units']}
  old8=load(R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V8'/'LITERAL_ARGV_V8_01.json');hist8=load(R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V8'/'COMPILE_RESULT_V8_01.json');old6=load(R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V6'/'LITERAL_ARGV_V6_01.json')
  b8={x['id']:x for x in old8['translation_units']};b6={x['id']:x for x in old6['translation_units']}
  assert hist8['unstarted_C_ids']==order and hist8['C_compile_attempts']==39 and hist8['scope_accepted_count']==38
  assert out['original_V6_record']==dict(compiler_success=1,post_ABI_accepted_prefix=0,pass_gate=False,unchanged=True)
  for i in order:
   row=copy.deepcopy(by[i]);k=row['argv'].index('-o')+1
   for field in ('output_object','stdout','stderr'):row[field]=b8[i][field]
   row['argv'][k]=b8[i]['argv'][k];assert row==b8[i]
   row.pop('fresh_source_pin')
   for field in ('output_object','stdout','stderr'):row[field]=b6[i][field]
   row['argv'][k]=b6[i]['argv'][k];assert row==b6[i]
  assert delta['all122_output_only_inverse_to_V8_and_V6'] is True
  oldbytes=Path(der['old']['path']).read_bytes();newbytes=Path(der['new']['path']).read_bytes();exact(der['old']);exact(der['new']);inverse=newbytes
  for change in reversed(der['substitutions']):
   assert inverse.count(change['new'].encode())==change['occurrences'];inverse=inverse.replace(change['new'].encode(),change['old'].encode())
  assert inverse==oldbytes and ast.dump(ast.parse(inverse.decode()))==ast.dump(ast.parse(oldbytes.decode()))
  fn=lambda b:{n.name:ast.dump(n) for n in ast.parse(b.decode()).body if isinstance(n,ast.FunctionDef)}
  for name in ('gate','capacity_reason'):assert fn(oldbytes)[name]==fn(newbytes)[name]
  assert out['status']=='ALL122_NEW_C_OBJECTS_SCOPE_ACCEPTED_NOT_LINKED_ASM_UNSTARTED'
  assert out['attempted_TU_ids']==order and out['reader_call_count']==122 and out['C_compile_attempts']==122
  assert out['new_compile_success_with_nonempty_object_count']==122 and out['scope_accepted_count']==122 and out['failed_TU'] is None
  assert out['unstarted_C_ids']==[] and out['ASM_unstarted_ids']==[0] and out['ASM_compile_count']==0 and out['fromelf_probe_version_link_UV_flash']==0
  assert len(out['TU_results'])==122 and len(out['native_invocations'])==122
  assert [x['id'] for x in out['scope_accepted_prefix']]==order and [x['id'] for x in out['native_invocations']]==order
  prefix={x['id']:x for x in out['scope_accepted_prefix']};rows=[];nonchecks=0;types=0;code_count=0;symbol_scope_count=0;symbol_table_reads=0;histogram={};maxobj=(0,None);maxsec=(0,None);emptylogs=0;emptysources=0
  for item in out['TU_results']:
   i=item['id'];row=by[i]
   assert item['exit']==0 and item['object_nonempty'] is True and item['reader_called'] is True and item['scope_pass'] is True
   assert item['argv']==row['argv'] and item['cwd']==row['cwd']
   assert exact(item['source_before'])==row['fresh_source_pin'] and exact(item['source_after'])==item['source_before']
   assert item['object']['path']==row['output_object'] and exact(item['object'])==prefix[i]['object']
   assert exact(item['scope_record'])==prefix[i]['scope_record']
   for k in ('stdout','stderr'):
    assert item[k]['path']==row[k];exact(item[k]);emptylogs+=item[k]['bytes']==0
   emptysources+=item['source_before']['bytes']==0
   scope=load(Path(item['scope_record']['path']))
   assert scope['pass_gate'] is True and all(x['pass_gate'] for x in scope['non_type_checks']+scope['type_checks'])
   assert len(scope['non_type_checks'])==11
   meta=scope['metadata'];nonchecks+=len(scope['non_type_checks']);types+=len(scope['type_checks']);code_count+=len(meta['code_sections']);symbol_scope_count+=len(meta['public_symbol_ids']);symbol_table_reads+=meta['symbol_table_index_metadata_read']
   for x in scope['type_checks']:
    c=x['effective'];assert c['classification']!='UNKNOWN'
    key='tag%s/%s/%s'%(x['tag'],c['classification'],c['value']);histogram[key]=histogram.get(key,0)+1
   if item['object']['bytes']>maxobj[0]:maxobj=(item['object']['bytes'],i)
   if meta['section_count']>maxsec[0]:maxsec=(meta['section_count'],i)
   rows.append(dict(id=i,name=item['name'],source=item['source_after'],object=item['object'],scope=item['scope_record'],object_bytes=item['object']['bytes'],sections=meta['section_count'],code_sections=len(meta['code_sections']),actual_public_SYMBOLs=meta['public_symbol_ids'],type_checks=len(scope['type_checks']),scope_gate=True))
  ledger=O/'EXECUTION_LEDGER_V11_01.jsonl';events=[json.loads(s) for s in ledger.read_text(encoding='utf-8').splitlines()]
  assert len(events)==489
  for label in ('NATIVE_ATTEMPT','NATIVE_RETURN','SINGLE_SEALED_V10_READER_CALL','NEW_C_SCOPE_ACCEPTED'):
   assert [e['id'] for e in events if e['event']==label]==order
  assert all(n['kind']=='REAL_C_TU_COMPILE_ONLY' and n['exit']==0 for n in out['native_invocations'])
  maxobj=dict(bytes=maxobj[0],id=maxobj[1]);maxsec=dict(sections=maxsec[0],id=maxsec[1])
  facts=dict(status='SAVED_ONLY_V11_ALL122_C_RECORDS_VERIFIED_NOT_FULL_TARGET',C_attempts=122,C_compiler_success=122,nonempty_objects=122,new_scope_accepted=122,new_reader_calls=122,C_unstarted=0,ASM_unstarted=1,ASM_calls=0,other_native_calls=0,failed_TU=None,new_scope_non_type_checks=nonchecks,new_scope_type_checks=types,new_EXEC_sections=code_count,new_actual_public_SYMBOLs=symbol_scope_count,new_symbol_table_index_reads=symbol_table_reads,type_histogram=histogram,max_new_object=maxobj,max_new_section_count=maxsec,empty_compiler_logs=emptylogs,compiler_logs=244,zero_byte_C_sources=emptysources,ledger_events=len(events),distinct_fresh_C_source_paths=len({x['source'].casefold() for x in plan['translation_units']}),all_source_and_header_and_old_ref_SHA_stable=True,all122_output_only_inverse_to_V8_and_V6=True,pure_gate_and_capacity_reason_AST_unchanged=True,executor_byte_AST_inverse_exact=True,inherited_assessments=dict(V6_main_compiler1_original_gateFalse_unchanged=True,V7_main_static_type_scope_separate=True,V8_compiler39_scope38_capacity_TU40_unchanged=True,V10_TU40_static_new_gateTrue_separate=True),unique_C_source_compile_coverage_metadata_only=dict(main_V6=1,prior_V8=39,new_V11=122,sum_unique_original_C_IDs=162,not_one_wave_or_full_target=True),new_C_rows=rows,ARM_link_firmware_runtime_library_FPSCR_WCET_qualified=False,PH10_cutoff_excluded=True)
  save('FACTS_V11_01.json',facts)
  state.update(status='SAVED_EVIDENCE_CLOSURE_VERIFIED_NO_NEW_NATIVE_OR_READER',C_attempts=122,new_C_success=122,new_scope_accepted=122,C_unstarted=0,ASM_unstarted=1,FACTS=rec(O/'FACTS_V11_01.json'));checkpoint()
  lines=['# V11：实际余下122 C compile-only波次已封存（非完整target/link）','', '- Catalog无robotics匹配；file/Python stdlib+既有trusted ARMCC5u6，未迁移工具链。显式AC5u6/O1-time诊断variant，不冒充旧u4或UV数值selector重现。', '- Native前锁全部122 literal argv、2059405B选中C fresh pins、两raw overlays及scope/executor/sealed V10 reader；每项source/CWD/includes/macros/CPU/警告/RTE不变，只换-o/output/log路径，双向inverse精确。', '- Executor仅plan/output/scope/122边界/reader版本窄派生；byte+AST inverse及pure gate/capacity_reason AST一致。历史capacity label未被当作新阈值或放宽gate。', '- 唯一真实串行波次：122次C调用、122 exit0且非空objects、122次新reader、122 scope-gate通过；首停条件未触发。每original TU一次，未静默修/重编/扩cap/补header。',f'- 实际source路径数={facts["distinct_fresh_C_source_paths"]}；新EXEC sections={code_count}；type checks={types}、原non-type checks={nonchecks}均通过。type histogram={histogram}。',f'- 实际public SYMBOL属性总数={symbol_scope_count}、conditional index-table读取物件数={symbol_table_reads}；如为0，不能冒充symbol-entry路径实物覆盖（V10另有新boundary fixture）。',f'- 新物件最大={maxobj}；新section-count最大={maxsec}；244份compiler logs中empty={emptylogs}。完整逐TU source/object/gate SHA见[事实](<FACTS_V11_01.json>)。', '- Ledger489行：每TU NATIVE_ATTEMPT/RETURN/READER/ACCEPTED，最小COMPILE_RESULT在每阶段先写；所有新物件/源/log/scope保存并只读hash核对，未再次parse object。', '- 本轮无failed TU、C未启动0；ASM id0仍未启动。main1/TU2..40无重编、旧38accepted/main/TU40 objects无重parse。', '- 旧V6 main编译1而原FILE-gate False；旧V8编译39/当时gate38/容量停止；V7 main与V10 TU40静态评定分开保留，不重写旧账。', '- 三段唯一C-source compile记录覆盖原162 C（1+39+122），不是一次完整build，也不是一套库/链接/启动/实机可用资格。', '- 所有122输出与V8/V6参数逆变换、source pre/post、两overlay及小refs SHA通过；sealed V10 reader只读SHA0a6437d1e5e3c56961547e3c3758a651a4c9e8ad36aeba7b1f1e71b282f522d0。', '- 0 ASM/fromelf/probe/version/UV/hooks/link/flash/realIO/oldQA/FK/PHY/Git/agent/root-goal动作；唯一job已完成collected，无自动下一波。', '- 余startup ASM、两库整体属性/ABI、scatter/库选择/链接ROM-RAM、固件运行与FPSCR/gradual/ISR/WCET以及物理MOD4绑定仍待独立审批验证。', '- 全部V11在PH10 cutoff外。即使122全pass也停，不运行ASM/link。', '- [最小实际结果](<COMPILE_RESULT_V11_01.json>) · [冻结PREEXEC](<PREEXEC_V11_01.json>) · [参数delta](<ARGV_DELTA_V11_01.json>) · [executor逆变换](<EXECUTOR_DERIVATION_01.json>) · [收据](<RECEIPT_V11_FINAL.json>)。']
  assert len(lines)<=35
  with (O/'REPORT_V11.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines)+'\n')
  refs=plan['source_refs']+plan['existing_raw_overlay_header_pins']
  save('RECEIPT_V11_FINAL.json',dict(status='SEALED_V11_122_C_COMPILE_ONLY_SUCCESS_WITH_SEPARATE_PRIOR_ASSESSMENTS_ASM_LINK_UNSTARTED',source_refs_after=[exact(x) for x in refs],C_attempts=122,C_success=122,new_gate_accepted=122,new_reader_calls=122,ASM_unstarted=1,ASM_calls=0,other_native_calls=0,saved_only_close_object_reader_calls=0,old_objects_read=0,old_history_unchanged=True,not_full_target_library_firmware_runtime_WCET=True,PH10_cutoff_excluded=True,artifacts=[rec(O/n) for n in ['REPORT_V11.md','FACTS_V11_01.json','COMPILE_RESULT_V11_01.json','EXECUTION_LEDGER_V11_01.jsonl','PREEXEC_V11_01.json','LITERAL_ARGV_V11_01.json','ARGV_DELTA_V11_01.json','EXECUTOR_DERIVATION_01.json','EXECUTOR_ONLY.patch','compile_v11_once.py','prepare_v11_once.py','close_v11_saved_once.py','prepare_01.log','compile_01.log']],report_lines=len(lines)))
  print(json.dumps(dict(status='SEALED_V11_ALL122_C_ONLY',report=rec(O/'REPORT_V11.md'),facts=rec(O/'FACTS_V11_01.json'),receipt=rec(O/'RECEIPT_V11_FINAL.json'),C=122,scope=122,unstarted_C=0,ASM=0,type_checks=types,non_type_checks=nonchecks,max_object=maxobj,max_sections=maxsec),ensure_ascii=False))
 except Exception:
  state.update(status='STOP_FIRST_SAVED_METADATA_CLOSE_ERROR_NO_RETRY',error=traceback.format_exc());checkpoint();print(json.dumps(state,ensure_ascii=False));raise SystemExit(1)
if __name__=='__main__':main()
