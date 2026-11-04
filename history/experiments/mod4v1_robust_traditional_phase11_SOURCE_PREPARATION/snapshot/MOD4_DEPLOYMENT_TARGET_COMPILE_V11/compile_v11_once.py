"""One C-only continuation. No repairs/retries/probes/fromelf/link. Minimum results first."""
from pathlib import Path
import copy,hashlib,importlib.util,json,struct,subprocess,time,traceback
O=Path(__file__).resolve().parent
R=O.parent

def rec(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def exact(ref):
 now=rec(Path(ref['path']));assert now==ref,('PIN_DRIFT',ref['path']);return now

def capacity_reason(data,message,reader):
 # Classification only after the SINGLE sealed reader call raises. No fallback qualification.
 if len(data)>reader.MAX_OBJECT:return 'OBJECT_SIZE_EXCEEDS_SEALED_65536'
 if len(data)>=52 and data[:6]==b'\x7fELF\x01\x01':
  shoff=struct.unpack_from('<I',data,32)[0];count=struct.unpack_from('<H',data,48)[0]
  if count>reader.MAX_SECTIONS:return 'SECTION_COUNT_EXCEEDS_SEALED_256'
  if message=='symbol-table bounds' and 0<count<=reader.MAX_SECTIONS and 52<=shoff and shoff+40*count<=len(data):
   for i in range(count):
    row=struct.unpack_from('<10I',data,shoff+40*i)
    if row[1]==2 and row[9]==16 and row[5]%16==0 and row[5]//16>1024:return 'SYMBOL_COUNT_EXCEEDS_SEALED_1024'
 if message in ('vendor count limit','public block limit','index list limit','attribute pair limit'):return message
 return None

def gate(data,reader,expected):
 parsed=reader.inspect_elf(data)  # Exactly one call per successful new object; no retries.
 a=parsed['attributes'];file_tags=a.scope(('FILE',0))['tags'];checks=[]
 for name in ('ELF_class','ELF_data','ELF_type','ELF_machine'):
  checks.append(dict(field=name,actual=parsed[name],expected=expected[name],pass_gate=parsed[name]==expected[name]))
 for tag,name in [(6,'CPU_arch'),(7,'CPU_profile'),(9,'THUMB_ISA_use'),(10,'FP_arch'),(27,'ABI_HardFP_use'),(28,'ABI_VFP_args'),(20,'ABI_FP_denormal')]:
  actual=file_tags.get(tag,'UNKNOWN');want=expected[name]
  ok=actual in want if isinstance(want,list) else actual==want
  checks.append(dict(field=name,tag=tag,actual=actual,expected=want,pass_gate=ok,source='ORIGINAL_V6_FILE_NON_TYPE_GATE_UNCHANGED'))
 type_checks=[]
 def typed(scope,tag,cell):
  wanted=2 if tag==18 else 1
  ok=(cell['value']==wanted and cell['classification']=='VALUE' and cell['origin_kind']=='EXPLICIT_ATTRIBUTE') or (cell['value']==0 and cell['classification']=='UNUSED' and cell['origin_kind'] in ('EXPLICIT_ATTRIBUTE','NORMATIVE_PUBLIC_DEFAULT_ZERO'))
  type_checks.append(dict(scope=scope,tag=tag,effective=cell,pass_gate=ok,allowed_nonzero=wanted,zero_is_normative_unused_not_width=True))
 for row in parsed['code_sections']:
  for tag in (18,26):typed('SECTION#'+str(row['id']),tag,row['tag'+str(tag)])
 for symbol in sorted(a.symbol_ids):
  for tag in (18,26):typed('SYMBOL#'+str(symbol),tag,a.typed(tag,('SYMBOL',symbol)))
 info={k:v for k,v in parsed.items() if k!='attributes'}
 info['public_file_explicit_tags']=file_tags
 info['raw_public_blocks']=a.raw_public_blocks
 info['vendor_blocks']=a.vendor_blocks
 info['public_explicit_scopes']=[dict(kind=k[0],index=k[1],**v) for k,v in a.scopes.items()]
 info['public_symbol_ids']=sorted(a.symbol_ids)
 info['symbol_defining_sections']=a.symbol_sections
 return dict(pass_gate=all(x['pass_gate'] for x in checks+type_checks),non_type_checks=checks,type_checks=type_checks,metadata=info,not_runtime_FPSCR_or_library_qualification=True)

def main():
 ledger_path=O/'EXECUTION_LEDGER_V11_01.jsonl';result_path=O/'COMPILE_RESULT_V11_01.json'
 if ledger_path.exists() or result_path.exists():raise RuntimeError('V11_ALREADY_STARTED_NO_RESTART_OR_RETRY')
 ledger=ledger_path.open('x',encoding='utf-8',newline='\n')
 result_path.open('x',encoding='utf-8').close()
 state=dict(status='EXECUTOR_ENTERED_BEFORE_NATIVE',variant='PARENT_NEW_V11_REMAINING_C_ONLY_SEALED_V10',native_invocations=[],TU_results=[],attempted_TU_ids=[],scope_accepted_prefix=[],failed_TU=None,reader_call_count=0,original_V6_record=dict(compiler_success=1,post_ABI_accepted_prefix=0,pass_gate=False,unchanged=True),inherited_main_not_recompiled=True,V7_main_static_resolution_separate=True,ASM_unstarted_ids=[0],ASM_compile_count=0,fromelf_probe_version_link_UV_flash=0,no_robot_old40_oldQA_Git_agents_root_goal=True)
 order=[];byid={};plan=None
 def event(value):
  ledger.write(json.dumps(value,ensure_ascii=False,allow_nan=False)+'\n');ledger.flush()
 def checkpoint():
  state['C_compile_attempts']=len(state['attempted_TU_ids'])
  state['compiler_exit0_count']=sum(x.get('exit')==0 for x in state['TU_results'])
  state['new_compile_success_with_nonempty_object_count']=sum(x.get('exit')==0 and x.get('object_nonempty',False) for x in state['TU_results'])
  state['scope_accepted_count']=len(state['scope_accepted_prefix'])
  state['each_C_at_most_once']=len(state['attempted_TU_ids'])==len(set(state['attempted_TU_ids']))
  state['unstarted_C_ids']=[i for i in order if i not in state['attempted_TU_ids']]
  state['unstarted_count_C_plus_ASM']=len(state['unstarted_C_ids'])+1
  with result_path.open('w',encoding='utf-8',newline='\n') as f:json.dump(state,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush()
 checkpoint()
 try:
  pre=load(O/'PREEXEC_V11_01.json')
  for key in ('plan','delta','executor','preparer','sealed_reader'):exact(pre[key])
  assert pre['executor']['path']==str(Path(__file__).resolve())
  plan=load(O/'LITERAL_ARGV_V11_01.json');order=plan['execution_order'];byid={x['id']:x for x in plan['translation_units']}
  assert order==list(range(41,163)) and len(byid)==122 and all(byid[i]['language']=='C' for i in order)
  assert plan['each_TU_attempt_max']==1 and plan['ASM_count']==0
  for ref in plan['source_refs']+plan['existing_raw_overlay_header_pins']+plan['selected_C_fresh_pins']:exact(ref)
  old=load(R/'MOD4_DEPLOYMENT_TARGET_COMPILE_V6'/'LITERAL_ARGV_V6_01.json')
  oldbyid={x['id']:x for x in old['translation_units']}
  assert oldbyid[0]==plan['original_ASM_id0_UNSTARTED_frozen_not_authorized']
  for i in order:
   row=byid[i];before=oldbyid[i];inv=copy.deepcopy(row);inv.pop('fresh_source_pin')
   k=inv['argv'].index('-o')+1
   for field in ('output_object','stdout','stderr'):
    assert Path(row[field]).is_relative_to(O) and not Path(row[field]).exists()
    inv[field]=before[field]
   inv['argv'][k]=before['argv'][k];assert inv==before
   assert row['argv'][0]==r'C:\Keil_v5\ARM\ARMCC\bin\armcc.exe'
  spec=importlib.util.spec_from_file_location('v11_sealed_v10_attrs',plan['metadata_gate_reader']);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
  assert reader.MAX_OBJECT==1048576 and reader.MAX_SECTIONS==4096
  for sub in ('objects','logs','attributes'):(O/sub).mkdir(exist_ok=True)
  state.update(status='FROZEN_PLAN_GUARDS_PASSED_READY_FIRST_C',plan=pre['plan'],executor=pre['executor'],sealed_reader=pre['sealed_reader']);checkpoint()
  event(dict(event='ALL122_PREFLIGHT_PINS_AND_OUTPUT_ONLY_INVERSE_PASSED',C_budget=122))
  for i in order:
   row=byid[i];src=Path(row['source']);obj=Path(row['output_object']);actual=rec(src)
   if actual!=row['fresh_source_pin']:
    state.update(status='STOP_SOURCE_PIN_DRIFT_BEFORE_C',failed_TU=dict(id=i,name=row['name'],not_compiled=True,actual=actual));break
   assert not obj.exists()
   state['attempted_TU_ids'].append(i)
   item=dict(id=i,name=row['name'],source_before=actual,argv=row['argv'],cwd=row['cwd'],exit=None,object_nonempty=False,reader_called=False)
   state['TU_results'].append(item)
   begin=time.monotonic_ns();native=dict(kind='REAL_C_TU_COMPILE_ONLY',id=i,name=row['name'],argv=row['argv'],cwd=row['cwd'],stdout=row['stdout'],stderr=row['stderr'],start_host_monotonic_ns=begin)
   state['native_invocations'].append(native);event(dict(event='NATIVE_ATTEMPT',**native));checkpoint()
   with Path(row['stdout']).open('xb') as out,Path(row['stderr']).open('xb') as err:
    cp=subprocess.run(row['argv'],cwd=row['cwd'],stdout=out,stderr=err,check=False)
   native.update(exit=cp.returncode,elapsed_host_ns_not_WCET=time.monotonic_ns()-begin)
   item.update(exit=cp.returncode,stdout=rec(Path(row['stdout'])),stderr=rec(Path(row['stderr'])),source_after=rec(src),object_nonempty=obj.is_file() and obj.stat().st_size>0)
   if obj.is_file():item['object']=rec(obj)
   event(dict(event='NATIVE_RETURN',**native));state['status']='NATIVE_RETURN_SAVED_BEFORE_ANY_READER';checkpoint()
   if cp.returncode!=0:state.update(status='STOP_FIRST_REAL_COMPILER_ERROR',failed_TU=item);break
   if not item['object_nonempty']:state.update(status='STOP_COMPILER_EXIT0_MISSING_OR_EMPTY_OBJECT',failed_TU=item);break
   if item['source_after']!=actual:state.update(status='STOP_SOURCE_PIN_DRIFT_AFTER_C',failed_TU=item);break
   data=obj.read_bytes();assert hashlib.sha256(data).hexdigest()==item['object']['SHA']
   state['reader_call_count']+=1;item['reader_called']=True;event(dict(event='SINGLE_SEALED_V10_READER_CALL',id=i,object=item['object']));checkpoint()
   attrpath=O/'attributes'/('%03d_scope.json'%i)
   try:
    result=gate(data,reader,plan['first_object_expected_unchanged_non_type'])
   except reader.ScopeConflict as exc:
    result=dict(pass_gate=False,classification='SCOPE_CONFLICT_STOP',error=str(exc));state['status']='SCOPE_CONFLICT_STOP'
   except reader.ParseError as exc:
    cap=capacity_reason(data,str(exc),reader)
    result=dict(pass_gate=False,classification='READER_CAPACITY_STOP' if cap else 'UNSUPPORTED_OR_MALFORMED_METADATA_STOP',error=str(exc),capacity_detail=cap,object_bytes=len(data));state['status']=result['classification']
   with attrpath.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
   item['scope_record']=rec(attrpath);item['scope_pass']=result['pass_gate']
   if not result['pass_gate']:
    if state['status']=='NATIVE_RETURN_SAVED_BEFORE_ANY_READER':state['status']='STOP_UNKNOWN_OR_UNEXPECTED_NON_TYPE_OR_TYPE_ABI'
    state['failed_TU']=item;event(dict(event='FIRST_METADATA_STOP',id=i,status=state['status'],scope_record=item['scope_record']));checkpoint();break
   state['scope_accepted_prefix'].append(dict(id=i,name=row['name'],object=item['object'],scope_record=item['scope_record']))
   state['status']='C_PREFIX_ACCEPTED_BEFORE_NEXT_C';event(dict(event='NEW_C_SCOPE_ACCEPTED',id=i,name=row['name']));checkpoint()
  else:state['status']='ALL122_NEW_C_OBJECTS_SCOPE_ACCEPTED_NOT_LINKED_ASM_UNSTARTED'
 except Exception:
  state.update(status='STOP_EXECUTOR_EXCEPTION_NO_RETRY',executor_exception=traceback.format_exc());event(dict(event='EXECUTOR_EXCEPTION',error=state['executor_exception']))
 finally:
  if plan is not None:
   try:
    for ref in plan['source_refs']+plan['existing_raw_overlay_header_pins']:exact(ref)
    state['end_small_refs_and_two_headers_unchanged']=True
   except Exception:state['end_pin_error']=traceback.format_exc();state['status_before_end_pin_error']=state['status'];state['status']='STOP_INPUT_DRIFT_AT_WAVE_END'
  checkpoint();ledger.close()
 print(json.dumps(dict(status=state['status'],result=rec(result_path),C_attempts=state['C_compile_attempts'],new_compile_success=state['new_compile_success_with_nonempty_object_count'],new_scope_accepted=state['scope_accepted_count'],reader_calls=state['reader_call_count'],failed_name=state['failed_TU'].get('name') if state['failed_TU'] else None,unstarted_C=len(state['unstarted_C_ids']),ASM=0,fromelf_probe_version_link=0),ensure_ascii=False))
 raise SystemExit(0 if state['status']=='ALL122_NEW_C_OBJECTS_SCOPE_ACCEPTED_NOT_LINKED_ASM_UNSTARTED' else 1)
if __name__=='__main__':main()
