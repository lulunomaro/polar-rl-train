"""Freeze exactly the original V6 unstarted C subset. Metadata+selected pins only."""
from pathlib import Path
import copy,hashlib,json,ast
O=Path(__file__).resolve().parent
R=O.parent
V6=R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V6'
V7=R/'MOD4_DEPLOYMENT_ABI_SCOPE_STATIC_V7'

def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def save(n,v):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 scope=load(O/'PARENT_CONTINUATION_SCOPE.json')
 for name,sha in scope['V7_pins'].items():assert rec(V7/name)['SHA']==sha,name
 old=load(V6/'LITERAL_ARGV_V6_01.json');hist=load(V6/'COMPILE_RESULT_V6_01.json')
 assert rec(V6/'LITERAL_ARGV_V6_01.json')['SHA']=='50d1928a10e15f53f03ded9edee9e4a7caeba8dfe69cb0d8bb991622310c1e8c'
 assert rec(V6/'COMPILE_RESULT_V6_01.json')['SHA']=='0e6cd3773d5dad671ea13e66f54d834330fd6a6c656c2601aa1b9dbfe4632443'
 assert old['tu_count']==163 and old['C_count']==162 and old['ASM_count']==1
 assert hist['attempted_TU_ids']==[1] and hist['first_object_gate']['pass_gate'] is False
 assert hist['unstarted_TU_ids']==[i for i in old['execution_order'] if i!=1]
 byid={x['id']:x for x in old['translation_units']};assert len(byid)==163
 ids=[i for i in old['execution_order'] if i in hist['unstarted_TU_ids'] and byid[i]['language']=='C']
 asm=[i for i in hist['unstarted_TU_ids'] if byid[i]['language']=='ASM']
 assert len(ids)==161 and 1 not in ids and asm==[0] and ids==list(range(2,163))
 units=[];delta=[];sources=[];used=set()
 for i in ids:
  before=byid[i];row=copy.deepcopy(before);assert row['argv'][0]==r'C:\Keil_v5\ARM\ARMCC\bin\armcc.exe'
  assert Path(row['cwd']).is_dir() and Path(row['source']).is_file()
  actual=rec(Path(row['source']));assert actual['SHA']==row['source_pin']['SHA'],('SOURCE_DRIFT',i)
  assert actual['bytes']<=2*1024*1024
  assert row['argv'].count('-o')==1
  k=row['argv'].index('-o')+1;assert row['argv'][k]==row['output_object']
  changes={}
  for key,sub in [('output_object','objects'),('stdout','logs'),('stderr','logs')]:
   before_path=Path(row[key]);assert before_path.is_relative_to(V6/sub)
   newpath=O/sub/before_path.name;assert not newpath.exists(),newpath
   assert str(newpath).casefold() not in used;used.add(str(newpath).casefold())
   changes[key]={'old':row[key],'new':str(newpath)};row[key]=str(newpath)
  row['argv'][k]=row['output_object']
  inv=copy.deepcopy(row)
  for key in changes:inv[key]=changes[key]['old']
  inv['argv'][k]=before['argv'][k]
  assert inv==before,('NON_OUTPUT_DIFFERENCE',i)
  row['fresh_source_pin']=actual;units.append(row);sources.append(actual)
  delta.append({'id':i,'name':row['name'],'only_changed_argv_index':k,'paths':changes,'exact_row_inverse':True})
 headers=[]
 for suffix,expected in [('device_header_supplement002/device_headers/stm32f407xx.h','a0e7f720b1c7c311ceb7a8ab3afba31a35d377a7ebeb6ded3237f771d9d7b786'),('cmsis_header_overlay/cmsis_os.h','51420495a86c8aea829f63a156c475c225bf9c51429e0bb210eb35db0b1fd1ba')]:
  matches=[x for x in old['source_refs'] if x['path'].replace('\\','/').endswith(suffix)]
  assert len(matches)==1
  a=rec(Path(matches[0]['path']));assert (a['bytes'],a['SHA'])==(matches[0]['bytes'],expected);headers.append(a)
 for name in ['compile_v8_once.py','prepare_v8_once.py']:ast.parse((O/name).read_text(encoding='utf-8'),filename=name)
 refs=[rec(x) for x in [O/'PARENT_CONTINUATION_SCOPE.json',O/'METHOD.md',V6/'LITERAL_ARGV_V6_01.json',V6/'COMPILE_RESULT_V6_01.json',V6/'FIRST_OBJECT_GATE_V6_01.json',V6/'EXECUTION_LEDGER_V6_01.jsonl',V7/'REPORT.md',V7/'RECEIPT.json',V7/'scoped_attrs_v7.py',V7/'OBJECT_SCOPE_RESULT_01.json',V7/'OFFICIAL_RULES.json']]
 plan={'variant':'PARENT_NEW_V8_ORIGINAL_UNSTARTED_C_ONLY','source_refs':refs,'metadata_gate_reader':str(V7/'scoped_attrs_v7.py'),'first_object_expected_unchanged_non_type':old['first_object_expected'],'execution_order':ids,'translation_units':units,'C_count':161,'ASM_count':0,'original_ASM_id0_UNSTARTED_frozen_not_authorized':byid[0],'consumed_main_id1_excluded':True,'selected_C_fresh_pins':sources,'existing_raw_overlay_header_pins':headers,'each_TU_attempt_max':1,'new_fromelf_version_probe_link_UV_flash':0,'source_full_tree_hash':False,'old_V6_historical':{'compiler_success':1,'post_ABI_accepted_prefix':0,'pass_gate':False},'source_pin_basis':'Every selected161 C fresh hash equals saved V6 SHA; two approved overlay headers fresh equal V6. Not all indirect headers or423 tree repinned.'}
 save('LITERAL_ARGV_V8_01.json',plan)
 save('ARGV_DELTA_V8_01.json',{'source_plan':rec(V6/'LITERAL_ARGV_V6_01.json'),'rows':delta,'all161_exact_output_only_inverse':True,'original_ASM_unchanged_unstarted':True,'ignored_consumed_main':1})
 save('PREEXEC_V8_01.json',{'variant':plan['variant'],'plan':rec(O/'LITERAL_ARGV_V8_01.json'),'delta':rec(O/'ARGV_DELTA_V8_01.json'),'executor':rec(O/'compile_v8_once.py'),'preparer':rec(Path(__file__).resolve()),'sealed_reader':rec(V7/'scoped_attrs_v7.py'),'C_budget':161,'ASM_fromelf_probe_version_link':0,'execution_started':False})
 print(json.dumps({'status':'FROZEN_ALL161_OUTPUT_ONLY_ARGV_AND_SELECTED_SOURCE_PINS_BEFORE_NATIVE','plan':rec(O/'LITERAL_ARGV_V8_01.json'),'preexec':rec(O/'PREEXEC_V8_01.json'),'C':161,'ASM':0,'selected_source_bytes':sum(x['bytes'] for x in sources),'approved_header_count':len(headers)},ensure_ascii=False))
if __name__=='__main__':main()
