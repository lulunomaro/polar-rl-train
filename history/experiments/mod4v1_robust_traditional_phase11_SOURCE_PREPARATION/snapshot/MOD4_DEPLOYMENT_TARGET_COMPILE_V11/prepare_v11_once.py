"""Freeze actual remaining 122 C, exact output-only argv and narrow executor derivation."""
from pathlib import Path
import ast,copy,difflib,hashlib,json,traceback
O=Path(__file__).resolve().parent;R=O.parent
V6=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V6';V8=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V8';V10=R/'MOD4_DEPLOYMENT_SCOPED_READER_V10'
def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(n,v):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 marker=O/'PREPARATION_RESULT_01.json'
 with marker.open('x',encoding='utf-8') as f:f.write('{}\n')
 result=dict(status='METADATA_PREPARATION_STARTED_BEFORE_NATIVE',native_calls=0,old_object_reads=0)
 def checkpoint():
  with marker.open('w',encoding='utf-8',newline='\n') as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush()
 checkpoint()
 try:
  p8=V8/'LITERAL_ARGV_V8_01.json';h8=V8/'COMPILE_RESULT_V8_01.json';p6=V6/'LITERAL_ARGV_V6_01.json';ex8=V8/'compile_v8_once.py';reader=V10/'scoped_attrs_v10.py'
  assert rec(p8)['SHA']=='546dacbcc72983f9a9bd0265d435662a03fea228fee742983ab4809721c13874'
  assert rec(h8)['SHA']=='06b0201840d1465005b4e663a2675af3fd73315f7085aec265d3abe87f82d79d'
  assert rec(p6)['SHA']=='50d1928a10e15f53f03ded9edee9e4a7caeba8dfe69cb0d8bb991622310c1e8c'
  assert rec(ex8)['SHA']=='5ba3874d0929150fe56858c772ad09df3c46e059af832ab20c658813ddced7ab'
  assert rec(reader)==dict(path=str(reader),bytes=11180,SHA='0a6437d1e5e3c56961547e3c3758a651a4c9e8ad36aeba7b1f1e71b282f522d0')
  old8=load(p8);hist=load(h8);old6=load(p6);review=load(V10/'STUDY_RESULT_MIN_01.json')
  assert hist['attempted_TU_ids']==list(range(2,41)) and hist['scope_accepted_count']==38 and hist['status']=='READER_CAPACITY_STOP'
  assert hist['new_compile_success_with_nonempty_object_count']==39 and hist['failed_TU']['id']==40
  ids=hist['unstarted_C_ids'];assert ids==list(range(41,163)) and len(ids)==122 and hist['ASM_unstarted_ids']==[0]
  assert review['TU40_gate'] is True and review['actual_object_parse_calls']==1 and len(review['fixture_pass_prefix'])==6
  old8by={x['id']:x for x in old8['translation_units']};old6by={x['id']:x for x in old6['translation_units']}
  assert ids==[i for i in old8['execution_order'] if i not in hist['attempted_TU_ids']]
  assert old8['original_ASM_id0_UNSTARTED_frozen_not_authorized']==old6by[0]
  source=ex8.read_bytes();new=source
  substitutions=[
   (b'EXECUTION_LEDGER_V8_01.jsonl',b'EXECUTION_LEDGER_V11_01.jsonl'),
   (b'COMPILE_RESULT_V8_01.json',b'COMPILE_RESULT_V11_01.json'),
   (b'V8_ALREADY_STARTED_NO_RESTART_OR_RETRY',b'V11_ALREADY_STARTED_NO_RESTART_OR_RETRY'),
   (b'PARENT_NEW_V8_ORIGINAL_UNSTARTED_C_ONLY',b'PARENT_NEW_V11_REMAINING_C_ONLY_SEALED_V10'),
   (b'PREEXEC_V8_01.json',b'PREEXEC_V11_01.json'),
   (b'LITERAL_ARGV_V8_01.json',b'LITERAL_ARGV_V11_01.json'),
   (b'order==list(range(2,163)) and len(byid)==161',b'order==list(range(41,163)) and len(byid)==122'),
   (b"'v8_sealed_v7_attrs'",b"'v11_sealed_v10_attrs'"),
   (b'reader.MAX_OBJECT==65536 and reader.MAX_SECTIONS==256',b'reader.MAX_OBJECT==1048576 and reader.MAX_SECTIONS==4096'),
   (b'ALL161_PREFLIGHT_PINS_AND_OUTPUT_ONLY_INVERSE_PASSED',b'ALL122_PREFLIGHT_PINS_AND_OUTPUT_ONLY_INVERSE_PASSED'),
   (b'C_budget=161',b'C_budget=122'),
   (b'SINGLE_SEALED_V7_READER_CALL',b'SINGLE_SEALED_V10_READER_CALL'),
   (b'ALL161_NEW_C_OBJECTS_SCOPE_ACCEPTED_NOT_LINKED_ASM_UNSTARTED',b'ALL122_NEW_C_OBJECTS_SCOPE_ACCEPTED_NOT_LINKED_ASM_UNSTARTED')]
  replacements=[]
  for a,b in substitutions:
   n=new.count(a);assert n>0,('DERIVATION_TOKEN_MISSING',a)
   assert b not in new;new=new.replace(a,b);replacements.append(dict(old=a.decode(),new=b.decode(),occurrences=n))
  inverse=new
  for x in reversed(replacements):
   assert inverse.count(x['new'].encode())==x['occurrences'];inverse=inverse.replace(x['new'].encode(),x['old'].encode())
  assert inverse==source
  oldast=ast.parse(source.decode('utf-8'));newast=ast.parse(new.decode('utf-8'))
  funcs=lambda tree:{n.name:ast.dump(n) for n in tree.body if isinstance(n,ast.FunctionDef)}
  assert funcs(oldast)['gate']==funcs(newast)['gate'] and funcs(oldast)['capacity_reason']==funcs(newast)['capacity_reason']
  assert ast.dump(ast.parse(inverse.decode('utf-8')))==ast.dump(oldast)
  execpath=O/'compile_v11_once.py'
  with execpath.open('xb') as f:f.write(new)
  with (O/'EXECUTOR_ONLY.patch').open('x',encoding='utf-8',newline='\n') as f:f.write(''.join(difflib.unified_diff(source.decode().splitlines(True),new.decode().splitlines(True),fromfile='sealed_V8_executor',tofile='new_V11_executor')))
  derivation=dict(status='EXACT_PLAN_SCOPE_READER_VERSION_DERIVATION_NO_GATE_CHANGE',old=rec(ex8),new=rec(execpath),substitutions=replacements,raw_byte_inverse_exact=True,AST_inverse_exact=True,pure_gate_AST_identical=True,capacity_reason_AST_identical=True,capacity_classifier_labels_are_legacy_not_actual_new_limits=True)
  save('EXECUTOR_DERIVATION_01.json',derivation)
  units=[];delta=[];pins=[];used=set()
  for i in ids:
   before=old8by[i];base=old6by[i];row=copy.deepcopy(before)
   assert row['language']=='C' and row['argv'][0]==r'C:\Keil_v5\ARM\ARMCC\bin\armcc.exe'
   assert Path(row['cwd']).is_dir() and row['source']==base['source'] and row['cwd']==base['cwd']
   actual=rec(Path(row['source']));assert actual==before['fresh_source_pin'] and actual['SHA']==base['source_pin']['SHA'],('SOURCE_DRIFT',i)
   assert actual['bytes']<=2*1024*1024 and row['argv'].count('-o')==1
   k=row['argv'].index('-o')+1;assert row['argv'][k]==row['output_object'];changes={}
   for key,sub in [('output_object','objects'),('stdout','logs'),('stderr','logs')]:
    oldpath=Path(row[key]);assert oldpath.is_relative_to(V8/sub)
    newpath=O/sub/oldpath.name;assert not newpath.exists() and str(newpath).casefold() not in used
    used.add(str(newpath).casefold());changes[key]=dict(old=row[key],new=str(newpath));row[key]=str(newpath)
   row['argv'][k]=row['output_object'];row['fresh_source_pin']=actual
   inv=copy.deepcopy(row)
   for key in changes:inv[key]=changes[key]['old']
   inv['argv'][k]=before['argv'][k];assert inv==before,('V8_NON_OUTPUT_DIFFERENCE',i)
   inv6=copy.deepcopy(row);inv6.pop('fresh_source_pin')
   for key in changes:inv6[key]=base[key]
   inv6['argv'][k]=base['argv'][k];assert inv6==base,('V6_NON_OUTPUT_DIFFERENCE',i)
   units.append(row);pins.append(actual);delta.append(dict(id=i,name=row['name'],paths=changes,only_changed_argv_index=k,exact_V8_inverse=True,exact_V6_inverse=True))
  headers=[]
  for h in old8['existing_raw_overlay_header_pins']:
   now=rec(Path(h['path']));assert now==h;headers.append(now)
  assert len(headers)==2 and {h['bytes'] for h in headers}=={1350860,53065}
  refs=[rec(p) for p in [O/'PARENT_CONTINUATION_SCOPE.json',O/'METHOD.md',p8,h8,p6,V8/'FACTS_V8_01.json',V8/'RECEIPT_V8_FINAL.json',ex8,reader,V10/'REPORT.md',V10/'RECEIPT.json',V10/'STUDY_RESULT_MIN_01.json',O/'EXECUTOR_DERIVATION_01.json']]
  plan=dict(variant='PARENT_NEW_V11_REMAINING_C_ONLY_SEALED_V10',source_refs=refs,metadata_gate_reader=str(reader),first_object_expected_unchanged_non_type=old8['first_object_expected_unchanged_non_type'],execution_order=ids,translation_units=units,C_count=122,ASM_count=0,original_ASM_id0_UNSTARTED_frozen_not_authorized=old6by[0],consumed_main_and_ids2_to40_excluded=True,selected_C_fresh_pins=pins,existing_raw_overlay_header_pins=headers,each_TU_attempt_max=1,new_fromelf_version_probe_link_UV_flash=0,source_full_tree_hash=False,source_pin_basis='Only these122 C fresh hashes equal both savedV8 and savedV6; two original raw overlays. Not423 full tree.',inherited_assessments_separate=dict(V6_compile1_historical_gateFalse_unchanged=True,V8_compile39_scope38_capacity_TU40_unchanged=True,V10_TU40_static_new_gateTrue_not_recompile=True))
  save('LITERAL_ARGV_V11_01.json',plan)
  save('ARGV_DELTA_V11_01.json',dict(source_plan_V8=rec(p8),source_plan_V6=rec(p6),rows=delta,all122_output_only_inverse_to_V8_and_V6=True,unstarted_source_is_actual_V8_result=rec(h8),excluded_consumed_main_and_ids2_to40=True,ASM0_excluded=True))
  for p in [Path(__file__).resolve(),execpath]:ast.parse(p.read_bytes().decode('utf-8'))
  save('PREEXEC_V11_01.json',dict(variant=plan['variant'],plan=rec(O/'LITERAL_ARGV_V11_01.json'),delta=rec(O/'ARGV_DELTA_V11_01.json'),executor=rec(execpath),preparer=rec(Path(__file__).resolve()),sealed_reader=rec(reader),C_budget=122,ASM_fromelf_probe_version_link=0,execution_started=False))
  result.update(status='FROZEN_ALL122_BEFORE_ANY_NATIVE',plan=rec(O/'LITERAL_ARGV_V11_01.json'),preexec=rec(O/'PREEXEC_V11_01.json'),executor_derivation=rec(O/'EXECUTOR_DERIVATION_01.json'),C=122,ASM=0,selected_source_bytes=sum(x['bytes'] for x in pins),raw_headers=2,gate_AST_unchanged=True,byte_AST_inverse_exact=True)
 except Exception:
  result.update(status='STOP_FIRST_METADATA_ERROR_NO_RETRY_NO_NATIVE',error=traceback.format_exc());checkpoint();print(json.dumps(result,ensure_ascii=False));raise SystemExit(1)
 checkpoint();print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
