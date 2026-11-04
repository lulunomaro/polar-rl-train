"""Saved V8 result, exact-delta, old pins and object/log hash close; no native/parser rerun."""
from pathlib import Path
import copy,hashlib,json,re
O=Path(__file__).resolve().parent
R=O.parent

def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def exact(ref):assert rec(Path(ref['path']))==ref,ref['path']
def save(name,value):
 with (O/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def relative(p):return Path(p).resolve().relative_to(O).as_posix()
def link(label,p):return '['+label+'](<'+relative(p)+'>)'
def main():
 pre=load(O/'PREEXEC_V8_01.json');plan=load(O/'LITERAL_ARGV_V8_01.json');result=load(O/'COMPILE_RESULT_V8_01.json');repair=load(O/'SUFFIX_REPAIR_RECEIPT_001.json')
 for key in ('plan','delta','executor','preparer','sealed_reader'):exact(pre[key])
 for ref in plan['source_refs']+plan['existing_raw_overlay_header_pins']:exact(ref)
 assert result['end_small_refs_and_two_headers_unchanged'] is True
 assert 'executor_exception' not in result and result['status'] not in ('EXECUTOR_ENTERED_BEFORE_NATIVE','NATIVE_RETURN_SAVED_BEFORE_ANY_READER','C_PREFIX_ACCEPTED_BEFORE_NEXT_C')
 for ref in repair['first_failure_records_unchanged']:
  exact(ref['current']);exact(ref['original_snapshot']);assert Path(ref['current']['path']).read_bytes()==Path(ref['original_snapshot']['path']).read_bytes()
 exact(repair['parent_scope']);exact(repair['new_preparer']);exact(repair['old_preparer']);exact(repair['patch'])
 before=Path(repair['old_preparer']['path']).read_bytes();after=Path(repair['new_preparer']['path']).read_bytes()
 assert after.replace(b'EXECUTION_LEDGER_V6_01.jsonl\'',b'EXECUTION_LEDGER_V6_01.json\'',1)==before
 hist=load(R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V6'/'COMPILE_RESULT_V6_01.json');old=load(R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V6'/'LITERAL_ARGV_V6_01.json')
 oldby={x['id']:x for x in old['translation_units']};by={x['id']:x for x in plan['translation_units']}
 assert plan['execution_order']==[i for i in hist['unstarted_TU_ids'] if oldby[i]['language']=='C']==list(range(2,163))
 for i in plan['execution_order']:
  row=copy.deepcopy(by[i]);row.pop('fresh_source_pin');k=row['argv'].index('-o')+1
  for field in ('output_object','stdout','stderr'):row[field]=oldby[i][field]
  row['argv'][k]=oldby[i]['argv'][k];assert row==oldby[i]
 assert plan['original_ASM_id0_UNSTARTED_frozen_not_authorized']==oldby[0]
 ids=result['attempted_TU_ids'];assert ids==plan['execution_order'][:len(ids)] and len(set(ids))==len(ids)<=161
 assert result['C_compile_attempts']==len(ids) and result['ASM_compile_count']==0
 assert result['unstarted_C_ids']==[i for i in plan['execution_order'] if i not in ids]
 assert len(result['native_invocations'])==len(ids) and all(x['kind']=='REAL_C_TU_COMPILE_ONLY' for x in result['native_invocations'])
 accepted=result['scope_accepted_prefix'];assert [x['id'] for x in accepted]==ids[:len(accepted)]
 assert result['original_V6_record']==dict(compiler_success=1,post_ABI_accepted_prefix=0,pass_gate=False,unchanged=True)
 objects=[];gates=[]
 for item in result['TU_results']:
  row=by[item['id']];assert item['argv']==row['argv'] and item['cwd']==row['cwd']
  assert item['source_before']==row['fresh_source_pin'] and item['source_after']==item['source_before']
  exact(item['stdout']);exact(item['stderr']);exact(item['source_after'])
  if 'object' in item:exact(item['object']);objects.append(item['object'])
  if 'scope_record' in item:exact(item['scope_record']);gates.append(load(Path(item['scope_record']['path'])))
 assert result['reader_call_count']==sum(x.get('reader_called',False) for x in result['TU_results'])
 assert result['new_compile_success_with_nonempty_object_count']==sum(x['exit']==0 and x['object_nonempty'] for x in result['TU_results'])
 assert result['scope_accepted_count']==len(accepted)
 assert sum(x.get('scope_pass',False) for x in result['TU_results'])==len(accepted)
 assert sum(x.get('pass_gate',False) for x in gates)==len(accepted)
 ledger=[json.loads(s) for s in (O/'EXECUTION_LEDGER_V8_01.jsonl').read_text(encoding='utf-8').splitlines()]
 assert sum(x['event']=='NATIVE_ATTEMPT' for x in ledger)==len(ids)
 assert sum(x['event']=='SINGLE_SEALED_V7_READER_CALL' for x in ledger)==result['reader_call_count']
 failed=result['failed_TU'];failed_gate=gates[-1] if failed and gates and failed.get('reader_called') else None
 facts={'status':'SAVED_EVIDENCE_VERIFIED_NOT_FULL_BUILD','actual_native_stop':result['status'],'C_attempts':len(ids),'new_compile_success_with_object':result['new_compile_success_with_nonempty_object_count'],'new_scope_accepted_prefix':len(accepted),'sealed_reader_calls':result['reader_call_count'],'unstarted_C':len(result['unstarted_C_ids']),'ASM_unstarted':1,'ASM_fromelf_version_probe_link_UV_flash':0,'consumed_main_recompile':0,'old_V6_history_unchanged':result['original_V6_record'],'failed_TU':failed,'failed_gate':failed_gate,'compile_objects':objects,'preparation_history':{'attempt01_failed':'own metadata .json/.jsonl typo before any native, saved unchanged','exact_parent_approved_suffix_derivation':repair,'one_new_suffix_freeze_success':True},'all161_argv_exact_inverse':True,'old_small_ref_count':len(plan['source_refs']),'selected_C_fresh_pins_pre_native':161,'two_existing_headers_unchanged':True,'not_all_indirect_header_dependency_proof':True,'close_has_no_reader_native_or_old_QA_calls':True,'PH10_excluded':True}
 save('FACTS_V8_01.json',facts)
 status='PARTIAL_V8_PREFIX_STOPPED_PRESERVED_NO_RETRY_NO_LINK' if len(accepted)<161 else 'ALL161_NEW_C_SCOPE_PREFIX_SEALED_NOT_LINKED_ASM_UNSTARTED'
 failed_name=failed['name'] if failed and 'name' in failed else '无'
 failed_label='['+failed_name+'](<'+Path(failed['source_before']['path']).as_posix()+'>)' if failed else '无'
 lines=['# V8：原UNSTARTED C-only独立前缀实际结果','',f"**{status}**；先落最低result/ledger，后作本saved-only报告；旧V6/V7不改账。",'', '## 本轮实际计数','', '| 项 | 真实结果 |','|---|---:|',f"| 新C尝试／exit0且保有非空物件 | {len(ids)}／{result['new_compile_success_with_nonempty_object_count']} |",f"| 新scope认可prefix／sealed reader调用 | {len(accepted)}／{result['reader_call_count']} |",f"| 未启动新C／原ASM | {len(result['unstarted_C_ids'])}／1 |",'| 重编main／ASM/fromelf/version/probe/link/UV/flash | 0／0 |','',f"- 首个停止类别：`{result['status']}`；对应TU：{failed_label}。详见{link('最低编译结果',O/'COMPILE_RESULT_V8_01.json')}、{link('执行账本',O/'EXECUTION_LEDGER_V8_01.jsonl')}、{link('首次wrapper日志',O/'compile_01.log')}。"]
 if failed:
  lines.append('- 原始stdout／stderr：'+link('stdout',Path(failed['stdout']['path']))+' / '+link('stderr',Path(failed['stderr']['path']))+'；未编辑诊断、补header或重编。')
 if failed and 'object' in failed:
  lines.append('- 保留编译物件：'+link('停止物件',Path(failed['object']['path']))+'，'+str(failed['object']['bytes'])+' B；SHA `'+failed['object']['SHA']+'`。')
 if failed_gate and failed_gate.get('capacity_detail')=='SECTION_COUNT_EXCEEDS_SEALED_256':
  lines.append('- 本例物件58720B未超64KiB；容量分类来自e_shnum超过256。最小stop记录未保存具体section数；本轮没有再解析/扩cap补齐属性，不由容量停止推断ABI不兼容。')
 if failed_gate:
  lines.append('- '+link('首个不认可物件的完整scope/错误记录',Path(failed['scope_record']['path']))+'：成功编译与该gate认可分列；容量或格式不支持不被冒充为真实ABI不兼容。')
  if 'classification' in failed_gate:lines.append('- reader stop分类：`'+failed_gate['classification']+'`；原始错误：`'+failed_gate['error']+'`；capacity detail：`'+str(failed_gate.get('capacity_detail'))+'`。')
  else:
   bad=[x for x in failed_gate['non_type_checks']+failed_gate['type_checks'] if not x['pass_gate']]
   for entry in bad[:12]:
    if 'field' in entry:lines.append(f"- 原非type gate：`{entry['field']}` actual=`{entry['actual']}`，expected=`{entry['expected']}`；未套用新type规则放宽。")
    else:lines.append(f"- 类型gate：`{entry['scope']}` tag{entry['tag']} actual=`{entry['effective']['value']}`，classification=`{entry['effective']['classification']}`，完整来源保留原JSON。")
 lines+=['','## 执行前锁定与首次metadata失败保留','', '- '+link('父C-only grant',O/'PARENT_CONTINUATION_SCOPE.json')+'与'+link('唯一suffix修订grant',O/'PARENT_METADATA_SUFFIX_REPAIR_001.json')+'均先读。catalog无匹配ARM/ELF skill，采用文件/Python标准库和指定installed ARMCC5u6；无ARMCLANG迁移。','- 首次prepare因我方误写旧ledger扩展名退出1，在冻结前0 native；'+link('原partial报告',O/'PRE_NATIVE_STOP_REPORT_01.md')+'、'+link('原最低stop记录',O/'PRE_NATIVE_STOP_RESULT_01.json')+'与first script/log/snapshot原字节保留。','- 后续仅父批的`.json`→`.jsonl`一字节派生；'+link('patch',O/'PREPARER_SUFFIX_ONLY_001.patch')+'及'+link('inverse/SHA receipt',O/'SUFFIX_REPAIR_RECEIPT_001.json')+'证明原executed脚本未覆盖、exact byte inverse成立。一次新metadata freeze成功后才进入本唯一native wave。','- '+link('冻结PREEXEC',O/'PREEXEC_V8_01.json')+'先于native，含'+link('161 argv/source计划',O/'LITERAL_ARGV_V8_01.json')+'及'+link('路径逆变换',O/'ARGV_DELTA_V8_01.json')+'。唯一argv变化为-o物件路径；stdout/stderr改V8，原CWD/includes/两overlay/macros/flags/CPU与warning policy完全保留。','- 所选161 C共3227070B在首个native前fresh比V6 saved pins；two raw overlay headers前后pin不变，执行TU源before/after相等。未做423全树或全部间接header hash/重新解析project。','', '## 属性策略、历史和资格边界','', '- 新成功对象各只调用sealed V7 reader一次；保留64KiB/256section/1024symbol等上限，未扩cap、无fromelf fallback/额外probe/测试循环。每个EXEC section和真实SYMBOL的18只接受2或规范UNUSED0，26只接受1或规范UNUSED0；完整scope来源留存。','- 原V6非type FILE gate未改。规范UNUSED0不是实际sizeof0；现存SYMBOL数量及真实metadata覆盖以各物件JSON为准，不把旧四个synthetic fixture算本轮QA。','- 原V6历史仍compile成功1/postABI认可prefix0/gate=false；V7对既有main的静态解释独立保留。本轮不重编main、不回改旧账，也不把继承main加进新scope-prefix计数。','- 原ASM计划仅冻结、始终UNSTARTED。所有后缀在首次错误/容量/未知处停止；后续修复、余下C/ASM、库ABI及link均待独立决定。','- compile-only不是全target/libABI/link地址容量/固件/target执行/FPSCR/WCET/实际MOD4校准；旧MF9025/LK与新Damiao映射仍未绑定。无机器人/PHY/old40/oldQA/Git/新agent/root-goal动作，V8和suffix修订全部在PH10 cutoff外。']
 text='\n'.join(lines)+'\n';assert len(lines)<=120
 with (O/'REPORT_V8.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
 for target in re.findall(r'\]\(<([^>]+)>\)',text):assert (O/target.split('#',1)[0]).is_file(),target
 artifact_names=['METHOD.md','PARENT_CONTINUATION_SCOPE.json','PARENT_METADATA_SUFFIX_REPAIR_001.json','PREEXEC_V8_01.json','LITERAL_ARGV_V8_01.json','ARGV_DELTA_V8_01.json','SUFFIX_REPAIR_RECEIPT_001.json','COMPILE_RESULT_V8_01.json','EXECUTION_LEDGER_V8_01.jsonl','compile_01.log','FACTS_V8_01.json','REPORT_V8.md','close_v8_once.py']
 receipt={'status':status,'report_lines':len(lines),'counts':{k:facts[k] for k in ['C_attempts','new_compile_success_with_object','new_scope_accepted_prefix','sealed_reader_calls','unstarted_C','ASM_unstarted','ASM_fromelf_version_probe_link_UV_flash','consumed_main_recompile']},'old_V6_unchanged':result['original_V6_record'],'old_small_refs_verified':plan['source_refs'],'two_overlay_headers_verified':plan['existing_raw_overlay_header_pins'],'artifacts':[rec(O/n) for n in artifact_names],'actual_native_only_installed_armcc':True,'metadata_close_no_reader_or_native_rerun':True,'first_prepare_failure_not_upgraded':True,'full_target_qualified':False,'further_native_authorized':False}
 save('RECEIPT_V8_FINAL.json',receipt)
 print(json.dumps({'status':status,'report':rec(O/'REPORT_V8.md'),'receipt':rec(O/'RECEIPT_V8_FINAL.json'),'facts':rec(O/'FACTS_V8_01.json'),'counts':receipt['counts']},ensure_ascii=False))
if __name__=='__main__':main()
